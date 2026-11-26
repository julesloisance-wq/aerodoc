# Faire une démo d'AeroDoc en direct

Ce guide permet de lancer l'interface et de faire une démo de 3 à 5 minutes en entretien, en présentiel ou en partage d'écran. Le pitch et les réponses aux questions sont dans [`PRESENTATION.md`](PRESENTATION.md) ; ce document ne couvre que la démo.

**Règle d'or : on ne fait jamais le premier démarrage pendant l'entretien.** Le premier lancement télécharge les documents et construit l'index (environ 10 minutes). Il se fait la veille ; le jour J, le démarrage prend quelques secondes.

---

## 1. La veille : installer une fois (≈ 20 min)

À faire une seule fois sur l'ordinateur de la démo.

1. **Installer Docker Desktop** ([docker.com](https://www.docker.com/products/docker-desktop/)) et l'ouvrir. *Docker* fait tourner des « conteneurs » : de petites machines isolées qui contiennent déjà tout ce qu'il faut (Python, la base de données, les modèles). Pas besoin d'installer Python soi-même.
2. **Récupérer une clé API Gemini** sur [aistudio.google.com](https://aistudio.google.com) → *Get API key*. Une *clé API* est un mot de passe qui autorise le programme à utiliser le LLM de Google ; l'offre gratuite suffit.
3. **Télécharger le projet et y mettre la clé** (dans un terminal) :

   ```bash
   git clone https://github.com/julesloisance-wq/aerodoc.git
   ```

   ```bash
   cd aerodoc
   ```

   ```bash
   cp .env.example .env
   ```

   Ouvrir le fichier `.env` avec un éditeur de texte et coller la clé après `GEMINI_API_KEY=` (sans espace ni guillemets). Ce fichier reste sur l'ordinateur : il est exclu de Git.
4. **Premier démarrage** :

   ```bash
   docker compose up --build
   ```

   Les journaux défilent. Attendre la ligne `First start: downloading the corpus and building the index`, puis, une dizaine de minutes plus tard, `Uvicorn running on http://0.0.0.0:8000`. L'index est alors stocké dans un volume Docker (un disque virtuel qui survit à l'arrêt) : il ne sera plus reconstruit.
5. **Vérifier** : ouvrir <http://localhost:8501>. La barre de gauche doit afficher environ **225** consignes et **5 300** passages indexés. Poser une question d'exemple : la réponse arrive en 2 à 3 secondes.

   Le nombre exact dépend du jour du téléchargement : `make data` prend les consignes publiées depuis 2022, donc celles parues depuis la rédaction du README s'ajoutent (test du 26/11/2026 : 227 consignes, 5 324 passages). Si on vous le fait remarquer : « le corpus se reconstruit à partir de la source officielle ; les chiffres du benchmark portent sur l'instantané d'origine. »
6. **Répéter la démo une fois en entier** (section 3), chronomètre en main.
7. Arrêter avec `Ctrl+C` dans le terminal (ou `docker compose down`, qui garde l'index).

---

## 2. Le jour J : démarrer (≈ 1 min)

1. Ouvrir Docker Desktop et attendre qu'il indique *Engine running*.
2. Dans le dossier `aerodoc` :

   ```bash
   docker compose up -d
   ```

   `-d` lance tout en arrière-plan et rend la main au terminal.
3. Ouvrir <http://localhost:8501> et vérifier les compteurs dans la barre de gauche. Si elle affiche *API not reachable*, l'API charge encore ses modèles : attendre 20 secondes et recharger la page.
4. **Faire chauffer le système** : poser une première question avant que l'entretien commence. La première réponse peut prendre 30 à 40 secondes (chargement des modèles en mémoire) ; les suivantes, 2 à 3 secondes.
5. Préparer les onglets du navigateur, dans cet ordre :
   - l'interface : <http://localhost:8501> ;
   - la documentation de l'API : <http://localhost:8000/docs> (pour une question technique) ;
   - le dépôt GitHub, ouvert sur le README (plan de secours, avec la vidéo de démo).
6. En partage d'écran : zoomer le navigateur à 125 %, fermer les notifications, partager **la fenêtre du navigateur** plutôt que tout l'écran.

---

## 3. Le scénario de démo (3 à 5 min)

Quatre questions, chacune montre une propriété du système. Les cinq boutons en haut de l'interface remplissent la question en un clic (leur texte est tronqué ; on les reconnaît à leur début) : pas de risque de faute de frappe. Toutes les questions ci-dessous ont été testées dans l'interface le 26/11/2026 et répondent en 2 à 3 secondes. Pour chaque étape : **ce qu'on fait**, **ce qu'on montre**, **ce qu'on dit**.

### Étape 1 — Une réponse citée (bouton « Which airplanes are affected by AD 2026-18-03… »)

- **On montre** : la réponse avec ses numéros **[1]**, **[4]**… ; dessous, *Sources* : ouvrir une source, montrer le texte exact et le lien *Open the original document ↗* vers le Federal Register.
- **On dit** : « Chaque affirmation renvoie au passage d'où elle vient : la consigne, la section, la page. Un technicien peut vérifier en un clic dans le document officiel. »

### Étape 2 — L'assistant dit « je ne sais pas » (bouton « What is the maximum takeoff weight of the Airbus A350-1000? »)

- **On montre** : l'encadré jaune *I don't know based on the available documents*.
- **On dit** : « Cette information n'est pas dans les documents. Un LLM seul aurait donné un chiffre de mémoire, peut-être faux. Sur mon benchmark, Gemini seul invente une réponse à la moitié des questions sans réponse ; AeroDoc, jamais. »
- **Variante plus parlante** : taper `What is the unsafe condition addressed by AD 2024-08-03?`. Ce numéro est à un chiffre d'une vraie consigne du corpus (AD 2024-08-02), mais il n'existe pas : le système ne les confond pas, alors qu'un LLM seul décrit volontiers une consigne inventée.

### Étape 3 — Sous le capot (même réponse, déplier *Other passages retrieved… and how they were found*)

- **On montre** : la liste des 5 passages lus par le LLM, avec pour chacun le score du reranker et *found by* : quelle recherche l'a trouvé, et à quel rang. Lors du test, les 3 passages cités (AD 2026-18-03) portaient *found by bm25* seulement, et les 2 passages non cités venaient de la recherche par le sens et parlaient d'**autres** consignes (AD 2026-13-05, AD 2026-04-05).
- **On dit** : « Le système fait deux recherches : une par le sens (*dense*, en comparant des vecteurs) et une par mots-clés (*BM25*). Regardez : les trois passages utiles n'ont été trouvés que par BM25. La recherche par le sens, elle, a ramené d'autres consignes au numéro proche : elle comprend le sujet mais confond les identifiants. C'est exactement ce que mon analyse d'erreurs avait montré, et c'est pour ça que j'ai combiné les deux. Ensuite un reranker relit les 20 meilleurs candidats et en garde 5. »

### Étape 4 — Une question en français (bouton « Quels avions sont concernés par l'AD 2024-08-02 ? »)

- **On montre** : la réponse en français, avec des sources en anglais.
- **On dit** : « Les documents sont en anglais. La question est traduite pour la recherche seulement, et la réponse est écrite dans la langue de la question. »

### Si on a du temps : laisser le recruteur poser sa question

C'est souvent le moment le plus convaincant. Rappeler le périmètre avant : « Le corpus couvre 225 consignes FAA sur A320, A350, Boeing 737 et ATR 72, de 2022 à 2026, plus le manuel de maintenance générale de la FAA. » Si la question est hors du corpus, l'abstention est elle-même une bonne démonstration.

Questions de réserve qui marchent bien :

- `How should a portable fire extinguisher be inspected?` (manuel FAA, réponse en liste) ;
- `What problem was found on the ATR 72 nose landing gear drag brace panels, and which part numbers are affected?` (recherche par sujet, sans numéro) ;
- `What are the detailed inspection steps required by EASA AD 2026-0142?` (abstention : la consigne FAA renvoie à cette consigne européenne, dont le texte n'est pas dans le corpus ; bon exemple de limite expliquée honnêtement).

**À éviter** : les questions de comptage ou de liste (« Combien de consignes ATR 72 ? »). Le système ne lit que 5 passages et répondra mal. Si on la pose, c'est l'occasion de parler des limites : « Pour ça, il faudrait extraire les consignes dans une table et répondre en SQL ; c'est ma prochaine étape. »

---

## 4. Si quelque chose ne marche pas

| Symptôme | Cause probable | Que faire |
|---|---|---|
| *API not reachable* dans la barre de gauche | L'API démarre encore (chargement des modèles) | Attendre 20 s, recharger la page. Sinon : `docker compose logs api --tail 30` |
| *The assistant is not available: … 429* ou *quota* | Limite de l'offre gratuite Gemini atteinte | Attendre une minute. Plan B ci-dessous |
| *… 401*, *403* ou *API key* | Clé absente ou invalide dans `.env` | Vérifier `.env`, puis `docker compose up -d --force-recreate api` |
| Réponse très lente (20 s ou plus) | Première question après le démarrage, ou latence variable de Gemini gratuit | D'où la question de chauffe. Sinon, le dire : « latence de l'offre gratuite ; d'habitude c'est 2 à 3 secondes » |
| *Cannot connect to the Docker daemon* | Docker Desktop n'est pas lancé | L'ouvrir, attendre *Engine running* |
| *port is already allocated* | Un autre programme utilise le port 5432, 8000 ou 8501 | Fermer l'autre programme (souvent une autre base PostgreSQL) |
| L'index se reconstruit (10 min) | Le volume a été supprimé (`docker compose down -v`) | Ne jamais utiliser `-v` avant une démo |

**Plan B, si Gemini ne répond pas** : la recherche fonctionne sans LLM. Dans un terminal :

```bash
docker compose exec api aerodoc search "Which airplanes are affected by AD 2026-18-03?"
```

Elle affiche les passages retrouvés et par quelle recherche (sens, mots-clés). On peut aussi utiliser <http://localhost:8000/docs> → `POST /search` → *Try it out*.

**Plan C, si rien ne marche** : ouvrir le README sur GitHub et lancer la vidéo de 30 secondes, puis montrer [`EXEMPLES.md`](EXEMPLES.md) (vraies réponses générées par le système). Dire calmement ce qui se passe : un incident réseau pendant une démo est banal, savoir le diagnostiquer compte plus.

---

## 5. Aide-mémoire

| Commande | Effet |
|---|---|
| `docker compose up -d` | Tout démarrer en arrière-plan |
| `docker compose ps` | Voir quels services tournent (`db`, `api`, `ui`) |
| `docker compose logs api --tail 30` | Lire les derniers messages de l'API |
| `docker compose down` | Tout arrêter (l'index est gardé) |

| Adresse | Contenu |
|---|---|
| <http://localhost:8501> | L'interface (Streamlit) |
| <http://localhost:8000/docs> | La documentation interactive de l'API (FastAPI) |
| <http://localhost:8000/health> | Vérification rapide : l'API répond-elle ? |

**Ce que fait chaque service**, si on vous le demande : `db` est la base PostgreSQL avec l'extension pgvector, qui stocke les ~5 300 passages et leurs vecteurs ; `api` charge les modèles (embedding, reranker) une fois pour toutes et répond aux questions ; `ui` est l'interface web, qui n'est qu'un client de l'API, comme le serait une application mobile.
