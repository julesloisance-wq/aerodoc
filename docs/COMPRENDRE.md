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

### La recherche pas à pas, sur un exemple réel : « landing gear inspection »

**1. Deux listes séparées (30 passages chacune).**
| Rang | Recherche par le sens (score cosinus) | BM25 (score mots-clés) |
|---|---|---|
| #1 | Manuel, ch. 10, Special Inspections (0,806) | AD 2025-11-08, (e) Unsafe Condition (5,29) |
| #2 | Manuel, ch. 10, Checklists (0,794) | Manuel, ch. 14, Human Factors… (5,17) ← hors sujet |
| #3 | Manuel, ch. 4, Reading Drawings (0,780) | Manuel, ch. 6, Weight & Balance (4,79) ← hors sujet |

Chaque méthode a ses erreurs : BM25 remonte des pages qui contiennent juste les mots « landing » ou « gear » dans un autre contexte.

**2. La fusion (RRF).** Les deux listes réunies donnent **45 passages différents** (15 sont dans les deux). Chacun reçoit 1/(60 + rang) pour chaque liste où il apparaît :
- AD 2025-11-08 : 8ᵉ en sens, 1ᵉʳ en BM25 → 1/68 + 1/61 = **0,0311** ;
- Manuel, Reading Drawings : 3ᵉ en sens, 5ᵉ en BM25 → 1/63 + 1/65 = **0,0313** ;
- un passage présent dans une seule liste n'a qu'un des deux termes, donc un score plus faible.

On trie les 45 par ce score et on garde les **20 premiers** : ce sont « les 20 meilleurs en sortie de RRF ».

**3. Le reranker relit ces 20 passages avec la question** et les reclasse :
| Classement final | Score reranker | Rang après RRF |
|---|---|---|
| #1 AD 2025-11-08, (e) Unsafe Condition | 5,77 | 2ᵉ |
| #2 Manuel, ch. 10, Checklists | 4,64 | 8ᵉ |
| #3 Manuel, ch. 10, Special Inspections | 4,33 | **16ᵉ** |
| #4 AD 2023-23-11, (e) Reason | 4,07 | 5ᵉ |
| #5 Manuel, ch. 10, Severe Turbulence Inspection | 4,02 | 13ᵉ |

Le passage « Reading Drawings », 1ᵉʳ après la fusion, sort du top 5 : en lisant la question et le passage ensemble, le reranker voit qu'il parle de lire des plans, pas d'inspection. À l'inverse, « Special Inspections », 16ᵉ, remonte en 3ᵉ position.

**Lire « dense #8, bm25 #1 »** : avant la fusion, ce passage était 8ᵉ dans la liste de la recherche par le sens et 1ᵉʳ dans celle de BM25. S'il n'y a qu'une méthode, par exemple « dense #1 », le passage n'était pas dans les 30 premiers de l'autre.

### L'index HNSW
**Le problème.** Trouver les vecteurs les plus proches de la question parmi 5 295. La méthode naïve compare la question à chacun.

**L'idée (*Hierarchical Navigable Small World*).** À l'indexation, chaque vecteur est relié à quelques voisins proches, ce qui forme un réseau. On ajoute des étages : en haut, peu de points reliés par de longues liaisons, comme des autoroutes ; en bas, tous les points reliés à leurs proches voisins, comme des rues. Pour chercher, on part du haut, on saute à chaque fois vers le voisin le plus proche de la question, puis on descend d'étage, jusqu'à arriver dans le bon quartier. On examine ainsi quelques centaines de vecteurs au lieu de tous.

**Le compromis.** C'est une recherche **approximative** : très rarement, elle peut manquer le vrai plus proche voisin, en échange d'une énorme accélération. À 5 295 passages, la comparaison exhaustive serait aussi très rapide. HNSW devient indispensable à partir de centaines de milliers de vecteurs, et c'est l'index standard de pgvector.

### Le reranker, plus en détail
- **Les embeddings (bi-encoder)** résument la question et chaque passage **séparément**, en un vecteur chacun, puis comparent les vecteurs. Le résumé du passage a été fait à l'avance, **sans connaître la question**. C'est rapide (les 5 295 vecteurs sont déjà calculés), mais approximatif.
- **Le reranker (cross-encoder)** reçoit la question **et** le passage **collés ensemble** et lit les deux en même temps : chaque mot de la question est mis en relation avec chaque mot du passage. Il sort un score de pertinence (plus il est haut, plus le passage répond à la question). C'est beaucoup plus précis, mais il faut refaire ce calcul pour chaque paire au moment de la question : environ 1 s pour 20 passages, donc environ 4 à 5 minutes pour les 5 295. D'où l'organisation en entonnoir : une recherche rapide réduit à 20 candidats, et le reranker, précis mais lent, les départage.

---

## Étape 5 — La réponse avec citations et abstention

### Ce qui a été construit
`aerodoc ask "question"` fait tout le parcours :
```
question ─► (si elle est en français : traduction en anglais, pour la recherche seulement)
         ─► recherche hybride + reranker ─► 5 passages numérotés [1] à [5]
         ─► prompt (règles + passages + question) ─► Gemini ─► réponse avec [n]
         ─► affichage : réponse + liste des sources citées (document, section, page, lien)
```
Exemples réels : `docs/EXEMPLES.md` (regénérables avec `uv run python scripts/make_examples.py`).

### Le prompt, c'est quoi ?
Le **prompt** est le texte envoyé au LLM. Il a deux parties :
- le **message système** : les règles du jeu, identiques pour toutes les questions ;
- le **message utilisateur** : les 5 passages numérotés, puis la question.

Les règles (dans `src/aerodoc/answer.py`) :
1. répondre **uniquement** avec les passages, jamais avec ses connaissances ;
2. **citer** chaque affirmation avec le numéro du passage, par exemple [2] ;
3. si l'information manque, commencer par le mot-clé `NOT_IN_DOCUMENTS` puis dire ce qui manque (c'est l'**abstention**) ; si seule une partie est couverte, répondre à cette partie et signaler le reste ;
4. signaler quand une consigne renvoie à un autre document (par exemple une consigne EASA) ;
5. recopier exactement les identifiants (numéros d'AD, modèles, références de pièces) ;
6. répondre dans la langue de la question.

Le programme repère ensuite les `[n]` dans la réponse pour afficher les sources correspondantes, et le mot-clé `NOT_IN_DOCUMENTS` pour afficher « je ne sais pas ».

### Exemple réel, de bout en bout
Question : « Which airplanes are affected by AD 2026-18-03 and what is the unsafe condition? »
1. La recherche trouve 5 passages, tous de l'AD 2026-18-03.
2. Gemini reçoit les règles, les passages et la question (1 603 tokens en entrée).
3. Il répond (221 tokens) : les modèles A318-112, A319-115…, puis la condition dangereuse (fatigue du support de train principal, risque d'effondrement), avec les citations [4], [1], [3].
4. Le programme affiche la réponse et les 3 sources citées, avec leur page du Federal Register et leur lien.

### L'abstention, en pratique
« What is the maximum takeoff weight of the Airbus A350-1000? » : la recherche trouve des pages du manuel sur la masse et le centrage, mais aucune ne parle de l'A350-1000. L'assistant répond « je ne sais pas » au lieu d'inventer un chiffre (qu'un LLM « connaît » peut-être, mais qui ne serait ni vérifiable ni citable).

### Choix et raisons (détails dans `docs/CHOIX.md`, section 7)
- **`gemini-3.1-flash-lite` en premier, `gemini-3.8-flash` en secours** : sur l'offre gratuite, le second était souvent saturé ou limité ; le premier répond en 1 à 5 s avec de bonnes réponses citées.
- **Température 0** : la température règle la part de hasard dans les réponses du LLM ; à 0, il choisit toujours la formulation la plus probable, ce qu'on veut pour des réponses factuelles.
- **Traduction des questions en français** : le modèle d'embedding et le reranker ne connaissent que l'anglais ; sans traduction, la question « Quels avions sont concernés par l'AD 2026-18-03 ? » ne trouvait pas la bonne section et l'assistant s'abstenait.

### Temps de réponse (modèles déjà chargés)
| Étape | Temps |
|---|---|
| Recherche par le sens | ≈ 20 ms |
| BM25 | ≈ 1 ms |
| Reranker | 0,7 à 0,9 s |
| Gemini | 0,9 à 4,8 s (variable sur l'offre gratuite) |
| **Total** | **1,6 à 5,6 s** |

La toute première question après le démarrage prend environ 10 s de plus : il faut charger les modèles en mémoire. L'API (étape 7) les gardera chargés.

### Limites observées
- Pour « What are the detailed inspection steps required by EASA AD 2026-0142? », l'assistant s'abstient, ce qui est juste sur le fond (le détail n'est pas dans le corpus), mais le reranker a écarté les passages de l'AD 2026-18-03 qui citent cette consigne : l'idéal aurait été de dire « l'AD 2026-18-03 renvoie à cette consigne, dont le détail n'est pas disponible ».
- Le reranker MiniLM est générique (questions web) : il peut écarter un bon passage dans des formulations inhabituelles.
