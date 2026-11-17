# Comprendre AeroDoc

Ce document explique le système à Jules, étape par étape, sans supposer de connaissances préalables. Il grandit à chaque étape du plan.

**La justification détaillée de chaque choix (options, raisons, limites, formulation pour l'entretien) est dans [`docs/CHOIX.md`](CHOIX.md).**

---

## Le projet en une phrase
AeroDoc répond à des questions sur la documentation de maintenance des avions (publiée par la FAA, l'autorité américaine de l'aviation civile) en **cherchant d'abord les bons passages** dans les documents, puis en demandant à un LLM de **répondre uniquement à partir de ces passages, en les citant**. C'est ce qu'on appelle un **RAG** (*Retrieval-Augmented Generation*, « génération augmentée par la recherche »).

## Schéma du flux (cible)

```
                    PRÉPARATION (une fois)
  Documents FAA ──► découpage en passages ──► embeddings ──► PostgreSQL + pgvector
  (PDF, textes)      (chunks)                 (vecteurs)      (texte + vecteurs + page, URL)

                    À CHAQUE QUESTION
  Question ──► recherche des passages proches ──► LLM (Gemini) ──► réponse citée
                (par le sens + par mots-clés)      « réponds avec ces    ou « je ne sais pas »
                                                    passages seulement »
```

---

## Glossaire

| Terme | Explication simple |
|---|---|
| **LLM** (*Large Language Model*) | Modèle d'IA qui comprend et écrit du texte (ChatGPT, Gemini, Mistral…). |
| **API** | « Porte d'entrée » qui permet à un programme d'utiliser un service. Notre code envoie une question à l'API de Gemini et reçoit une réponse. |
| **Clé API** | Mot de passe qui identifie ton compte auprès d'un service. Secret : jamais dans Git. |
| **Jeton Bearer / en-tête** | La façon dont la clé est jointe à chaque requête envoyée au service. |
| **RAG** | Chercher les passages pertinents, puis faire répondre le LLM uniquement à partir d'eux. Limite les inventions et permet de citer. |
| **Chunk** (passage) | Morceau de document de quelques centaines de mots. On cherche des chunks plutôt que des documents entiers : c'est plus précis. |
| **Embedding** (vecteur) | Liste de nombres qui représente le sens d'un texte. Deux textes de sens proche donnent des listes proches. |
| **pgvector** | Extension de PostgreSQL qui stocke les vecteurs et trouve les plus proches. |
| **Docker / conteneur** | Outil qui fait tourner un logiciel dans une « boîte » préconfigurée, identique sur toutes les machines. |
| **docker compose** | Fichier (`docker-compose.yml`) qui décrit les conteneurs du projet et les lance d'une commande. |
| **FAA** | *Federal Aviation Administration* : autorité américaine de l'aviation civile. |
| **AD** (*Airworthiness Directive*, consigne de navigabilité) | Document officiel obligatoire : « sur tel avion, faites telle inspection sous tel délai ». |
| **Federal Register** | Journal officiel américain, où sont publiées les AD ; il a une API gratuite. |
| **Hugging Face** | Site qui héberge des modèles d'IA gratuits, dont nos modèles d'embedding. |

---

## Étape 1 — Mise en place

### Ce qui a été construit
- **Le squelette du projet** : un package Python `aerodoc` (dans `src/aerodoc/`), une commande `aerodoc`, des tests.
- **La base de données** : PostgreSQL avec l'extension pgvector, lancée dans un conteneur Docker par `make db`.
- **La configuration** : les réglages (adresse de la base, fournisseur de LLM, clé API) sont lus depuis des variables d'environnement ou un fichier `.env` local, jamais écrits dans le code.

### Les outils et pourquoi
| Outil | Rôle | Pourquoi ce choix |
|---|---|---|
| `uv` | Installe les bibliothèques Python et fige leurs versions (`uv.lock`) | Rapide ; tout le monde obtient exactement les mêmes versions |
| PostgreSQL 17 + pgvector 0.8 | Stocke le texte, les vecteurs et les métadonnées (document, page, URL) | Une seule base pour tout ; pas besoin d'un service vectoriel séparé |
| Docker / docker compose | Lance la base sans rien installer à la main | Le projet marche pareil sur n'importe quelle machine |
| `psycopg` | Bibliothèque Python qui parle à PostgreSQL | La référence actuelle (version 3) |
| `pydantic-settings` | Lit la configuration depuis `.env` | Vérifie les types, évite les secrets dans le code |
| `typer` | Crée la commande `aerodoc ...` | Une ligne de commande propre en quelques lignes |
| `pytest`, `ruff` | Tests automatiques ; vérification du style du code | Détecter les erreurs tôt |

### Choix et raisons
- **Image Docker `pgvector/pgvector:pg17`** : l'image officielle de pgvector, avec PostgreSQL et l'extension déjà installés.
- **Fichier `.env` ignoré par Git, `.env.example` versionné** : on montre quelles variables existent sans jamais publier la clé.
- **Tests « integration » ignorés si la base est éteinte** : `make test` reste utilisable même sans Docker.

### Pourquoi une base vectorielle ?
Une base classique sait répondre à « trouve les lignes où `avion = 'A320'` ». Elle ne sait pas répondre à « trouve les passages qui **parlent de la même chose** que ma question ». pgvector ajoute cette opération : on lui donne le vecteur de la question, il renvoie les vecteurs les plus proches. Le test `tests/test_db.py` le montre en miniature : on range « landing gear » en `[1,0,0]` et « fuel pump » en `[0,1,0]`. Une question représentée par `[0.9,0.1,0]` retrouve « landing gear », car c'est le vecteur le plus proche.

### Commandes
- `make db` : démarre la base et vérifie qu'elle répond ;
- `make test` : vérifie le style du code et lance les tests ;
- `uv run aerodoc health` : affiche les versions de PostgreSQL et de pgvector.

---

## Étape 2 — Le corpus

### Ce qui a été construit
`make data` télécharge tous les documents et produit :
- `data/raw/directives/` : **225 consignes de navigabilité (AD)** publiées entre janvier 2022 et novembre 2026, en texte brut ;
- `data/raw/handbooks/FAA-H-8083-30B.pdf` : le **manuel de maintenance de la FAA** (677 pages) ;
- `data/manifest.jsonl` : la **liste de tous les documents**, une ligne par document (titre, numéro d'AD, avions concernés, dates, adresse source, empreinte SHA-256 qui prouve que le fichier n'a pas changé) ;
- la table `documents` dans la base, visible dans Adminer.

Répartition : A320 (et A318/A319/A321) 70, A350 72, B737 61, ATR 72 24. Deux consignes concernent deux familles à la fois.

### Le corpus, c'est quoi ?
L'ensemble des documents dans lesquels l'assistant a le droit de chercher. **Un RAG ne vaut que par son corpus** : si l'information n'y est pas, il ne peut pas la trouver (et doit dire « je ne sais pas »).

Notre corpus mélange deux types de documents, ce qui rend le problème réaliste :
| | Consignes (AD) | Manuel |
|---|---|---|
| Taille | courtes (1 à 15 pages) | longue (677 pages) |
| Style | juridique, très structuré, plein d'identifiants | pédagogique, avec figures |
| Questions typiques | « Quelle AD concerne le train d'atterrissage de l'A320 ? » | « Comment inspecter une soudure ? » |

### À quoi ressemble une consigne de navigabilité
Exemple réel : **AD 2026-18-03** (document `2026-18052`, publié le 3 septembre 2026). Chaque AD a la même structure :
- **(a) Effective Date** : date d'entrée en vigueur (18 septembre 2026) ;
- **(c) Applicability** : quels avions exactement (ici A318-112, A319-115…, A320-214…, A321-211…) ;
- **(d) Subject** : le système concerné, avec un code ATA (classification standard des systèmes d'avion ; 57 = ailes) ;
- **(e) Unsafe Condition** : le danger. Ici, des marques d'outil sur les supports du train principal, qui pourraient provoquer une fissure de fatigue puis l'effondrement du train ;
- **(f) Compliance / (g) Requirements** : ce qu'il faut faire et dans quel délai.

Particularité : pour les avions européens (Airbus, ATR), la FAA reprend souvent une consigne de l'**EASA** (l'agence européenne de la sécurité aérienne) et écrit simplement « appliquez l'EASA AD 2026-0142 ». Le détail des actions n'est alors **pas dans notre corpus** : c'est une limite à connaître (l'assistant devra dire qu'il ne sait pas).

Le texte contient aussi des repères de page du Federal Register, comme `[[Page 56578]]`. On s'en servira pour **citer la page exacte**.

### Choix et raisons
- **API du Federal Register pour chercher, govinfo.gov pour le texte** : l'API donne les métadonnées propres (dates, numéro d'AD) ; le texte brut du Federal Register est protégé contre les robots, alors que govinfo.gov (l'imprimerie officielle du gouvernement américain) sert le même document en texte simple.
- **Texte plutôt que PDF pour les AD** : le PDF du Federal Register est sur 3 colonnes, difficile à lire proprement ; la version texte est propre et garde les numéros de page.
- **Filtre sur le résumé** : une AD n'est gardée que si son résumé mentionne bien le modèle (par exemple « A350 »), pour éviter les documents hors sujet.
- **Depuis 2022, 70 au maximum par famille** : assez pour être réaliste, assez peu pour indexer en quelques minutes.
- **`make data` est relançable** : les fichiers déjà présents ne sont pas retéléchargés.
- **Aucun document dans Git** : ils sont publics et se retéléchargent ; on versionne la recette (`configs/corpus.yaml`), pas les données.

### Voir la base de données (Adminer)
Adminer est une page web qui affiche la base comme un tableur : http://localhost:8080. Connexion : système **PostgreSQL**, serveur **db**, utilisateur / mot de passe / base **aerodoc**. Ouvrir la table `documents`, puis « Afficher les données ».

---

## Étape 3 — Découpage et indexation

### Ce qui a été construit
`make index` transforme les 226 documents en **5 295 passages (chunks)** rangés dans la table `chunks` : 3 478 pour les consignes, 1 817 pour le manuel. Pour chaque passage, la base stocke :
- le texte ;
- un **en-tête** (numéro d'AD, avions, date d'effet, section) ;
- la page (page du Federal Register, ou numéro imprimé du manuel comme `10-13`) ;
- la section ;
- son **vecteur** (384 nombres) ;
- un index « plein texte » qui servira à la recherche par mots-clés à l'étape 4.

`aerodoc search "question"` affiche les 5 passages les plus proches, sans LLM. `aerodoc explore` produit une page web (`data/explorer.html`) qui montre tout cela.

### Que se passe-t-il quand on cherche « landing gear inspection » ?
1. La question est transformée en vecteur par le même modèle d'embedding que les passages (avec une courte consigne devant, recommandée par ce modèle pour les questions).
2. PostgreSQL compare ce vecteur aux 5 295 vecteurs des passages avec la **similarité cosinus**, qui mesure à quel point deux vecteurs pointent dans la même direction (1 = identiques, 0 = sans rapport). Un index **HNSW**, une sorte de « carte routière » entre vecteurs voisins, évite de tout comparer un par un.
3. On garde les 5 meilleurs. Résultat réel : 4 passages du chapitre 10 du manuel (« Inspection Concepts & Techniques », page 10-13 en tête, score 0,81), puis une consigne.

### Pourquoi la recherche par le sens rate un numéro de consigne exact
Résultat réel pour « AD 2026-18-03 » : la bonne consigne n'arrive qu'en **3ᵉ position** (score 0,744), derrière AD 2026-09-03 (0,751) et AD 2025-23-04 (0,745). Les scores sont presque identiques.

La raison : le modèle d'embedding encode le **sens**, pas les caractères exacts. Pour lui, « 2026-18-03 » et « 2026-09-03 » sont deux « numéros de consigne » quasi équivalents. Une recherche par **mots-clés** (étape 4) trouve en revanche la chaîne exacte « 2026-18-03 » sans hésiter. C'est tout l'intérêt de combiner les deux.

### Choix et raisons
| Choix | Pourquoi |
|---|---|
| **Modèle `BAAI/bge-small-en-v1.5`** (384 dimensions) | Mesuré ici : 9,6 passages/s contre 2,7 pour `bge-base`, donc 7 min d'indexation au lieu d'environ 25. La qualité perdue est récupérée par la recherche hybride et le reranker. Gratuit, tourne sur CPU, documents en anglais. |
| **Passages d'environ 250 mots, chevauchement de 40 mots** | Assez petits pour être précis et citables, assez grands pour garder le contexte. Sous la limite de 512 tokens du modèle, en-tête compris. Le chevauchement évite de couper une idée en deux sans trace. |
| **Coupure aux changements de section** (si le passage a déjà 80 mots) | Un passage parle d'un seul sujet ; les petites sections, comme « (d) Subject », sont regroupées avec leurs voisines. |
| **En-tête ajouté à chaque passage** | Un passage qui dit seulement « appliquez l'EASA AD 2026-0142 » sait quand même qu'il appartient à l'AD 2026-18-03, sur A320, section (g). |
| **Sections administratives ignorées** (adresses, Paperwork Reduction Act…) | Elles ne répondent à aucune question de maintenance et pollueraient les résultats. |
| **Manuel découpé page par page, section tirée de la table des matières du PDF** | Permet de citer « chapitre 10, section Special Inspections, page 10-13 ». |
| **PyTorch version CPU** | Environ 3 Go de moins que la version prévue pour les cartes graphiques, dont on n'a pas besoin. |

### Schéma
```
Fichier AD (.txt) ──► paragraphes (+ page, section) ──► passages de ~250 mots ─┐
Manuel (.pdf)     ──► pages (+ numéro imprimé, chapitre) ──► passages ─────────┤
                                                                               ▼
                                            en-tête + texte ──► bge-small ──► vecteur (384)
                                                                               ▼
                                            PostgreSQL : table chunks (texte, page, section,
                                                         vecteur + index HNSW, plein texte)
```

---

## Étape 4 — Une recherche efficace (hybride + reranker)

### Ce qui a été construit
La recherche se fait désormais en 4 temps :
```
question ─┬─► recherche par le sens (embeddings) ─► 30 meilleurs ─┐
          └─► recherche par mots-clés (BM25)     ─► 30 meilleurs ─┤
                                                                  ▼
                                  fusion des deux classements (RRF) ─► 20 meilleurs
                                                                  ▼
                            reranker : relit chaque paire (question, passage) ─► 5 meilleurs ─► LLM
```
- `aerodoc search "question"` affiche les 5 passages retenus, et **par quelle méthode chacun a été trouvé** (par exemple « dense #8, bm25 #1 »).
- `aerodoc probe` compare les configurations sur 16 questions de test (`eval/retrieval_probe.jsonl`).

### Les trois briques, simplement
- **BM25** : un moteur de recherche par mots-clés. Un passage marque des points pour chaque mot de la question qu'il contient, d'autant plus que ce mot est **rare** dans l'ensemble des documents. « 2026-18-03 » est rare, donc décisif ; « airplane » est partout, donc il compte peu.
- **RRF (Reciprocal Rank Fusion)** : pour fusionner deux classements, chaque passage reçoit 1/(60 + son rang) dans chaque liste, et on additionne. Un passage bien classé par les deux méthodes l'emporte. On n'utilise que les rangs, parce que les scores des deux méthodes ne sont pas sur la même échelle.
- **Reranker (cross-encoder)** : un petit modèle qui lit la question **et** le passage **ensemble** et note leur pertinence. Plus précis que la comparaison de vecteurs calculés séparément, mais plus lent : on ne l'applique qu'aux 20 meilleurs candidats.

### Exemple réel
« AD 2026-18-03 » :
- **avant** (recherche par le sens seule) : la bonne consigne en 3ᵉ position, derrière deux autres consignes ;
- **après** : les 5 passages retenus viennent tous de l'AD 2026-18-03, trouvés par BM25 puis réordonnés par le reranker.

« landing gear inspection » : la recherche par le sens apporte les pages du chapitre 10 du manuel (Inspection) que BM25 classait loin. Les deux méthodes se complètent.

### Les chiffres (16 questions de test)
| Configuration | 1ʳᵉ position | Top 5 | MRR | Latence |
|---|---|---|---|---|
| Sens seul | 75 % | 81 % | 0,78 | 20 ms |
| BM25 seul | 88 % | 100 % | 0,92 | 1 ms |
| Hybride | 75 % | 100 % | 0,85 | 17 ms |
| **Hybride + reranker MiniLM (retenu)** | **88 %** | **100 %** | **0,94** | **≈ 1 s** |
| Hybride + reranker bge-base | 94 % | 100 % | 0,97 | ≈ 4,9 s |

Le détail des raisons et des limites est dans `docs/CHOIX.md`, section 6.
