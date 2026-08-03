---
id: api-testing
title: API Testing Standards
domain: api
applies_to: [unit, api, integration, e2e]
tags: [rest, http, contract, validation, pagination, idempotency, errors]
version: 1.0
---

# API Testing Standards

## Scope

Applies to any change that adds, modifies, or removes an HTTP endpoint, a request or response
schema, a status code, a query parameter, or a service-to-service call. Use this document to
derive **API-level** and **integration-level** test cases. UI-visible behaviour is covered in
`ui_testing.md`; access control is covered in `authentication.md`.

## How to use these rules

Each rule has a stable ID (`API-###`). Every proposed test case should cite the rule ID it is
derived from. If the requirement or change summary does not state the behaviour a rule needs (for
example, no page size limit is given), apply the rule's **Default assumption** and mark the
resulting test case as an assumption rather than silently guessing.

---

## API-001 — Every endpoint has a documented happy path

**Test levels:** api, integration
**Rule:** Each endpoint needs at least one test that exercises the primary success path with a
fully valid, minimal request and asserts the status code, the response body shape, and the
persisted side effect if any.
**Why it matters:** The happy path is the contract the caller depends on. Without it, a refactor
can change the response shape and only be caught in production.
**How to test:** Send the minimal valid request. Assert (a) the status code, (b) every field a
consumer reads, (c) the resulting state via a follow-up read or a direct data assertion.
**Default assumption:** If the success status code is not stated, assume `200` for reads and
updates, `201` for resource creation, and `204` for deletions.

## API-002 — Request validation is tested per field, not per endpoint

**Test levels:** unit, api
**Rule:** For each input field, cover: missing when required, present when optional, wrong type,
out-of-range value, and empty string versus `null`. These are separate cases, not one combined
case.
**Why it matters:** Bundled validation tests hide which field failed and can pass for the wrong
reason once one field short-circuits validation.
**How to test:** One test per field per violation class. Assert the error status **and** that the
error body names the offending field.
**Default assumption:** If no validation rules are given for a field, assume required fields
reject `null`, empty string, and whitespace-only values, and mark the case as an assumption.

## API-003 — Error responses use a consistent, machine-readable shape

**Test levels:** api, integration
**Rule:** All 4xx and 5xx responses return the same envelope — a stable error code, a human
message, and an optional field-level detail list. Tests assert the error **code**, not the message
string.
**Why it matters:** Clients branch on codes. Asserting on prose makes tests brittle and lets a
code change ship unnoticed.
**How to test:** Trigger each documented failure and assert the code, the HTTP status, and that no
internal detail (stack trace, SQL, hostname, driver error) leaks into the body.

## API-004 — Correct status codes for each failure class

**Test levels:** api
**Rule:** Distinguish `400` (malformed or invalid input), `401` (missing or invalid credentials),
`403` (authenticated but not permitted), `404` (absent or not visible to the caller), `409` (state
conflict or duplicate), `422` (well-formed but semantically invalid), `429` (rate limited).
**Why it matters:** Collapsing these into one code breaks client retry logic and disguises
authorization bugs as "not found" bugs.
**How to test:** One case per class the endpoint can actually produce. Explicitly test that an
authenticated-but-unauthorized caller receives `403` and not `404`, unless the spec deliberately
hides existence — see `authentication.md` (AUTH-006).

## API-005 — Boundary values on every numeric, string, and collection input

**Test levels:** unit, api
**Rule:** Test min, min−1, max, max+1, and zero or empty for each bounded input, including string
length, array length, numeric range, and date range.
**Why it matters:** Off-by-one errors concentrate at boundaries and rarely surface in typical
values.
**Default assumption:** If no bound is specified, assume the field is unbounded, propose one
oversized-input case (very long string, very large array) as an assumption, and flag that the
limit needs confirmation.

## API-006 — Pagination, sorting, and filtering are tested together

**Test levels:** api, integration
**Rule:** For list endpoints cover: first page, middle page, last page, a page beyond the end
(empty result, not an error), page size at the maximum, page size above the maximum, an invalid
cursor or offset, the default sort order, each supported sort field, and a combined
filter + sort + page request.
**Why it matters:** Pagination bugs — rows skipped or duplicated at page edges — are invisible in
small datasets and appear only once real data volume arrives.
**How to test:** Seed more records than one page holds. Assert the union of all pages equals the
full set with no duplicates and no gaps, and that total counts stay consistent.
**Default assumption:** If no default page size is given, assume 20 and mark it as an assumption.

## API-007 — Write endpoints are tested for idempotency and duplicate submission

**Test levels:** api, integration
**Rule:** Send the same create or update request twice. `PUT` and `DELETE` must be idempotent.
`POST` must either deduplicate via an idempotency key or produce a documented conflict.
**Why it matters:** Client retries, double-clicks, and at-least-once queues make duplicate
delivery normal rather than exceptional.
**How to test:** Repeat the request with an identical payload and identical idempotency key;
assert one resource exists. Repeat with a different key and assert the documented behaviour.

## API-008 — Concurrency and lost-update protection

**Test levels:** integration
**Rule:** When two callers can modify the same resource, test simultaneous updates and assert the
documented outcome: optimistic-locking rejection (`409` or `412`), last-write-wins, or merge.
**Why it matters:** Read-modify-write without a version check silently discards one user's change.
**How to test:** Read a resource twice, update through the first copy, then update through the
stale copy and assert the stale write is rejected or resolved as documented.
**Default assumption:** If concurrency behaviour is unspecified, propose an optimistic-locking
test and mark it as an assumption requiring product confirmation.

## API-009 — Contract stability for existing consumers

**Test levels:** api, integration
**Rule:** A change to an existing endpoint needs a test proving that previously valid requests
still succeed and that no response field consumers rely on has been removed, renamed, or retyped.
**Why it matters:** Additive changes are safe; removals and renames are breaking and are the most
common cause of cross-service incidents.
**How to test:** Assert the old response shape explicitly. New fields are permitted; missing or
retyped fields must fail. See also `regression.md` (REG-004).

## API-010 — Dependency failure and timeout handling

**Test levels:** integration
**Rule:** For each downstream dependency (database, cache, queue, third-party API) test: timeout,
connection refused, a 5xx from the dependency, a malformed response, and a slow-but-successful
response.
**Why it matters:** Unhandled dependency failure turns a degraded feature into a full outage or,
worse, into silent data loss.
**How to test:** Stub or fault-inject the dependency. Assert the endpoint returns a controlled
error rather than a stack trace, does not partially commit, and does not retry unbounded.

## API-011 — Partial failure leaves no half-written state

**Test levels:** integration
**Rule:** For any operation writing to more than one place (two tables, a table plus a queue, a
table plus an external call), test a failure after the first write and assert the system converges
to a consistent state via transaction, compensation, or outbox.
**Why it matters:** Half-completed writes are the hardest class of production bug to detect and
the most expensive to repair.

## API-012 — Rate limiting and payload size limits

**Test levels:** api
**Rule:** Where limits exist, test just under the limit (allowed), just over (`429` or `413`), and
recovery after the window elapses. Assert limits are enforced at the documented scope — per user,
per IP, or per API key.
**Default assumption:** If limits are not mentioned, record their absence as a risk rather than
inventing thresholds.

## API-013 — Content negotiation and malformed payloads

**Test levels:** api
**Rule:** Test an unsupported `Content-Type`, a missing `Content-Type`, malformed JSON, an empty
body on a body-required endpoint, and unexpected extra fields.
**Why it matters:** Parser-level failures often bypass validation and surface as `500`s.
**How to test:** Assert `415` for unsupported media type and `400` for malformed JSON — never a
`500`. Assert the documented policy for unknown fields (reject or ignore) rather than assuming it.

## API-014 — Data isolation between tenants and users

**Test levels:** api, integration
**Rule:** For every endpoint returning or mutating user-owned data, test that user A cannot read
or modify user B's record by supplying B's identifier.
**Why it matters:** This is among the most common real-world API vulnerabilities and it is
invisible to single-user testing. See `security.md` (SEC-002).

## API-015 — Test data is independent and self-cleaning

**Test levels:** unit, api, integration
**Rule:** Each test creates the data it needs and does not depend on execution order or on data
left behind by another test. Tests pass when run individually, in reverse order, and in parallel.
**Why it matters:** Order-dependent tests produce flaky failures that erode trust in the suite and
eventually get muted, hiding real regressions.

---

## Coverage checklist for an API change

Use this to detect gaps before finalising a plan. An uncovered row is a coverage gap, not a
passing result.

| Dimension | Covered when the plan includes |
|---|---|
| Happy path | API-001 case per endpoint |
| Input validation | API-002 and API-005 per field |
| Error contract | API-003, API-004 |
| List semantics | API-006 (if any list endpoint changed) |
| Retry safety | API-007 |
| Concurrency | API-008 (if the resource is shared) |
| Backward compatibility | API-009 (if the endpoint pre-existed) |
| Dependency failure | API-010, API-011 |
| Access isolation | API-014 |
