# Healthcare Literature Review Analytics

Dashboard and chart generator for the literature review dataset (`LIT REV.xlsx`).

## Setup

```bash
pip install -r requirements.txt
python make_graphs.py
```

## React dashboard

```bash
cd dashboard
npm install
npm run dev
```

Open the URL shown in the terminal (usually http://localhost:5173).

## Deploy to Vercel

1. Push this repo to GitHub.
2. Import the repo in [Vercel](https://vercel.com).
3. Set **Root Directory** to `dashboard`.
4. Build command: `npm run build`
5. Output directory: `dist`
6. Before deploy, run `python make_graphs.py` locally and commit updated `dashboard/public/` files so charts and data are included.

## Project structure

- `LIT REV.xlsx` — source data
- `make_graphs.py` — generates charts + React data
- `graphs/` — PNG/JPG chart exports
- `dashboard/` — React (Vite) web app
- `index.html` — standalone HTML dashboard (no build step)
