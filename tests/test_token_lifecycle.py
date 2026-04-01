"""
Tests for token lifecycle management functions.

Tests the create_reset_token() and decode_reset_token() functions
for password reset JWT token handling.
"""

import pytest
import time
from datetime import datetime, timedelta
from jose import jwt

# Import the functions under test
import sys
sys.path.insert(0, '/Users/gpiroux/Documents/Sfax/yds-training-exercise3/src')
from app_3 import create_reset_token, decode_reset_token, _JWT_SECRET, _JWT_ALGORITHM


class TestCreateResetToken:
    """Test suite for create_reset_token() function."""
    
    def test_returns_jwt_string(self):
        """Test that create_reset_token returns a JWT string."""
        token = create_reset_token("test@example.com")
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT has 3 parts separated by dots
        assert token.count('.') == 2
    
    def test_token_contains_email_in_sub_claim(self):
        """Test that the token encodes email in 'sub' claim."""
        email = "alice@example.com"
        token = create_reset_token(email)
        
        # Decode without verification to inspect payload
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        assert payload["sub"] == email
    
    def test_token_has_expiration_claim(self):
        """Test that token includes 'exp' claim set to 15 minutes."""
        token = create_reset_token("test@example.com")
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        
        assert "exp" in payload
        # Verify expiration is approximately 15 minutes from now
        exp_time = datetime.utcfromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + timedelta(minutes=15)
        # Allow 2 seconds tolerance for test execution time
        assert abs((exp_time - expected_exp).total_seconds()) < 2
    
    def test_token_has_issued_at_claim(self):
        """Test that token includes 'iat' (issued at) claim."""
        token = create_reset_token("test@example.com")
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        
        assert "iat" in payload
        # Verify iat is approximately now
        iat_time = datetime.utcfromtimestamp(payload["iat"])
        now = datetime.utcnow()
        # Allow 2 seconds tolerance
        assert abs((iat_time - now).total_seconds()) < 2
    
    def test_uses_correct_secret_and_algorithm(self):
        """Test that token is signed with correct secret and algorithm."""
        token = create_reset_token("test@example.com")
        
        # Should decode successfully with correct secret
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        assert payload is not None
        
        # Should fail with wrong secret
        with pytest.raises(Exception):
            jwt.decode(token, "wrong-secret", algorithms=[_JWT_ALGORITHM])


class TestDecodeResetToken:
    """Test suite for decode_reset_token() function."""
    
    def test_decodes_valid_token(self):
        """Test that decode_reset_token extracts email from valid token."""
        email = "bob@example.com"
        token = create_reset_token(email)
        
        decoded_email = decode_reset_token(token)
        assert decoded_email == email
    
    def test_raises_error_on_expired_token(self):
        """Test that expired token raises ValueError."""
        # Create an expired token (expired 1 minute ago)
        expiration = datetime.utcnow() - timedelta(minutes=1)
        payload = {
            "sub": "test@example.com",
            "exp": expiration,
            "iat": datetime.utcnow()
        }
        expired_token = jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)
        
        with pytest.raises(ValueError) as exc_info:
            decode_reset_token(expired_token)
        
        assert "invalid or expired token" in str(exc_info.value).lower()
    
    def test_raises_error_on_invalid_signature(self):
        """Test that token with invalid signature raises ValueError."""
        # Create token with wrong secret
        payload = {
            "sub": "test@example.com",
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "iat": datetime.utcnow()
        }
        invalid_token = jwt.encode(payload, "wrong-secret", algorithm=_JWT_ALGORITHM)
        
        with pytest.raises(ValueError) as exc_info:
            decode_reset_token(invalid_token)
        
        assert "invalid or expired token" in str(exc_info.value).lower()
    
    def test_raises_error_on_malformed_token(self):
        """Test that malformed token raises ValueError."""
        malformed_tokens = [
            "invalid.jwt.token",
            "not-a-jwt",
            "",
            "a.b",  # Only 2 parts
        ]
        
        for token in malformed_tokens:
            with pytest.raises(ValueError) as exc_info:
                decode_reset_token(token)
            assert "invalid or expired token" in str(exc_info.value).lower()
    
    def test_raises_error_on_missing_sub_claim(self):
        """Test that token without 'sub' claim raises ValueError."""
        # Create token without 'sub' claim
        payload = {
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "iat": datetime.utcnow()
        }
        token_without_sub = jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)
        
        with pytest.raises(ValueError) as exc_info:
            decode_reset_token(token_without_sub)
        
        assert "missing required 'sub' claim" in str(exc_info.value).lower()
    
    def test_error_messages_do_not_leak_sensitive_info(self):
        """Test that error messages don't expose sensitive information."""
        try:
            decode_reset_token("invalid.token.string")
        except ValueError as e:
            error_msg = str(e)
            # Should not contain stack traces or internal details
            assert "_JWT_SECRET" not in error_msg
            assert "traceback" not in error_msg.lower()
            # Should be a clean, safe message
            assert len(error_msg) < 200  # Reasonably short


class TestIntegration:
    """Integration tests for token lifecycle."""
    
    def test_create_and_decode_roundtrip(self):
        """Test complete create -> decode workflow."""
        test_emails = [
            "user@example.com",
            "admin@test.org",
            "developer+test@company.io"
        ]
        
        for email in test_emails:
            token = create_reset_token(email)
            decoded = decode_reset_token(token)
            assert decoded == email
    
    def test_tokens_are_unique(self):
        """Test that each call generates a unique token."""
        email = "test@example.com"
        token1 = create_reset_token(email)
        time.sleep(1.1)  # Ensure different second (Unix timestamp is second-precision)
        token2 = create_reset_token(email)
        
        # Tokens should be different due to different 'iat' timestamps
        assert token1 != token2
    
    def test_token_expires_after_15_minutes(self):
        """Verify token expiration is exactly 15 minutes."""
        token = create_reset_token("test@example.com")
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        
        exp_timestamp = payload["exp"]
        iat_timestamp = payload["iat"]
        lifetime_seconds = exp_timestamp - iat_timestamp
        
        # Should be exactly 15 minutes (900 seconds)
        assert lifetime_seconds == 900
