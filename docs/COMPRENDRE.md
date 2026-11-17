# Comprendre AeroDoc

Ce document explique le système à Jules, étape par étape, sans supposer de connaissances préalables. Il grandit à chaque étape du plan.

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
