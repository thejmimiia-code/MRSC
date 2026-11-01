#!/usr/bin/env node
/**
 * Banc de `outils/attente-navigateur.cjs` : une attente qui expire dit ce qu'elle attendait.
 *
 * Le 31 octobre 2026, `test-experience.cjs` est tombé en rouge sur un
 * `TimeoutError: Waiting failed: 30000ms exceeded`. Le message ne nommait ni la
 * condition, ni la ligne : il a fallu relancer et lire la source pour retrouver
 * l'attente fautive. L'enveloppe `attendre` répond à ce défaut — mais une
 * enveloppe qu'on n'a jamais vue échouer ne prouve rien.
 *
 * Quatre cas sont éprouvés sur une page factice, sans Chromium :
 *
 * 1. le succès rend la valeur et transmet les arguments, sans mentir sur l'appel ;
 * 2. un délai dépassé nomme la **condition**, le délai et la cause d'origine ;
 * 3. une erreur qui n'est pas un délai (`TypeError` dans la page) est aussi
 *    nommée, avec sa cause — les deux ne se réparent pas de la même façon ;
 * 4. une condition très longue est tronquée, jamais recopiée en entier.
 *
 * Limite écrite : ce banc ne dit rien du comportement de Puppeteer lui-même. Il
 * vérifie que le message d'échec est utilisable, pas qu'une attente de 30 s
 * suffit à un vrai navigateur.
 *
 * Usage :
 *   node outils/test_attente_navigateur.cjs
 */

'use strict';

const assert = require('node:assert/strict');
const { attendre, LONGUEUR, DELAI_DEFAUT } = require('./attente-navigateur.cjs');

const resultats = [];

/** Une page qui répond ce qu'on lui demande, et note comment elle a été appelée. */
function pageFactice(reponse) {
  const appels = [];
  return {
    appels,
    async waitForFunction(condition, options, ...arguments_) {
      appels.push({ condition, options, arguments_ });
      return reponse(condition, options, arguments_);
    },
  };
}

async function cas(nom, action) {
  try {
    await action();
    resultats.push({ nom, reussi: true });
    console.log(`OK — ${nom}`);
  } catch (erreur) {
    resultats.push({ nom, reussi: false });
    console.error(`ÉCHEC — ${nom}\n${erreur && erreur.message}`);
  }
}

async function principal() {
  await cas('le succès rend la valeur et transmet les arguments', async () => {
    const page = pageFactice((_condition, _options, arguments_) => `vue-${arguments_[0]}`);
    const valeur = await attendre(page, (attendu) => attendu, { timeout: 1500 }, 'panorama');
    assert.equal(valeur, 'vue-panorama');
    assert.equal(page.appels.length, 1);
    assert.equal(page.appels[0].options.timeout, 1500);
    assert.deepEqual(page.appels[0].arguments_, ['panorama']);
  });

  await cas('un délai dépassé nomme la condition, le délai et la cause', async () => {
    const page = pageFactice(() => {
      throw new Error('Waiting failed: 30000ms exceeded');
    });
    await assert.rejects(
      () =>
        attendre(page, () => document.documentElement.dataset.layout === 'panorama', {
          timeout: 2000,
        }),
      (erreur) => {
        assert.match(erreur.message, /Attente expirée après 2000 ms/);
        assert.match(erreur.message, /dataset\.layout === 'panorama'/);
        assert.match(erreur.message, /cause d'origine : Error: Waiting failed/);
        return true;
      }
    );
    // Sans option de délai, le message dit le délai par défaut, pas « undefined ».
    await assert.rejects(
      () => attendre(pageFactice(() => { throw new Error('boum'); }), () => true),
      (erreur) => {
        assert.match(erreur.message, new RegExp(`après ${DELAI_DEFAUT} ms`));
        assert.match(erreur.message, /condition : \(\) => true/);
        return true;
      }
    );
  });

  await cas('une erreur qui n’est pas un délai est nommée aussi', async () => {
    const page = pageFactice(() => {
      throw new TypeError('Cannot read properties of null (reading \'open\')');
    });
    await assert.rejects(
      () => attendre(page, () => document.querySelector('[data-x]')?.open === true, { timeout: 800 }),
      (erreur) => {
        assert.match(erreur.message, /condition : \(\) => document\.querySelector/);
        assert.match(erreur.message, /TypeError: Cannot read properties of null/);
        return true;
      }
    );
  });

  await cas('une condition très longue est tronquée', async () => {
    // Une fonction se lit par sa source (`() => …`) : c'est donc une chaîne
    // longue qu'il faut pour éprouver la troncature.
    const longue = `() => ${'x'.repeat(600)}`;
    const page = pageFactice(() => {
      throw new Error('délai');
    });
    await assert.rejects(
      () => attendre(page, longue, { timeout: 400 }),
      (erreur) => {
        assert.ok(
          erreur.message.length < LONGUEUR + 200,
          `message de ${erreur.message.length} caractères : la condition n'est pas tronquée`
        );
        assert.match(erreur.message, /…/);
        return true;
      }
    );
  });

  const echoues = resultats.filter((r) => !r.reussi).length;
  if (echoues) {
    console.error(
      `\n${echoues} échec(s) sur ${resultats.length} — l'attente nommée ne dit pas ce qu'elle attendait.`
    );
    process.exit(1);
  }
  console.log(
    `\nOK — ${resultats.length} cas : l'attente nommée rend la valeur, et son échec nomme la condition.`
  );
}

principal().catch((erreur) => {
  console.error(erreur);
  process.exit(1);
});
