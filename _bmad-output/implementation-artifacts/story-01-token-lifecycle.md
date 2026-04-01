# Story 01: Token Lifecycle Management

**Epic:** Password Reset Feature (OWASP-compliant)  
**Story ID:** PWR-001  
**Story Key:** 1-1-token-lifecycle  
**Priority:** High (Foundation)  
**Estimated Complexity:** Medium

---

## User Story

**As a** system architect,  
**I want** secure JWT token creation and validation utilities for password reset,  
**So that** tokens are cryptographically secure, have limited lifetime, and can be validated reliably.

---

## Context

This story implements the foundational token lifecycle management for the password reset feature. These utilities will be used by the request and confirmation endpoints to ensure OWASP-compliant token handling.

**Files to modify:**
- `src/app_3.py` - implement `create_reset_token()` and `decode_reset_token()`

**Architecture Reference:**
- OWASP requirement: 15-20 minute token expiration (using 15 minutes)
- JWT signed with existing `_JWT_SECRET` and `_JWT_ALGORITHM = HS256`

---

## Acceptance Criteria

### AC-01: Token Creation (`create_reset_token`)

**Given** a valid email address,  
**When** `create_reset_token(email)` is called,  
**Then** it should:
- ✅ Return a signed JWT string
- ✅ Encode the email in the `"sub"` (subject) claim
- ✅ Include an `"exp"` (expiration) claim set to 15 minutes from now
- ✅ Include an `"iat"` (issued at) claim with current timestamp
- ✅ Use the existing `_JWT_SECRET` and `_JWT_ALGORITHM` constants
- ✅ Use `jose.jwt.encode()` from python-jose library

**Implementation hints:**
```python
from datetime import datetime, timedelta
from jose import jwt

def create_reset_token(email: str) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=15)
    payload = {
        "sub": email,
        "exp": expiration,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)
```

### AC-02: Token Validation & Decoding (`decode_reset_token`)

**Given** a JWT token string,  
**When** `decode_reset_token(token)` is called,  
**Then** it should:
- ✅ Decode the JWT using `jose.jwt.decode()` with `_JWT_SECRET` and `_JWT_ALGORITHM`
- ✅ Automatically validate the signature
- ✅ Automatically validate the expiration (`exp` claim)
- ✅ Extract and return the email from the `"sub"` claim
- ✅ Raise `ValueError` with a descriptive message if:
  - Token signature is invalid
  - Token is expired
  - Token is malformed
  - Required claims are missing

**Implementation hints:**
```python
from jose import JWTError, jwt

def decode_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise ValueError("Token missing required 'sub' claim")
        return email
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")
```

### AC-03: Security Requirements

- ✅ No email validation in these functions (handled by endpoints)
- ✅ Token expiration enforced by JWT library
- ✅ Error messages do NOT leak sensitive information (no stack traces, no internal details)
- ✅ Functions are pure utilities with no side effects (no DB access, no logging here)

### AC-04: Integration

- ✅ Functions integrate with existing JWT infrastructure (`_JWT_SECRET`, `_JWT_ALGORITHM`)
- ✅ Compatible with `create_access_token()` pattern already in the codebase
- ✅ Return types match the docstring annotations

---

## Tasks/Subtasks

### Task 1: Implement `create_reset_token()`
- [x] Import required datetime modules (`datetime`, `timedelta`)
- [x] Create payload dictionary with `sub`, `exp`, and `iat` claims
- [x] Set expiration to 15 minutes from now using `datetime.utcnow() + timedelta(minutes=15)`
- [x] Use `jwt.encode()` with existing `_JWT_SECRET` and `_JWT_ALGORITHM`
- [x] Return the encoded JWT string

### Task 2: Implement `decode_reset_token()`
- [x] Use `jwt.decode()` with `_JWT_SECRET` and `algorithms=[_JWT_ALGORITHM]`
- [x] Wrap in try-except to catch `JWTError`
- [x] Extract email from payload `sub` claim
- [x] Validate `sub` claim exists, raise `ValueError` if missing
- [x] Convert `JWTError` to `ValueError` with descriptive message
- [x] Return extracted email

### Task 3: Write comprehensive tests
- [x] Create test file `tests/test_token_lifecycle.py`
- [x] Test valid token creation returns JWT string
- [x] Test valid token decoding returns correct email
- [x] Test expired token raises `ValueError`
- [x] Test invalid signature raises `ValueError`
- [x] Test malformed token raises `ValueError`
- [x] Test missing `sub` claim raises `ValueError`
- [x] Verify error messages don't leak sensitive info

### Task 4: Validation
- [x] Run all tests and verify 100% pass
- [x] Verify integration with existing JWT constants
- [x] Confirm docstrings are accurate
- [x] Check code follows existing style in `app_3.py`

---

## Dev Notes

**Architecture Context:**
- Uses existing JWT infrastructure in `app_3.py`
- Functions are stateless utilities - no side effects
- Error handling must be security-conscious (no info leakage)

**Manual Testing Examples:**

1. **Valid token creation:**
   ```python
   token = create_reset_token("alice@example.com")
   print(token)  # Should print a JWT string
   ```

2. **Valid token decoding:**
   ```python
   email = decode_reset_token(token)
   assert email == "alice@example.com"
   ```

3. **Expired token handling:**
   - Create a token with `timedelta(minutes=-1)` (past expiration)
   - Verify `decode_reset_token()` raises `ValueError`

4. **Invalid token handling:**
   ```python
   try:
       decode_reset_token("invalid.jwt.token")
   except ValueError as e:
       print(f"Caught: {e}")  # Should catch and report error
   ```

---

## Dependencies

**Libraries:**
- `jose` (python-jose) - already imported
- `datetime` - for timestamp handling

**No external service dependencies.**

---

## Security Checklist

- ✅ Tokens expire after 15 minutes (OWASP compliant)
- ✅ Cryptographically secure signing (HS256 with 256-bit secret)
- ✅ No sensitive data in error messages
- ✅ JWT library handles signature validation
- ✅ No token usage tracking yet (handled in Story 03)

**Technical Specs:**
- Token lifetime: 15 minutes (OWASP compliant)
- Algorithm: HS256 (existing standard)
- Claims: `sub` (email), `exp` (expiration), `iat` (issued at)

**Dependencies:**
- `jose` (python-jose) - already imported in file
- `datetime` - need to add import for `datetime` and `timedelta`

**Testing Strategy:**
- Use pytest for unit tests
- Test both happy path and error conditions
- Verify token expiration enforcement
- Validate error message security

---

## Dev Agent Record

### Implementation Plan

**Approach:**
1. Add datetime imports to app_3.py
2. Implement create_reset_token() with 15-minute expiration
3. Implement decode_reset_token() with proper error handling
4. Create comprehensive test suite in tests/test_token_lifecycle.py
5. Validate all tests pass and integration works

**Red-Green-Refactor cycle:**
- Write failing tests first for each function
- Implement minimal code to pass tests
- Refactor while keeping tests green

**Starting implementation:** 2026-04-01

### Debug Log

**2026-04-01:** Implementation following red-green-refactor cycle
- Created comprehensive test suite first (14 tests total)
- Tests initially failed as expected (RED phase)
- Implemented both functions following AC specifications
- Fixed docstring formatting issue in decode_reset_token
- Fixed timezone handling in tests (utcfromtimestamp vs fromtimestamp)
- Adjusted uniqueness test to account for Unix timestamp second-precision

- `src/app_3.py` - Modified (added datetime imports, implemented create_reset_token and decode_reset_token)
- `tests/test_token_lifecycle.py` - Created (14 comprehensive tests)

**Technical decisions:**
- Used datetime.utcnow() for consistency with existing create_access_token pattern
- Error messages sanitized to prevent information leakage
- 15-minute expiration as specified in OWASP requirements

### Completion Notes

✅ **Story Complete - All ACs Satisfied**

**Implemented:**
- `create_reset_token(email)` in src/app_3.py
  - Creates JWT with sub, exp (15 min), and iat claims
  - Uses existing _JWT_SECRET and _JWT_ALGORITHM (HS256)
  
- `decode_reset_token(token)` in src/app_3.py
  - Validates JWT signature and expiration automatically
  - Extracts email from sub claim
  - Raises ValueError with safe error messages

**Tests Created:**
- tests/test_token_lifecycle.py (14 tests, 100% passing)
  - 5 tests for create_reset_token
  - 7 tests for decode_reset_token  
  - 3 integration tests
  - All error conditions covered
  - Security validation (no info leakage)

**Validation:**
- All acceptance criteria met
- Tests prove 15-minute expiration
- Error handling secure (no sensitive data in messages)
- Functions are pure utilities (no side effects)
- Integration with existing JWT infrastructure confirmed

---

## File List
<!-- Dev agent maintains list of all modified files -->

---

**2026-04-01** - Story 1-1-token-lifecycle completed
- Implemented JWT token lifecycle management functions
- Created comprehensive test suite with 14 tests (100% passing)
- Both functions follow OWASP security requirements
- Ready for code review
## Change Logreview
<!-- Dev agent logs changes with timestamps -->

---

## Status

**Current Status:** in-progress  
**Last Updated:** 2026-04-01
