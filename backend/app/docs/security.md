---
id: security
title: Security Testing Standards
domain: security
applies_to: [unit, api, integration, e2e, manual]
tags: [owasp, injection, xss, idor, secrets, upload, ssrf, logging, privacy]
version: 1.0
---

# Security Testing Standards

## Scope

Applies to any change that accepts untrusted input, renders user-controlled content, stores or
returns personal data, uploads or downloads files, calls an outbound URL, or writes logs. Use this
document to derive **abuse cases** and **failure states**. Identity, session, and role rules live
in `authentication.md`.

## Framing

Security tests assert that a documented control **holds** under hostile input. A test that finds no
issue is evidence about that one control, not a statement that the feature is secure. Never
conclude "secure" or "release-ready" from a passing security test — report what was covered and
what was not.

## How to use these rules

Each rule has a stable ID (`SEC-###`). Cite the ID on each derived case. If the change summary does
not describe the trust boundary, state the boundary you assumed and mark the derived cases as
assumptions.

---

## SEC-001 — All input is untrusted, including input from your own clients

**Test levels:** api, integration
**Rule:** Every validation rule enforced in the UI is re-tested directly against the API with the
UI bypassed — oversized values, disallowed enum values, negative numbers, wrong types, and
read-only fields supplied by the caller.
**Why it matters:** Client-side validation is a usability feature, never a control. Anyone can call
the API with curl.
**How to test:** Take each UI-side rule and issue the equivalent violating request straight to the
endpoint. Assert rejection at the server, not merely at the form.

## SEC-002 — Insecure direct object reference (IDOR) probing

**Test levels:** api, integration
**Rule:** For every endpoint accepting an identifier, test another user's ID, another tenant's ID,
a deleted record's ID, a non-existent ID, and an ID of the wrong resource type.
**Why it matters:** Object-level authorization is the most frequently missed control, and a single
missed check exposes the entire dataset by iteration.
**How to test:** Authenticate as a low-privilege user and enumerate. Assert denial and assert that
the response does not disclose whether the record exists when existence itself is sensitive.

## SEC-003 — Mass assignment and over-posting

**Test levels:** api
**Rule:** Send extra fields the caller should not control — `role`, `is_admin`, `owner_id`,
`status`, `price`, `created_at`, `id` — on create and update requests.
**Why it matters:** Frameworks that bind the whole request body to a model turn any update endpoint
into a privilege-escalation endpoint.
**How to test:** Submit the field, then read the record back and assert the protected attribute is
unchanged. Asserting only on the response body is not sufficient.

## SEC-004 — Injection through every input channel

**Test levels:** unit, api, integration
**Rule:** For inputs reaching a query, a shell, a template, an LDAP or LDAP-like directory, or a
serialiser, test payloads containing quotes, semicolons, comment markers, null bytes, and
templating delimiters. Cover headers, query parameters, path segments, JSON bodies, and file
contents — not just form fields.
**Why it matters:** Injection remains one of the highest-impact vulnerability classes, and inputs
that reach a query indirectly (sort field, filter name, filename) are routinely missed.
**How to test:** Assert the payload is stored or rejected verbatim as data, that no error reveals a
query or driver detail, and that the underlying store is unchanged.

## SEC-005 — Output encoding and cross-site scripting

**Test levels:** unit, e2e, manual
**Rule:** For every field rendered back to a user, store a script payload and assert it renders as
inert text. Cover reflected (echoed in a response), stored (persisted then rendered elsewhere), and
DOM-based (written into the page by client code) variants.
**Why it matters:** Stored XSS escalates from one attacker's input to every viewer's session,
including administrators.
**How to test:** Include admin-facing and export views in the check — content is often escaped in
the main UI and rendered raw in reports, emails, or CSV exports.

## SEC-006 — File upload handling

**Test levels:** api, integration, e2e
**Rule:** Cover: a disallowed extension, a permitted extension with mismatched real content, a
double extension, an oversized file, a zero-byte file, an executable or archive, a path-traversal
filename (`../../etc/passwd`), a unicode or very long filename, and a malformed image.
**Why it matters:** Upload endpoints combine untrusted content with filesystem writes and later
retrieval, giving them an unusually large blast radius.
**How to test:** Assert type is determined by content and not by extension, that the stored path
cannot escape the upload directory, and that retrieval serves a safe `Content-Type` with
`Content-Disposition` where relevant.

## SEC-007 — Server-side request forgery on outbound URLs

**Test levels:** api, integration
**Rule:** Where a user supplies a URL (webhooks, imports, avatar-by-URL, link previews), test
loopback addresses, private ranges, cloud metadata endpoints, non-HTTP schemes (`file://`,
`gopher://`), redirects to an internal address, and DNS names resolving to internal addresses.
**Why it matters:** A single unvalidated fetch can expose internal services and cloud credentials.

## SEC-008 — Secrets never appear in responses, logs, URLs, or errors

**Test levels:** unit, integration, manual
**Rule:** Assert that passwords, tokens, API keys, full card numbers, and government identifiers do
not appear in response bodies, log output, query strings, error messages, or analytics events.
**Why it matters:** Logs are widely readable and long-lived; a secret in a log is a secret leaked to
everyone with dashboard access.
**How to test:** Capture logs during a happy path and during a failure path, then assert the
sensitive value is absent or masked. Include the failure path explicitly — exception handlers are
where redaction is usually forgotten.

## SEC-009 — Errors fail closed

**Test levels:** unit, integration
**Rule:** When an authorization check, a policy lookup, or a token verification throws or times
out, the request must be denied rather than allowed.
**Why it matters:** Fail-open error handling converts an availability blip into an open door.
**How to test:** Fault-inject the check itself and assert `401` or `403`, never a success or an
unauthenticated fallback path.

## SEC-010 — Sensitive actions are audit-logged

**Test levels:** integration
**Rule:** Permission changes, data exports, deletions, impersonation, and credential changes emit
an audit record containing actor, target, action, timestamp, and outcome — for failed attempts as
well as successful ones.
**Why it matters:** Without failed-attempt logging, an attack in progress is indistinguishable from
normal traffic.

## SEC-011 — Transport and browser security headers

**Test levels:** api, e2e
**Rule:** Assert HTTPS enforcement and redirect from HTTP, presence of HSTS, `X-Content-Type-
Options`, a frame-ancestors or `X-Frame-Options` policy, and a Content-Security-Policy. For
cookies, assert `Secure`, `HttpOnly`, and an appropriate `SameSite`.
**Why it matters:** These are cheap, high-value controls that silently disappear during proxy,
framework, or infrastructure changes.

## SEC-012 — Cross-origin policy is explicit and narrow

**Test levels:** api
**Rule:** Test a request from a disallowed origin and assert it is not granted access. Assert the
service never reflects an arbitrary `Origin` while also allowing credentials.
**Why it matters:** A wildcard-plus-credentials CORS configuration makes every authenticated
endpoint readable by any site the user visits.

## SEC-013 — Personal data handling and retention

**Test levels:** integration, manual
**Rule:** Where the change touches personal data, test that only the fields required by the use
case are returned, that deletion or anonymisation requests take effect across primary storage,
caches, exports, and backups as documented, and that data is not copied into non-production
environments unmasked.
**Default assumption:** If retention or deletion behaviour is unspecified, propose the case, mark
it as an assumption, and flag the missing policy.

## SEC-014 — Denial-of-service resistance on expensive operations

**Test levels:** api, integration
**Rule:** For endpoints performing search, export, report generation, regex matching on user input,
or archive expansion, test a deliberately expensive input and assert bounded time, bounded memory,
and a documented limit or rejection.
**Why it matters:** One unbounded query from a single caller can exhaust a shared resource pool and
take down unrelated features.

## SEC-015 — Dependency and configuration drift

**Test levels:** integration, manual
**Rule:** Where the change adds or upgrades a dependency, or alters configuration, verify that
debug modes are off in production configuration, that default credentials do not exist, that
directory listing is disabled, and that the new dependency has no known critical advisory.

---

## Abuse-case checklist

Derive at least one case per applicable row; mark rows that do not apply, with the reason.

| Vector | Applies when | Rule |
|---|---|---|
| Bypass client validation | Any form or API input | SEC-001 |
| Another user's ID | Any identifier parameter | SEC-002 |
| Extra privileged fields | Any create or update body | SEC-003 |
| Injection payloads | Input reaching a query, shell, or template | SEC-004 |
| Script payload rendered | Any user-supplied text shown to anyone | SEC-005 |
| Hostile file | Any upload | SEC-006 |
| Internal URL | Any user-supplied URL fetched by the server | SEC-007 |
| Secret in log or response | Any credential or personal data | SEC-008 |
| Check throws | Any authorization dependency | SEC-009 |
| Expensive input | Search, export, or report | SEC-014 |
