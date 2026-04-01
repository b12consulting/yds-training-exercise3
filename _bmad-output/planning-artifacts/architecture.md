---
stepsCompleted: [1, 2]
inputDocuments:
  - README.md
  - requirements.md
  - src/app_3.py
  - src/helpers.py
workflowType: 'architecture'
project_name: 'YDS Training Exercise 3 - Password Reset API'
user_name: 'Yds'
date: '2026-04-01'
security_posture: 'OWASP-compliant (Option A+)'
---

# Architecture Decision Document

## Project Overview

**Project:** YDS Training Exercise 3 - Password Reset API  
**Architect:** Winston  
**Date:** April 1, 2026  
**Security Posture:** OWASP-compliant (Option A+)

This document captures architectural decisions for implementing a secure password reset feature following OWASP Forgot Password Cheat Sheet recommendations.

---

## Context

This is Round 3 of a hands-on SSDLC exercise demonstrating spec-driven development with AI agents. The goal is to implement a password reset API with proper security controls, guided by architecture-first thinking.

**Scope:**
- 4 methods to implement in `app_3.py`
- Password reset flow: request → token generation → email → confirmation → password update
- Focus: Security-first design with OWASP compliance

**Existing Infrastructure:**
- FastAPI application with `/register` and `/login` endpoints
- In-memory document store (DB mock)
- JWT authentication infrastructure
- Email sending mock
- Python 3.11+, dependencies: fastapi, uvicorn, python-jose, passlib

**Input Documents:**
1. **README.md** - Exercise structure and learning objectives
2. **requirements.md** - User stories with acceptance criteria
3. **src/app_3.py** - Code skeleton with 4 stubs to implement
4. **src/helpers.py** - Shared utilities (read-only)

---

## Security Analysis

### Requirements Coverage

The user stories (US-01, US-02, US-03) provide a baseline but omit critical OWASP requirements:

**✅ Specified:**
- Unpredictable, unique tokens
- Token-to-user association
- Password hashing
- Generic confirmation messages (anti-enumeration)

**🚨 Missing (OWASP Critical):**
1. Token expiration (TTL)
2. One-time use / invalidation
3. Rate limiting
4. Strong password hashing algorithm
5. Password complexity validation
6. Audit logging

### Threat Model

| Threat | Mitigation |
|--------|-----------|
| **Brute force token guessing** | Cryptographically secure JWT with 256-bit secret |
| **Token replay attack** | One-time use with immediate invalidation |
| **Indefinite token validity** | 15-20 minute expiration (OWASP recommendation) |
| **Email enumeration** | Generic responses regardless of email existence |
| **Request flooding / DoS** | Rate limiting: 3 requests per email per hour |
| **Weak passwords** | Complexity validation: 8+ chars, mixed case, digit |
| **Rainbow table attacks** | bcrypt hashing (replacing existing MD5) |
| **Timing attacks** | Constant-time comparisons where applicable |

### OWASP Compliance Checklist

- ✅ Cryptographically secure tokens (JWT with HS256)
- ✅ Token expiration (15-20 minutes)
- ✅ Single-use tokens
- ✅ Rate limiting (3 attempts/email/hour)
- ✅ Strong password hashing (bcrypt via passlib)
- ✅ Password complexity validation
- ✅ No user enumeration (generic messages)
- ✅ Audit logging (all reset operations)

---

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

This project implements a secure password reset flow for an existing FastAPI user management application. The core functionality spans 4 implementation artifacts:

- **FR-01**: Password reset token generation - creates cryptographically secure JWT tokens encoding user email with expiration
- **FR-02**: Token validation & decoding - validates JWT signature, expiration, and extracts user identity
- **FR-03**: Reset request endpoint - accepts email, generates token, sends reset email with generic response
- **FR-04**: Reset confirmation endpoint - validates token, enforces password policy, updates user password in database

The implementation must integrate seamlessly with existing `/register` and `/login` endpoints and utilize the provided infrastructure (DocumentStore, JWT helpers, email mock).

**Non-Functional Requirements:**

- **Security (Critical Priority)**: OWASP Forgot Password Cheat Sheet compliance
  - Cryptographically secure tokens (JWT HS256 with 256-bit secret)
  - Token expiration: 15-20 minutes (OWASP recommendation)
  - One-time use tokens with immediate invalidation
  - Rate limiting: 3 requests per email per hour
  - Strong password hashing: migrate from MD5 to bcrypt
  - Password complexity: 8+ chars, mixed case, digit required
  - Anti-enumeration: generic responses regardless of email existence
  
- **Auditability**: Comprehensive logging of all password reset operations for security monitoring

- **Maintainability**: Clear, documented code suitable for educational purposes demonstrating security-first architecture

- **Performance**: Standard REST API latency expectations (<200ms response time)

**Scale & Complexity:**

- Primary domain: **REST API Backend** (FastAPI)
- Complexity level: **Low-to-Medium**
- Estimated architectural components: **4-6 components**
  - Token lifecycle manager
  - Password validator
  - Rate limiter (in-memory)
  - Request endpoint handler
  - Confirmation endpoint handler
  - Audit logger wrapper

**Technical Challenge:** The complexity lies not in feature richness but in **disciplined application of security patterns** across the token lifecycle. Each component must enforce OWASP best practices consistently.

### Technical Constraints & Dependencies

**Existing Infrastructure (must preserve):**

- FastAPI application with JWT authentication configured
- In-memory DocumentStore pre-seeded with test users (alice@example.com, bob@example.com)
- Email mock function: `send_reset_email(address, token)` prints to stdout
- Logger instance: pre-configured for application logging
- JWT configuration: `_JWT_SECRET` and `_JWT_ALGORITHM = "HS256"` already defined

**Available Dependencies:**

- `fastapi` - REST framework
- `uvicorn` - ASGI server  
- `python-jose[cryptography]` - JWT encoding/decoding
- `passlib` - Password hashing library (bcrypt available)

**Exercise Constraints:**

- Implementation restricted to `app_3.py` only
- Cannot modify `helpers.py`, `/register`, or `/login` endpoints
- Must implement exactly 4 specified stubs (2 utility functions + 2 endpoints)

### Cross-Cutting Concerns Identified

1. **Security (Critical)**
   - Affects: Token generation, validation, password storage, endpoint responses
   - Requires: Consistent OWASP pattern application across all layers
   - Strategy: Defense-in-depth with multiple validation checkpoints

2. **Error Handling & Information Disclosure**
   - Affects: All endpoints and validation logic
   - Requires: Balance between user-facing generic messages and detailed audit logs
   - Strategy: Generic HTTP responses + comprehensive logging backend

3. **Input Validation**
   - Affects: Email format, token structure, password complexity
   - Requires: Centralized validation with clear error reporting
   - Strategy: Pydantic models + custom validators for security constraints

4. **State Management**
   - Affects: Token storage in user document, one-time use enforcement
   - Requires: Atomic operations for token invalidation
   - Strategy: Store token hash in user doc, compare on use, null on success

5. **Observability & Audit Trail**
   - Affects: All security-sensitive operations
   - Requires: Structured logging with security event classification
   - Strategy: Log all reset attempts (success/failure) with email, timestamp, outcome

6. **Rate Limiting**
   - Affects: Reset request endpoint only
   - Requires: Per-email request tracking with time-based expiry
   - Strategy: In-memory dict with email→[timestamp list] mapping, prune old entries

---

_This document builds collaboratively through step-by-step discovery. Additional sections will be appended as we work through each architectural decision together._
