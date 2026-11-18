# Les choix du projet AeroDoc, et comment les défendre

Ce document justifie **chaque décision** prise pendant le projet. Pour chacune :
- **Le problème** : ce qu'il fallait décider ;
- **Les options** : ce qui était possible ;
- **Le choix et pourquoi** : la décision, avec les raisons et, quand il y en a, les chiffres mesurés ;
- **Les limites** : ce que ce choix sacrifie (un recruteur appréciera que tu les connaisses) ;
- **En entretien** : une formulation courte, à dire avec tes mots.

Les termes techniques sont expliqués dans le glossaire de `docs/COMPRENDRE.md`. Les mesures sont dans `EXPERIMENTS.md`.

---

## Ce qui a été construit, et ce qui a été réutilisé

Comme presque tout projet logiciel, AeroDoc **assemble des briques existantes** (bibliothèques open source, modèles pré-entraînés, services, algorithmes publiés) avec du **code écrit pour le projet** (environ 2 800 lignes, dont les tests), qui les relie et les adapte au problème. Savoir faire ce partage est important en entretien : on ne prétend pas avoir inventé un modèle ou une base de données, mais on peut expliquer précisément ce qu'on a conçu.

**Analogie.** Construire une maison : on n'invente ni les briques, ni le ciment, ni la chaudière ; on choisit lesquels utiliser, on dessine le plan, et on les assemble. Ici, FastAPI ou PostgreSQL sont des matériaux ; l'architecture, la façon de découper les documents, la recherche hybride, le prompt et l'évaluation sont le plan et l'assemblage.

### Réutilisé tel quel (créé par d'autres)

| Brique | Ce que c'est | Qui l'a créée | Ce qu'elle fait pour nous |
|---|---|---|---|
| **Données** : consignes FAA, manuel FAA-H-8083-30B | Documents publics | FAA, gouvernement américain | Le corpus |
| API du Federal Register, govinfo.gov | Services publics | Gouvernement américain | Chercher et télécharger les consignes |
| **PostgreSQL** | Base de données | Communauté open source | Stocker texte, métadonnées, vecteurs |
| **pgvector** | Extension de PostgreSQL | Open source (A. Kane) | Stocker les vecteurs, chercher les plus proches (index HNSW) |
| **HNSW** | Algorithme de recherche de voisins | Malkov et Yashunin (2016), implémenté dans pgvector | Recherche rapide des vecteurs proches |
| **`BAAI/bge-small-en-v1.5`** | Modèle d'embedding pré-entraîné | Beijing Academy of Artificial Intelligence | Transformer un texte en vecteur |
| **`sentence-transformers`** | Bibliothèque Python | UKP Lab / Hugging Face | Faire tourner le modèle d'embedding et le reranker |
| **`cross-encoder/ms-marco-MiniLM-L6-v2`** | Reranker pré-entraîné | Équipe sentence-transformers, entraîné sur MS MARCO (Microsoft) | Relire et reclasser les 20 meilleurs passages |
| **PyTorch** | Bibliothèque de calcul pour l'IA | Meta | Moteur de calcul des modèles |
| **BM25** | Formule de classement par mots-clés | Robertson et al. (années 1990) | Recherche par mots-clés |
| **`bm25s`** | Bibliothèque Python | X. H. Lù | Implémentation rapide de BM25 |
| **RRF** | Formule de fusion de classements | Cormack et al. (2009) | Fusionner recherche par le sens et par mots-clés |
| **Gemini** (`gemini-3.1-flash-lite`) | LLM | Google | Rédiger la réponse, traduire, générer des questions |
| **`openai`** (bibliothèque cliente) | Bibliothèque Python | OpenAI | Envoyer les requêtes au LLM (format compatible) |
| **PyMuPDF** | Bibliothèque Python | Artifex | Lire le texte et la table des matières du PDF |
| **FastAPI** + **Uvicorn** | Framework web + serveur | S. Ramírez / Encode | Exposer le moteur sous forme d'API |
| **Streamlit** | Framework d'interface web | Snowflake | Créer la page web en Python |
| **Docker**, **docker compose** | Outils de conteneurs | Docker Inc. | Lancer le projet à l'identique partout |
| **`uv`**, `pydantic`, `typer`, `httpx`, `pytest`, `ruff` | Outils Python | Divers | Dépendances, validation, ligne de commande, HTTP, tests, style |
| **Intervalle de Wilson** | Formule statistique | E. B. Wilson (1927) | Marges d'erreur des scores |
| **Adminer** | Interface web pour bases de données | Open source | Explorer la base (optionnel) |

**Aucun modèle n'a été entraîné ni modifié** : tous sont utilisés tels quels (voir « Et le fine-tuning ? »).

### Construit pour le projet (code écrit avec Claude Code, conçu et validé par Jules)

| Partie | Fichiers | Ce qui est propre au projet |
|---|---|---|
| Constitution du corpus | `corpus.py`, `configs/corpus.yaml` | Choix des familles d'avions et de la période, filtre sur le résumé, contournement du texte protégé (govinfo), manifeste avec empreintes |
| Découpage | `chunking.py` | Découpage qui suit les sections (a)-(k) et les pages des consignes, table des matières du manuel, en-tête contextuel, sections administratives écartées |
| Indexation | `index.py`, `db.py` | Schéma de la base, index vectoriel et plein texte |
| Recherche | `search.py` | Assemblage dense + BM25 + RRF + reranker, découpage en mots adapté aux identifiants (« A321-271NX »), filtre par numéro de consigne |
| Réponse | `answer.py`, `llm.py` | Prompt (citations, abstention), détection de l'abstention, traduction des questions en français, bascule entre modèles |
| Évaluation | `evaluate.py`, `probe.py`, `scripts/`, `eval/questions/` | Les 3 jeux de questions, la génération et le filtrage automatique, les métriques, les points de comparaison, l'analyse des erreurs |
| API | `api.py` | Les 4 points d'entrée (`/ask`, `/search`, `/health`, `/stats`) et le format des réponses |
| Interface | `ui.py` | La page : question, réponse citée, sources dépliables, passages retrouvés |
| Déploiement | `Dockerfile`, `docker-compose.yml`, `aerodoc bootstrap` | Image avec modèles intégrés, construction de l'index au premier lancement |

**En entretien.** « Je n'ai entraîné aucun modèle : j'utilise un modèle d'embedding et un reranker open source, et Gemini pour la génération. Mon travail porte sur la conception du système autour : comment découper des documents réglementaires, comment combiner recherche sémantique, recherche par mots-clés et métadonnées, comment forcer le LLM à citer et à s'abstenir, et surtout comment mesurer que ça marche. »

---

## Vue d'ensemble : pourquoi un RAG ?

**Le problème.** On veut un assistant qui répond à des questions sur des documents de maintenance aéronautique, sans inventer.

**Les options.**
1. Poser la question directement à un LLM : il répond « de mémoire », peut inventer (on parle d'**hallucination**), ne connaît pas les consignes publiées après son entraînement, et ne peut pas citer de source.
2. **Fine-tuner** un LLM (le ré-entraîner sur nos documents) : coûteux, lent, il faut tout refaire à chaque nouvelle consigne, et il ne cite toujours pas ses sources.
3. **RAG** : chercher les bons passages, puis demander au LLM de répondre **uniquement** avec eux.

**Le choix et pourquoi : le RAG.**
- Les réponses s'appuient sur des passages réels, qu'on peut **citer** (document, section, page) et donc **vérifier**.
- Une nouvelle consigne ? On l'ajoute à l'index en quelques secondes, sans ré-entraîner quoi que ce soit.
- Si la réponse n'est pas dans les passages trouvés, l'assistant peut dire « je ne sais pas ».
- Dans l'aéronautique, la traçabilité est obligatoire : une réponse sans source est inutilisable.

**Les limites.** Le système ne vaut que par sa recherche : si le bon passage n'est pas retrouvé, le LLM ne peut pas bien répondre.

**En entretien.** « Dans un domaine réglementé comme la maintenance aéronautique, une réponse doit être traçable. Le RAG permet de citer la source exacte, de mettre à jour la base sans ré-entraîner de modèle, et de s'abstenir quand l'information manque. »

### Et le fine-tuning ?
**Ce que c'est.** Poursuivre l'entraînement d'un modèle sur ses propres exemples (par exemple des milliers de paires question/réponse de maintenance), pour modifier le modèle lui-même. Analogie : le RAG donne au technicien le classeur de documentation pendant l'examen ; le fine-tuning lui fait apprendre la matière par cœur.

**Pourquoi on n'en fait pas.**
- Les consignes changent chaque semaine : il faudrait ré-entraîner à chaque nouvelle publication, alors qu'avec le RAG on ajoute le document à l'index en quelques secondes.
- Un modèle fine-tuné répond de mémoire : il ne peut pas citer de source, et ses erreurs sont invérifiables.
- Le fine-tuning apprend surtout un **style ou un format**, pas des faits fiables.
- Il faut des milliers d'exemples de qualité et de la puissance de calcul.

**Où il aurait du sens.** Pour adapter le **modèle d'embedding ou le reranker** au vocabulaire aéronautique : notre reranker a été entraîné sur des questions web génériques, et l'analyse des erreurs montre qu'il ignore les numéros de consigne (voir 6.5). C'est une piste d'amélioration crédible.

**En entretien.** « Je n'ai pas fait de fine-tuning, parce que le besoin était d'accéder à des documents qui changent souvent et de citer la source exacte. Le fine-tuning modifie le modèle lui-même : il faut le ré-entraîner à chaque nouvelle consigne, et il ne peut pas citer. Par contre, ajuster le reranker sur des données aéronautiques serait une bonne piste pour améliorer la recherche. »

---

## 1. Infrastructure

### 1.1 Python et `uv`
**Le problème.** Choisir le langage et l'outil qui installe les bibliothèques.

**Le choix et pourquoi.** Python est le standard de l'IA : toutes les bibliothèques utiles (sentence-transformers, PyTorch, FastAPI) y sont. `uv` installe les dépendances très vite et **fige leurs versions exactes** dans `uv.lock` : n'importe qui obtient exactement le même environnement.

**Les limites.** Aucune notable pour ce projet.

**En entretien.** « `uv` fige les versions dans un lockfile : le projet est reproductible à l'identique. »

### 1.2 PostgreSQL + pgvector plutôt qu'une base vectorielle dédiée
**Le problème.** Où stocker le texte des passages, leurs vecteurs et leurs métadonnées (document, page, section) ?

**Les options.**
- Une base vectorielle spécialisée : Qdrant, Weaviate, Chroma, Pinecone (service payant en ligne) ;
- une bibliothèque en mémoire : FAISS ;
- **PostgreSQL avec l'extension pgvector**.

**Le choix et pourquoi : PostgreSQL + pgvector.**
- **Une seule base pour tout** : texte, vecteurs, métadonnées, et même la recherche plein texte. Pas de synchronisation entre deux systèmes.
- On peut **combiner recherche vectorielle et filtres SQL** classiques (par exemple « seulement les consignes A320 publiées depuis 2024 ») dans une même requête.
- PostgreSQL est éprouvé, connu des entreprises, et tu le connais déjà.
- À notre échelle (5 295 passages), pgvector avec un index HNSW répond en quelques millisecondes.

**Les limites.** Pour des centaines de millions de vecteurs, une base spécialisée serait plus performante. Ce n'est pas notre cas.

**En entretien.** « J'ai choisi pgvector pour garder une seule base : texte, vecteurs et métadonnées au même endroit, avec la possibilité de filtrer en SQL. À quelques milliers de passages, une base vectorielle dédiée n'apporterait que de la complexité. »

### 1.3 Docker et docker compose
**Le problème.** Faire tourner la base de données (et plus tard l'API et l'interface) de la même façon sur toutes les machines.

**Le choix et pourquoi.** Docker emballe chaque logiciel avec tout ce dont il a besoin, dans un **conteneur**. Le fichier `docker-compose.yml` décrit les conteneurs du projet, et une seule commande les lance. Un recruteur peut donc lancer le projet sans rien installer à la main, et on évite le « ça marche chez moi mais pas chez toi ».

**Les limites.** Il faut Docker installé sur la machine.

**En entretien.** « Docker rend l'environnement reproductible : la base PostgreSQL avec pgvector est décrite dans un fichier, et `docker compose up` lance tout. »

### 1.4 Les secrets hors du code
**Le problème.** Le projet utilise une clé API, qui ne doit jamais être publiée.

**Le choix et pourquoi.** Les réglages sont lus depuis des variables d'environnement ou un fichier `.env`, que Git ignore. Le fichier `.env.example`, lui, est versionné : il montre quelles variables existent, sans valeur.

**En entretien.** « Aucun secret dans le dépôt : configuration par variables d'environnement, avec un `.env.example` documenté. »

---

## 2. Le LLM

### 2.1 Gemini (offre gratuite) plutôt que Mistral, OpenAI ou un modèle local
**Le problème.** Choisir le LLM qui rédige les réponses : il doit être de bonne qualité, et gratuit ou très bon marché.

**Les options.**
- **Mistral** : l'offre gratuite ne donnait plus de clé API au moment du projet ;
- **OpenAI, Anthropic** : payants ;
- **un modèle local via Ollama** : gratuit, mais sur notre machine (4 processeurs, pas de carte graphique), compter 30 à 60 secondes par réponse ;
- **Gemini (Google)** : offre gratuite avec clé API, sans carte bancaire.

**Le choix et pourquoi : Gemini, version « Flash ».** Gratuit, rapide, de bonne qualité pour rédiger une réponse à partir de passages. La limite de requêtes par minute de l'offre gratuite suffit largement pour un prototype.

**Les limites.**
- Les requêtes de l'offre gratuite peuvent être utilisées par Google pour améliorer ses produits. Ce n'est acceptable que parce que nos documents sont **publics**.
- Pour des documents confidentiels d'entreprise, il faudrait une offre payante sans réutilisation des données, ou un modèle hébergé en interne.

**En entretien.** « J'ai pris Gemini Flash pour son offre gratuite et sa qualité. Mes documents étant publics, le partage des données de l'offre gratuite n'était pas un problème. En entreprise, avec des documents confidentiels, je passerais à un modèle hébergé en interne ou à une offre sans réutilisation des données. »

### 2.2 L'interface « compatible OpenAI »
**Le problème.** Ne pas rester bloqué sur un fournisseur.

**Le choix et pourquoi.** Gemini, Mistral, Groq et Ollama acceptent tous le même format de requête, celui d'OpenAI. On utilise ce format : **changer de fournisseur revient à changer une adresse et un nom de modèle dans la configuration**, sans toucher au code.

**En entretien.** « Le code parle le format OpenAI, que la plupart des fournisseurs acceptent : le LLM est interchangeable par configuration. »

---

## 3. Le corpus

### 3.1 Des consignes de navigabilité (AD) et un manuel de la FAA
**Le problème.** Sur quels documents l'assistant cherche-t-il ?

**Le choix et pourquoi.**
- **Des documents réels, publics et libres de droits** : ceux du gouvernement américain ne sont pas soumis au droit d'auteur.
- **Un mélange réaliste** : des consignes courtes, juridiques et pleines d'identifiants (« AD 2026-18-03 », « A321-271NX »), et un manuel long et pédagogique (677 pages). Un vrai technicien cherche dans les deux. Ce mélange met en évidence des difficultés réelles, comme la recherche d'un identifiant exact.
- **Le domaine aéronautique** colle aux candidatures visées (Safran, Airbus…).

**Les limites.** Les consignes Airbus et ATR renvoient souvent à une consigne européenne (EASA) qui n'est **pas** dans le corpus : le détail des actions manque alors. L'assistant doit le dire.

**En entretien.** « J'ai mélangé des documents courts et structurés avec un manuel long, comme dans la réalité. C'est ce qui m'a permis de voir les limites de la recherche vectorielle seule sur les identifiants. »

### 3.2 4 familles d'avions, depuis 2022, 70 consignes au maximum par famille
**Le choix et pourquoi.** A320, A350, B737 et ATR 72 : des avions très répandus, de deux constructeurs, avec des consignes nombreuses. 225 consignes suffisent pour un problème réaliste (des dizaines de consignes qui se ressemblent) tout en s'indexant en quelques minutes.

**Les limites.** Ce n'est pas exhaustif. Le corpus ne remplace pas la base officielle de la FAA.

### 3.3 Chercher via l'API du Federal Register, télécharger le texte sur govinfo.gov
**Le problème.** Obtenir proprement les consignes.

**Le choix et pourquoi.**
- L'**API du Federal Register** (le journal officiel américain) donne des métadonnées propres : date de publication, date d'effet, numéro d'AD, avions.
- Le texte brut du Federal Register est protégé contre les robots. **govinfo.gov** (l'imprimerie officielle du gouvernement) sert le même document en texte simple.
- **Le texte plutôt que le PDF** : le PDF du Federal Register est sur 3 colonnes, difficile à lire proprement. Le texte garde les repères de page (`[[Page 56578]]`), ce qui permet de citer.

### 3.4 Une consigne n'est gardée que si son résumé mentionne le modèle d'avion
**Pourquoi.** La recherche par mot-clé de l'API remonte parfois des documents hors sujet (sièges, bouteilles d'oxygène, conditions spéciales). Le filtre évite de polluer le corpus.

### 3.5 Aucun document dans Git, mais un manifeste
**Le choix et pourquoi.** On versionne la **recette** (`configs/corpus.yaml`), pas les données. `make data` retélécharge tout. Le manifeste (`data/manifest.jsonl`) garde, pour chaque document, son adresse source et son **empreinte SHA-256**, qui permet de vérifier qu'un fichier n'a pas changé.

---

## 4. Le découpage en passages (chunking)

### 4.1 Pourquoi découper
1. Le modèle d'embedding lit au maximum 512 tokens (environ 380 mots). Au-delà, le texte est ignoré.
2. Un vecteur résume bien **une** idée. Un vecteur pour 677 pages serait une moyenne floue.
3. On n'envoie au LLM que l'utile : 5 passages plutôt que des documents entiers.
4. Chaque passage connaît sa page et sa section : les citations sont précises.

### 4.2 Environ 250 mots, avec 40 mots de chevauchement
**Les options.** Des passages de taille fixe (100, 250, 500 mots…) ou découpés selon la structure du document.

**Le choix et pourquoi.**
- **250 mots** : assez petit pour être précis et citable, assez grand pour garder le contexte. Une fois l'en-tête ajouté, ça reste sous la limite de 512 tokens du modèle. C'est une valeur standard dans les RAG.
- **40 mots de chevauchement** : le passage suivant reprend la fin du précédent, pour qu'une phrase coupée en deux reste lisible d'un côté ou de l'autre.

**Les limites.** La taille n'a pas été optimisée par des mesures : c'est un bon point de départ, assumé.

### 4.3 Découpage qui respecte la structure (sections et pages)
**Pourquoi.** Une consigne est très structurée : (c) Applicability, (e) Unsafe Condition, (g) Requirements… Un passage s'arrête à un changement de section **s'il fait déjà au moins 80 mots**. Ainsi, un passage parle d'un seul sujet, et les toutes petites sections (« (d) Subject », une ligne) sont regroupées avec leurs voisines. Pour le manuel, la section vient de la **table des matières du PDF**, et la page du numéro imprimé (par exemple « 10-13 »).

### 4.4 Un en-tête ajouté à chaque passage (contextual chunk header)
**Le problème.** La section (g) de l'AD 2026-18-03 dit seulement « appliquez l'EASA AD 2026-0142 ». Elle ne mentionne ni l'A320, ni le train d'atterrissage, ni son propre numéro.

**Le choix et pourquoi.** On colle devant chaque passage un en-tête : « AD 2026-18-03 (Airbus SAS Airplanes; aircraft: A320; effective 2026-09-18) | (g) Requirements ». Cet en-tête est inclus dans le vecteur **et** dans l'index par mots-clés. Résultat : chaque passage sait à quelle consigne, à quel avion et à quelle section il appartient. C'est aussi ce qui permet à la recherche par mots-clés de placer les 5 passages de l'AD 2026-18-03 en tête.

**En entretien.** « J'ai enrichi chaque passage avec un en-tête contextuel (document, avion, section), pour qu'un passage court ne soit pas orphelin, à la fois pour la recherche par le sens et par mots-clés. »

### 4.5 Sections administratives ignorées
**Pourquoi.** « Paperwork Reduction Act », adresses, « Regulatory Flexibility Act »… sont identiques dans toutes les consignes et ne répondent à aucune question de maintenance. Les garder ajouterait du bruit dans les résultats.

---

## 5. Les embeddings

### 5.1 Le modèle `BAAI/bge-small-en-v1.5`
**Le problème.** Choisir le modèle qui transforme un texte en vecteur, parmi des milliers sur Hugging Face.

**La démarche.**
1. **Présélection** : un modèle fait **pour la recherche de documents** (retrieval), **pour l'anglais**, **assez petit pour un CPU**, **open source** (licence MIT), **très utilisé** et bien classé sur **MTEB**, le classement de référence des modèles d'embedding. Il reste quelques familles : `bge`, `e5`, `gte`, `all-MiniLM`. `bge` est l'une des plus utilisées en RAG.
2. **Mesure sur notre machine** entre deux tailles : `bge-small` traite 9,6 passages par seconde, `bge-base` 2,7. Soit 7 minutes d'indexation contre environ 25.

**Le choix.** `bge-small` : la vitesse, la qualité perdue étant récupérée par la recherche hybride et le reranker (voir 6).

**Les limites.** On n'a pas comparé la qualité de plusieurs modèles d'embedding sur nos données.

**En entretien.** « J'ai présélectionné des modèles de retrieval open source bien classés sur MTEB et utilisables sur CPU, puis mesuré le compromis vitesse/qualité. J'ai pris le petit modèle, parce que le reranker compense ensuite. »

### 5.2 PyTorch version CPU
**Pourquoi.** La version standard embarque le support des cartes graphiques (environ 3 Go de plus) dont on n'a pas besoin. La version CPU allège l'installation et l'image Docker.

### 5.3 Vecteurs normalisés, similarité cosinus, index HNSW
- **Similarité cosinus** : elle mesure si deux vecteurs pointent dans la même direction (1 = même sens, 0 = sans rapport). C'est la mesure standard pour les embeddings de texte.
- **Normalisation** : tous les vecteurs ont la même longueur, ce qui rend le calcul simple et stable.
- **Index HNSW** : une sorte de « carte routière » entre vecteurs voisins, qui permet de trouver les plus proches sans comparer la question aux 5 295 passages un par un.

### 5.4 Une consigne devant la question (« Represent this sentence for searching relevant passages: »)
**Pourquoi.** C'est la recommandation des auteurs de `bge` : une question courte et un passage long ne se ressemblent pas dans leur forme, et cette consigne aide le modèle à les rapprocher. On ne l'ajoute qu'aux questions, pas aux passages.

---

## 6. La recherche

### 6.1 Pourquoi la recherche par le sens seule ne suffit pas
**Mesuré.** Pour « AD 2026-18-03 », la recherche par le sens place la bonne consigne en 3ᵉ position, derrière AD 2026-09-03 et AD 2025-23-04. Sur nos 16 questions de test, elle ne retrouve que **1 question sur 4 posées par numéro de consigne**.

**Pourquoi.** Le modèle encode le **sens** : pour lui, « 2026-18-03 » et « 2026-09-03 » sont deux « numéros de consigne » presque équivalents.

### 6.2 BM25 (recherche par mots-clés)
**Le principe.** BM25 classe les passages selon les mots de la question qu'ils contiennent, en donnant plus de poids aux mots **rares** : « 2026-18-03 » apparaît dans très peu de passages, donc il pèse lourd ; « airplane » apparaît partout, donc il pèse peu.

**Les options.** La recherche plein texte intégrée à PostgreSQL, ou une vraie implémentation de BM25.

**Le choix et pourquoi : BM25 avec la bibliothèque `bm25s`.** Le classement de PostgreSQL (`ts_rank`) ne tient pas compte de la rareté des mots dans l'ensemble des documents, qui est justement ce qui fait la force de BM25. `bm25s` est récente, maintenue et rapide. Son index de 5 295 passages se construit en mémoire en environ 1 seconde, et une recherche prend environ 1 ms.

**Un détail qui compte : le découpage en mots (tokenisation).** Un identifiant comme « A321-271NX » est gardé **entier** et aussi **découpé** (« a321 », « 271nx »). La question « A321 » trouve donc aussi les passages qui parlent de « A321-271NX ».

### 6.3 Recherche hybride avec la Reciprocal Rank Fusion (RRF)
**Le problème.** Combiner deux classements dont les scores ne sont pas comparables : un cosinus va de 0 à 1, un score BM25 de 0 à 30 environ.

**Le choix et pourquoi : la RRF.** Elle n'utilise que les **rangs**. Chaque passage reçoit 1/(60 + rang) pour chaque classement où il apparaît, et on additionne. Un passage bien classé par les deux méthodes passe devant. Le 60 est la valeur du papier original : elle évite qu'une première place écrase tout.

**Mesuré.** La recherche hybride retrouve **les 16 questions dans le top 5** (contre 13 sur 16 pour la recherche par le sens seule). Mais pour les questions par numéro, la bonne consigne n'est souvent qu'en 2ᵉ à 4ᵉ position (MRR 0,85).

### 6.4 Le reranker (cross-encoder)
**Le principe.** Les embeddings comparent deux vecteurs calculés **séparément** : rapide, mais approximatif. Un **cross-encoder** lit la question **et** le passage **ensemble**, et juge leur pertinence mot à mot. C'est beaucoup plus précis, mais trop lent pour 5 295 passages. On ne l'applique donc qu'aux 20 meilleurs candidats de la recherche hybride.

**Les options mesurées** (16 questions de test) :
| Configuration | Bonne réponse en 1ʳᵉ position | Dans le top 5 | MRR | Latence médiane |
|---|---|---|---|---|
| Recherche par le sens seule | 75 % | 81 % | 0,78 | 20 ms |
| BM25 seul | 88 % | 100 % | 0,92 | 1 ms |
| Hybride (RRF) | 75 % | 100 % | 0,85 | 17 ms |
| **Hybride + reranker MiniLM** | **88 %** | **100 %** | **0,94** | **≈ 1 s** |
| Hybride + reranker bge-base | 94 % | 100 % | 0,97 | ≈ 4,9 s |

Le **MRR** (*Mean Reciprocal Rank*) vaut 1 si la bonne réponse est toujours 1ʳᵉ, 0,5 si elle est toujours 2ᵉ, etc.

**Le choix et pourquoi : hybride + reranker `ms-marco-MiniLM-L6-v2`.** Il apporte l'essentiel du gain (MRR de 0,85 à 0,94) pour 1 seconde. Le reranker `bge-base` gagne encore un peu (0,97), mais il est 5 fois plus lent. Près de 5 secondes d'attente en plus de la génération de réponse, c'est trop pour un assistant interactif.

**Les limites, à dire honnêtement.**
- 16 questions, c'est peu : une question de plus ou de moins change un score de 6 points.
- Les questions ont été écrites en regardant les passages : elles reprennent souvent leurs mots, ce qui **avantage BM25**. Sur de vraies questions d'utilisateurs, formulées autrement, la recherche par le sens compterait davantage. C'est justement pour ça qu'on garde les deux.
- MiniLM a été entraîné sur des questions web génériques, pas sur l'aéronautique.

**En entretien.** « La recherche vectorielle ratait les numéros de consigne. J'ai ajouté BM25, fusionné les deux classements avec la RRF, puis un cross-encoder pour réordonner les 20 meilleurs candidats. Sur mon jeu de test, le MRR passe de 0,78 à 0,94, pour environ une seconde de latence. Un reranker plus gros gagnait encore 3 points mais coûtait 5 fois plus de temps : j'ai privilégié l'interactivité. »

### 6.5 Le filtre par numéro de consigne (métadonnées)
**Le problème, trouvé par l'analyse des erreurs sur dev.** Question : « What is the minimum revision date for the maintenance task required by AD 2026-09-14? » BM25 classait bien les passages de l'AD 2026-09-14 aux places 1 à 5, mais ils disparaissaient : la fusion RRF favorise les passages trouvés par les deux méthodes, puis le reranker, entraîné sur des questions web génériques, préférait d'autres consignes au vocabulaire proche (« revision of the maintenance program ») et **ignorait le numéro exact**.

**Les options testées.**
1. Changer la façon de choisir les candidats du reranker (alterner les meilleurs de chaque méthode) : les bons passages arrivaient au reranker, mais il les classait toujours derrière. Abandonné.
2. **Un filtre sur les métadonnées** : si la question cite un numéro d'AD présent dans la base, les passages de cette AD sont toujours relus par le reranker, et 3 d'entre eux sont gardés parmi les 5 envoyés au LLM.

**Le choix et pourquoi : le filtre (option 2).** Un numéro de consigne est une information **structurée** et sans ambiguïté : il est plus fiable de l'exploiter directement que d'espérer qu'un modèle généraliste y fasse attention. On garde 2 places pour d'autres consignes, pour qu'une question comme « l'AD 2025-13-12 a-t-elle été remplacée ? » trouve encore la consigne qui la remplace (vérifié : AD 2025-25-12 reste en 1ʳᵉ position).

**Mesuré sur dev.** Questions par numéro : 7/8 → 8/8 ; abstentions à tort : 2/35 → 1/35 ; aucune autre catégorie ne baisse.

**En entretien.** « L'analyse des erreurs m'a montré que le reranker ignorait les identifiants exacts. Plutôt que de compter sur un modèle généraliste, j'exploite le numéro de consigne comme une métadonnée : si la question en cite un, ses passages sont garantis dans le contexte. C'est un bon exemple de combinaison entre recherche sémantique et données structurées. »

### 6.6 Les paramètres de la recherche
- **30 candidats par méthode** : assez pour que la fusion ait du choix, sans coût notable.
- **20 candidats relus par le reranker** : son coût augmente avec ce nombre. 20 couvre largement les cas où la bonne réponse était en 2ᵉ à 4ᵉ position.
- **5 passages envoyés au LLM** : environ 1 250 mots. Assez pour couvrir une réponse qui demande plusieurs passages, assez peu pour ne pas noyer le LLM.

---

## 7. La génération de la réponse

### 7.1 Un prompt à règles strictes
**Le problème.** Empêcher le LLM d'inventer, et rendre chaque affirmation vérifiable.

**Le choix et pourquoi.** Le message système impose de répondre **uniquement** avec les passages, de **citer** chaque affirmation par le numéro du passage, et de **s'abstenir** quand l'information manque. Les passages sont numérotés [1] à [5] avec leur référence (document, section, page). Le programme retrouve ensuite les numéros cités pour afficher les sources.

**Les limites.** Un prompt ne garantit rien : le LLM peut encore mal citer ou mal résumer. C'est ce que le test de l'étape 6 mesure.

**En entretien.** « Le prompt impose trois choses : répondre seulement à partir des passages, citer chaque affirmation, et dire "je ne sais pas" si l'information manque. Les passages sont numérotés avec leur référence, ce qui permet d'afficher des citations cliquables. »

### 7.2 Un mot-clé d'abstention (`NOT_IN_DOCUMENTS`)
**Pourquoi.** Si le LLM écrit simplement « I don't know » à sa façon, le programme ne peut pas le détecter de manière fiable. Un mot-clé imposé en première ligne permet de savoir **automatiquement** que l'assistant s'est abstenu : on peut l'afficher clairement et le compter dans le test de qualité.

### 7.3 Pourquoi s'abstenir plutôt que répondre de mémoire
Pour « Quelle est la masse maximale au décollage de l'A350-1000 ? », le LLM connaît peut-être la réponse. Mais elle n'est ni dans nos documents, ni vérifiable, ni citable. Dans la maintenance aéronautique, une réponse non sourcée est plus dangereuse qu'une absence de réponse.

**En entretien.** « Je préfère qu'il dise "je ne sais pas" plutôt que de donner un chiffre non vérifiable : dans un contexte réglementé, une erreur confiante coûte plus cher qu'une abstention. »

### 7.4 `gemini-3.1-flash-lite` en premier, `gemini-3.8-flash` en secours
**Mesuré.**
- `gemini-2.5-flash` n'est plus proposé aux nouveaux comptes (erreur 404).
- `gemini-3.8-flash`, sur l'offre gratuite, était soit saturé (erreur 503 au bout d'environ 7 s), soit limité (erreur 429).
- `gemini-3.1-flash-lite` répond en 1 à 5 s, et ses réponses citées étaient justes sur nos exemples.

**Le choix.** `flash-lite` en premier. En cas de saturation, on passe **immédiatement** au modèle suivant ; on n'attend avant de réessayer qu'une fois tous les modèles essayés. Une première version qui réessayait d'abord le modèle saturé faisait monter une réponse à 85 secondes.

**Les limites.** Un modèle « lite » raisonne moins bien sur des questions complexes. Avec une offre payante, on mettrait `gemini-3.8-flash` en premier, en changeant une ligne de `configs/default.yaml`.

### 7.5 Température 0
La **température** règle la part de hasard dans le choix des mots du LLM. À 0, il prend toujours la formulation la plus probable : des réponses factuelles et (presque) reproductibles. Gemini n'accepte pas de graine de hasard (`seed`), donc une reproductibilité parfaite n'est pas garantie.

### 7.6 Traduire en anglais les questions posées en français, pour la recherche seulement
**Mesuré.** « Quels avions sont concernés par l'AD 2026-18-03 ? » : sans traduction, la recherche ne trouvait pas la section « Applicability », car le modèle d'embedding et le reranker ne connaissent que l'anglais. L'assistant s'abstenait. Avec traduction, il répond correctement, en français.

**Le choix.** Si la question contient au moins deux mots français courants, le LLM la traduit en anglais (en gardant les identifiants intacts). La recherche utilise la traduction, mais la réponse est rédigée dans la langue de la question.

**Les limites.** Un appel au LLM en plus (environ 1 s). La détection ne couvre que le français. Une alternative aurait été un modèle d'embedding multilingue, plus lourd.

### 7.7 5 passages envoyés au LLM
Environ 1 200 à 2 200 tokens en entrée : assez pour couvrir une réponse qui demande plusieurs passages, assez peu pour rester rapide et ne pas noyer le LLM dans du texte inutile.

---

## 8. API, interface et déploiement

### 8.1 FastAPI pour l'API
**Pourquoi.** C'est le standard Python pour exposer un service : il valide automatiquement les requêtes (une question vide est refusée avec une erreur claire), produit une documentation interactive (`/docs`) et gère proprement le chargement des modèles au démarrage. Les modèles ne sont chargés qu'**une fois**, pas à chaque question.

**En entretien.** « Le moteur est exposé par une API FastAPI ; les modèles sont chargés au démarrage du serveur, donc une question ne coûte que la recherche et l'appel au LLM, environ 2 secondes. »

### 8.2 Streamlit pour l'interface, séparée de l'API
**Pourquoi.** Streamlit permet une interface web en Python pur, en une centaine de lignes. L'interface n'appelle que l'API, comme n'importe quel autre client : on pourrait la remplacer par un site React ou un plugin dans un outil de maintenance sans toucher au moteur.

**Les limites.** Streamlit convient à une démo ou un outil interne, pas à une application grand public.

### 8.3 Une image Docker avec les modèles intégrés, l'index construit au premier lancement
- **Les modèles (embedding et reranker) sont intégrés à l'image** : pas de téléchargement au démarrage, et la recherche fonctionne hors connexion.
- **Les documents et l'index ne sont pas dans l'image** : ils sont téléchargés et construits au premier lancement (`aerodoc bootstrap`, environ 10 minutes), puis conservés dans des volumes Docker. Ça respecte la règle « aucun document dans le dépôt » tout en gardant une seule commande pour tout lancer.
- **PyTorch en version CPU** : image d'environ 3,4 Go, contre plus de 6 Go avec le support des cartes graphiques.

**En entretien.** « `docker compose up` lance la base, l'API et l'interface ; au premier lancement, le corpus est reconstruit depuis les sources publiques, ce qui garantit qu'aucun document n'est versionné et que l'index est reproductible. »

## 9. Méthode de travail

### 9.1 Une évaluation légère plutôt qu'un protocole de recherche
**Le choix et pourquoi.** La priorité était un système qui marche et qu'on comprend, en deux jours. On mesure donc simplement :
- une petite série de questions pour choisir la recherche (16 questions) ;
- une vingtaine de questions pour le score final (étape 6).

C'est suffisant pour justifier les choix et donner un chiffre crédible.

**Les limites.** Avec si peu de questions, les écarts de quelques points ne sont pas significatifs. En production, il faudrait des centaines de questions, idéalement posées par de vrais techniciens.

### 9.2 Le test de qualité : 73 questions, dev/test, trois systèmes comparés
**Le problème.** Prouver que le système marche, avec des chiffres qui résistent aux questions d'un recruteur.

**La démarche, en deux temps.**
1. Un premier test de 20 questions (16/16 réponses justes). Il prouvait que le système fonctionne, mais pas à quel point : 16/16 est compatible avec un vrai taux d'environ 80 %, et les questions reprenaient les mots des documents.
2. **Un test plus sérieux** : 73 questions, une séparation dev/test, trois systèmes comparés et des marges d'erreur.

**Les choix et pourquoi.**
- **Des questions générées par le LLM, avec obligation de reformuler**, à partir de passages tirés au hasard (graine fixe) : on obtient du volume sans écrire chaque question à la main. Un **filtre automatique** rejette les questions dont la réponse n'est pas dans le passage ou est déjà dans la question, et une **relecture** retire les questions ambiguës (19 sur 66).
- **Des cas difficiles écrits à la main** : numéros de consigne presque identiques, consignes remplacées, questions multi-documents, questions en français, et 22 % de questions sans réponse (dont 3 numéros de consigne qui n'existent pas).
- **Une validation humaine par échantillon** (20 questions tirées au hasard) avant tout calcul : c'est ce qui rend le jeu crédible sans tout relire.
- **Dev / test (60/40)** : on analyse les erreurs et on corrige sur dev ; test est utilisé une seule fois. Sinon, on adapte le système (ou le test) aux questions qui servent à le juger.
- **Trois systèmes comparés** : Gemini seul montre ce que le RAG apporte ; le RAG simple montre ce qu'apportent BM25, le reranker et le filtre par numéro.
- **Mots-clés plutôt qu'un juge LLM** : simple, gratuit, transparent. Les échecs sont relus à la main pour repérer les faux négatifs.
- **Mesurer les deux côtés de l'abstention** : un assistant qui dit toujours « je ne sais pas » n'invente jamais, mais ne sert à rien.
- **Intervalles de confiance (Wilson)** : avec 22 questions, un score sans marge d'erreur trompe.

**Résultat (test).** Réponses justes : Gemini seul 27 %, RAG simple 50 %, **RAG final 82 % [62-93]**. Réponses inventées sur les questions sans réponse : 50 %, 0 %, **0 %**. Bon passage dans les 5 : 73 % → **91 %**.

**Les limites.** Un test plus grand reste souhaitable ; la vérification par mots-clés est grossière (1 faux négatif sur 4 échecs) ; les questions sans réponse sont écrites à la main.

**En entretien.** « J'ai construit 73 questions, dont 22 % sans réponse et des pièges, séparées en dev et test. J'ai comparé trois systèmes : le LLM seul invente sur la moitié des questions sans réponse et répond juste à 27 % ; mon RAG final répond juste à 82 %, avec un intervalle de confiance de 62 à 93 %, et n'invente jamais. L'analyse des erreurs sur dev m'a fait ajouter un filtre sur les numéros de consigne, et je n'ai lancé le test qu'une fois, à la fin. »

### 9.3 Configuration versionnée, mesures notées
Tous les paramètres sont dans `configs/default.yaml`, versionné dans Git. Chaque mesure est notée dans `EXPERIMENTS.md`. On peut donc toujours dire quelle configuration a produit quel résultat.

### 9.4 Le rôle de l'IA dans le projet
Le code a été écrit par un assistant de code IA (Claude Code). Le rôle de Jules :
- concevoir le système et définir les priorités (simplicité, rapidité, compréhension) ;
- valider chaque choix technique à partir des mesures ;
- relire les questions de test ;
- analyser les résultats.

**En entretien.** « J'ai utilisé un assistant de code IA pour écrire le code. Mon travail a été de concevoir le système, de choisir entre les options à partir des mesures, et de valider la qualité. Ce document de justification en est la trace. »
