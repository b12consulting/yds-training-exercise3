# Story 02: Password Reset Request Endpoint

**Epic:** Password Reset Feature (OWASP-compliant)  
**Story ID:** PWR-002  
**Priority:** High  
**Estimated Complexity:** Medium-High

---

## User Story

**As a** registered user who has forgotten my password,  
**I want to** request a password reset by providing my email address,  
**So that** I receive a secure reset link and can regain access to my account.

---

## Context

This story implements the `/reset-password/request` endpoint which generates reset tokens and sends them via email. Critical security features include rate limiting to prevent abuse and generic responses to prevent email enumeration.

**Files to modify:**
- `src/app_3.py` - implement `request_password_reset()` endpoint function

**Dependencies:**
- Story PWR-001 must be complete (`create_reset_token` available)
- Existing utilities: `db`, `send_reset_email`, `logger` from `helpers.py`

**Architecture Reference:**
- See `_bmad-output/planning-artifacts/architecture.md` 
- OWASP requirement: Rate limiting (3 requests/email/hour)
- OWASP requirement: Generic responses (anti-enumeration)

---

## Acceptance Criteria

### AC-01: Basic Endpoint Functionality

**Given** a user submits a password reset request,  
**When** `POST /reset-password/request` is called with `{"email": "user@example.com"}`,  
**Then** it should:
- ✅ Accept a `PasswordResetRequestModel` (already defined)
- ✅ Return HTTP 200 with a generic message: `{"message": "If your email is registered, you will receive a password reset link shortly."}`
- ✅ Return the SAME response regardless of whether email exists in database

**Generic response requirement:**
```python
# ALWAYS return this, whether email exists or not
return {"message": "If your email is registered, you will receive a password reset link shortly."}
```

### AC-02: Happy Path - Email Exists

**Given** the email exists in the database,  
**When** the request is processed,  
**Then** it should:
- ✅ Check if user exists: `user = db.get(request.email)`
- ✅ Generate reset token: `token = create_reset_token(request.email)`
- ✅ Store token in user document: `user["reset_token"] = token`
- ✅ Update database: `db.set(request.email, user)`
- ✅ Send email: `send_reset_email(request.email, token)`
- ✅ Log the action: `logger.info(f"Password reset requested for {request.email}")`

### AC-03: Email Not Found Path

**Given** the email does NOT exist in the database,  
**When** the request is processed,  
**Then** it should:
- ✅ Return the same generic success message (no indication email doesn't exist)
- ✅ Log the attempt: `logger.warning(f"Password reset requested for non-existent email: {request.email}")`
- ✅ NOT send an email
- ✅ NOT generate a token

### AC-04: Rate Limiting (OWASP Critical)

**Given** rate limiting is in effect,  
**When** a user makes multiple reset requests,  
**Then** it should:
- ✅ Track reset attempts per email in memory
- ✅ Allow maximum 3 requests per email per hour
- ✅ On 4th+ request within 1 hour, return HTTP 429 with message: `{"detail": "Too many password reset requests. Please try again later."}`
- ✅ Clean up old timestamps to prevent memory growth

**Implementation hints:**

```python
from datetime import datetime, timedelta
from fastapi import HTTPException

# Add at module level (after imports)
_reset_attempts: dict[str, list[datetime]] = {}

def check_rate_limit(email: str) -> None:
    """Check if email has exceeded rate limit (3 requests/hour)."""
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    
    # Get existing attempts for this email
    if email not in _reset_attempts:
        _reset_attempts[email] = []
    
    # Remove attempts older than 1 hour
    _reset_attempts[email] = [
        timestamp for timestamp in _reset_attempts[email]
        if timestamp > one_hour_ago
    ]
    
    # Check limit
    if len(_reset_attempts[email]) >= 3:
        logger.warning(f"Rate limit exceeded for {email}")
        raise HTTPException(
            status_code=429,
            detail="Too many password reset requests. Please try again later."
        )
    
    # Record this attempt
    _reset_attempts[email].append(now)

# In the endpoint:
@app.post("/reset-password/request")
def request_password_reset(request: PasswordResetRequestModel):
    # Check rate limit FIRST (before any DB operations)
    check_rate_limit(request.email)
    
    # ... rest of implementation
```

### AC-05: Logging & Audit Trail

- ✅ Log successful requests: `logger.info(f"Password reset requested for {email}")`
- ✅ Log failed requests (email not found): `logger.warning(f"Password reset requested for non-existent email: {email}")`
- ✅ Log rate limit violations: `logger.warning(f"Rate limit exceeded for {email}")`
- ✅ Do NOT log tokens in plain text

### AC-06: Security Requirements

- ✅ Generic response prevents email enumeration
- ✅ Rate limiting prevents brute force and DoS
- ✅ No timing differences between "email exists" and "email not found" paths
- ✅ Token stored in user document for later validation (Story 03)
- ✅ Email validation handled by Pydantic model (already configured)

---

## Implementation Flow

```
1. Request arrives: POST /reset-password/request {"email": "..."}
2. Check rate limit (raise 429 if exceeded)
3. Check if email exists in DB
4. IF exists:
   a. Generate token
   b. Store token in user doc
   c. Send email with token
   d. Log success
5. IF not exists:
   a. Log warning (non-existent email)
   b. Do nothing else (no email, no token)
6. Return generic success message (ALWAYS)
```

---

## Testing Guidance

**Manual testing scenarios:**

1. **Happy path:**
   ```bash
   POST http://localhost:2626/reset-password/request
   {"email": "alice@example.com"}
   
   Expected: 200 OK, generic message, email printed to console
   ```

2. **Non-existent email:**
   ```bash
   POST http://localhost:2626/reset-password/request
   {"email": "unknown@example.com"}
   
   Expected: 200 OK, SAME generic message, NO email printed
   ```

3. **Rate limiting:**
   ```bash
   # Send 4 requests in rapid succession
   POST /reset-password/request {"email": "alice@example.com"}
   POST /reset-password/request {"email": "alice@example.com"}
   POST /reset-password/request {"email": "alice@example.com"}
   POST /reset-password/request {"email": "alice@example.com"}
   
   Expected: First 3 succeed (200), 4th returns 429 Too Many Requests
   ```

4. **Rate limit expiry:**
   - Wait 61 minutes between requests
   - Verify counter resets

---

## Dependencies

**Required from Story PWR-001:**
- ✅ `create_reset_token(email)` function

**Existing utilities:**
- ✅ `db` - DocumentStore instance
- ✅ `send_reset_email(address, token)` - email mock
- ✅ `logger` - logging instance
- ✅ `PasswordResetRequestModel` - Pydantic model (already defined)

**New module-level storage:**
- ✅ `_reset_attempts: dict[str, list[datetime]]` - rate limiting tracker

---

## Security Checklist

- ✅ Generic responses (no email enumeration)
- ✅ Rate limiting (3 requests/email/hour) - OWASP compliant
- ✅ Audit logging for security monitoring
- ✅ No timing attacks (constant response time regardless of email existence)
- ✅ Token stored securely in database
- ✅ No sensitive data in error messages

---

## Definition of Done

- [ ] Endpoint accepts POST requests at `/reset-password/request`
- [ ] Generic message returned in all cases
- [ ] Token generated and stored for existing emails
- [ ] Email sent for existing emails only
- [ ] Rate limiting works (3 requests/hour max)
- [ ] Rate limit returns HTTP 429 when exceeded
- [ ] Logging captures all relevant security events
- [ ] No email enumeration possible
- [ ] Manual testing shows all acceptance criteria pass

---

**Previous Story:** PWR-001 - Token Lifecycle Management  
**Next Story:** PWR-003 - Password Reset Confirmation Endpoint
