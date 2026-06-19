# Healthcare Literature Review Analytics

Dashboard and chart generator for the literature review dataset (`LIT REV.xlsx`).

## Setup

```bash
pip install -r requirements.txt
python make_graphs.py
```

## React dashboard (local)

```bash
cd dashboard
npm install
npm run dev
```

Open the URL shown in the terminal (usually http://localhost:5173).

**Login passkey:** `100120`

---

## Deploy with Google Firebase (recommended)

**Flow:** `git push` → GitHub → auto build → **Firebase Hosting** → live site

### One-time setup

#### 1. Create Firebase project
1. Go to [Firebase Console](https://console.firebase.google.com)
2. **Create a project** (e.g. `healthcare-research`)
3. Open **Build → Hosting → Get started**

#### 2. Set your project ID
Edit `.firebaserc` and replace `YOUR_FIREBASE_PROJECT_ID` with your Firebase project ID.

#### 3. GitHub secrets
In GitHub: **healthcare_research → Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|-------------|--------|
| `FIREBASE_PROJECT_ID` | Your Firebase project ID |
| `FIREBASE_SERVICE_ACCOUNT` | Full JSON from Firebase (see below) |

**Get service account JSON:**
1. Firebase Console → ⚙️ **Project settings**
2. **Service accounts** tab
3. **Generate new private key** → download JSON
4. Copy **entire JSON file contents** into the `FIREBASE_SERVICE_ACCOUNT` secret

#### 4. Push to deploy
```bash
git add .
git commit -m "Your message"
git push
```

GitHub Actions will:
1. Regenerate charts from `LIT REV.xlsx`
2. Build the React app
3. Deploy to Firebase Hosting

Your site will be at: `https://YOUR_PROJECT_ID.web.app`

---

## Deploy to Vercel (alternative)

1. Import repo on [Vercel](https://vercel.com)
2. Set **Root Directory** to `dashboard`
3. Build: `npm run build` · Output: `dist`

---

## Project structure

- `LIT REV.xlsx` — source data
- `make_graphs.py` — generates charts + React data
- `graphs/` — PNG/JPG chart exports
- `dashboard/` — React (Vite) web app
- `firebase.json` — Firebase Hosting config
- `.github/workflows/firebase-deploy.yml` — auto deploy on push
