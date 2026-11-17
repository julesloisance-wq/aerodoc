# PLAN — AeroDoc (version simplifiée)

Assistant qui répond à des questions sur la documentation de maintenance aéronautique de la FAA (l'autorité américaine de l'aviation civile), **en citant ses sources** et en disant « je ne sais pas » quand la réponse n'est pas dans les documents.

**Format : 2 jours.** Claude Code écrit tout le code. Jules doit comprendre chaque étape et savoir l'expliquer en entretien.

**Priorité : un système qui marche bien et qu'on comprend.** L'évaluation est volontairement légère.

---

## Objectif à la fin du jour 2
1. Un dépôt GitHub propre, qui se lance avec `docker compose up`.
2. Un assistant qui répond avec citations (document, page) et qui s'abstient quand il ne sait pas.
3. Une interface web simple.
4. Un score simple sur une vingtaine de questions, pour le README et le CV.
5. Un `README.md` en anglais et un `docs/COMPRENDRE.md` en français.

## Outils
| Rôle | Outil | Pourquoi |
|---|---|---|
| Langage | Python, `uv` | Standard en IA ; `uv` installe les dépendances vite et de façon reproductible |
| Sources | API du Federal Register (consignes FAA), PDF du manuel FAA | Documents publics, réels, techniques |
| Lecture des PDF | PyMuPDF | Rapide, garde les numéros de page (utile pour citer) |
| Base de données | PostgreSQL + pgvector, dans Docker | Une seule base pour le texte, les vecteurs et les métadonnées |
| Embeddings | modèle open source via `sentence-transformers` | Gratuit, tourne sur CPU |
| Recherche par mots-clés | plein texte PostgreSQL ou BM25 | Trouve les identifiants exacts (« AD 2024-12-05 ») |
| Reranker | cross-encoder open source | Trie finement les meilleurs passages |
| LLM | Gemini (offre gratuite) | Gratuit, bonne qualité ; fournisseur changeable par configuration |
| API, interface | FastAPI, Streamlit | Standards, rapides à mettre en place |
| Tests | pytest, ruff | Fiabilité, lisibilité |

---

## Étapes

### Jour 1 — Un assistant qui marche
1. **Mise en place** : structure du dépôt, dépendances, PostgreSQL + pgvector dans Docker, `.env.example`. *Livrable : `make db` démarre la base, `make test` passe.*
2. **Corpus** : 200 à 300 consignes FAA récentes (A320, B737, ATR 72, A350) via l'API du Federal Register, plus un volume du manuel FAA de maintenance (*Aviation Maintenance Technician Handbook*). *Livrable : `make data`, manifeste des documents, `DATA_LICENSES.md`.*
3. **Découpage et indexation** : texte page par page, découpage en passages (chunks), embeddings, stockage avec métadonnées (document, page, URL). *Livrable : `make index`, une commande affiche les passages les plus proches d'une question.*
4. **Recherche efficace** : recherche par sens + par mots-clés, fusionnées, puis reranker. On applique directement la configuration reconnue comme la meilleure, avec une comparaison rapide pour la justifier. *Livrable : la recherche trouve aussi bien « inspection du train d'atterrissage » que « AD 2024-12-05 ».*
5. **Réponse avec citations et abstention** : prompt qui impose de répondre uniquement à partir des passages, de citer, et de dire « je ne sais pas » sinon. *Livrable : `aerodoc ask "..."`, 5 exemples dans `docs/EXEMPLES.md` dont une question sans réponse.*

### Jour 2 — Présenter et mesurer simplement
6. **Petit test de qualité** : ~20 questions (dont 3 ou 4 sans réponse dans les documents), relues rapidement par Jules. Un script mesure : bon passage trouvé ou non, réponse correcte ou non (vérification simple), abstention correcte, temps de réponse. *Livrable : `make eval`, résultats dans `EXPERIMENTS.md`.*
7. **API, interface, Docker** : FastAPI (`POST /ask`, `GET /health`), interface Streamlit (question, réponse, citations cliquables), `docker compose up` complet. *Livrable : capture d'écran de l'interface.*
8. **Finalisation** : README en anglais (pitch, architecture, résultats, limites, transparence sur l'assistant de code IA), `docs/COMPRENDRE.md` complet, entraînement à la présentation de 3 minutes.

### Bonus si du temps reste
- Extraction structurée : chaque consigne transformée en fiche (avion, date, actions, délais), pour filtrer par avion ou par date.
- Agent qui appelle des outils, serveur MCP, CI GitHub Actions, déploiement en ligne.

---

## Présenter le projet honnêtement
Jules n'a pas écrit le code : il a **conçu le système avec un assistant de code IA, fait les choix techniques, relu le jeu de questions et analysé les résultats**. C'est ce qu'il dit en entretien, sans prétendre davantage.

### Questions d'entretien à savoir traiter
1. Explique le fonctionnement d'un RAG, de la question à la réponse.
2. Pourquoi combiner recherche par sens et recherche par mots-clés ?
3. Comment as-tu choisi la taille des passages ?
4. Qu'est-ce qu'un reranker et que coûte-t-il ?
5. Comment limites-tu les hallucinations ?
6. Comment sais-tu que ton système marche ?
7. Quelles sont ses limites, et que ferais-tu ensuite ?
8. Quelle part du travail est la tienne si le code a été généré par une IA ?
