# Stock Automation – Backend Module

## Overview

The **Stock_Automation** module is a backend-focused Python package designed to automate stock-related workflows such as data collection, analysis, and API exposure. The structure follows a **Dockerized, service-oriented design**, where each major responsibility (data collection, analysis, APIs) is isolated into its own container-ready module.

This folder acts as a **self-contained backend system** that can be plugged into a larger agent or automation platform.

---

## High-Level Architecture

```
Stock_Automation/
│
├── DATA_COLLECTION_DOCKER/
│   ├── Data_fetching_from_db/          # Firebase data retrieval
│   ├── Stock_price_fetching/           # Price collection via APIs
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py                          # Entry point
│
├── ANALYSIS_GMAIL_DOCKER/
│   ├── Stock_analysis_modules/         # Data analysis & statistics
│   ├── Daily_stock_analysis/           # Daily reports & JSON conversion
│   ├── Backend_to_user_sender/         # Email & message delivery
│   ├── Csv_path_cleaner/               # Data cleanup utilities
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── runDailyAnalysis.py
│   ├── runGmail.py
│   └── runMessage.py
│
├── API_ENDPOINTS_DOCKER/
│   ├── stock_endpoints/
│   │   ├── options/                    # Stock search & pricing
│   │   └── trends/                     # Market trends (gainers, losers, active)
│   ├── main.py                         # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
│
├── environment/                        # Environment configuration
├── __init__.py
├── requirements.txt
├── README.md
└── doc.txt
```

Each major folder is designed to be **Dockerized independently**, making the system scalable and modular.

---

## Folder & File Breakdown

### 📁 DATA_COLLECTION_DOCKER/

**Purpose:**
Responsible for **collecting raw stock data** from external sources and databases.

**Key Responsibilities:**
- Fetch live stock prices from financial APIs
- Retrieve user-subscribed stocks from Firebase
- Normalize and store raw market data in CSV format
- Match user-friendly stock names to ticker symbols using fuzzy logic

**Key Components:**
- `Data_fetching_from_db/` – Queries Firebase for user subscriptions and stock lists
- `Stock_price_fetching/` – Fetches prices via API and writes to CSV files
- `run.py` – Orchestrates the data collection pipeline

**Data Flow:**
1. Connects to Firebase to get subscribed users and their stocks
2. Calls stock price API endpoints
3. Writes price data to user-organized CSV files
4. Feeds data to analysis services

---

### 📁 ANALYSIS_GMAIL_DOCKER/

**Purpose:**
Responsible for **processing, analyzing stock data, and delivering insights** to users via email and other channels.

**Key Responsibilities:**
- Statistical analysis of stock prices (mean, median, std, OHLC)
- Daily report generation in JSON and HTML formats
- AI-powered stock interpretation and summaries
- Email delivery of analysis reports
- Data cleanup to prevent storage buildup

**Key Components:**
- `Stock_analysis_modules/` – Pandas-based statistical analysis
- `Daily_stock_analysis/` – Daily report generation and JSON conversion
- `Backend_to_user_sender/` – Email composition and delivery
- `Csv_path_cleaner/` – Cleanup of processed CSV files

**Data Flow:**
1. Reads CSV files from `DATA_COLLECTION_DOCKER`
2. Performs statistical analysis using Pandas
3. Generates daily reports in JSON format
4. Formats HTML emails with analysis insights
5. Sends emails to subscribed users
6. Cleans up processed files

---

### 📁 API_ENDPOINTS_DOCKER/

**Purpose:**
Serves as the **public API layer** for the stock automation system.

**Key Responsibilities:**
- Expose REST endpoints for stock queries
- Provide trending stock data (gainers, losers, most active)
- Allow real-time stock price lookups
- Enable fuzzy search for stock names

**Key Endpoints:**
- `GET /stock/{symbol}` – Fetch price data for a specific stock
- `GET /search/{symbol}` – Search stocks by name
- `GET /gainer` – Get top gaining stocks
- `GET /looser` – Get top losing stocks
- `GET /mostActive` – Get most active stocks

**Framework:** FastAPI with CORS support

**Data Flow:**
1. Receives requests from frontend or external services
2. Scrapes or queries stock data
3. Uses fuzzy matching for stock name resolution
4. Returns JSON responses

---

## System Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    External Sources                         │
│              (Firebase, Stock APIs, Web Scraping)           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   DATA_COLLECTION_DOCKER       │
        │  • Fetch user subscriptions    │
        │  • Collect stock prices        │
        │  • Store in CSV by user/stock  │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │  ANALYSIS_GMAIL_DOCKER         │
        │  • Statistical analysis        │
        │  • Generate daily reports      │
        │  • Create HTML emails          │
        │  • Send to users               │
        │  • Cleanup data                │
        └────────────┬───────────────────┘
                     │
         ┌───────────┴────────────┐
         ▼                        ▼
    ┌─────────────┐      ┌─────────────────────┐
    │  User Email │      │ API_ENDPOINTS_DOCKER│
    │  (Reports)  │      │ (REST API Layer)    │
    └─────────────┘      └─────────────────────┘
```

---

## Key Features

### 1. **Data Collection Pipeline**
- Automated stock price fetching
- Multi-user support with per-user CSV organization
- Fuzzy matching for stock name normalization
- Concurrent data fetching for performance

### 2. **Analysis Engine**
- Comprehensive statistical analysis (mean, median, std, quartiles)
- OHLC (Open-High-Low-Close) calculations
- Price volatility and movement analysis
- Percentage change calculations

### 3. **Email Delivery**
- HTML-formatted stock analysis reports
- Per-user customized summaries
- Scheduled daily/weekly deliveries
- Beautiful, responsive email templates

### 4. **REST API**
- FastAPI-based endpoints
- Real-time stock price lookups
- Market trend data (gainers, losers, most active)
- Fuzzy search for user-friendly stock discovery
- CORS-enabled for frontend integration

### 5. **Data Management**
- Organized CSV file structure per user
- JSON-based daily report archives
- Automatic cleanup of processed files
- Timestamp tracking for data integrity

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Backend Framework | FastAPI |
| Data Processing | Pandas, NumPy |
| Database | Firebase Firestore |
| Containerization | Docker, Docker Compose |
| Web Scraping | BeautifulSoup4, Requests |
| Fuzzy Matching | RapidFuzz |
| Email | yagmail |
| Task Scheduling | Cron (external) |
| AI/LLM | Google Generative AI (Gemini) |

---

## Environment Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Firebase credentials (JSON key file)
- API keys for stock and AI services

### Installation

**1. Clone the repository:**
```bash
git clone <repository-url>
cd Stock_Automation
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Set environment variables:**
```bash
export DOCKER_PATH="/path/to/data/directory"
export GEMINI_API_KEY="your-api-key"
```

**4. Add Firebase credentials:**
Place your Firebase service account JSON file in:
- `DATA_COLLECTION_DOCKER/Data_fetching_from_db/`
- `ANALYSIS_GMAIL_DOCKER/Daily_stock_analysis/`

---

## Running the Services

### Option 1: Docker Compose

```bash
# Start data collection service
docker-compose up -d fetcher

# Start analysis service
docker-compose up -d analyzer

# Start API endpoints
docker-compose up -d api
```

### Option 2: Manual Execution

**Data Collection:**
```bash
cd DATA_COLLECTION_DOCKER
python run.py
```

**Daily Analysis:**
```bash
cd ANALYSIS_GMAIL_DOCKER
python runDailyAnalysis.py
```

**Email Delivery:**
```bash
cd ANALYSIS_GMAIL_DOCKER
python runGmail.py
```

**API Server:**
```bash
cd API_ENDPOINTS_DOCKER
uvicorn main:app --host 0.0.0.0 --port 1555
```

---

## Scheduled Execution

Services are orchestrated using cron jobs:

```bash
# Data collection: 9:20 AM on weekdays
20 9 * * 1-5 /path/to/docker/compose/up fetcher

# Stop collection: 3:45 PM on weekdays
45 15 * * 1-5 /path/to/docker/compose/stop fetcher

# Start analysis: 3:46 PM on weekdays
46 15 * * 1-5 /path/to/docker/compose/up analyzer

# Stop analysis: 4:00 PM on weekdays
0 16 * * 1-5 /path/to/docker/compose/stop analyzer
```

---

## Database Schema (Firebase)

```
Users/
├── {userId}/
│   ├── Email: string
│   ├── Agents/
│   │   └── Finance/
│   │       ├── Stock_Added/
│   │       │   └── {stockId}/
│   │       │       └── stockName: string
│   │       └── Stock_Data/
│   │           └── IntraDay/
│   │               └── Data/
│   │                   └── {timestamp}/
│   │                       ├── last_added: timestamp
│   │                       └── DATA: object
```

---

## File Organization

```
/data/
├── csvFiles/
│   └── {user-email}/
│       └── {stock-name}.csv
└── reports/
    └── {user-email}/
        └── {date}.html (or .json)
```

---

## API Endpoints (Development)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/stock/{symbol}` | Fetch stock price & volume |
| GET | `/search/{symbol}` | Search stock by name |
| GET | `/gainer` | Top gaining stocks |
| GET | `/looser` | Top losing stocks |
| GET | `/mostActive` | Most active stocks |

**Base URL:** `http://localhost:1555` (local) or configured production URL

---

## Best Practices

### Data Modeling
- Store stock data per user to minimize cross-partition queries
- Use hierarchical directory structure for fast file access
- Archive old reports to prevent storage bloat

### Performance
- Use concurrent data fetching with ThreadPoolExecutor
- Implement retry logic for network failures
- Cache ticker symbols and company names locally

### Error Handling
- Log all exceptions with context
- Implement graceful degradation for API failures
- Monitor cron job execution with logging

### Security
- Store sensitive credentials in environment variables
- Never commit API keys or authentication tokens
- Use CORS restrictions in production
- Validate all user inputs before processing

---

## Troubleshooting

### No data in CSVs
- Verify Firebase credentials are valid
- Check if users have subscribed to the Finance agent
- Ensure API rate limits aren't exceeded

### Email not sending
- Verify SMTP credentials and permissions
- Check firewall rules for outgoing email
- Review email logs for authentication errors

### API endpoints failing
- Verify stock symbol format (e.g., `ASHOKLEY` for NSE stocks)
- Check if web scraping selectors have changed
- Review rate limiting from financial websites

### Storage growing too large
- Verify cleanup job is running (`cleaningData()`)
- Check if archive process is functioning
- Monitor disk space usage

---

## Contributing

1. Create a feature branch from `main`
2. Follow PEP 8 code style
3. Add docstrings to new functions
4. Test locally before submitting
5. Update this README for significant changes

---

## Architecture Notes

### Design Philosophy
- **Modularity:** Each service is independent and Dockerized
- **Scalability:** Services can be deployed and scaled separately
- **Maintainability:** Clear separation of concerns
- **Extensibility:** Easy to add new data sources or analysis methods

### Technology Decisions
- **Firebase:** Provides real-time user management and flexibility
- **FastAPI:** High-performance, easy to deploy, great for APIs
- **Pandas:** Industry-standard for data analysis
- **Docker:** Ensures consistency across environments
- **Cron:** Simple, reliable scheduling for batch jobs

---

## License

[Add your license here]

---

## Support

For issues, questions, or contributions, please:
- Open an issue on the repository
- Contact the development team
- Review the documentation in `/docs` folder

---

## Changelog

### v1.0.0
- Initial release with data collection, analysis, and API services
- Email delivery automation
- Cron-based scheduling

---

**Last Updated:** 8 feb 2025
**Maintained By:** saifmk.online