<div align="center">

# AGENT-BE

### Quantitative FinTech Intelligence Pipeline for NSE/BSE Markets

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Ollama-Offline_LLM-black?style=flat-square"/>
  <img src="https://img.shields.io/badge/Railway-Deployed-0B0D0E?style=flat-square&logo=railway&logoColor=white"/>
  <img src="https://img.shields.io/badge/Market-NSE%20%2F%20BSE-FF6600?style=flat-square"/>
</p>

*From raw tickers to institutional-grade narrative — fully automated, zero-touch.*

</div>

---

## What This Is

Most traders drown in data. AGENT-BE inverts that problem: it ingests raw NSE/BSE intraday feeds, runs them through a quantitative signal engine, and delivers a plain-English market briefing — structured like a Senior Market Strategist wrote it — directly to each subscriber's inbox.

The pipeline runs on a cron schedule aligned to Indian market hours. Nothing needs to be triggered manually. By the time the market closes, the report is already in your inbox.

---

## Architecture

The system is organized into three layers, each running as an independent Docker container:

```
╔══════════════════════════════════════════════════════════════════════════╗
║  LAYER 1 · INGESTION                                                     ║
║                                                                          ║
║   [Google Finance] ──┐                    ┌── [User DB]                  ║
║   [Yahoo Finance]  ──┼──▶ [FastAPI Layer] ◀┘  subscriptions             ║
║                       │    stock-api.saifmk.online                       ║
║                       ▼                                                  ║
║              [DATA_COLLECTION_DOCKER]                                    ║
║               fetchingStock.py                                           ║
║               · Polls every 5 minutes (09:20–15:45 IST)                 ║
║               · ThreadPoolExecutor — all stocks run concurrently        ║
║               · Writes: /csvFiles/{user_email}/{TICKER}.csv             ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  LAYER 2 · INTELLIGENCE                              (triggered 15:46)  ║
║                                                                          ║
║              [ANALYSIS_GMAIL_DOCKER]                                     ║
║                                                                          ║
║   CSV → Pandas ──▶ [Statistical Engine] ──▶ [Weekly Aggregator]         ║
║                     · VWAP Hold/Rejection   · Volatility expansion       ║
║                     · RVOL & Volume Intensity · Squeeze detection        ║
║                     · 25+ signals per stock · Flow conviction score     ║
║                                │                                         ║
║                                ▼                                         ║
║                       [LLM Synthesis]                                    ║
║                        Gemini 2.5-flash  ←  primary                     ║
║                        Ollama            ←  offline fallback             ║
║                        "Senior Market Strategist" system prompt         ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  LAYER 3 · DELIVERY                                                      ║
║                                                                          ║
║   ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  ║
║   │  Gmail SMTP     │  │  JSON Archive    │  │  REST API (public)   │  ║
║   │  HTML report    │  │  Weekly reports  │  │  FastAPI · port 1555 │  ║
║   │  per subscriber │  │  per-user files  │  │  Cloudflare tunnel   │  ║
║   └─────────────────┘  └──────────────────┘  └──────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════════╝

  Cron  09:20 IST  ·  fetcher starts
        15:45 IST  ·  fetcher stops
        15:46 IST  ·  analyzer + delivery starts
        16:00 IST  ·  analyzer stops
```

---

## Services

| Container | Role | Lifecycle |
|---|---|---|
| `DATA_COLLECTION_DOCKER` | Polls the stock API and writes intraday CSVs per user | Cron-managed |
| `ANALYSIS_GMAIL_DOCKER` | Runs the stat engine, calls Gemini, sends Gmail reports | Cron-managed |
| `API_ENDPOINTS_DOCKER` | Serves the public FastAPI layer on port 1555 | Always-on |
| `ollama` | Local LLM inference (offline fallback) | Always-on |

---

## Core Signals

The statistical engine computes these indicators for every stock, every session:

**Momentum**

| Signal | What it measures |
|---|---|
| `intraday_pct_change` | % move from open to current price |
| `overnight_gap_pct` | Gap between previous close and today's open |
| `day_range_position` | Where price sits within today's high–low range (0–100%) |

**Conviction**

| Signal | What it measures |
|---|---|
| `RVOL` | Current volume vs average daily volume |
| `volume_intensity` | Volume pace-adjusted for time elapsed in session |
| `VWAP_Hold / VWAP_Rejection` | Whether price is holding above or below session VWAP |

**Behaviour**

| Signal | What it measures |
|---|---|
| `Dip_Absorption` | Price dipped below open but recovered above median — institutional buying signal |
| `Buyer_Control / Seller_Control` | Closing sentiment relative to session median and open |
| `Trend_Day_Up / Down` | Clean directional session with close near the range extreme |
| `Consolidation_Squeeze_Alert` | Weekly range narrower than 60% of mean — breakout precursor |

**Valuation overlay**

| Signal | What it measures |
|---|---|
| `target_upside_pct` | Distance to analyst 1-year price target |
| `price_to_52w_high_pct` | How far below the yearly high the stock currently sits |
| `valuation_health` | P/E below 20 = Undervalued, else Premium |

---

## Tech Stack

**Backend**

| Tool | Purpose |
|---|---|
| FastAPI + Uvicorn | REST API layer and stock data endpoints |
| Pandas / NumPy | Intraday statistical computation |
| Requests | HTTP polling with retry and exponential backoff |
| ThreadPoolExecutor | Concurrent multi-stock data collection |
| Linux Cron | Market-hour service orchestration |

**Intelligence**

| Tool | Purpose |
|---|---|
| Google Gemini 2.5-flash | Primary LLM — cloud inference |
| Ollama | Fallback LLM — local / offline inference |
| google-genai SDK | Rate-limited client with 3-model fallback chain |

**Infrastructure**

| Tool | Purpose |
|---|---|
| Docker + docker-compose | Service isolation and orchestration |
| Railway | Cloud container deployment |
| Cloudflare Tunnel | Zero-config HTTPS exposure for the public API |
| Gmail SMTP | Automated HTML report delivery per subscriber |

---

## Project Layout

```
AGENT-BE/
├── docker-compose.yml
├── railway.json
│
└── Stock_Automation/
    │
    ├── DATA_COLLECTION_DOCKER/           ← Service 1: Ingestion
    │   ├── run.py                        entry point
    │   ├── Stock_price_fetching/
    │   │   └── fetchingStock.py          core 5-min polling loop
    │   └── Data_fetching_from_db/
    │       └── fetching_tokenization.py  user → stock resolver
    │
    ├── ANALYSIS_GMAIL_DOCKER/            ← Service 2: Intelligence + Delivery
    │   ├── runDailyAnalysis.py           entry point
    │   ├── runGmail.py                   delivery entry point
    │   ├── Stock_analysis_modules/
    │   │   └── collectedDataAnalysis.py  pandas stat engine (25+ signals)
    │   ├── Daily_stock_analysis/
    │   │   └── AnalysisModules/
    │   │       └── dailyStockAnalysis.py intraday snapshot builder
    │   ├── Weekly_stocks_analysis/
    │   │   └── AnalysisModules/
    │   │       └── weeklyStockAnalysis.py  7-day aggregation + Gemini call
    │   └── subscriptions/
    │       └── mail_parser/
    │           └── gmailSubscription.py  SMTP automation
    │
    └── API_ENDPOINTS_DOCKER/             ← Service 3: Public REST API
        ├── main.py                       FastAPI app + route registration
        └── stock_endpoints/
            ├── options/
            │   ├── priceFetcher.py       GET /stock/{symbol}
            │   └── searchedStock.py      GET /search/{symbol}
            └── trends/
                ├── gainers.py            GET /gainer
                ├── looser.py             GET /looser
                └── mostActive.py         GET /mostActive
```

---

## API Reference

Base URL: `https://stock-api.saifmk.online` (public) · `http://localhost:1555` (local)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/stock/{symbol}` | Full OHLCV snapshot for an NSE ticker |
| `GET` | `/search/{symbol}` | Search NSE-listed equities by name |
| `GET` | `/gainer` | Top gaining stocks, current session |
| `GET` | `/looser` | Top losing stocks, current session |
| `GET` | `/mostActive` | Highest volume stocks, current session |

**Example request:**
```bash
curl https://stock-api.saifmk.online/stock/RELIANCE
```

**Example response:**
```json
{
  "stockName": "RELIANCE",
  "stockPrice": "2947.35",
  "stockVolume": "4823910",
  "stockAvgVolume": "6120000",
  "stockOpen": "2930.00",
  "stockPreviousClosing": "2921.80",
  "stockDayRangeOpening": "2918.50",
  "stockDayRangeClosing": "2951.00",
  "stock52WeekRangeClosing": "3217.90",
  "stockPERatio": "24.6",
  "stockTargetPrice": "3250.00"
}
```

---

## Weekly Report Output

Every Friday post-market, the pipeline produces a structured JSON file per user. Quantitative weekly metrics plus the Gemini narrative in one document:

```json
{
  "date": "14-03-2025",
  "time": "16:02:11",
  "stocks": [
    {
      "stock": "RELIANCE",
      "report": {
        "net_weekly_return": 3.42,
        "volatility_expansion_ratio": 2.87,
        "volume_conviction_score": 1.63,
        "closing_sentiment_bias": 0.72,
        "liquidity_absorption_rate": 0.60,
        "consolidation_squeeze_alert": "No"
      }
    },
    {
      "stock": "INFY",
      "report": {
        "net_weekly_return": -1.14,
        "volatility_expansion_ratio": 1.38,
        "volume_conviction_score": 0.71,
        "closing_sentiment_bias": 0.34,
        "liquidity_absorption_rate": 0.22,
        "consolidation_squeeze_alert": "Yes"
      }
    }
  ],
  "summary": {
    "RELIANCE": "**Headline:** Institutional accumulation confirmed on expanding range and strong weekly close.\n**Key Takeaway:** Volume conviction above 1.5x signals professional buying interest.\n**Narrative:** Reliance demonstrated clear buyer dominance through the week, with price holding above its mean on 4 of 5 sessions...",
    "INFY": "**Headline:** Consolidation squeeze forming — low-energy week masks a coiled spring setup.\n**Key Takeaway:** Narrowing range and declining volume signal compression, not distribution.\n**Narrative:** Infosys spent the week in a low-conviction holding pattern..."
  }
}
```

The `summary` field is the Gemini output — one narrative per ticker, structured as Headline → Key Takeaway → Narrative, enforced via the system prompt.

---

## Setup & Installation

### Prerequisites

- Docker Engine ≥ 24.x and Docker Compose v2
- Linux host (Ubuntu 22.04+ recommended)
- Google Gemini API key ([Google AI Studio](https://aistudio.google.com))
- Gmail account with App Password enabled
- Cloudflare account (optional — for public API exposure)

### 1 · Clone the repository

```bash
git clone https://github.com/your-org/AGENT-BE.git
cd AGENT-BE
```

### 2 · Configure environment variables

```bash
cp Stock_Automation/API_ENDPOINTS_DOCKER/.env.example .env
```

Open `.env` and fill in your credentials:

```env
BASE_DIR=/app
DOCKER_PATH=/app/Data_collection_automation/Analysed_Files_data

GEMINI_API_KEY=your_gemini_api_key
GMAIL_SENDER=you@gmail.com
GMAIL_APP_PASSWORD=your_app_password
DB_CONNECTION_STRING=your_db_connection_string
```

> `.env` is excluded from version control via `.gitignore`. Never commit it.

### 3 · Set up the data volume

Update the host path in `docker-compose.yml`:

```yaml
volumes:
  - /your/local/data/path:/app/Data_collection_automation/Analysed_Files_data
```

Then create the directory:

```bash
mkdir -p /your/local/data/path
```

### 4 · Build and launch

```bash
docker compose up -d --build
docker compose ps
```

`fast-api` and `ollama` start immediately. `fetcher` and `daily-analysis` are managed by cron.

### 5 · Verify

```bash
curl http://localhost:1555/
# → {"STATUS": "Api is running"}

curl http://localhost:1555/stock/TCS
```

### 6 · Cloudflare Tunnel (optional)

```bash
cloudflared tunnel login
cloudflared tunnel create agent-be
# Add tunnel config to ~/.cloudflare/config.yml
cloudflared tunnel run agent-be
```

---

## Cron Schedule

Add to `crontab -e`. All times IST, weekdays only.

```cron
# Start data collection at market open
20 9 * * 1-5   cd /path/to/AGENT-BE && docker compose up -d fetcher >> /data/fetcher-cron.log 2>&1

# Stop collection at close
45 15 * * 1-5  docker compose stop fetcher >> /data/fetcher-stop.log 2>&1

# Trigger analysis + delivery
46 15 * * 1-5  cd /path/to/AGENT-BE && docker compose up -d daily-analysis >> /data/analyzer-cron.log 2>&1

# Stop analysis container
0 16 * * 1-5   docker compose stop daily-analysis >> /data/analyzer-stop.log 2>&1
```

---

## Environment Variables

| Variable | Used by | Purpose |
|---|---|---|
| `DOCKER_PATH` | All | Root path for the shared data volume inside containers |
| `BASE_DIR` | All | Working directory base |
| `GEMINI_API_KEY` | Analysis | Google AI Studio authentication key |
| `GMAIL_APP_PASSWORD` | Analysis | Gmail App Password for SMTP delivery |
| `DB_CONNECTION_STRING` | Collection, Analysis | Database connection for user subscriptions |

---

## License

Proprietary. Unauthorized distribution or commercial use without explicit permission is prohibited.