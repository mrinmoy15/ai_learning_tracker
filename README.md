# AI/ML Complete Training Tracker

Personal tracker for AI/ML training progress. Static site with in-browser SQLite storage — no backend or login required.

**Live site:** https://mrinmoy15.github.io/ai_learning_tracker/

## Local development

**Option A — Node (fast iteration):**
```bash
git clone https://github.com/mrinmoy15/ai_learning_tracker.git
cd ai_learning_tracker/frontend
npm install
npm run dev
```

**Option B — Docker (mirrors production):**
```bash
make start   # builds image and runs on http://localhost:3000
make stop    # stop
```

Both serve the same static site on http://localhost:3000.

## Deploying

Push to `main` — GitHub Actions builds the TypeScript and deploys to GitHub Pages automatically.

To trigger manually: GitHub → Actions → "Deploy frontend to GitHub Pages" → Run workflow.

**First-time setup:** Repo Settings → Pages → Source: `gh-pages` branch, `/ (root)`.

## How progress is stored

Checkboxes are tracked in memory until you click **Save Progress**, which writes to a SQLite database stored in your browser's `localStorage`. Nothing leaves your browser.

## Troubleshooting

| Issue | Solution |
|---|---|
| Port 3000 in use | Change the port in `frontend/package.json` dev script |
| Progress lost after clearing browser data | Use **Save Progress** regularly — it's stored in `localStorage` |
| GitHub Pages not updating | Check the Actions tab for workflow errors |
