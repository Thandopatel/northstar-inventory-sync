# northstar-inventory-sync

Northstar Retail Co. Sprint 2 — live inventory synchronization service.

## Status
Working prototype. Backend (FastAPI) and frontend (HTML/JS) are built and
connected — the frontend can send webhook inventory updates and query
current stock levels against the live backend. Day 1–2 solo prototype,
Learning & Blocker Journal, and initial docs are in place. Scope Delta
Analysis and Architecture docs are in progress.

## Structure
- `day-1-2-mini-prototype/` — solo mini-prototype for the privately assigned
  tool (webhook verification), built independently on Days 1–2
- `backend/` — FastAPI inventory sync service
  - `main.py` — app entrypoint, routes (`POST /api/v1/webhooks/inventory`,
    `GET /api/v1/stock/{sku}`)
  - `models.py` — SQLAlchemy `InventoryItem` model
  - `database.py` — SQLite engine/session setup
  - `inventory.py` — stock update/lookup logic
  - `webhook.py` — request/response schemas
- `frontend/` — support tool UI (`index.html`, `script.js`, `style.css`),
  served locally and calling the backend directly
- `tests/` — test suite
- `docs/` — Learning & Blocker Journal, Scope Delta Analysis, Architecture
  notes

## Running it locally
Backend:
```
py -m uvicorn backend.main:app --reload
```
Frontend (from the `frontend/` folder):
```
py -m http.server 5500
```
Then open `http://127.0.0.1:5500` in the browser.

## Current implementation
The service currently implements a **webhook push model**: the warehouse
system pushes stock changes to `POST /api/v1/webhooks/inventory`, and the
support tool queries current stock via `GET /api/v1/stock/{sku}`.

See `docs/scope-delta-analysis.md` for how this compares to the original
polling-based spec, and `docs/learning-blocker-journal.md` for the
real-time log of how this was built.