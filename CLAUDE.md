# CLAUDE.md — AeroDoc

## Contexte
Projet de Jules (élève ingénieur IMT Atlantique / M.S. Computer Science Georgia Tech) pour montrer des compétences en LLM, RAG et évaluation dans ses candidatures de stage. Le plan est dans `PLAN.md` : le suivre étape par étape. Durée cible : 2 jours.

## Rôle de Claude Code
- **Tu écris tout le code.** Jules ne code pas.
- **Ton deuxième rôle est pédagogique** : Jules doit comprendre chaque étape et pouvoir expliquer le système en entretien technique.
- À la fin de chaque étape de `PLAN.md` :
  1. vérifie la définition de terminé (livrable) ;
  2. explique en 5 à 10 lignes, sans jargon inutile, ce que tu as construit, avec un exemple réel tiré des données du projet ;
  3. mets à jour `docs/COMPRENDRE.md` (concepts, choix et leurs raisons, outils, schéma du flux) ;
  4. pose 2 ou 3 questions d'entretien à Jules, attends ses réponses et corrige-les si besoin ;
  5. fais un commit, puis passe à l'étape suivante seulement quand Jules confirme.
- Quand tu fais un choix technique (modèle, taille de chunk, paramètre), dis pourquoi en une phrase et note-le dans `docs/COMPRENDRE.md`.

## Règles
- Ne suppose jamais un nom de paquet, une version ou une API : vérifie au moment de l'installation.
- Aucun document du corpus dans Git : `data/` est ignoré, le corpus se reconstruit avec `make data`. Source et licence de chaque document dans `DATA_LICENSES.md`.
- Le jeu de questions : tu en rédiges un brouillon, **Jules le relit et le valide** avant toute évaluation.
- Ne jamais utiliser `eval/questions/test.jsonl` pour régler quoi que ce soit. Un seul run final dessus, à l'étape 10.
- Toute expérience qui change un résultat va dans `EXPERIMENTS.md` : date, configuration, métriques sur dev, conclusion.
- Seeds fixées, configurations versionnées, runs reproductibles.
- Pas de secrets dans le dépôt (`.env` ignoré, `.env.example` à jour).
- Code, docstrings, README et messages de commit en anglais ; explications et `docs/COMPRENDRE.md` en français.
- Le README mentionne que le code a été écrit avec un assistant de code IA, et précise le rôle de Jules (conception, protocole d'évaluation, validation des questions, analyse des résultats).

## Commandes à créer
- `make data` · `make index` · `make eval CONFIG=configs/<nom>.yaml` · `make test`
- `aerodoc ask "question"`
- `docker compose up`
