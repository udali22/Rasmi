# Rasmi 📧

**Écris juste, Écris Formel**

Rasmi est une application web qui transforme vos intentions courtes en emails académiques formels en français. Parfait pour les étudiants qui souhaitent communiquer professionnellement avec leurs professeurs.

![Rasmi Banner](https://img.shields.io/badge/Angular-17-red?style=for-the-badge&logo=angular) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi) ![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)

## ✨ Fonctionnalités

- 📝 **Génération intelligente** : Transforme une intention courte en email académique complet
- 🎯 **Types d'emails** : Demande, Excuse, Relance, Remerciement
- 📊 **Niveaux de formalité** : Faible, Moyen, Élevé
- 🔐 **Authentification** : Interface split-screen avec option "Se connecter avec Google" (Mock)
- �📋 **Copie rapide** : Copiez l'email en un clic
- 📧 **Envoi direct** : Ouvrez votre client mail avec l'email pré-rempli
- 🎨 **Interface premium** : Design Emerald Green & White, mode sombre, et responsive
- 🚀 **Déploiement gratuit** : Prêt pour Render, Railway ou Vercel

## 🏗️ Architecture

```
Rasmi/
├── frontend/              # Angular 17 Application
│   ├── src/
│   │   ├── app/
│   │   │   ├── home/              # Interface principale (Générateur)
│   │   │   │   ├── home.component.ts
│   │   │   │   ├── home.component.html
│   │   │   │   └── home.component.scss
│   │   │   ├── login/             # Interface de connexion
│   │   │   │   ├── login.component.ts
│   │   │   │   ├── login.component.html
│   │   │   │   └── login.component.scss
│   │   │   ├── services/
│   │   │   │   └── email.service.ts
│   │   │   ├── app.component.ts   # Routeur / Switcher
│   │   │   └── app.config.ts
│   │   └── styles.scss
│   ├── Dockerfile
│   └── package.json
├── backend/               # FastAPI Application
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Installation & Lancement

### Prérequis

- **Node.js** 20+ et npm
- **Python** 3.11+
- **Docker** (optionnel, pour déploiement conteneurisé)

### Option 1 : Lancement Local (Développement)

#### Backend

```powershell
# Naviguer vers le dossier backend
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel (Windows)
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur FastAPI
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Le backend sera accessible sur `http://localhost:8000`

#### Frontend

```powershell
# Naviguer vers le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement Angular
npm start
```

Le frontend sera accessible sur `http://localhost:4200`

### Option 2 : Docker Compose (Recommandé)

```powershell
# Depuis la racine du projet
docker-compose up --build
```

- Frontend : `http://localhost:4200`
- Backend : `http://localhost:8000`
- API Docs : `http://localhost:8000/docs`

## 📖 Utilisation

1. **Entrez votre intention** : Décrivez simplement ce que vous voulez dire
   - Exemple : "Je voudrais un rendez-vous pour discuter de mon projet"

2. **Sélectionnez le type d'email** :
   - 📝 Demande
   - 🙏 Excuse
   - 🔔 Relance
   - 💐 Remerciement

3. **Choisissez le niveau de formalité** :
   - 😊 Faible
   - 🙂 Moyen
   - 🎩 Élevé

4. **Générez l'email** : Cliquez sur "Générer l'email"

5. **Utilisez le résultat** :
   - 📋 Copiez l'email
   - 📧 Envoyez via votre client mail

## 🔧 Configuration

### Variables d'environnement (Backend)

Créez un fichier `.env` dans le dossier `backend/` :

```env
# Utiliser Ollama pour la génération LLM (optionnel)
USE_OLLAMA=false

# Si USE_OLLAMA=true, assurez-vous qu'Ollama est installé et en cours d'exécution
# Installation Ollama : https://ollama.ai/
# Commande : ollama run mistral
```

### Intégration LLM Avancée (Optionnel)

Pour une génération d'emails encore plus intelligente avec Ollama :

1. **Installer Ollama** : [https://ollama.ai/](https://ollama.ai/)

2. **Télécharger Mistral** :
   ```bash
   ollama pull mistral
   ```

3. **Activer dans le backend** :
   ```env
   USE_OLLAMA=true
   ```

4. **Redémarrer le backend**

## 🌐 Déploiement Gratuit

### Déploiement sur Render

#### Backend (API)

1. Créez un compte sur [Render](https://render.com)
2. Créez un nouveau **Web Service**
3. Connectez votre repository GitHub
4. Configuration :
   - **Root Directory** : `backend`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment** : Python 3.11

#### Frontend (Static Site)

1. Créez un nouveau **Static Site**
2. Configuration :
   - **Root Directory** : `frontend`
   - **Build Command** : `npm install && npm run build`
   - **Publish Directory** : `dist/frontend/browser`

3. **Variables d'environnement** :
   - Mettez à jour l'URL de l'API dans `email.service.ts` avec l'URL de votre backend Render

### Déploiement sur Railway

1. Créez un compte sur [Railway](https://railway.app)
2. Créez un nouveau projet
3. Déployez depuis GitHub
4. Railway détectera automatiquement les Dockerfiles

### Déploiement sur Vercel (Frontend uniquement)

```powershell
# Installer Vercel CLI
npm install -g vercel

# Depuis le dossier frontend
cd frontend
vercel
```

Pour le backend, utilisez Render ou Railway.

## 🧪 Tests

### Tester le Backend

```powershell
cd backend

# Lancer le serveur
uvicorn main:app --reload

# Dans un autre terminal, tester l'endpoint
curl -X POST "http://localhost:8000/generate-email" \
  -H "Content-Type: application/json" \
  -d '{
    "intention": "Je voudrais un rendez-vous",
    "type_email": "demande",
    "niveau_formalite": "moyen"
  }'
```

### Documentation API Interactive

Accédez à `http://localhost:8000/docs` pour tester l'API via Swagger UI.

## 📚 API Reference

### POST `/generate-email`

Génère un email académique formel.

**Request Body:**
```json
{
  "intention": "string (min 5 caractères)",
  "type_email": "demande" | "excuse" | "relance" | "remerciement",
  "niveau_formalite": "faible" | "moyen" | "élevé"
}
```

**Response:**
```json
{
  "objet": "string",
  "corps": "string"
}
```

## 🎨 Personnalisation

### Modifier les couleurs (Frontend)

Les styles sont maintenant modulaires. 

Pour l'interface principale, éditez `frontend/src/app/home/home.component.scss` :

```scss
:host {
    --primary: #059669;       /* Emerald 600 */
    --primary-hover: #047857; /* Emerald 700 */
    /* ... */
}
```

Pour la page de connexion, éditez `frontend/src/app/login/login.component.scss`.

### Ajouter des types d'emails

1. Modifiez `backend/main.py` pour ajouter la logique
2. Mettez à jour `frontend/src/app/services/email.service.ts`
3. Ajoutez l'option dans `app.component.html`

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **Angular Team** pour le framework frontend
- **FastAPI** pour le framework backend
- **Ollama** pour l'intégration LLM locale

## 📞 Support

Pour toute question ou problème :

- Ouvrez une **Issue** sur GitHub
- Contactez-nous par email

---

**Fait avec ❤️ pour les étudiants**

*Rasmi - Transformez vos intentions en emails professionnels*
