---
id: qa-plan-standards
title: QA Plan and Test Case Quality Standards
domain: process
applies_to: [unit, api, integration, e2e, playwright, manual]
tags: [acceptance-criteria, coverage, duplicates, priority, assumptions, versioning]
version: 1.0
---

# QA Plan and Test Case Quality Standards

## Scope

Governs the **shape** of a generated QA plan rather than the subject matter of any single test.
Every generated test case is checked against these rules before it is presented for review. The
domain documents (`api_testing.md`, `authentication.md`, `security.md`, `ui_testing.md`,
`regression.md`) supply *what* to test; this document defines *what a well-formed test case and a
well-formed plan look like*.

---

## PLAN-001 — A test case is atomic and independently verifiable

**Rule:** One case asserts one behaviour. If the title needs "and", or the steps contain a second
independent expected result, split it.
**Why it matters:** Compound cases report a single pass/fail for several behaviours, so a partial
failure is either lost or blocks the whole case.
**Incomplete when:** The expected result describes more than one outcome that could fail
independently.

## PLAN-002 — Required fields of a test case

**Rule:** Every case carries: a title, a level (`unit` | `api` | `integration` | `e2e` |
`playwright` | `manual`), preconditions and test data, steps or the action under test, an explicit
expected result, the acceptance criteria it maps to, the guidance rule ID it derives from, a
priority, and a rationale.
**Incomplete when:** Any of these is empty, or the expected result is non-assertable ("works
correctly", "behaves as expected", "no errors"). An expected result must state an observable
value, status code, message, or state change.

## PLAN-003 — Every test maps to at least one acceptance criterion

**Rule:** Each case references one or more acceptance criteria by their stable identifier. A case
that maps to none is either testing something outside scope or has revealed a missing criterion —
report which.
**Why it matters:** Mapping is what makes coverage measurable rather than impressionistic.
**Exception:** Regression and security cases derived from `regression.md` or `security.md` may
legitimately map to no stated criterion. Label these `implicit-quality` and list them separately
so they neither inflate nor deflate the coverage figure.

## PLAN-004 — Coverage is computed deterministically, never estimated

**Rule:** Acceptance-criteria coverage is a counted ratio over the explicit mapping: criteria with
at least one mapped, non-rejected test case, divided by total criteria. It is computed in code from
the mapping table, never asserted by the model.
**Why it matters:** A model-stated percentage is unverifiable and drifts as cases are edited,
approved, or rejected during review.
**Reporting:** State the fraction and list every uncovered criterion by identifier. A criterion
covered only by a rejected case counts as uncovered.

## PLAN-005 — Coverage counts mapping, not adequacy

**Rule:** A criterion mapped to at least one test is "covered" for the purposes of the metric. A
covered criterion may still be under-tested, so a criterion with only a happy-path case and no
negative case is additionally flagged as **thin coverage**.
**Why it matters:** Reporting 100% coverage from a suite of happy paths is the most common way a
coverage number misleads its reader.

## PLAN-006 — Duplicate detection

**Rule:** Two cases are duplicates when they exercise the same level, the same entry point, and the
same input class with the same expected result. Cases differing only in wording are duplicates;
cases differing in level (a component validation test and its API counterpart) are **not** — that
pairing is required by `security.md` (SEC-001).
**Reporting:** Group duplicates, keep the most complete one, and present the others as
merge candidates for the reviewer to decide on. Never delete silently.

## PLAN-007 — Near-duplicate and over-specification detection

**Rule:** Flag clusters of cases that differ only in input value and belong at the same level.
Propose collapsing them into one parameterised case listing the values.
**Why it matters:** Twelve near-identical E2E cases cost twelve times the runtime and provide
roughly the information of one parameterised test — see `ui_testing.md` (level-selection table).

## PLAN-008 — Every case states why it is relevant

**Rule:** The rationale answers: which acceptance criterion or risk this protects, what failure it
would catch, and why that failure is plausible in this change. Cite the guidance rule ID.
**Why it matters:** The rationale is what allows a reviewer to reject a case confidently, and it is
what keeps the case meaningful to the next reader months later.
**Incomplete when:** The rationale restates the steps instead of naming the risk.

## PLAN-009 — Assumptions are explicit, attributed, and separated

**Rule:** When the requirement, acceptance criteria, or change summary does not supply a detail a
case depends on, the case is marked `assumption: true`, states the assumed value, states what was
missing, and states which answer would change the case. Assumptions are also collected into a
single list at the top of the plan.
**Why it matters:** An unmarked assumption is indistinguishable from a specified requirement, so it
gets approved without the missing question ever being asked.
**Rule of restraint:** Assume defaults for gaps in mechanics (page size, status code, timeout).
Escalate rather than assume when the gap concerns who is permitted to do something, what happens to
data on failure, or a regulatory or financial rule.

## PLAN-010 — Priority reflects risk, not effort

**Rule:** Assign `P0`–`P3` on impact × likelihood:
- `P0` — data loss, security or permission failure, money handled incorrectly, or the primary flow
  blocked.
- `P1` — a main flow broken in a common condition, or a documented acceptance criterion unmet.
- `P2` — an edge case, a degraded state, or a secondary flow.
- `P3` — cosmetic, rare-configuration, or nice-to-have coverage.

Priority is proposed by the assistant and is always editable by the reviewer, since only the team
knows the deployment and user context.

## PLAN-011 — Level assignment is justified and pushed downward

**Rule:** Each case sits at the cheapest level that can catch the failure. When a case is proposed
at E2E, the rationale states why a lower level cannot catch it (typically: it spans components,
services, or persistence).
**Why it matters:** Test-level inflation is the main driver of slow, flaky suites that teams stop
trusting and eventually stop running.

## PLAN-012 — Gaps are reported as gaps, not filled with filler

**Rule:** When the input is too thin to derive real cases for an area, say so explicitly and name
the question that would unblock it. Do not emit generic placeholder cases to make coverage look
complete.
**Why it matters:** Filler cases inflate the coverage figure while testing nothing, which is worse
than a visible, honest gap.

## PLAN-013 — The assistant proposes; it does not certify

**Rule:** Output is a *proposed* plan. The assistant never states or implies that a feature passes,
is verified, is release-ready, is secure, or is safe to ship. It reports what is covered, what is
uncovered, what is assumed, and what is risky. Pass/fail is the outcome of executing tests, and
release readiness is a human decision.
**Why it matters:** A generated plan is evidence about intent, not about behaviour. No test has run
at the time the plan is produced.

## PLAN-014 — Review actions are preserved, not overwritten

**Rule:** Reviewer actions — edit, approve, reject, reprioritise — are recorded against the case
with the original AI-proposed content retained. Rejected cases stay in the plan, marked, with the
rejection reason.
**Why it matters:** Retaining rejections prevents the same case being regenerated and re-argued on
the next run, and preserves the reasoning behind the decision.

## PLAN-015 — Plans are versioned and diffable

**Rule:** Saving a reviewed plan creates a new immutable version recording the source inputs, the
retrieved guidance rule IDs, the resulting cases with their review state, the computed coverage
figure, and the reviewer and timestamp. Earlier versions remain readable.
**Why it matters:** Requirements change mid-review. Without versioning it is impossible to tell
whether coverage dropped because a criterion was added or because a case was rejected.

---

## Plan-level completeness checklist

Run before presenting a plan. Every "no" is reported to the reviewer rather than silently fixed.

- [ ] Every acceptance criterion has at least one mapped case, or is listed as uncovered.
- [ ] Coverage is computed from the mapping table, not stated by the model (PLAN-004).
- [ ] Criteria with happy-path-only coverage are flagged as thin (PLAN-005).
- [ ] Main user flows are identified and each has an end-to-end case (UI-001).
- [ ] Edge, permission, and failure cases exist for each flow (API-005, AUTH checklist, API-010).
- [ ] Regression areas are named with a stated reason (`regression.md`).
- [ ] Duplicates and near-duplicates are grouped, not deleted (PLAN-006, PLAN-007).
- [ ] Every case has an assertable expected result and a rationale (PLAN-002, PLAN-008).
- [ ] Every assumption is marked and listed at the top (PLAN-009).
- [ ] No case, summary, or heading claims the feature passes or is release-ready (PLAN-013).
