# SmartLink — Context-Aware URL Shortener

A production-grade URL shortener that routes users to different destinations based on **device, geolocation, referrer, and time of day**. Built with a focus on backend systems: Redis caching, sliding window rate limiting, async click logging, and a rule engine with priority ordering.

**Live Demo:** https://smartlink-frontend-ten.vercel.app  
**API Docs:** https://smartlink-production-028d.up.railway.app/docs

---

## Features

- **Custom slugs** — choose your own short code (e.g. `smartlink.app/my-portfolio`)
- **Rule-based routing** — route mobile users to one URL, desktop to another; route by country, referrer, or time of day
- **A/B testing** — split traffic between two URLs with configurable ratio
- **Redis caching** — sub-10ms redirects for cached links
- **Sliding window rate limiting** — 60 requests/minute per IP
- **Analytics dashboard** — clicks by country, device, date, A/B variant
- **Token-based management** — no login required; manage token is your key
- **Link expiry** — set an expiration date on any link

---

## Architecture

```
React Frontend (Vercel)
        ↓
FastAPI Backend (Railway)
        ↓               ↓
PostgreSQL          Redis
(links, rules,      (cache + rate
 clicks)             limiter)
```

### Redirect flow

1. Request hits `GET /{short_code}`
2. Rate limiter checks IP against Redis sliding window
3. Redis cache checked — if hit, redirect immediately (sub-10ms)
4. On cache miss — fetch link + rules from PostgreSQL, cache result
5. Rule engine evaluates conditions in priority order (device → country → referrer → time)
6. Click logged asynchronously (non-blocking)
7. Redirect issued

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Cache + Rate Limiting | Redis |
| Frontend | React, Recharts, React Router |
| Deployment | Railway (backend), Vercel (frontend) |
| Containerization | Docker + docker-compose |

---

## Key Engineering Decisions

**Sliding window rate limiting** — uses Redis sorted sets with timestamps as scores. Each request adds a timestamp, entries older than 60s are removed, count determines if limit is exceeded. More accurate than fixed window which allows burst at window boundaries.

**Async click logging** — clicks are logged via `asyncio.create_task()` so the redirect response is not blocked by a DB write. Redirect latency is unaffected by logging.

**Redis cache invalidation** — when a link is updated or deleted, the cache key is immediately invalidated. TTL is 1 hour for unchanged links.

**Token-based auth** — no user accounts. Each link gets a UUID manage token returned once on creation. Simpler than JWT for anonymous public tooling.

**Rule priority ordering** — rules are sorted by priority integer before evaluation. First match wins. Allows fine-grained control (e.g. mobile India users get a different URL than desktop India users by setting two rules with different priorities).

**Base62 short code generation** — uses `a-z`, `A-Z`, `0-9` character set. 6-character codes give 56 billion unique combinations. Collision check runs up to 5 attempts before failing gracefully.

---

## Performance

| Scenario | Latency |
|---|---|
| Cache hit (Redis) | < 10ms |
| Cache miss (PostgreSQL) | < 100ms |
| Rate limit check | < 5ms |

Benchmarked with 100 sequential requests on Railway free tier.

---

## Database Schema

```sql
links (
  id              SERIAL PRIMARY KEY,
  short_code      VARCHAR(50) UNIQUE NOT NULL,
  default_url     TEXT NOT NULL,
  manage_token    UUID UNIQUE NOT NULL,
  created_at      TIMESTAMP DEFAULT NOW(),
  expires_at      TIMESTAMP,
  is_ab_test      BOOLEAN DEFAULT FALSE,
  ab_url_b        TEXT,
  ab_split_ratio  INTEGER DEFAULT 50
)

rules (
  id               SERIAL PRIMARY KEY,
  link_id          INTEGER REFERENCES links(id),
  condition_type   VARCHAR(20),   -- device | country | referrer | time_range
  condition_value  VARCHAR(100),  -- mobile | IN | twitter.com | 09:00-17:00
  target_url       TEXT NOT NULL,
  priority         INTEGER DEFAULT 0
)

clicks (
  id               SERIAL PRIMARY KEY,
  link_id          INTEGER REFERENCES links(id),
  clicked_at       TIMESTAMP DEFAULT NOW(),
  country          VARCHAR(2),
  device           VARCHAR(10),
  referrer         TEXT,
  matched_rule_id  INTEGER,
  ab_variant       VARCHAR(1)
)
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/links` | None | Create short link |
| GET | `/{short_code}` | None | Redirect |
| GET | `/check/{slug}` | None | Check slug availability |
| POST | `/links/{code}/rules` | Token | Add routing rule |
| GET | `/links/{code}/rules` | Token | Get all rules |
| DELETE | `/rules/{id}` | Token | Remove rule |
| GET | `/links/{code}/analytics` | Token | Click analytics |
| PUT | `/links/{code}` | Token | Update link |
| DELETE | `/links/{code}` | Token | Delete link |
| GET | `/health` | None | Health check |

---

## Routing Rule Reference

| condition_type | condition_value example | Description |
|---|---|---|
| `device` | `mobile` / `desktop` / `tablet` | Route by device type |
| `country` | `IN` / `US` / `GB` | Route by country code |
| `referrer` | `twitter.com` / `linkedin.com` | Route by referring site |
| `time_range` | `09:00-17:00` | Route by time of day (UTC) |

Rules are evaluated in priority order — lower number = higher priority. First match wins. If no rule matches, the default URL is used.

---

## Running Locally

**Prerequisites:** Docker, Python 3.10+, Node.js

```bash
# Clone
git clone https://github.com/AtharvMalusare/smartlink
cd smartlink

# Start PostgreSQL + Redis
cd backend
docker-compose up -d

# Install and run backend
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
python -m uvicorn api.main:app --reload

# Install and run frontend (new terminal)
cd ../frontend
npm install
npm run dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Project Structure

```
smartlink/
├── backend/
│   ├── api/
│   │   ├── main.py               ← FastAPI app entry
│   │   ├── models.py             ← SQLAlchemy models
│   │   ├── schemas.py            ← Pydantic schemas
│   │   ├── database.py           ← PostgreSQL connection
│   │   ├── routes/
│   │   │   ├── links.py          ← CRUD for links
│   │   │   ├── redirect.py       ← GET /{short_code}
│   │   │   ├── rules.py          ← routing rules
│   │   │   ├── analytics.py      ← click data
│   │   │   └── slug.py           ← availability check
│   │   └── services/
│   │       ├── rule_engine.py    ← priority rule evaluation
│   │       ├── shortcode.py      ← base62 generation
│   │       ├── geoip.py          ← IP → country
│   │       ├── cache.py          ← Redis layer
│   │       ├── ratelimit.py      ← sliding window
│   │       └── ab_test.py        ← traffic splitting
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
└── frontend/
    └── src/
        ├── pages/
        │   ├── Home.jsx          ← create link
        │   ├── Manage.jsx        ← manage + rules
        │   └── Analytics.jsx     ← charts
        ├── components/
        │   ├── RuleBuilder.jsx
        │   └── SlugInput.jsx
        ├── api.js                ← axios calls
        └── App.jsx
```

---

## Deployment

**Backend — Railway**
- PostgreSQL and Redis provisioned as Railway services
- Environment variables `DATABASE_URL` and `REDIS_URL` injected automatically
- SSL enforced for PostgreSQL connection

**Frontend — Vercel**
- Connected to GitHub repo, auto-deploys on push
- `VITE_API_URL` points to Railway backend

---

## Author

**Atharv Malusare**  
MS Computer Science — Indiana University Bloomington  
[LinkedIn](https://linkedin.com/in/atharvmalusare) · [GitHub](https://github.com/AtharvMalusare)
