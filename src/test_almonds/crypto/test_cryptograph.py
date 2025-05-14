import base64
import json

import pytest

from almonds.crypto.cryptograph import Cryptograph


@pytest.fixture
def encryption_keys() -> dict:
    key1 = Cryptograph.generate_key()
    key2 = Cryptograph.generate_key()
    return {"v1": key1, "v2": key2}


@pytest.fixture
def cryptograph(encryption_keys: dict):
    return Cryptograph(keys=encryption_keys, active_key_id="v1")


def test_encrypt_decrypt(cryptograph: Cryptograph):
    plaintext = "Sensitive data"
    ciphertext = cryptograph.encrypt(plaintext)
    assert isinstance(ciphertext, str)
    decrypted = cryptograph.decrypt(ciphertext)
    assert decrypted == plaintext


def test_encrypt_decrypt_with_associated_data(cryptograph: Cryptograph):
    plaintext = "Sensitive data"
    aad = b"header"
    ciphertext = cryptograph.encrypt(plaintext, associated_data=aad)
    decrypted = cryptograph.decrypt(ciphertext, associated_data=aad)
    assert decrypted == plaintext
    # Wrong associated data should fail
    with pytest.raises(Exception):
        cryptograph.decrypt(ciphertext, associated_data=b"wrong")


def test_key_rotation(encryption_keys: dict):
    helper = Cryptograph(keys=encryption_keys, active_key_id="v1")
    plaintext = "Rotate me"
    ct_v1 = helper.encrypt(plaintext)
    # Rotate to v2
    helper.rotate_keys(encryption_keys, new_active_key_id="v2")
    ct_v2 = helper.encrypt(plaintext)
    # Both ciphertexts should decrypt
    assert helper.decrypt(ct_v1) == plaintext
    assert helper.decrypt(ct_v2) == plaintext


def test_export_import_keys(encryption_keys: dict):
    helper = Cryptograph(keys=encryption_keys, active_key_id="v1")
    keys_json = helper.get_keys_json()
    loaded = {k: Cryptograph.decode_key(v) for k, v in json.loads(keys_json).items()}
    assert loaded == encryption_keys


def test_invalid_key_id_on_decrypt(cryptograph):
    plaintext = "Secret"
    ct = cryptograph.encrypt(plaintext)
    # Tamper with key_id in payload
    payload = json.loads(base64.b64decode(ct).decode("utf-8"))
    payload["key_id"] = "invalid"
    tampered = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    with pytest.raises(ValueError):
        cryptograph.decrypt(tampered)


def test_invalid_ciphertext_format(cryptograph: Cryptograph):
    # Not base64
    with pytest.raises(ValueError):
        cryptograph.decrypt("not_base64")
    # Not JSON
    bad = base64.b64encode(b"not_json").decode("utf-8")
    with pytest.raises(ValueError):
        cryptograph.decrypt(bad)


def test_generate_and_encode_decode_key():
    key = Cryptograph.generate_key()
    encoded = Cryptograph.encode_key(key)
    decoded = Cryptograph.decode_key(encoded)
    assert key == decoded
    assert isinstance(encoded, str)
    assert isinstance(decoded, bytes)
