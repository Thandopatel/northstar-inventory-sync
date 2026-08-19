# Day 1–2 Mini-Prototype

Solo prototype for the privately assigned unfamiliar tool.
No teammate/instructor how-to help — built and documented independently.

## Tool assigned
Webhook verification

## Prior familiarity
None

## What this demonstrates
`webhook_verification_prototype.py` is a standalone script (no framework)
that shows how a webhook receiver can confirm an incoming request genuinely
came from the sender it claims to be from, using an HMAC-SHA256 signature:

- **Scenario 1:** a correctly signed payload is accepted.
- **Scenario 2:** a request with an invalid/forged signature is rejected.
- **Scenario 3:** a genuine payload that was altered after signing (signature
  no longer matches) is rejected.

This concept — verify before you trust the payload — was then carried into
the team's actual webhook endpoint in `backend/webhook.py`.

## Run it
```
python webhook_verification_prototype.py
```

See `../docs/learning-blocker-journal.md` for the real-time log of getting
to this understanding (Entries 1–2).