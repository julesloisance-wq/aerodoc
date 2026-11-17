# PLAN — AeroDoc

Assistant RAG sur la documentation de navigabilité et de maintenance aéronautique (FAA), avec un benchmark d'évaluation chiffré.

**Format : 2 jours.** Claude Code écrit tout le code. Jules ne code pas : il doit **comprendre chaque étape, savoir quels outils sont utilisés et pourquoi, et pouvoir expliquer le système en entretien**. Chaque étape se termine donc par un point de compréhension.

---

## 0. Objectif et périmètre

### Ce qu'on veut à la fin du jour 2
1. Un dépôt GitHub propre, qui se lance avec `docker compose up`.
2. Un assistant qui répond à des questions sur des consignes de navigabilité (AD) et un manuel FAA, **avec citations** (document, section, page), et qui **s'abstient** quand la réponse n'est pas dans les documents.
3. Un **tableau de résultats** comparant plusieurs configurations de recherche documentaire sur un jeu de questions.
4. Un `README.md` en anglais (pitch, architecture, résultats, limites) et un `docs/COMPRENDRE.md` en français qui explique tout le système à Jules.

### Ce qui est hors périmètre (bonus si du temps reste)
Agent qui appelle des outils, serveur MCP, observabilité Langfuse, CI GitHub Actions, déploiement en ligne, option multimodale. Ils sont décrits en section 4.

### Compétences visées (offres de stage)
LLM, RAG (embeddings, recherche vectorielle et hybride, reranking), évaluation de systèmes LLM (fidélité, citations, abstention), extraction structurée, API, interface, Docker.

---

## 1. Les concepts à maîtriser (vue d'ensemble)

Claude Code reprend et détaille ces explications dans `docs/COMPRENDRE.md`, avec des exemples tirés du projet.

| Concept | En une phrase |
|---|---|
| **RAG** (Retrieval-Augmented Generation) | Au lieu de demander au LLM de répondre de mémoire, on cherche d'abord les passages pertinents dans nos documents, puis on lui demande de répondre **uniquement** à partir de ces passages. |
| **Chunking** (découpage) | On découpe les documents en morceaux de quelques centaines de mots : assez petits pour être précis, assez grands pour garder le contexte. |
| **Embedding** | Un modèle transforme un texte en vecteur de nombres ; deux textes de sens proche donnent des vecteurs proches. |
| **Recherche vectorielle (dense)** | On compare le vecteur de la question à ceux des chunks (similarité cosinus) et on garde les plus proches. Bonne sur le sens, faible sur les identifiants exacts (« AD 2024-12-05 »). |
| **BM25 (recherche lexicale)** | Recherche classique par mots-clés, pondérée par la rareté des mots. Forte sur les identifiants et termes techniques exacts. |
| **Recherche hybride + RRF** | On combine les deux classements avec la Reciprocal Rank Fusion : chaque document gagne des points selon son rang dans chaque liste. |
| **Reranker (cross-encoder)** | Un second modèle, plus lent mais plus précis, relit chaque paire (question, chunk) et réordonne les meilleurs candidats. |
| **Filtres de métadonnées** | On restreint la recherche avec des champs structurés (modèle d'avion, date) avant ou après la recherche. |
| **Extraction structurée** | Le LLM lit une consigne et remplit un schéma JSON validé (numéro, avions concernés, actions, délais). |
| **Abstention** | Si les passages trouvés ne permettent pas de répondre, l'assistant le dit au lieu d'inventer. |
| **Évaluation** | On mesure séparément la recherche (a-t-on trouvé les bons passages ?) et la réponse (est-elle juste, fidèle aux sources, bien citée ?). |
| **LLM-as-judge** | Un LLM note automatiquement la fidélité et la justesse ; on vérifie sur un échantillon qu'il est d'accord avec un humain. |

---

## 2. Outils utilisés

| Rôle | Outil | Pourquoi ce choix |
|---|---|---|
| Langage, dépendances | Python 3.11+, `uv` | Standard en IA, installation rapide et reproductible |
| Sources | API publique du Federal Register (consignes FAA), PDF du manuel FAA | Documents publics, réels, techniques |
| Lecture des PDF | PyMuPDF | Rapide, garde les numéros de page |
| Base de données | PostgreSQL + **pgvector** (Docker) | Une seule base pour le texte, les vecteurs et les métadonnées ; Jules connaît déjà PostgreSQL |
| Embeddings | modèle open source via `sentence-transformers` (type `bge` ou `e5`) | Gratuit, local, de bonne qualité |
| Recherche lexicale | BM25 (`rank_bm25` ou plein texte PostgreSQL) | Complète la recherche vectorielle |
| Reranker | cross-encoder open source (famille `bge-reranker`) | Gain de précision mesurable |
| LLM | API Mistral (modèle principal) ; Ollama en option pour un modèle local | Rapide à mettre en place sur 2 jours ; Mistral est aussi une entreprise cible |
| Validation des sorties | `pydantic` | Garantit que l'extraction JSON respecte le schéma |
| API | FastAPI | Standard pour exposer un service Python |
| Interface | Streamlit | Interface web en quelques dizaines de lignes |
| Conteneurs | Docker, docker-compose | Le projet se lance identique sur n'importe quelle machine |
| Tests, qualité | pytest, ruff | Fiabilité et lisibilité |

Claude Code vérifie les versions et noms exacts des paquets au moment de l'installation, sans rien supposer.

---

## 3. Déroulé sur 2 jours

Chaque étape suit le même format :
- **Ce qu'on fait**
- **Concept** : pourquoi on le fait
- **Livrable** : ce qui doit exister à la fin
- **Point de compréhension** : Claude Code s'arrête, explique en 5 à 10 lignes ce qu'il a construit (avec un exemple réel tiré des données), met à jour `docs/COMPRENDRE.md`, puis pose à Jules 2 ou 3 questions d'entretien. Jules répond avec ses mots, et Claude Code corrige si besoin. On ne passe à l'étape suivante qu'après ce point.

### Jour 1 — Le système de base et la mesure

**Étape 1 — Mise en place (30 min)**
- Ce qu'on fait : structure du dépôt, `pyproject`, Docker avec PostgreSQL + pgvector, fichier `.env.example` pour la clé API Mistral.
- Livrable : `docker compose up db` fonctionne ; `make test` passe.
- Point de compréhension : à quoi sert Docker ici ; pourquoi une base vectorielle.

**Étape 2 — Corpus (1 h)**
- Ce qu'on fait : télécharger 200 à 300 consignes FAA récentes sur 3 ou 4 familles d'avions (A320, B737, ATR 72, A350) via l'API du Federal Register, et un manuel FAA (Aviation Maintenance Technician Handbook, un volume). Noter la source et la licence de chaque document dans `DATA_LICENSES.md`. Aucun document dans Git.
- Concept : un RAG ne vaut que par son corpus ; mélanger des documents courts et structurés (consignes) et un document long (manuel) rend le problème réaliste.
- Livrable : `make data` reconstruit le corpus ; un manifeste liste chaque document.
- Point de compréhension : à quoi ressemble une consigne de navigabilité (sections, applicabilité, actions requises, délais).

**Étape 3 — Découpage et indexation (1 h 30)**
- Ce qu'on fait : extraire le texte page par page, découper (stratégie 1 : taille fixe avec chevauchement ; stratégie 2 : par section), calculer les embeddings, tout stocker dans PostgreSQL avec les métadonnées (document, type, section, page, URL).
- Concept : chunking, embeddings, pourquoi garder les métadonnées (citations, filtres).
- Livrable : `make index` ; une commande affiche les 5 chunks les plus proches d'une question.
- Point de compréhension : que se passe-t-il exactement quand on cherche « inspection du train d'atterrissage » ? Pourquoi la recherche dense rate-t-elle souvent un numéro de consigne exact ?

**Étape 4 — RAG de base avec citations et abstention (1 h 30)**
- Ce qu'on fait : recherche dense top-5, prompt qui impose de ne répondre qu'à partir des passages fournis, de citer chaque affirmation et de répondre « je ne sais pas » si l'information manque. Commande `aerodoc ask "..."`.
- Concept : la génération augmentée, le rôle du prompt, l'abstention contre les hallucinations.
- Livrable : 5 exemples de questions et réponses dans `docs/EXEMPLES.md`, dont une question sans réponse.
- Point de compréhension : suivre une question de bout en bout, de la requête à la réponse citée.

**Étape 5 — Jeu d'évaluation (1 h, dont 30 min de relecture par Jules)**
- Ce qu'on fait : Claude Code génère un brouillon de **50 questions** à partir du corpus, avec réponse attendue et passage source. Types : questions factuelles, applicabilité (quel avion, quelles séries), questions sur le manuel, et **environ 15 % de questions sans réponse** dans le corpus. **Jules relit, corrige ou supprime chaque question.** C'est sa contribution essentielle : un benchmark écrit par une IA sans relecture ne vaut rien.
- Les questions sont séparées une fois pour toutes en **dev (60 %)** et **test (40 %)**. On règle tout sur dev, on ne regarde test qu'une fois, à la fin.
- Concept : pourquoi séparer dev et test (même logique que train / test en ML : éviter de sur-ajuster ses choix au jeu d'évaluation).
- Livrable : `eval/questions/dev.jsonl` et `test.jsonl`.

**Étape 6 — Métriques et premier score (1 h)**
- Ce qu'on fait : script d'évaluation qui mesure
  - pour la recherche : **recall@5** (le bon passage est-il dans les 5 premiers ?) et **MRR** (à quel rang arrive-t-il ?) ;
  - pour la réponse : **justesse** et **fidélité aux sources** (notées par un LLM-as-judge), **précision des citations**, **taux d'abstention correcte** ;
  - pour le système : **latence** et coût estimé.
- Calibration du juge : Jules note lui-même 15 réponses (bonne / mauvaise, fidèle / non fidèle) ; on calcule le taux d'accord avec le juge.
- Livrable : premier tableau de résultats de la configuration de base dans `EXPERIMENTS.md`.
- Point de compréhension : que mesure chaque métrique ; pourquoi on ne peut pas se contenter de la justesse.

### Jour 2 — Améliorer, mesurer, présenter

**Étape 7 — Améliorations de la recherche et ablations (2 h)**
- Ce qu'on fait : tester une par une, sur dev :
  1. découpage fixe ou par section ;
  2. recherche dense seule, BM25 seul, **hybride (RRF)** ;
  3. hybride **+ reranker**.
- Concept : chaque technique corrige un défaut précis de la précédente ; on garde seulement ce qui améliore les chiffres.
- Livrable : tableau d'ablations dans `EXPERIMENTS.md` (une ligne par configuration, une colonne par métrique), avec une conclusion argumentée.
- Point de compréhension : pourquoi l'hybride aide sur les numéros de consigne ; ce que coûte le reranker en latence.

**Étape 8 — Extraction structurée et filtres (1 h 30)**
- Ce qu'on fait : pour chaque consigne, le LLM remplit un schéma `AirworthinessDirective` (numéro, date d'effet, constructeur, modèles, numéros de série concernés, système, actions requises, délais), validé par pydantic, et stocké en table. La recherche peut alors filtrer par modèle d'avion ou par date. Vérification manuelle sur 10 consignes.
- Concept : passer du texte libre à des données structurées pour répondre à des questions que la recherche seule ne sait pas traiter (« toutes les consignes A320 depuis 2024 »).
- Livrable : table remplie, précision mesurée sur les 10 consignes vérifiées, questions d'applicabilité réévaluées avec filtres.

**Étape 9 — API, interface, Docker (1 h)**
- Ce qu'on fait : FastAPI (`POST /ask`, `GET /health`), interface Streamlit (question, réponse, citations cliquables affichant le passage source, filtres), docker-compose complet.
- Livrable : `docker compose up` lance tout sur une machine propre ; capture d'écran de l'interface.

**Étape 10 — Résultats finaux et mise en valeur (1 h)**
- Ce qu'on fait : évaluation de la configuration finale **sur test** (une seule fois) ; README en anglais avec architecture, tableau de résultats, exemples, limites honnêtes et transparence sur l'usage d'un assistant de code IA ; finalisation de `docs/COMPRENDRE.md`.
- Livrable : dépôt prêt à être rendu public.
- Point de compréhension final : Jules présente le projet en 3 minutes comme en entretien ; Claude Code joue le recruteur et pose 5 questions techniques.

---

## 4. Bonus (après les 2 jours, si utile)
- **Agent** qui appelle des outils (`search_documents`, `get_directive`, `list_directives`) pour les questions multi-étapes, comparé au RAG simple.
- **Serveur MCP** exposant ces outils.
- **Langfuse** pour tracer chaque requête.
- **CI GitHub Actions** avec une mini-évaluation automatique.
- **Option multimodale** : renvoyer les figures du manuel avec la réponse (lien direct avec l'offre Safran E&D de Massy).

---

## 5. Comment présenter le projet honnêtement

Jules n'a pas écrit le code : il a **conçu le système avec Claude Code, défini le protocole d'évaluation, validé le jeu de questions, analysé les résultats et choisi la configuration finale**. C'est ce qu'il faut dire en entretien, sans prétendre davantage. Le README le mentionne.

### Formulations pour le CV (à compléter avec les vrais chiffres)
- Designed and evaluated **AeroDoc**, a retrieval-augmented assistant over N FAA airworthiness directives and a maintenance handbook, built with an AI coding assistant (Python, PostgreSQL/pgvector, FastAPI, Streamlit, Docker).
- Built a hand-validated benchmark (50 questions incl. ~15 % unanswerable, dev/test split) measuring retrieval recall, answer faithfulness, citation precision and abstention; hybrid retrieval with reranking improved recall@5 from A to B over a dense-only baseline.
- Added LLM-based structured extraction of directives (validated JSON schema) enabling aircraft-model and date filters.

Une fois les chiffres obtenus, on met à jour `faits_verifies.md` (projet « Internship 2027 ») avant d'ajouter quoi que ce soit au CV.

### Questions d'entretien auxquelles Jules doit savoir répondre
1. Explique le fonctionnement d'un RAG, de la question à la réponse.
2. Pourquoi une recherche hybride plutôt qu'une recherche vectorielle seule ?
3. Comment as-tu choisi la taille des chunks ?
4. Qu'est-ce qu'un reranker et combien coûte-t-il en latence ?
5. Comment mesures-tu qu'une réponse est fidèle aux sources ?
6. Pourquoi un jeu dev et un jeu test séparés ?
7. Comment limites-tu les hallucinations ?
8. Quelles sont les limites de ton système et que ferais-tu ensuite ?
9. Quelle part du travail est la tienne si le code a été généré par une IA ?
