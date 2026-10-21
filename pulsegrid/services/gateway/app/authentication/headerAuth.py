"""
    This Header Auth module is used for the preparation of the auth credientials that which will we send along with the
    request thorugh the gateway,

    so that requests that is passed only through the gateway will be accepted by the internal servicessss.
    Here we are using the Libsodium library for the generation of the crypto signatures

    for the pythonic support of libsodium we are using thr nacl which provides the official bindings of libsodium which that supports python.
"""
import os
import time
import uuid
import hashlib
import base64
from nacl.signing import SigningKey

# 1. Your 32-byte Ed25519 private seed (Keep this secret in your Gateway .env!)
# (You can generate a fresh one using the Python script we looked at earlier)
GATEWAY_PRIVATE_SEED_BS64 = os.getenv('GATEWAY_SECRET_KEY') or ''

def generate_libsodium_signature_headers(method: str, path: str) -> dict:
    """
    Generates cryptographically signed headers using Libsodium Ed25519.
    """
    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())
    
    # Simple, human-readable canonical message format
    message = f"{method.upper()}|{path}|{timestamp}|{nonce}".encode("utf-8")
    
    # Decode Base64 private key and sign the message
    seed_bytes = base64.b64decode(GATEWAY_PRIVATE_SEED_BS64)
    signing_key = SigningKey(seed_bytes)
    signed_message = signing_key.sign(message)


    return {
        "X-Signature": signed_message.signature.hex(),
        "X-Timestamp": timestamp,
        "X-Nonce": nonce
    }

