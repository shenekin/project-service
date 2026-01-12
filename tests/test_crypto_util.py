"""
Unit tests for crypto utility
"""

import pytest
from app.utils.crypto_util import CryptoUtil


def test_encrypt_decrypt():
    """Test encryption and decryption functionality"""
    crypto = CryptoUtil()
    
    plaintext = "test_secret_key_12345"
    encrypted = crypto.encrypt(plaintext)
    
    assert encrypted != plaintext
    assert len(encrypted) > 0
    
    decrypted = crypto.decrypt(encrypted)
    assert decrypted == plaintext


def test_encrypt_empty_string():
    """Test encryption of empty string"""
    crypto = CryptoUtil()
    
    encrypted = crypto.encrypt("")
    assert encrypted == ""
    
    decrypted = crypto.decrypt("")
    assert decrypted == ""


def test_mask_access_key():
    """Test access key masking"""
    masked = CryptoUtil.mask_access_key("ABCD1234567890", visible_chars=4)
    assert masked == "ABCD**********"
    
    masked = CryptoUtil.mask_access_key("SHORT", visible_chars=4)
    assert masked == "*****"
    
    masked = CryptoUtil.mask_access_key("", visible_chars=4)
    assert masked == ""


def test_mask_access_key_custom_visible():
    """Test access key masking with custom visible characters"""
    masked = CryptoUtil.mask_access_key("ABCD1234567890", visible_chars=6)
    assert masked == "ABCD12********"
    
    masked = CryptoUtil.mask_access_key("ABCD1234567890", visible_chars=2)
    assert masked == "AB************"

