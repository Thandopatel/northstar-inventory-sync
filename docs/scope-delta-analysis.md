# Scope Delta Analysis
**Date:** 2026-08-22
**Sprint:** Northstar Retail Co. — Meridian Pivot
**Author:** Thando Patel

## Executive Summary
On Day 4, the client announced that the polling-based inventory sync method would be killed in 48 hours. The team pivoted to a webhook push model. This document captures what changed, what was removed, what was added, and the trade-offs made to meet the deadline.

---

## 1. Dropped (Removed Completely)

### Polling System
- **Files removed:**
  - `backend/poller.py` — contained the polling loop with 5-minute interval
  - `test_warehouse_client.py` — tests specific to polling client
- **Code removed from `backend/main.py`:**
  - `from .pollers import InventoryPoller` (import)
  - `poller = InventoryPoller()` (initialization)
  - `poller.start()` (startup event)
  - `await poller.stop()` (shutdown event)
  - `@app.on_event("startup")` block
  - `@app.on_event("shutdown")` block
- **Features removed:**
  - Scheduled polling every 5 minutes
  - Outbound HTTP requests to warehouse API
  - Polling-based caching logic
- **Why:** Vendor API deprecation — no extension possible

---

## 2. Modified (Changed to Fit New Model)

### Database Schema
- **Kept:** `inventory_cache` table with `sku`, `quantity`, `last_updated`
- **Modified:** `last_updated` now reflects webhook push time, not poll time
- **No schema changes needed** — the existing table worked with both models

### API Endpoints
| Old Endpoint | New Endpoint | Change |
| :--- | :--- | :--- |
| `GET /api/v1/stock` | `GET /api/v1/stock` | **KEPT** — still queries all inventory |
| `GET /api/v1/stock/{sku}` | `GET /api/v1/stock/{sku}` | **KEPT** — still queries specific SKU |
| `POST /api/v1/webhooks/inventory` | **NEW** | **ADDED** — receives warehouse push updates |
| `GET /api/v1/poll` | **REMOVED** | No longer needed |

### Code Structure
- **Changed:** `main.py` — removed all poller references, added webhook endpoint
- **Kept:** `database.py` — unchanged (database connection logic)
- **Kept:** `inventory.py` — unchanged (stock update/lookup logic)

---

## 3. Added (New for Webhooks)

### Webhook Endpoint
- `POST /api/v1/webhooks/inventory` — accepts JSON payload with SKU and quantity
- Returns 200 OK on success, 400 on validation failure, 404 if SKU not found

### Webhook Handler Logic
- Upsert operation: insert new inventory or update existing
- Timestamp tracking: `last_updated` set to current time on each webhook
- Logging: all webhook events logged for audit trail

### Service Status Endpoint
- `GET /` — returns service info including "model": "webhook-push"
- Helps verify the service is running in the correct mode

---

## 4. Reprioritized Backlog

### Items Deprioritized to Meet Deadline
1. **Advanced logging** — postponed; basic logging kept
2. **Webhook retry logic** — postponed to Sprint 3
3. **Webhook signature verification** — postponed (mock warehouse only)
4. **Frontend real-time updates** — out of scope for this sprint

### Items Prioritized
1. Core webhook endpoint — **must work**
2. Database upsert logic — **critical for data integrity**
3. Removal of all polling code — **non-negotiable requirement**
4. Service status endpoint — **simple to implement**

---

## 5. Trade-off Documentation

### What We Gained
✅ **Real-time inventory updates** — no 5-minute delay
✅ **Reduced server load** — no constant polling requests
✅ **Better scalability** — warehouse pushes only when stock changes
✅ **Simpler codebase** — removed 111 lines of polling code

### What We Lost
❌ **Simplicity** — polling was simpler to implement and debug
❌ **Control** — now dependent on warehouse sending webhooks reliably
❌ **Predictability** — no guaranteed update cadence

### New Risks Introduced
⚠️ **Webhook delivery failure** — if warehouse can't reach our endpoint
⚠️ **Out-of-order events** — if webhooks arrive in wrong sequence
⚠️ **Network dependency** — service must be publicly accessible

### Mitigations Implemented
- Upsert logic (idempotent updates) — safe to replay webhooks
- Logging for all webhook events (audit trail)
- Graceful error handling with 400/500 responses
- Database transactions to prevent partial updates

---

## 6. Testing Strategy

### Tests Added for Webhooks
- Webhook endpoint accepts valid payload → 200 OK
- Webhook with missing fields → 400 Bad Request
- Webhook updates inventory correctly → database reflects change

### Tests Removed
- All tests that relied on polling client (`test_warehouse_client.py`)
- Tests that assumed 5-minute update cadence

### Tests Kept
- `test_api_client.py` — cleaned up (removed poller imports)
- `test_inventory.py` — unchanged (tests inventory logic)
- `test_webhook.py` — unchanged (tests webhook functionality)

---

## 7. Time/Effort Impact

| Activity | Time Spent |
| :--- | :--- |
| Initial polling implementation (Days 1-3) | ~6 hours |
| Webhook refactor (Day 4-5) | ~5 hours |
| Testing and debugging | ~2 hours |
| Documentation | ~1 hour |
| **Total** | **~14 hours** |

### What Got Faster
- Stock updates: **from 5 minutes → instant (webhook trigger)**
- Data freshness: **real-time vs delayed**

### What Got Slower
- Initial setup: **more complex configuration**
- Debugging: **harder to trace webhook failures**

---

## 8. Lessons Learned

1. **Always design for asynchronous updates** — even if spec says sync now
2. **Keep the webhook simple** — upsert logic is enough for MVP
3. **Log everything** — webhooks are harder to debug than polling
4. **Idempotency is critical** — prevent duplicate updates from out-of-order webhooks
5. **Delete old code completely** — don't leave it in comments or commented out

---

## 9. Conclusion

The pivot from polling to webhooks was successfully completed within the 48-hour deadline. The new system is more scalable, provides real-time updates, and meets the client's new requirements. Trade-offs were carefully managed, and risks were mitigated through logging and idempotent updates.

The service now operates entirely on the webhook push model, with no polling code remaining in production.

---

**Signed:** Thando Patel
**Date:** 2026-08-22