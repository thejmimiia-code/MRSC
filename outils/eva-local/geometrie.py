"""Extraction/atlas sur CPU pour éviter toolkit CUDA, compilation et OpenGL.

Le réseau TripoSR reste exécuté sur le GPU. Ce module ne crée pas de rig.
"""
import importlib.machinery
import sys
import types


def installer_marching_cubes_cpu():
    import numpy as np
    import torch
    from skimage.measure import marching_cubes

    def marcher(level, seuil):
        data = level.detach().float().cpu().numpy()
        vertices, faces, _normals, _values = marching_cubes(data, level=seuil)
        # MarchingCubeHelper de TripoSR inverse ensuite les axes 0 et 2.
        # Les inverser ici conserve les coordonnées de la grille de skimage.
        return (torch.from_numpy(vertices[:, [2,1,0]].copy()),
                torch.from_numpy(np.asarray(faces, dtype=np.int64).copy()))

    module = types.ModuleType('torchmcubes')
    module.__spec__ = importlib.machinery.ModuleSpec('torchmcubes', loader=None)
    module.marching_cubes = marcher
    sys.modules['torchmcubes'] = module


def rasteriser_positions(vertices, faces, uvs, resolution):
    """Associe à chaque texel couvert une position du maillage (pas une photo projetée)."""
    import numpy as np
    vertices = np.asarray(vertices, dtype=np.float32)
    faces = np.asarray(faces, dtype=np.int64)
    uvs = np.asarray(uvs, dtype=np.float32)
    if resolution < 8 or resolution > 2048:
        raise ValueError('Résolution atlas hors limites.')
    if vertices.ndim != 2 or vertices.shape[1] != 3 or uvs.shape != (len(vertices),2):
        raise ValueError('Positions ou UV invalides.')
    if not np.isfinite(vertices).all() or not np.isfinite(uvs).all():
        raise ValueError('Valeurs non finies.')
    if faces.ndim != 2 or faces.shape[1] != 3 or faces.min() < 0 or faces.max() >= len(vertices):
        raise ValueError('Indices invalides.')
    if (uvs < -1e-5).any() or (uvs > 1.00001).any():
        raise ValueError('UV hors atlas.')
    pixels = np.column_stack((uvs[:,0]*resolution, (1-uvs[:,1])*resolution))
    positions = np.zeros((resolution,resolution,3), dtype=np.float32)
    masque = np.zeros((resolution,resolution), dtype=bool)
    for face in faces:
        tri = pixels[face]
        lo = np.maximum(np.floor(tri.min(axis=0)).astype(int),0)
        hi = np.minimum(np.ceil(tri.max(axis=0)).astype(int),resolution-1)
        if (hi < lo).any():
            continue
        (ax,ay),(bx,by),(cx,cy) = tri
        den = (by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(den) < 1e-10:
            continue
        xx,yy = np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
        w0 = ((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/den
        w1 = ((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/den
        w2 = 1-w0-w1
        inside = (w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6)
        py,px = np.where(inside)
        if not len(px):
            continue
        points = w0[inside,None]*vertices[face[0]]+w1[inside,None]*vertices[face[1]]+w2[inside,None]*vertices[face[2]]
        py,px = py+lo[1],px+lo[0]
        positions[py,px] = points
        masque[py,px] = True
    if not masque.any():
        raise ValueError('Atlas vide.')
    return positions,masque


def marger_texture(couleurs, masque, pixels=4):
    import numpy as np
    from scipy.ndimage import distance_transform_edt
    if not masque.any():
        raise ValueError('Atlas vide.')
    result = np.array(couleurs, copy=True)
    distance, indices = distance_transform_edt(~masque, return_indices=True)
    band = (~masque)&(distance<=pixels)
    result[band] = result[indices[0][band],indices[1][band]]
    return result


def cuire_texture(mesh, model, scene_code, resolution, chunk_size=2048):
    import numpy as np
    import torch
    import trimesh
    import xatlas
    from PIL import Image

    print('Dépliage UV et rasterisation CPU ; aucune création de rig.', flush=True)
    mapping,indices,uvs = xatlas.parametrize(mesh.vertices, mesh.faces)
    vertices = np.asarray(mesh.vertices)[mapping]
    positions,mask = rasteriser_positions(vertices, indices, uvs, resolution)
    rows,cols = np.where(mask)
    colors = np.zeros((resolution,resolution,3), dtype=np.uint8)
    # Interrogation du champ neural par petits lots sur le GPU.
    for begin in range(0,len(rows),chunk_size):
        rr,cc = rows[begin:begin+chunk_size],cols[begin:begin+chunk_size]
        points = torch.as_tensor(positions[rr,cc],device=scene_code.device)
        with torch.inference_mode():
            rgb = model.renderer.query_triplane(model.decoder,points,scene_code)['color']
        data = rgb.detach().float().cpu().numpy()
        if not np.isfinite(data).all():
            raise ValueError('Texture neurale non finie.')
        colors[rr,cc] = np.uint8(np.clip(data,0,1)*255)
    image = Image.fromarray(marger_texture(colors,mask))
    material = trimesh.visual.material.PBRMaterial(name='Texture_neurale_TripoSR',baseColorTexture=image,roughnessFactor=.85,metallicFactor=0)
    textured = trimesh.Trimesh(vertices=vertices,faces=indices,process=False)
    textured.visual = trimesh.visual.texture.TextureVisuals(uv=uvs,material=material)
    return textured,image


def normaliser_metres(mesh, hauteur=1.8):
    """TripoSR documente Z vers le haut. GLB exporté Y vers le haut, pieds à zéro."""
    import numpy as np
    result = mesh.copy()
    zmin,zmax = float(result.bounds[0,2]),float(result.bounds[1,2])
    if not np.isfinite([zmin,zmax]).all() or zmax-zmin < .01:
        raise ValueError('Hauteur reconstruite dégénérée.')
    vertices = np.array(result.vertices, copy=True)
    vertices[:,2] -= zmin
    vertices *= hauteur/(zmax-zmin)
    # Rotation propre de -90° autour de X, et non miroir.
    result.vertices = np.column_stack((vertices[:,0],vertices[:,2],-vertices[:,1]))
    result.metadata.update({'unite':'metre','hauteur_cible':hauteur,'rig':'absent','statut':'Reconstruction expérimentale non validée, pas personnage fini'})
    return result
