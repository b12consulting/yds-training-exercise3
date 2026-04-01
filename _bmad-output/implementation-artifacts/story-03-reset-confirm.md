# Story 03: Password Reset Confirmation Endpoint

**Epic:** Password Reset Feature (OWASP-compliant)  
**Story ID:** PWR-003  
**Priority:** High  
**Estimated Complexity:** High

---

## User Story

**As a** user who received a password reset link,  
**I want to** submit a new password along with the reset token,  
**So that** my account password is securely updated and I can log in again.

---

## Context

This story implements the `/reset-password/confirm` endpoint which validates reset tokens, enforces password policies, and updates user passwords. Critical security features include one-time token use, password complexity validation, and migration from MD5 to bcrypt hashing.

**Files to modify:**
- `src/app_3.py` - implement `confirm_password_reset()` endpoint function
- `src/app_3.py` - refactor `hash_password()` to use bcrypt instead of MD5

**Dependencies:**
- Story PWR-001 must be complete (`decode_reset_token` available)
- Story PWR-002 must be complete (tokens stored in user docs)
- Existing utilities: `db`, `logger` from `helpers.py`

**Architecture Reference:**
- See `_bmad-output/planning-artifacts/architecture.md`
- OWASP requirement: One-time token use
- OWASP requirement: Strong password hashing (bcrypt)
- OWASP requirement: Password complexity validation

---

## Acceptance Criteria

### AC-01: Basic Endpoint Functionality

**Given** a user submits a password reset confirmation,  
**When** `POST /reset-password/confirm` is called with `{"token": "...", "new_password": "..."}`,  
**Then** it should:
- ✅ Accept a `PasswordResetConfirmModel` (already defined)
- ✅ Validate the token
- ✅ Validate password complexity
- ✅ Update the user's password
- ✅ Return HTTP 200 with message: `{"message": "Password has been reset successfully."}`

### AC-02: Token Validation & One-Time Use

**Given** a reset token is provided,  
**When** the token is validated,  
**Then** it should:
- ✅ Decode token using `decode_reset_token(request.token)` - this validates signature & expiration
- ✅ Extract email from token
- ✅ Retrieve user from DB: `user = db.get(email)`
- ✅ Verify user exists (if not, raise HTTP 400 "Invalid or expired reset token")
- ✅ Verify stored token matches provided token (if not, raise HTTP 400 "Invalid or expired reset token")
- ✅ **One-time use:** After successful password update, set `user["reset_token"] = None` to invalidate token

**Implementation hints:**
```python
@app.post("/reset-password/confirm")
def confirm_password_reset(request: PasswordResetConfirmModel):
    # 1. Decode and validate token (signature + expiration)
    try:
        email = decode_reset_token(request.token)
    except ValueError:
        logger.warning("Invalid or expired token submitted")
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    
    # 2. Retrieve user
    user = db.get(email)
    if not user:
        logger.warning(f"Token valid but user {email} not found")
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    
    # 3. Verify token matches stored token (one-time use check)
    if user.get("reset_token") != request.token:
        logger.warning(f"Token mismatch or already used for {email}")
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    
    # 4. Validate password complexity
    validate_password_complexity(request.new_password)
    
    # 5. Update password with bcrypt
    user["password_hash"] = hash_password(request.new_password)
    
    # 6. Invalidate token (one-time use)
    user["reset_token"] = None
    db.set(email, user)
    
    logger.info(f"Password reset successful for {email}")
    return {"message": "Password has been reset successfully."}
```

### AC-03: Password Complexity Validation (OWASP)

**Given** a new password is provided,  
**When** password complexity is validated,  
**Then** it should enforce:
- ✅ Minimum 8 characters
- ✅ At least 1 uppercase letter (A-Z)
- ✅ At least 1 lowercase letter (a-z)
- ✅ At least 1 digit (0-9)
- ✅ If validation fails, raise HTTP 400 with descriptive message

**Implementation:**
```python
import re
from fastapi import HTTPException

def validate_password_complexity(password: str) -> None:
    """
    Validate password meets OWASP complexity requirements.
    
    Raises:
        HTTPException: If password doesn't meet requirements.
    """
    errors = []
    
    if len(password) < 8:
        errors.append("at least 8 characters")
    if not re.search(r'[A-Z]', password):
        errors.append("at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        errors.append("at least one digit")
    
    if errors:
        message = f"Password must contain {', '.join(errors)}."
        logger.warning(f"Password complexity validation failed: {message}")
        raise HTTPException(status_code=400, detail=message)
```

### AC-04: Migrate to bcrypt Hashing

**Given** the current code uses MD5 (insecure),  
**When** refactoring `hash_password()`,  
**Then** it should:
- ✅ Replace MD5 with bcrypt from passlib library
- ✅ Use bcrypt's built-in salting (no manual salt needed)
- ✅ Update function to use `CryptContext` from passlib
- ✅ Ensure existing `/register` and `/login` endpoints still work

**CRITICAL:** This change affects password storage system-wide.

**Implementation:**
```python
from passlib.context import CryptContext

# Add at module level (replace MD5 import)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt with automatic salting."""
    return _pwd_context.hash(password)

# Also need to update login verification:
# In login() endpoint, replace:
#   if user["password_hash"] != hash_password(request.password):
# With:
#   if not _pwd_context.verify(request.password, user["password_hash"]):
```

**Note:** Existing test users (alice, bob) have MD5 hashes. For the exercise, you can either:
- Re-register them with bcrypt, or
- Add a migration check in login endpoint

### AC-05: Error Handling & Security

**Given** various error conditions,  
**When** they occur,  
**Then** it should:
- ✅ Invalid/expired token → HTTP 400 "Invalid or expired reset token."
- ✅ Token already used → HTTP 400 "Invalid or expired reset token." (same message)
- ✅ User not found → HTTP 400 "Invalid or expired reset token." (same message)
- ✅ Weak password → HTTP 400 with specific complexity requirements
- ✅ All errors logged with appropriate level (warning for security events)
- ✅ Generic error messages prevent information disclosure

### AC-06: Logging & Audit Trail

- ✅ Log successful password resets: `logger.info(f"Password reset successful for {email}")`
- ✅ Log token validation failures: `logger.warning("Invalid or expired token submitted")`
- ✅ Log password complexity failures: `logger.warning(f"Password complexity validation failed")`
- ✅ Log token reuse attempts: `logger.warning(f"Token mismatch or already used for {email}")`
- ✅ Do NOT log passwords (plain or hashed) except in bcrypt hash storage

---

## Implementation Flow

```
1. Request arrives: POST /reset-password/confirm {"token": "...", "new_password": "..."}
2. Decode token (validates signature & expiration)
   - If invalid: 400 "Invalid or expired reset token"
3. Get user from DB using email from token
   - If not found: 400 "Invalid or expired reset token"
4. Verify stored token matches provided token (one-time use)
   - If mismatch: 400 "Invalid or expired reset token"
5. Validate password complexity
   - If invalid: 400 with specific requirements
6. Hash password with bcrypt
7. Update user: password_hash = new hash, reset_token = None
8. Save to DB
9. Log success
10. Return 200 "Password has been reset successfully."
```

---

## Testing Guidance

**Manual testing scenarios:**

1. **Happy path:**
   ```bash
   # First, request a reset
   POST /reset-password/request {"email": "alice@example.com"}
   # Copy token from console output
   
   # Then confirm with valid password
   POST /reset-password/confirm {
     "token": "<token from console>",
     "new_password": "NewPass123"
   }
   
   Expected: 200 OK, success message
   ```

2. **Verify one-time use:**
   ```bash
   # Try to use the same token again
   POST /reset-password/confirm {
     "token": "<same token>",
     "new_password": "AnotherPass456"
   }
   
   Expected: 400 "Invalid or expired reset token"
   ```

3. **Weak password:**
   ```bash
   POST /reset-password/confirm {
     "token": "<valid token>",
     "new_password": "weak"
   }
   
   Expected: 400 with complexity requirements
   ```

4. **Expired token:**
   - Modify `create_reset_token` to use `timedelta(minutes=-1)`
   - Generate expired token
   - Attempt to use it
   - Expected: 400 "Invalid or expired reset token"

5. **Verify bcrypt login:**
   ```bash
   # After successful reset
   POST /login {
     "email": "alice@example.com",
     "password": "NewPass123"
   }
   
   Expected: 200 OK with access_token
   ```

---

## Dependencies

**Required from Story PWR-001:**
- ✅ `decode_reset_token(token)` function

**Required from Story PWR-002:**
- ✅ Tokens stored in user documents (`user["reset_token"]`)

**Existing utilities:**
- ✅ `db` - DocumentStore instance
- ✅ `logger` - logging instance
- ✅ `PasswordResetConfirmModel` - Pydantic model (already defined)

**New imports required:**
- ✅ `from passlib.context import CryptContext` - bcrypt hashing
- ✅ `import re` - password regex validation

---

## Security Checklist

- ✅ One-time token use enforced (OWASP compliant)
- ✅ Token validation (signature, expiration, existence)
- ✅ Strong password hashing (bcrypt vs MD5) - OWASP compliant
- ✅ Password complexity enforced - OWASP compliant
- ✅ Generic error messages (no information disclosure)
- ✅ Audit logging for all security events
- ✅ Token invalidated immediately after use
- ✅ No plaintext passwords logged

---

## Migration Notes

**⚠️ Breaking Change: MD5 → bcrypt**

This change affects the entire password storage system. After implementation:
- New passwords (register & reset) use bcrypt
- Existing MD5 hashes won't validate with new code
- For the exercise, re-register test users or handle migration in login

**Suggested approach for exercise:**
Update the `if __name__ == "__main__"` section to re-create users with bcrypt hashes.

---

## Definition of Done

- [ ] Endpoint accepts POST requests at `/reset-password/confirm`
- [ ] Token validation works (signature, expiration, one-time use)
- [ ] Password complexity validation enforces OWASP requirements
- [ ] `hash_password()` refactored to use bcrypt
- [ ] Login endpoint updated to verify bcrypt hashes
- [ ] Token invalidated after successful reset
- [ ] Appropriate error messages for all failure cases
- [ ] Logging captures all security events
- [ ] Manual testing shows all acceptance criteria pass
- [ ] User can successfully log in with new password

---

**Previous Story:** PWR-002 - Password Reset Request Endpoint  
**Implementation:** Ready for development with all 3 stories complete
