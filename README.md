# 📰 AI News Hub — बहुभाषी समाचार

> A fully automated, AI-powered, multilingual news blog built entirely on **free-tier services**. New articles appear dynamically every 4 hours — no rebuilds needed.

![Tech Stack](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas_M0-47A248?logo=mongodb)
![Gemini](https://img.shields.io/badge/Gemini_1.5_Flash-Free_Tier-4285F4?logo=google)
![GitHub Actions](https://img.shields.io/badge/Automation-GitHub_Actions-2088FF?logo=githubactions)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌐 **Trilingual** | Every article in Hindi, English & Marathi |
| 🤖 **AI-Written** | Gemini 1.5 Flash rewrites news into SEO-friendly 200-word articles |
| ⏱️ **Auto-updated** | GitHub Actions runs the pipeline every 4 hours |
| 🏏 **5 Categories** | Politics · Sports · Entertainment · Local · Jobs |
| 🔍 **Multi-source** | Google News RSS + DuckDuckGo search |
| 🌙 **Premium Dark UI** | Glassmorphism, animations, responsive grid |
| 💰 **100% Free** | Vercel + Render + MongoDB Atlas M0 + Gemini free tier |

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  GitHub      │────▶│  FastAPI      │────▶│  MongoDB    │
│  Actions     │POST │  (Render)    │     │  Atlas M0   │
│  (cron 4hr)  │     │              │     │             │
└─────────────┘     └──────┬───────┘     └─────────────┘
       │                   │ GET
       │            ┌──────┴───────┐
       │            │  React App   │
       │            │  (Vercel)    │
       │            └──────────────┘
       │
┌──────┴──────┐
│ Gemini 1.5  │
│ Flash API   │
└─────────────┘
```

---

## 📁 Project Structure

```
ai-news-hub/
├── frontend/                 # React + Tailwind CSS app
│   ├── public/index.html
│   ├── src/
│   │   ├── App.jsx           # Main app with state & API calls
│   │   ├── index.js          # React entry point
│   │   ├── index.css         # Tailwind + custom styles
│   │   └── components/
│   │       ├── Navbar.jsx    # Site header
│   │       ├── FilterBar.jsx # Category & language filters
│   │       └── NewsCard.jsx  # Article card component
│   ├── package.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── backend/
│   ├── main.py               # FastAPI app
│   ├── requirements.txt
│   └── .env.example
├── scripts/
│   ├── main.py               # News automation pipeline
│   └── requirements.txt
├── .github/workflows/
│   ├── news_pipeline.yml     # Cron: every 4 hours
│   └── keep_alive.yml        # Cron: every 10 minutes
└── README.md
```

---

## 🚀 Deployment Guide

### Prerequisites (all free)

- [MongoDB Atlas](https://www.mongodb.com/atlas) account (M0 free tier)
- [Render](https://render.com/) account (free web service)
- [Vercel](https://vercel.com/) account (free tier)
- [Google AI Studio](https://aistudio.google.com/) API key (Gemini 1.5 Flash free tier)
- [GitHub](https://github.com/) account (for Actions)

---

### Step 1: MongoDB Atlas Setup

1. Create a free M0 cluster at [MongoDB Atlas](https://www.mongodb.com/atlas).
2. Create a database user with read/write access.
3. Whitelist `0.0.0.0/0` in Network Access (required for Render + GitHub Actions).
4. Copy the connection string:
   ```
   mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

---

### Step 2: Deploy Backend to Render

1. Push this repo to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) → **New Web Service**.
3. Connect your GitHub repo.
4. Configure:
   - **Name:** `ai-news-hub-api`
   - **Root Directory:** `backend`
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `MONGO_URI` = your MongoDB connection string
6. Deploy. Note the URL (e.g., `https://ai-news-hub-api.onrender.com`).

---

### Step 3: Deploy Frontend to Vercel

1. Go to [Vercel](https://vercel.com/) → **Import Project**.
2. Select your repo, set **Root Directory** to `frontend`.
3. Framework preset: **Create React App**.
4. Add environment variable:
   - `REACT_APP_API_BASE` = your Render URL (e.g., `https://ai-news-hub-api.onrender.com`)
5. Deploy.

---

### Step 4: Configure GitHub Actions

1. In your GitHub repo, go to **Settings → Secrets and variables → Actions**.
2. Add these repository secrets:
   - `GEMINI_API_KEY` — from [Google AI Studio](https://aistudio.google.com/apikey)
   - `API_URL` — your Render backend URL
3. Go to **Actions** tab and enable the workflows.
4. Optionally trigger **Auto News Pipeline** manually to test.

---

## 🧪 Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MONGO_URI
python main.py
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
# Create .env with: REACT_APP_API_BASE=http://localhost:8000
npm start
# App runs at http://localhost:3000
```

### Automation Script

```bash
cd scripts
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"
export API_URL="http://localhost:8000"
python main.py
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info |
| `GET` | `/ping` | Health check |
| `GET` | `/articles?category=sports&lang=hi&limit=20` | Fetch articles |
| `GET` | `/articles/{id}` | Get single article |
| `POST` | `/articles` | Create article (JSON body) |
| `DELETE` | `/articles/{id}` | Delete article |

### Article JSON Schema

```json
{
  "id": "a1b2c3d4",
  "category": "politics",
  "published": "2024-01-15T10:30:00Z",
  "content": {
    "hi": { "title": "हिंदी शीर्षक", "body": "हिंदी में लेख..." },
    "en": { "title": "English Title", "body": "Article in English..." },
    "mr": { "title": "मराठी शीर्षक", "body": "मराठीत लेख..." }
  }
}
```

---

## 💡 Environment Variables Summary

| Variable | Where | Value |
|----------|-------|-------|
| `MONGO_URI` | Render (backend) | MongoDB Atlas connection string |
| `REACT_APP_API_BASE` | Vercel (frontend) | Render API URL |
| `GEMINI_API_KEY` | GitHub Secrets | Google AI Studio API key |
| `API_URL` | GitHub Secrets | Render API URL |

---

## 📄 License

MIT — Free to use, modify, and deploy.
