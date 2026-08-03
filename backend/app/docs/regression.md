---
id: regression
title: Regression Risk and Impact Analysis Standards
domain: regression
applies_to: [unit, api, integration, e2e, playwright, manual]
tags: [regression, blast-radius, migration, feature-flag, rollback, contracts, config]
version: 1.0
---

# Regression Risk and Impact Analysis Standards

## Scope

Applies to every change, without exception. Where the other documents ask "does the new behaviour
work?", this one asks "what previously working behaviour could this break?". Use it to derive the
**likely regression areas** section of a QA plan.

## Method

Regression areas are derived from the change summary, not guessed. Work outward in three passes:

1. **Direct** — the exact functions, endpoints, components, and tables the change edits.
2. **One hop out** — every caller of what changed, every consumer of the data it writes, every
   screen that renders it, every job or webhook it triggers.
3. **Shared foundations** — anything the change touches that is used elsewhere: a shared utility, a
   base component, a middleware, a config value, a database column, a dependency version.

Each identified area becomes a regression case with a stated reason. An area named without a reason
is not a regression case — it is a guess, and should be marked as an assumption.

---

## REG-001 — Shared code changes require tests for existing callers

**Test levels:** unit, integration
**Rule:** When a shared function, utility, middleware, base component, or hook is modified, add or
verify a test for each existing caller, prioritising callers outside the feature being built.
**Why it matters:** The author tests the new call site; the pre-existing call sites are exactly the
ones nobody looks at, and they carry the same signature change.
**How to test:** Enumerate callers explicitly in the plan. If they cannot be enumerated from the
change summary, mark the caller list as an assumption and flag that a code search is required.

## REG-002 — Data model changes are tested against pre-existing rows

**Test levels:** integration
**Rule:** For added, renamed, retyped, or dropped columns, and for new constraints or indexes,
test: existing rows written before the change, rows with `NULL` in the new column, rows that
violate a newly added constraint, and the read path for both old-shape and new-shape records.
**Why it matters:** Migrations are validated against fresh test data far more often than against
the messy historical data that actually exists in production.

## REG-003 — Migrations are tested forward, backward, and mid-flight

**Test levels:** integration, manual
**Rule:** Cover: applying the migration to a populated database, the rollback path, running the
migration twice (idempotency), and the window where old application code runs against the new
schema and new code runs against the old schema.
**Why it matters:** During any rolling deploy both code versions run simultaneously. A migration
that is only correct after full rollout causes errors throughout the deployment window.
**Default assumption:** If the deployment strategy is not stated, assume a rolling deploy with
mixed versions and mark the mixed-version cases as an assumption.

## REG-004 — Contract changes are tested from the consumer's side

**Test levels:** api, integration
**Rule:** When a request or response schema, an event payload, or a queue message changes, test the
old consumer against the new producer and, where deployment order allows, the new consumer against
the old producer.
**Why it matters:** Producer-side tests pass while consumers break, because the producer's tests
were updated alongside the change and the consumer's were not. See `api_testing.md` (API-009).

## REG-005 — Shared UI component changes are tested at every usage site

**Test levels:** component, e2e, manual
**Rule:** When a design-system or shared component changes, verify each screen that renders it,
including states the new feature does not use — disabled, loading, error, long content, and
right-to-left layouts.
**Why it matters:** A style or prop-default change in a shared component propagates silently to
unrelated screens that nobody in the change's review path is looking at.

## REG-006 — Configuration, environment, and feature-flag combinations

**Test levels:** integration, e2e
**Rule:** For each new or changed flag or config value, test flag on, flag off, flag missing or
unset, and mid-session toggling. Where flags interact, test the combinations that are reachable in
production.
**Why it matters:** The off path is the rollback path. If it was never tested, the safety net does
not exist when it is most needed.
**Default assumption:** If default flag values are unspecified, assume the flag is off in
production and on in staging, and mark it as an assumption.

## REG-007 — Removed and deprecated behaviour is verified as removed

**Test levels:** api, e2e
**Rule:** When functionality is removed, test that the entry point is genuinely gone (or returns the
documented deprecation response), that no dead navigation path leads to it, and that data it
created is still readable or is intentionally cleaned up.
**Why it matters:** Partial removals leave orphaned routes and unreachable records that surface
later as confusing production errors.

## REG-008 — Performance-sensitive paths are re-checked

**Test levels:** integration, e2e
**Rule:** When a query, loop, serialisation step, or render path on a hot route changes, assert
query counts (N+1 detection), payload size, and response time against the previous behaviour.
**Why it matters:** Performance regressions pass every functional test and are only noticed once
they hurt users at production scale.
**Default assumption:** If no budget exists, propose a comparative check against the current
behaviour rather than an absolute threshold, and flag the missing budget.

## REG-009 — Background jobs, schedules, and async consumers

**Test levels:** integration
**Rule:** When a job, cron, queue consumer, or webhook handler is affected, test: retry after
failure, duplicate delivery, out-of-order delivery, a poison message, and the behaviour when the
job overlaps with its own previous run.
**Why it matters:** Async paths fail silently. Nobody is watching a screen when a consumer starts
dropping messages.

## REG-010 — Timezone, locale, and clock-boundary behaviour

**Test levels:** unit, integration
**Rule:** Where dates, scheduling, or expiry logic changes, test across timezone offsets, a
daylight-saving transition, month and year boundaries, leap day, and clock skew between services.
**Why it matters:** Date logic that is correct in one timezone is a recurring source of off-by-one-
day defects that only appear for a subset of users.

## REG-011 — Dependency upgrades are treated as behavioural changes

**Test levels:** integration, e2e
**Rule:** When a dependency version changes, identify the features that use it and re-run their
critical paths, giving explicit attention to any behaviour noted in the upgrade's changelog.
**Why it matters:** A minor version bump can alter defaults, serialisation, or error types without
any change in your own code and without any compile-time signal.

## REG-012 — Every fixed bug gains a permanent test

**Test levels:** unit, api, integration
**Rule:** For each bug the change fixes, add a test that reproduces the original failure and fails
against the unfixed code. Reference the original report.
**Why it matters:** Bugs recur most often in code that has already been touched twice; the
reproduction test is the only durable defence.

## REG-013 — Rollback and recovery are exercised

**Test levels:** integration, manual
**Rule:** Verify the change can be reverted without data corruption: the previous version reads
records written by the new version, and any new required field or format degrades safely.
**Why it matters:** A change that cannot be rolled back turns a small defect into a prolonged
incident.

## REG-014 — The existing suite is part of the regression evidence

**Test levels:** all
**Rule:** The plan states which existing suites must run for this change and calls out any test that
was modified or deleted, with the reason.
**Why it matters:** A "passing" run means little if the assertions were loosened to accommodate the
change. Deleted or weakened tests are a reviewable event.

---

## Regression scoping checklist

| Trigger in the change summary | Required regression cases |
|---|---|
| Shared function or utility edited | REG-001 |
| Schema or column changed | REG-002, REG-003 |
| Request, response, or event payload changed | REG-004 |
| Shared UI component changed | REG-005 |
| Flag or config added or changed | REG-006 |
| Feature or endpoint removed | REG-007 |
| Query or hot path touched | REG-008 |
| Job, queue, cron, or webhook touched | REG-009 |
| Date, expiry, or scheduling logic touched | REG-010 |
| Dependency version changed | REG-011 |
| Bug fixed | REG-012 |
| Any change | REG-013, REG-014 |
