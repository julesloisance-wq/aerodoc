# Présenter AeroDoc

Ce document prépare Jules à présenter le projet en entretien : un pitch de 3 minutes, des lignes de CV, et des réponses courtes aux questions les plus probables. Les justifications complètes sont dans `CHOIX.md`, les explications dans `COMPRENDRE.md`. Pour lancer et réussir une démo en direct de l'interface : `DEMO.md`.

À dire **avec ses propres mots** : ce sont des trames, pas un texte à réciter.

---

## Le pitch en 3 minutes

### 1. Le problème (30 s)
> « Dans la maintenance aéronautique, les techniciens doivent appliquer des consignes de navigabilité : des documents officiels de la FAA qui disent, par exemple, "sur tels A320, inspectez tel support du train d'atterrissage sous tel délai". Il y en a des milliers, elles changent chaque semaine, et une réponse n'a de valeur que si elle est traçable. Un LLM seul ne convient pas : sur mon benchmark, Gemini sans documents ne répond juste qu'à 27 % des questions, et il invente une réponse à la moitié des questions qui n'ont pas de réponse. »

### 2. La solution (30 s)
> « J'ai construit AeroDoc, un assistant RAG sur 225 consignes de la FAA et le manuel de maintenance de la FAA. Il cherche d'abord les passages pertinents, puis demande au LLM de répondre uniquement à partir de ces passages, en citant chaque affirmation avec la consigne, la section et la page. Si l'information n'y est pas, il dit qu'il ne sait pas. »

### 3. Comment ça marche (60 s)
> « Trois points techniques.
> D'abord, le découpage : je découpe les documents en passages qui suivent leur structure (applicabilité, condition dangereuse, actions requises…) et j'ajoute à chaque passage un en-tête avec le numéro de consigne et l'avion, pour qu'aucun passage ne soit orphelin.
> Ensuite, la recherche hybride : la recherche vectorielle comprend le sens mais confond les numéros de consigne ; j'ajoute BM25, une recherche par mots-clés, je fusionne les deux classements, puis un reranker relit les 20 meilleurs candidats. L'analyse des erreurs m'a montré que ce reranker ignorait les numéros exacts : j'ai ajouté un filtre sur les métadonnées.
> Enfin, le prompt impose de citer et de s'abstenir, avec un marqueur que le programme détecte. Le tout est exposé par une API FastAPI, avec une interface Streamlit, et se lance avec docker compose. »

### 4. Les résultats (40 s)
> « J'ai construit un benchmark de 73 questions, dont 22 % sans réponse et des pièges, séparé en dev et test. J'ai analysé les erreurs sur dev et je n'ai lancé le test qu'une fois, à la fin. Sur test, AeroDoc répond juste à 82 %, avec un intervalle de confiance de 62 à 93 %, contre 50 % pour un RAG vectoriel simple et 27 % pour le LLM seul. Il n'invente jamais de réponse, et le bon passage est retrouvé 9 fois sur 10. »

### 5. Limites et mon rôle (20 s)
> « Le benchmark reste petit, et les questions qui portent sur beaucoup de documents, comme "combien de consignes ATR 72 ?", sont hors de portée d'un RAG qui lit 5 passages : la suite serait d'extraire les consignes dans une table pour y répondre en SQL. J'ai écrit le code avec un assistant de code IA ; mon travail a été la conception, les choix techniques à partir des mesures, le protocole d'évaluation et l'analyse des résultats. »

---

## Pour le CV (en anglais)

- **AeroDoc — Retrieval-augmented assistant for aircraft maintenance documentation.** Designed and evaluated a RAG system over 225 FAA airworthiness directives and the FAA maintenance handbook, built with an AI coding assistant (Python, PostgreSQL/pgvector, BM25, cross-encoder reranking, Gemini, FastAPI, Streamlit, Docker).
- Built a 73-question benchmark (dev/test split, 22 % unanswerable, near-miss and multi-document traps): **82 % correct cited answers on the held-out test set (95 % CI 62–93 %) with no fabricated answer, vs 27 % correct and 50 % fabrication for the LLM alone**, and 50 % correct for a dense-only RAG.
- Improved retrieval through error analysis: hybrid dense + BM25 search with reciprocal rank fusion, reranking and an AD-number metadata match (relevant passage in top 5: 73 % → 91 %).

---

## Les questions probables, et l'essentiel de la réponse

| Question | L'essentiel (détails dans `CHOIX.md`) |
|---|---|
| **Explique un RAG, de la question à la réponse.** | Recherche des passages (sens + mots-clés, fusion, reranker) → 5 passages numérotés → prompt « réponds seulement avec ça, cite, sinon abstiens-toi » → réponse citée. Avantages : traçable, à jour sans ré-entraîner, abstention possible. |
| **Pourquoi une recherche hybride ?** | La recherche vectorielle comprend le sens mais confond « AD 2026-18-03 » et « AD 2026-09-03 » (1 question sur 4 par numéro retrouvée). BM25 trouve les identifiants exacts. Les deux se complètent ; fusion par RRF, qui n'utilise que les rangs. |
| **Comment as-tu choisi la taille des passages ?** | ~250 mots : sous la limite de 512 tokens du modèle d'embedding avec l'en-tête, assez précis pour citer, assez long pour le contexte ; 40 mots de chevauchement. Valeur standard, non optimisée : c'est une limite assumée. |
| **Qu'est-ce qu'un reranker, combien coûte-t-il ?** | Un modèle qui lit la question et le passage ensemble (cross-encoder), plus précis que la comparaison de vecteurs calculés séparément. ~1 s pour 20 passages sur CPU, donc appliqué seulement aux 20 meilleurs candidats. Un plus gros reranker gagnait 3 points de MRR mais coûtait 5 fois plus de temps. |
| **Comment mesures-tu la fidélité aux sources ?** | Précision des citations (98 % vers la bonne source), bon passage dans le contexte (91 %), et relecture manuelle des échecs. Limite : pas de juge automatique de fidélité phrase par phrase ; ce serait la prochaine étape, calibré sur des notes humaines. |
| **Pourquoi un jeu dev et un jeu test ?** | Pour ne pas régler le système (ou le test) sur les questions qui servent à le juger. J'ai analysé et corrigé sur dev ; test n'a servi qu'une fois. Même logique que train/test en apprentissage automatique. |
| **Comment limites-tu les hallucinations ?** | Réponse uniquement à partir des passages, citation obligatoire, marqueur d'abstention, température 0. Mesuré : 0 réponse inventée sur les questions sans réponse, contre 50 % pour le LLM seul. On mesure aussi les abstentions à tort (14 %), pour ne pas récompenser un assistant qui dirait toujours « je ne sais pas ». |
| **Limites, et que ferais-tu ensuite ?** | Benchmark petit ; questions de comptage et de liste hors de portée ; consignes qui renvoient à l'EASA ; modèles génériques. Ensuite : extraction structurée des consignes (SQL), fine-tuning du reranker sur l'aéronautique, benchmark plus grand avec de vrais techniciens, agent capable d'enchaîner les recherches. |
| **Quelle part du travail est la tienne si le code a été généré par une IA ?** | Conception du système et des priorités, choix techniques à partir des mesures (modèle d'embedding, reranker, filtre par numéro), protocole d'évaluation, validation des questions, analyse des résultats. Je sais expliquer et justifier chaque brique ; la trace en est `CHOIX.md`. Je ne prétends pas avoir écrit le code. |
| **Pourquoi pas de fine-tuning ?** | Les consignes changent chaque semaine et doivent être citées : le RAG s'adapte en ajoutant un document, le fine-tuning demanderait de ré-entraîner, et ne cite pas. Le fine-tuning aurait du sens pour le reranker. |
| **Pourquoi pgvector plutôt qu'une base vectorielle dédiée ?** | Une seule base pour le texte, les vecteurs et les métadonnées, avec filtres SQL ; à 5 000 passages, une base dédiée n'apporterait que de la complexité. |
