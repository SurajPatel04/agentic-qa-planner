---
id: authentication
title: Authentication and Authorization Testing Standards
domain: auth
applies_to: [unit, api, integration, e2e, manual]
tags: [login, session, token, rbac, permissions, mfa, password-reset, logout]
version: 1.0
---

# Authentication and Authorization Testing Standards

## Scope

Applies to any change touching login, logout, sessions, tokens, password handling, multi-factor
authentication, role or permission checks, ownership rules, impersonation, or API keys. Use this
document to derive **permission cases** and **identity-related edge cases**. Injection, transport,
and data-exposure concerns live in `security.md`.

## Vocabulary

- **Authentication** — proving *who* the caller is. Failure returns `401`.
- **Authorization** — deciding *what* that caller may do. Failure returns `403`.

Confusing the two is itself a defect class, so test them separately.

## How to use these rules

Each rule has a stable ID (`AUTH-###`). Cite the ID on every derived test case. When the change
summary does not state the role model, the session lifetime, or the token type, apply the rule's
**Default assumption** and mark the case as an assumption needing confirmation.

---

## AUTH-001 — Every protected route rejects anonymous access

**Test levels:** api, integration
**Rule:** For each protected endpoint or page, test with no credentials at all and assert `401`
(API) or a redirect to login (UI). This case is required even when the UI hides the entry point.
**Why it matters:** Hiding a button is not access control. Direct URL or API access is trivial and
is the first thing an attacker tries.
**How to test:** Call the endpoint with no `Authorization` header and no session cookie. Assert the
status, and assert no part of the protected payload appears in the response body.

## AUTH-002 — Invalid, expired, malformed, and tampered credentials are rejected

**Test levels:** unit, api
**Rule:** Cover as separate cases: a well-formed but unknown token, an expired token, a
structurally malformed token, a token with a modified payload but the original signature, a token
signed with the wrong key, and a token declaring an unexpected algorithm (including `none`).
**Why it matters:** Signature-verification and algorithm-confusion bugs grant full account takeover
and are invisible to happy-path tests.
**How to test:** Assert `401` for every variant, and assert the error does **not** reveal which
check failed.

## AUTH-003 — Login failure messages do not enumerate accounts

**Test levels:** api, e2e, manual
**Rule:** A wrong password and an unknown username produce an identical message, an identical
status code, and comparable response timing.
**Why it matters:** Differing responses let an attacker build a list of valid accounts before
attempting credential stuffing.
**How to test:** Compare the two responses field by field. Include a manual check that the UI copy
is identical too.

## AUTH-004 — Brute-force and credential-stuffing protection

**Test levels:** api, integration
**Rule:** Test repeated failed logins for one account and from one source. Assert the documented
control (lockout, exponential backoff, CAPTCHA, or rate limit) engages, and assert that a
successful login after the cooldown, or a correct password, resets the counter as documented.
**Default assumption:** If no threshold is specified, propose the case with a placeholder
threshold, mark it as an assumption, and flag the missing policy as a gap.

## AUTH-005 — The role and permission matrix is tested exhaustively per endpoint

**Test levels:** api, integration
**Rule:** Build a matrix of every role against every action the change touches. Each cell needs a
test: allowed roles succeed, every other role receives `403`. Do not test only the happy role.
**Why it matters:** Permission bugs are asymmetric — a missing "deny" case ships a privilege
escalation, while a missing "allow" case only causes a support ticket.
**How to test:** Parameterise one test over the role list so that adding a role forces a decision
rather than silently defaulting to allowed.
**Default assumption:** If the role list is not given, derive roles from the change summary,
enumerate them explicitly in the plan, and mark the matrix as an assumption.

## AUTH-006 — Ownership checks are enforced independently of role

**Test levels:** api, integration
**Rule:** A user with the correct role must still be blocked from another user's records. Test
role-correct + owner-wrong for every read, update, and delete.
**Why it matters:** Role checks alone permit horizontal privilege escalation — any customer can
read any other customer's data by changing an ID.
**How to test:** Authenticate as user A, target user B's resource ID, and assert `403` (or `404` if
the spec deliberately hides existence — state which policy applies and why).

## AUTH-007 — Privilege changes take effect on the existing session

**Test levels:** integration, e2e
**Rule:** After a role is revoked or downgraded, or the account is disabled, test that an already
issued token or active session can no longer perform the removed action.
**Why it matters:** Long-lived tokens carrying stale claims keep granting access after an
offboarding, which is a routine audit finding.
**How to test:** Authenticate, revoke the privilege out of band, then reuse the same token. Assert
denial within the documented propagation window.

## AUTH-008 — Session lifecycle: expiry, refresh, and renewal

**Test levels:** integration, e2e
**Rule:** Cover session expiry at the boundary, idle timeout versus absolute timeout, refresh with
a valid refresh token, refresh with an expired or already-used refresh token, and refresh-token
rotation with reuse detection.
**Default assumption:** If lifetimes are unspecified, assume a short-lived access token with a
longer-lived rotating refresh token, mark it as an assumption, and flag the missing policy.

## AUTH-009 — Logout fully terminates access

**Test levels:** integration, e2e
**Rule:** After logout, test that the previous token or cookie is rejected, that the back button
does not restore protected content from cache, and that "log out everywhere" invalidates other
active sessions.
**Why it matters:** A logout that only clears client state leaves a valid credential in
circulation, which matters most on shared devices.

## AUTH-010 — Password reset is single-use, expiring, and scoped

**Test levels:** api, integration, e2e
**Rule:** Cover: a reset token used twice (the second attempt fails), an expired token, a token
issued for user A used against user B, a reset request for a non-existent account (must not reveal
existence), concurrent reset requests, and invalidation of active sessions after a successful
reset.
**Why it matters:** Reset flows bypass the password check by design, so every weakness in them is
directly account-takeover-grade.

## AUTH-011 — Password and credential policy enforcement

**Test levels:** unit, api
**Rule:** Test minimum and maximum length at the boundary, unicode and emoji passwords, leading and
trailing whitespace handling, and rejection of the current password on change. Assert the password
is never returned in any response and never written to logs.
**Default assumption:** If no policy is stated, assume a minimum length of 8 with no composition
rules, and mark it as an assumption.

## AUTH-012 — Multi-factor authentication cannot be skipped

**Test levels:** integration, e2e
**Rule:** Test that the post-password, pre-MFA state grants no access to protected resources; that
a wrong code, an expired code, a reused code, and a code belonging to another user's factor all
fail; and that the MFA step limits attempts.
**Why it matters:** Partially authenticated sessions that already carry privileges are a common and
severe implementation slip.

## AUTH-013 — Cross-site request forgery protection on state-changing requests

**Test levels:** api, e2e
**Rule:** For cookie-authenticated state-changing endpoints, test the request with a missing CSRF
token, with a token from another session, and with a valid token. Assert only the last succeeds.
**Note:** If the API is header-token only and does not accept cookies, record that as the reason
CSRF cases are not applicable rather than omitting the topic silently.

## AUTH-014 — Third-party and SSO login edge cases

**Test levels:** integration, e2e, manual
**Rule:** Where SSO or social login exists, cover: the provider returns an error, the user cancels
at the provider, the provider returns an email already registered locally, the provider returns no
email, the state parameter is missing or mismatched, and the callback is replayed with the same
authorization code.
**Why it matters:** Account linking on an unverified email is a well-known account-takeover path.

## AUTH-015 — Service accounts, API keys, and impersonation are bounded

**Test levels:** api, integration
**Rule:** Test that a machine credential is limited to its documented scopes, that a revoked key
stops working immediately, and that any admin impersonation is audit-logged, time-bounded, and
blocked from privilege-escalating actions.

---

## Permission-case checklist

For each endpoint or UI action the change touches, the plan should contain a case for every row.
Missing rows are uncovered permission cases and must be highlighted.

| Caller state | Expected |
|---|---|
| Anonymous | `401` or redirect to login (AUTH-001) |
| Authenticated, wrong role | `403` (AUTH-005) |
| Authenticated, right role, not owner | `403`, or a documented `404` (AUTH-006) |
| Authenticated, right role, owner | Success |
| Expired or tampered credential | `401` (AUTH-002) |
| Privilege revoked mid-session | Denied (AUTH-007) |
| After logout | Denied (AUTH-009) |
