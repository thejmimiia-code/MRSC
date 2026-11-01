/**
 * Une attente qui expire doit dire **ce qu'elle attendait**.
 *
 * Le 31 octobre 2026, `test-experience.cjs` a fait tomber la CI sur un
 * `TimeoutError: Waiting failed: 30000ms exceeded` : le message ne nommait que
 * la mécanique de Puppeteer, sans la condition ni la ligne utile. Les journaux
 * du job ne sont pas atteignables depuis l'atelier, et l'annotation, bornée à
 * trois lignes de contexte, n'avait gardé que des cadres internes. Chercher la
 * cause a demandé deux relances et une lecture de la source, pour une
 * information que le script avait sous la main.
 *
 * La source de la condition est donc recopiée dans le message : elle est courte,
 * stable, et désigne l'attente sans ambiguïté. La cause d'origine est conservée,
 * parce qu'un `TypeError` dans la page et un simple délai dépassé ne se
 * réparent pas de la même façon.
 *
 * Ce module ne juge rien et n'attend rien lui-même : il enveloppe
 * `page.waitForFunction` en gardant exactement sa signature.
 *
 * Usage :
 *   const { attendre } = require('./attente-navigateur.cjs');
 *   await attendre(page, () => document.body.dataset.pret === 'oui', { timeout: 5000 });
 */

'use strict';

//: Longueur maximale de la condition recopiée : au-delà, une annotation GitHub
//: tronque de toute façon, et une condition de 2 000 caractères ne se lit pas.
const LONGUEUR = 220;

//: Délai que Puppeteer applique quand aucun n'est donné.
const DELAI_DEFAUT = 30000;

/**
 * @param {object} page objet page de Puppeteer (ou son équivalent de banc)
 * @param {Function|string} condition condition passée à `waitForFunction`
 * @param {object} [options] options de `waitForFunction` (dont `timeout`)
 * @param {...unknown} arguments_ arguments ajoutés à la condition
 */
async function attendre(page, condition, options, ...arguments_) {
  try {
    return await page.waitForFunction(condition, options, ...arguments_);
  } catch (erreur) {
    const brute = String(condition).replace(/\s+/g, ' ').trim();
    const source = brute.length > LONGUEUR ? `${brute.slice(0, LONGUEUR)}…` : brute;
    const delai = options && typeof options.timeout === 'number' ? options.timeout : DELAI_DEFAUT;
    // Le type compte autant que le texte : un `TimeoutError` dit qu'il faut
    // attendre plus longtemps ou corriger la condition, un `TypeError` dit que
    // la page a jeté avant même de répondre. `message` seul perd cette
    // distinction — le banc l'a montré.
    const nom = (erreur && erreur.name) || '';
    const cause = erreur && erreur.message ? (nom ? `${nom}: ${erreur.message}` : erreur.message) : String(erreur);
    throw new Error(
      `Attente expirée après ${delai} ms — condition : ${source} (cause d'origine : ${cause})`
    );
  }
}

module.exports = { attendre, LONGUEUR, DELAI_DEFAUT };
