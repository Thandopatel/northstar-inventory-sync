"""
Day 1-2 Solo Mini-Prototype
Tool/concept assigned: Webhook verification

This is a standalone, self-contained exploration of how a webhook receiver
can verify that an incoming request genuinely came from the sender it
claims to be from (e.g. a warehouse system), rather than trusting any
payload that hits the endpoint.

No framework (FastAPI, Flask, etc.) is used here on purpose - the goal of
Days 1-2 was to understand the *concept* of webhook verification in
isolation, before applying it inside the team's actual inventory-sync
service in backend/.

Run it directly:
    python webhook_verification_prototype.py
"""

import hmac
import hashlib
import json


# --- Setup -------------------------------------------------------------
# In a real system, this secret would be shared privately between the
# warehouse system and our service (e.g. an env variable), never hardcoded
# or sent over the wire.
SHARED_SECRET = "example-shared-secret-do-not-use-in-prod"


def sign_payload(payload: dict, secret: str) -> str:
    """
    Simulates what the SENDER (the warehouse system) would do:
    compute an HMAC-SHA256 signature of the payload using the shared
    secret, so the receiver can later confirm the payload wasn't
    forged or tampered with in transit.
    """
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256)
    return signature.hexdigest()


def verify_signature(payload: dict, received_signature: str, secret: str) -> bool:
    """
    Simulates what the RECEIVER (our inventory service) does:
    recompute the expected signature from the payload + shared secret,
    then compare it against the signature that arrived in the request
    header. Using hmac.compare_digest avoids timing-attack leaks.
    """
    expected_signature = sign_payload(payload, secret)
    return hmac.compare_digest(expected_signature, received_signature)


# --- Demonstration -------------------------------------------------------

def run_demo():
    print("=== Webhook Verification Prototype ===\n")

    # Scenario 1: legitimate webhook from the warehouse system
    genuine_payload = {"sku": "SKU-1001", "product_name": "Blue Mug", "quantity": 42}
    genuine_signature = sign_payload(genuine_payload, SHARED_SECRET)

    print("Scenario 1: Legitimate webhook")
    print(f"  Payload: {genuine_payload}")
    print(f"  Signature sent: {genuine_signature}")
    is_valid = verify_signature(genuine_payload, genuine_signature, SHARED_SECRET)
    print(f"  Result: {'ACCEPTED' if is_valid else 'REJECTED'}\n")

    # Scenario 2: a request claiming the same payload, but with no valid
    # signature (e.g. someone hitting the endpoint directly / spoofing it)
    print("Scenario 2: Spoofed request (invalid signature)")
    forged_signature = "0000000000000000000000000000000000000000000000000000000000000000"
    is_valid = verify_signature(genuine_payload, forged_signature, SHARED_SECRET)
    print(f"  Payload: {genuine_payload}")
    print(f"  Signature sent: {forged_signature}")
    print(f"  Result: {'ACCEPTED' if is_valid else 'REJECTED'}\n")

    # Scenario 3: payload tampered with AFTER signing (e.g. intercepted
    # and the quantity changed), signature no longer matches
    print("Scenario 3: Payload tampered with after signing")
    tampered_payload = dict(genuine_payload)
    tampered_payload["quantity"] = 999999  # attacker changes the stock count
    is_valid = verify_signature(tampered_payload, genuine_signature, SHARED_SECRET)
    print(f"  Original signature: {genuine_signature}")
    print(f"  Tampered payload: {tampered_payload}")
    print(f"  Result: {'ACCEPTED' if is_valid else 'REJECTED'}\n")


if __name__ == "__main__":
    run_demo()