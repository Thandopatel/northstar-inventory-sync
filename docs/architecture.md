# Architecture

_(Diagram / description of the system as it evolves. Updated to reflect the working webhook-based prototype.)_

## Components

- **Frontend (`frontend/`)** — `index.html`, `style.css`, `script.js`. Plain
  HTML/JS support-tool dashboard. Served locally via `py -m http.server
  5500`. Has two forms: one to submit a simulated inventory webhook, one to
  look up current stock by SKU.

- **Backend API (`backend/`)** — FastAPI service (`main.py`) exposing two
  routes:
  - `POST /api/v1/webhooks/inventory` — receives a stock update payload and
    writes it to the database.
  - `GET /api/v1/stock/{sku}` — returns current stock level for a given SKU.
  - `CORSMiddleware` is enabled with `allow_origins=["*"]` so the frontend
    (served from a different port) can call the API from the browser.

- **Data layer (`backend/models.py`, `backend/database.py`)** — SQLite
  database (`inventory.db`) accessed through SQLAlchemy. One table,
  `InventoryItem`, storing `sku`, `product_name`, `quantity`, `in_stock`,
  and `updated_at`.

- **Business logic (`backend/inventory.py`)** — `update_or_create_stock()`
  and `check_stock()`. Looks up a SKU; creates a new row if it doesn't
  exist, otherwise updates quantity/stock status in place.

- **Schemas (`backend/webhook.py`)** — Pydantic models defining the shape
  of webhook payloads and API responses (`InventoryWebhookPayload`,
  `WebhookResponse`, `StockCheckResponse`).

- **Day 1–2 solo prototype (`day-1-2-mini-prototype/`)** — standalone
  script exploring webhook signature verification (HMAC-SHA256) in
  isolation, before the concept was applied to the team build.

## Data flow

1. An external system (simulated via the frontend form, standing in for
   the warehouse) sends a `POST /api/v1/webhooks/inventory` request with
   `sku`, `product_name`, and `quantity`.
2. FastAPI validates the payload shape against `InventoryWebhookPayload`.
3. `inventory.update_or_create_stock()` looks up the SKU in SQLite. If it
   exists, quantity and `in_stock` are updated; if not, a new row is
   created.
4. The updated record is committed to `inventory.db` and returned in the
   response.
5. Separately, the support tool calls `GET /api/v1/stock/{sku}`, which
   reads the current row for that SKU and returns `in_stock` + `quantity`.
6. The frontend renders both flows' results directly in the browser.

**Note:** this is a push model — the backend does not poll anything. It
passively waits for `POST` requests and answers `GET` queries against
whatever was last pushed to it.

## Key decisions & trade-offs

- **Webhook push over polling.** The team implemented the pivoted
  (webhook) spec directly rather than the original polling spec (poll
  warehouse API every 5 minutes, cache, expose query endpoint). This
  removes constant outbound polling traffic and gives near-real-time
  updates, at the cost of relying on the warehouse system to reliably
  deliver every change — if a webhook delivery is missed, this service has
  no fallback mechanism to detect and correct the gap (a polling model
  would eventually self-correct on its next cycle).

- **No webhook signature verification implemented yet.** The Day 1–2 solo
  prototype explored HMAC-based verification as a concept, but the actual
  `backend/webhook.py` endpoint does not verify that incoming requests are
  genuinely from the warehouse system — any `POST` to that URL is trusted.
  This is a known gap, not an oversight: securing the endpoint (shared
  secret + signature check, mirroring the solo prototype) is the next
  priority before this could be considered production-ready.

- **CORS wide open (`allow_origins=["*"]`).** Necessary for local
  development since frontend and backend run on different ports, but this
  is not appropriate for production and would need to be scoped to a
  specific origin.

- **SQLite over a production database.** Chosen for local development
  speed and zero setup. Fine for a single-process prototype; would need
  to move to a networked database (e.g. Postgres) for any real deployment
  with concurrent writers.