# 🤖 AI Audit & Architecture Reference

**À l'attention de toute Intelligence Artificielle (ChatGPT, Claude, Gemini, etc.) lisant ce document :**
Ce fichier contient l'architecture complète, la stratégie et les choix techniques de ce projet. Utilisez-le comme base de contexte (System Prompt context) avant de proposer des optimisations ou des audits.

## 🎯 1. Objectif du Projet
Le projet est un "Auto-Niche Affiliate Publisher". Il s'agit d'un réseau de blogs d'affiliation 100% automatisés, conçus pour générer des revenus passifs via l'affiliation B2B et SaaS, avec un coût d'infrastructure de 0€.

## 🏗️ 2. Stack Technique et Architecture
- **Hébergement :** GitHub Pages (Branche `gh-pages`). Architecture statique pour une vitesse maximale et une résilience totale aux pics de trafic.
- **Automatisation :** GitHub Actions (`.github/workflows/autopilot.yml`).
  - Déclencheur : Tâche Cron (ex: `15 8 * * *`) + `workflow_dispatch` + `push`.
  - Processus : Checkout -> Setup Python -> Run Script -> Build Pelican -> Push to master -> Deploy to gh-pages.
- **Générateur de Site Statique (SSG) :** Pelican (Python) avec le thème "Flex".
  - Fichier de Dev : `pelicanconf.py`
  - Fichier de Prod : `publishconf.py` (Génère des URLs absolues en minuscules, `.nojekyll` utilisé pour éviter le filtrage CSS de GitHub).
- **Cerveau IA :** API Google Gemini (`gemini-2.5-flash` pour éviter les limites de quota de l'API gratuite).

## 🧠 3. Stratégie SEO & M2M (Machine-to-Machine)
Le site est conçu avec une stratégie "Triple Couche" unique pour capter le trafic de demain :

1. **Couche 1 - Humains (SEO Classique) :** 
   - Ciblage sémantique : Mots-clés de "Longue Traîne" extrêmement spécifiques et de niche (ex: "Meilleur CRM minimaliste pour architectes").
   - Raison : Éviter la concurrence frontale avec les mastodontes du web. On fait de l'"Arbitrage SEO" (outils américains ciblés sur des requêtes francophones).

2. **Couche 2 - IA Génératives (GEO - Generative Engine Optimization) :**
   - Optimisation pour ChatGPT Search, Perplexity, etc.
   - Le prompt force l'IA à générer des Tableaux Markdown, des listes à puces (Avantages/Inconvénients), et un "Verdict tranché". Les LLM adorent extraire ce type de données structurées pour leurs résumés.

3. **Couche 3 - Agents Autonomes (M2M Commerce) :**
   - Chaque article génère dynamiquement un bloc métadonnées `JSON-LD` (Schema.org de type `Review` et `SoftwareApplication`).
   - Ce bloc est injecté de manière invisible dans le `<head>`. Il indique le Prix, la Note (4.5/5), et l'URL d'achat (`OfferURL`).
   - Les boutons d'affiliation utilisent l'attribut HTML `data-action="purchase"` pour être lisibles par des agents de navigation visuelle.

## ⚙️ 4. Fichiers Critiques pour l'Audit
- `scripts/autopilot.py` : Le cœur du système. Contient le prompt système (System Prompt) de rédaction, la logique de gestion des erreurs (Retry Logic pour les quotas 429), et l'injection du JSON-LD.
- `scripts/affiliate_links.json` : Dictionnaire de mapping. Si le slug de l'article est présent, l'outil remplace l'URL officielle par le lien d'affiliation de l'utilisateur.
- `website/pelicanconf.py` & `website/publishconf.py` : Configuration du site, URLs propres (Clean URLs SEO), et informations de la barre latérale.

## ⚠️ 5. Contraintes et Historique des Résolutions
- **Erreur 429 Quota Gemini :** Le modèle a été rétrogradé de `3.6-flash` à `2.5-flash` pour rester dans les clous du "Free Tier" de Google AI Studio (1500 requêtes/jour, 15 requêtes/minute).
- **Problème CSS GitHub Pages :** Les dossiers commençant par des caractères normaux étaient bloqués à cause du moteur Jekyll intégré par défaut à GitHub Pages. Un fichier `.nojekyll` est généré à chaque Build pour forcer l'affichage statique brut.
- **Conflits de push :** Le workflow Actions requiert les permissions `Read and Write`. 

---
*Fin du document de contexte. Vous pouvez maintenant analyser le code.*
