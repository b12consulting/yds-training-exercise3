# AI in SSDLC: Hands-On Exercise

## What this exercise is about

You will implement the same feature twice — a password reset API — using an AI coding tool both times. The difference is *how* you engage with the AI before writing any code.

The goal is not a finished, production-ready implementation. The goal is to **feel the difference** between prompting instinctively and prompting deliberately, and to see what each approach misses on a security-sensitive feature.

---

## Setup

**Python version:** 3.11+

**Install dependencies:**
```bash
pip install fastapi uvicorn python-jose[cryptography] passlib
```

**Run the app.** This is an optional step, not needed for the scope of this exercise; the focus is on the implementation journey, not the final product.
```bash
uvicorn app:app --reload
```

The Swagger UI is available at `http://localhost:2626/docs` once the server is running.

## Files

| File | Description |
|------|-------------|
| `requirements.md` | Feature requirements: **read this before starting**. |
| `helpers.py` | Shared utilities: DB mock, email mock, JWT helpers, logger. **Do not modify.** |
| `app.py` | Starting point for **Round 1**. |
| `app_2.py` | Starting point for **Round 2**. Identical copy, fresh start. |

`/register` and `/login` are already implemented in both files. Do not modify them.

---

## What to implement

In both rounds, you implement the same four stubs:

| Stub | Description |
|------|-------------|
| `create_reset_token(email)` | Creates a signed JWT encoding the email address |
| `decode_reset_token(token)` | Decodes and validates a JWT, returns the email |
| `POST /reset-password/request` | Accepts `{ "email": "..." }`, generates a token, calls `send_reset_email`, returns a generic confirmation |
| `POST /reset-password/confirm` | Accepts `{ "token": "...", "new_password": "..." }`, validates the token, updates the password in the DB |

The document [`requirements.md`](requirements.md) contains the full feature requirements as user stories. Read it carefully before starting.

`helpers.py` provides everything you need: `db` (an in-memory document store pre-seeded with two users), `send_reset_email(address, token)` (prints to stdout), and `logger`.

---

## Round 1 — Vibe Coding (15 min)

**File:** `app.py`

Open [`requirements.md`](requirements.md), read it once, then start implementing using your AI tool, however you like. No rules, no structure. Just get it working.

When you are done, leave the code as-is. Do not tidy it up.

**Reflect before moving on:** 
- what security issues does your implementation handle?
- before jumping to the implementation, did you take the time to identify potential vulnerabilities?

---

## Round 2 — Spec-Driven (20 min)

**File:** `app_2.py`

**Before writing a single line of code**, open a conversation with your AI agent. Ask it to review [`requirements.md`](requirements.md) from a security perspective and identify what is missing.

There is no prompt template provided. Writing the prompt is part of the exercise; in the real world, thinking spec-first also means knowing what to ask. However, AI agents can help you refine your prompts if needed.

Once the agent has surfaced its findings, use that enriched understanding of the requirements to guide your implementation.

**After implementing, compare:**
- What did the agent flag that you had not thought of in Round 1?
- What did the agent miss?
- How different are [`app.py`](app.py) and [`app_2.py`](app_2.py)?
- Could the initial prompt "ask the agent to review the spec before coding" become a standard step on your projects?

---

---

## Round 3 — Using BMad (30 min)

**File:** `app_3.py`

**Workflow:**

1. **Create simplified architecture with Winston** (the architect agent)
   - Winston analyzes the repo, README, and requirements
   - Produces a lightweight architecture spec focused on security patterns and API design

2. **Ask Winston to create 3 stories for development**
   - Outside the formal BMad workflow, but informed by the architecture
   - Stories focus on: token generation, token validation, and password reset endpoints

3. **Have Bob (Scrum Master) manage the planning**
   - Bob takes the stories and creates a sprint plan
   - Ensures all stories are properly sequenced and actionable before dev starts
   - Use Bob's `[SP] Sprint Planning` capability

4. **Use the `/custom-dev-story-pipeline` skill/workflow** (to be created)
   - Launches Amelia (dev agent) to implement each story
   - Launches Rex (review agent) to perform code review after implementation
   - Runs in sequence: dev → review → dev → review → dev → review

**Goal:** Experience a multi-agent workflow where architecture → stories → implementation → review happens in an orchestrated pipeline, with each specialist agent handling their domain.

**After completing, compare:**
- How did having architecture-first change the implementation approach?
- What did the review agent (Rex) catch that you might have missed?
- Is the orchestrated pipeline worth the setup overhead for security-sensitive features?

---

## Rules

- Do not modify [`helpers.py`](helpers.py) or [`requirements.md`](requirements.md).
- Do not look at each other's Round 2 prompts before writing your own.
