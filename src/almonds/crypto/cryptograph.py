import base64
import json
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class Cryptograph:
    """
    AES-GCM encryption helper with key rotation support.
    - Keys are loaded from environment variables or a provided dict.
    - Each encryption includes the key ID for future decryption.
    - Supports key rotation and secure key management.
    """

    NONCE_SIZE = 12  # 96 bits, recommended for GCM

    def __init__(
        self,
        keys: Optional[dict[str, bytes]] = None,
        active_key_id: Optional[str] = None,
    ):
        """
        keys: dict mapping key_id to key bytes. If None, loads from env AES_KEYS_JSON.
        active_key_id: key_id to use for encryption. If None, uses env AES_ACTIVE_KEY_ID.
        """
        if keys is None:
            keys_json = os.environ.get("AES_KEYS_JSON")
            if not keys_json:
                raise ValueError("AES_KEYS_JSON environment variable not set")
            keys = {k: self.decode_key(v) for k, v in json.loads(keys_json).items()}
        self.keys = keys

        if active_key_id is None:
            active_key_id = os.environ.get("AES_ACTIVE_KEY_ID")
            if not active_key_id:
                raise ValueError("AES_ACTIVE_KEY_ID environment variable not set")
        if active_key_id not in self.keys:
            raise ValueError(f"Active key_id '{active_key_id}' not found in keys")
        self.active_key_id = active_key_id

    @staticmethod
    def generate_key() -> bytes:
        """Generate a new random AES-256 key."""
        return AESGCM.generate_key(bit_length=256)

    @staticmethod
    def encode_key(key: bytes) -> str:
        """Base64 encode a key for storage."""
        return base64.b64encode(key).decode("utf-8")

    @staticmethod
    def decode_key(key_str: str) -> bytes:
        """Base64 decode a key."""
        return base64.b64decode(key_str)

    def encrypt(self, plaintext: str, associated_data: Optional[bytes] = None) -> str:
        """
        Encrypt plaintext using the active key.
        Returns a base64-encoded JSON string containing key_id, nonce, and ciphertext.
        """
        key = self.keys[self.active_key_id]
        aesgcm = AESGCM(key)
        nonce = os.urandom(self.NONCE_SIZE)
        ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), associated_data)
        payload = {
            "key_id": self.active_key_id,
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "ciphertext": base64.b64encode(ct).decode("utf-8"),
        }
        return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    def decrypt(self, token: str, associated_data: Optional[bytes] = None) -> str:
        """
        Decrypt a base64-encoded JSON string produced by encrypt().
        """
        try:
            payload = json.loads(base64.b64decode(token).decode("utf-8"))
            key_id = payload["key_id"]
            nonce = base64.b64decode(payload["nonce"])
            ciphertext = base64.b64decode(payload["ciphertext"])
        except Exception as e:
            raise ValueError("Invalid ciphertext format") from e

        key = self.keys.get(key_id)
        if not key:
            raise ValueError(f"Key ID '{key_id}' not found for decryption")
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
        return plaintext.decode("utf-8")

    def rotate_keys(self, new_keys: dict[str, bytes], new_active_key_id: str):
        """
        Rotate to new keys. Existing ciphertexts can still be decrypted if old keys are retained.
        new_keys: dict mapping key_id to key bytes.
        new_active_key_id: key_id to use for new encryptions.
        """
        if new_active_key_id not in new_keys:
            raise ValueError("new_active_key_id must be present in new_keys")
        self.keys = new_keys
        self.active_key_id = new_active_key_id

    def get_keys_json(self) -> str:
        """
        Export keys as a JSON string (base64-encoded values), suitable for AES_KEYS_JSON.
        """
        return json.dumps({k: self.encode_key(v) for k, v in self.keys.items()})
