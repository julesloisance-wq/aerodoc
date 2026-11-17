# CLAUDE.md — AeroDoc

## Contexte
Projet de Jules (élève ingénieur IMT Atlantique / M.S. Computer Science Georgia Tech) pour montrer des compétences en LLM et RAG dans ses candidatures de stage. Le plan est dans `PLAN.md` : le suivre étape par étape. Durée cible : 2 jours.

**Priorité n° 1 : un assistant qui marche bien, construit vite, et que Jules comprend.** L'évaluation reste légère : elle sert à vérifier que le système fonctionne et à donner un chiffre crédible, pas à construire un protocole de recherche.

## Rôle de Claude Code
- **Tu écris tout le code.** Jules ne code pas.
- **Ton deuxième rôle est pédagogique.** Jules part de zéro sur les RAG, les API et les LLM :
  - explique **chaque terme technique et chaque acronyme** la première fois que tu l'emploies, en une phrase simple ;
  - préfère les exemples concrets tirés des données du projet aux définitions abstraites ;
  - ne suppose aucune connaissance préalable (clé API, embedding, Docker…).
- À la fin de chaque étape de `PLAN.md` :
  1. vérifie que le livrable fonctionne ;
  2. explique en 5 à 10 lignes, sans jargon, ce que tu as construit, avec un exemple réel ;
  3. mets à jour `docs/COMPRENDRE.md` (concepts, choix et leurs raisons, outils, schéma du flux) ;
  4. propose 1 ou 2 questions d'entretien **facultatives** : elles ne bloquent pas la suite ;
  5. fais un commit et pousse-le, puis passe à l'étape suivante quand Jules donne son accord.
- Quand tu fais un choix technique (modèle, taille de chunk, paramètre), dis pourquoi en une phrase et note-le dans `docs/COMPRENDRE.md`.

## Règles
- Ne suppose jamais un nom de paquet, une version ou une API : vérifie au moment de l'installation.
- Aucun document du corpus dans Git : `data/` est ignoré, le corpus se reconstruit avec `make data`. Source et licence de chaque document dans `DATA_LICENSES.md`.
- LLM : Gemini (offre gratuite de Google AI Studio). Le fournisseur se change dans la configuration, sans toucher au code.
- Jeu de questions : une vingtaine, rédigées par Claude Code, survolées par Jules. Pas de séparation dev/test, pas de LLM-juge.
- Les résultats chiffrés (scores, latence) sont notés dans `EXPERIMENTS.md`.
- Seeds fixées, configuration versionnée.
- Pas de secrets dans le dépôt (`.env` ignoré, `.env.example` à jour).
- Code, docstrings, README et messages de commit en anglais ; explications et `docs/COMPRENDRE.md` en français.
- Le README mentionne que le code a été écrit avec un assistant de code IA, et précise le rôle de Jules (conception, choix techniques, relecture des questions, analyse des résultats).

## Commandes à créer
- `make db` · `make data` · `make index` · `make eval` · `make test`
- `aerodoc ask "question"`
- `docker compose up`
