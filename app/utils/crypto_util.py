"""
Cryptographic utility for encrypting/decrypting sensitive data
"""

import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.settings import get_settings


class CryptoUtil:
    """Utility class for encryption and decryption operations"""
    
    def __init__(self):
        """Initialize crypto utility with encryption key"""
        self.settings = get_settings()
        self._cipher_suite: Optional[Fernet] = None
        self._initialize_cipher()
    
    def _initialize_cipher(self) -> None:
        """
        Initialize Fernet cipher suite with encryption key
        
        The encryption key is derived from environment variable or generated.
        In production, use a secure key management system.
        """
        # Get encryption key from environment or generate from settings
        encryption_key = os.getenv("ENCRYPTION_KEY")
        
        if not encryption_key:
            # Generate key from a combination of settings (for development)
            # In production, this should be a secure key from key management
            salt = os.getenv("ENCRYPTION_SALT", "project-service-salt").encode()
            password = os.getenv("ENCRYPTION_PASSWORD", "default-password-change-in-production").encode()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            # Use provided key (must be base64-encoded 32-byte key)
            if len(encryption_key) != 44:  # Base64 encoded 32 bytes = 44 chars
                raise ValueError("ENCRYPTION_KEY must be a base64-encoded 32-byte key")
            key = encryption_key.encode()
        
        self._cipher_suite = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string
        
        Args:
            plaintext: Plain text to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        if not self._cipher_suite:
            raise RuntimeError("Cipher suite not initialized")
        
        if not plaintext:
            return ""
        
        encrypted_bytes = self._cipher_suite.encrypt(plaintext.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt encrypted string
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            Decrypted plain text
        """
        if not self._cipher_suite:
            raise RuntimeError("Cipher suite not initialized")
        
        if not ciphertext:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted_bytes = self._cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")
    
    @staticmethod
    def mask_access_key(access_key: str, visible_chars: int = 4) -> str:
        """
        Mask access key to show only first N characters
        
        Args:
            access_key: Full access key
            visible_chars: Number of characters to show (default: 4)
            
        Returns:
            Masked access key (e.g., "ABCD****")
        """
        if not access_key:
            return ""
        
        if len(access_key) <= visible_chars:
            return "*" * len(access_key)
        
        return access_key[:visible_chars] + "*" * (len(access_key) - visible_chars)

