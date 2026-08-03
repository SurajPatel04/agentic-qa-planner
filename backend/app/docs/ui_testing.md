---
id: ui-testing
title: UI, End-to-End, and Playwright Testing Standards
domain: ui
applies_to: [unit, integration, e2e, playwright, manual]
tags: [playwright, selectors, accessibility, forms, states, responsive, flake]
version: 1.0
---

# UI, End-to-End, and Playwright Testing Standards

## Scope

Applies to any change affecting a screen, a component, a form, a navigation path, or user-visible
copy. Use this document to derive **component-level**, **end-to-end / Playwright**, and **manual**
test cases, and to decide which of the three each scenario belongs in.

## Choosing the right level

Push each scenario to the cheapest level that can genuinely catch the bug.

| Scenario | Level |
|---|---|
| Rendering logic, conditional display, formatting | Component / unit test |
| Client-side validation rules and error text | Component test |
| A complete user journey across pages and real data | E2E (Playwright) |
| One journey per critical flow — not every permutation | E2E (Playwright) |
| Visual polish, animation feel, copy tone, screen-reader experience | Manual |
| Exploratory probing of an unfamiliar flow | Manual |

**Rule of thumb:** a permutation that differs only in input values belongs in a component or API
test; E2E is reserved for proving the pieces connect. An E2E suite that grows with every input
variant becomes slow and flaky and stops being run.

---

## UI-001 — Every flow has one end-to-end happy path

**Test levels:** e2e, playwright
**Rule:** Each primary user flow the change introduces or modifies needs exactly one E2E test that
walks the flow as a user would — real navigation, real form entry, real submission — and asserts
the observable outcome plus the persisted result.
**Why it matters:** Component tests pass with mocked seams; only an end-to-end run proves routing,
state, API wiring, and persistence agree with each other.
**How to test:** Assert what the user sees (a confirmation, the new row in a list) rather than
internal state. Verify persistence by reloading the page instead of trusting the optimistic UI.

## UI-002 — All four data states are covered for every view

**Test levels:** component, e2e
**Rule:** Every view that loads data covers: loading, empty, populated, and error. Add
partial-failure where one panel fails while others succeed.
**Why it matters:** Empty and error states are commonly implemented last and shipped untested; they
appear to users at the worst possible moment.
**Default assumption:** If empty-state copy is not specified, assert that a non-blank, non-error
message renders, and mark the exact wording as an assumption.

## UI-003 — Form validation is tested field by field with inline feedback

**Test levels:** component, e2e
**Rule:** Per field: required-but-empty, whitespace-only, wrong format, too short, too long, and
valid. Assert the error message appears next to the correct field, that submission is blocked, and
that the error clears once corrected.
**Why it matters:** Errors displayed only in a summary, or attached to the wrong field, make forms
unusable for keyboard and screen-reader users.

## UI-004 — Submission is protected against double-submit and slow networks

**Test levels:** e2e, playwright
**Rule:** Test rapid double-click on submit, submission while the network is throttled, and
navigating away mid-submission. Assert exactly one record is created and the control is disabled or
guarded while in flight.
**Why it matters:** Duplicate orders, duplicate payments, and duplicate invites are among the most
common production complaints and are trivially reproducible.
**How to test:** In Playwright, route-intercept the request and delay it, then assert the button
state and the number of requests fired.

## UI-005 — Selectors are stable and user-facing

**Test levels:** e2e, playwright
**Rule:** Prefer role-, label-, and text-based locators (`getByRole`, `getByLabel`, `getByText`),
or an explicit `data-testid`. Never target CSS classes, generated class names, `nth-child`
positions, or deep DOM paths.
**Why it matters:** Structural selectors break on every styling change, producing failures that
teach the team to ignore the suite.
**How to test:** If a locator cannot be expressed by role or label, that usually indicates a real
accessibility gap — record it as a finding rather than reaching for a brittle selector.

## UI-006 — No fixed waits; assert on state

**Test levels:** e2e, playwright
**Rule:** Use web-first assertions and auto-waiting locators. Fixed sleeps are not permitted. Wait
for the specific network response, element state, or URL change that defines readiness.
**Why it matters:** Fixed waits are simultaneously too short on slow CI (flake) and too long on
fast machines (wasted minutes across the suite).

## UI-007 — Tests are isolated and can run in parallel

**Test levels:** e2e, playwright
**Rule:** Each test seeds its own data with unique identifiers, authenticates through a
programmatic path or stored session state rather than by driving the login form, and cleans up or
tolerates leftover data.
**Why it matters:** Shared fixtures make tests order-dependent and prevent parallelisation, which
is usually the single largest cost in a slow E2E suite.
**Exception:** The login flow itself must have at least one test that drives the real form
(AUTH-001, AUTH-003).

## UI-008 — Navigation, deep links, and browser controls

**Test levels:** e2e, playwright
**Rule:** Cover: direct navigation to a deep link while logged out (redirect to login, then return
to the original destination after login), browser back and forward through the flow, refresh
mid-flow, and an invalid or stale URL parameter.
**Why it matters:** Users bookmark, share, and refresh URLs; flows that only work when entered from
the beginning break constantly in real use.

## UI-009 — Unsaved-changes and destructive-action guards

**Test levels:** e2e, manual
**Rule:** Test navigating away with unsaved edits, and test each destructive action's confirmation
step — confirm, cancel, and dismiss. Assert cancel truly leaves state unchanged.
**Why it matters:** A confirmation dialog that deletes on cancel, or a guard that never fires, is a
data-loss bug rather than a cosmetic one.

## UI-010 — Permission-dependent UI matches server enforcement

**Test levels:** e2e, playwright
**Rule:** For each role, assert which controls are visible and enabled, and pair every hidden
control with an API-level test proving the server also denies it.
**Why it matters:** A hidden button is a usability affordance, not a security control. See
`authentication.md` (AUTH-001, AUTH-005) and `security.md` (SEC-001).

## UI-011 — Accessibility basics on every changed screen

**Test levels:** component, e2e, manual
**Rule:** Assert keyboard-only completion of the flow, a visible focus indicator, focus moving into
a dialog and returning on close, labels associated with inputs, alt text on meaningful images, and
errors announced to assistive technology. Run an automated accessibility scan on changed screens.
**Why it matters:** Accessibility defects are cheap to fix at build time and expensive to retrofit,
and an automated scan catches only a portion — keyboard and focus checks stay manual.

## UI-012 — Responsive and cross-browser behaviour

**Test levels:** e2e, manual
**Rule:** Verify the flow at a narrow mobile width, at tablet width, and at desktop width. Confirm
no horizontal scrolling, that touch targets remain reachable, and that content is not clipped by an
on-screen keyboard. Run critical flows on at least one Chromium and one non-Chromium engine.
**Default assumption:** If target breakpoints and browsers are unspecified, assume 375 px, 768 px,
and 1440 px on the latest Chromium and WebKit, and mark this as an assumption.

## UI-013 — Content edge cases in rendering

**Test levels:** component, manual
**Rule:** Test with very long strings without spaces, empty values, zero and negative numbers, large
numbers, right-to-left and multi-byte text, emoji, and HTML-like characters in user content.
**Why it matters:** Layouts silently break on real-world names, addresses, and pasted content well
before any functional bug appears.

## UI-014 — Loading performance and perceived responsiveness

**Test levels:** e2e, manual
**Rule:** Assert that a skeleton or spinner appears within a perceptible delay, that long lists
render without freezing interaction, and that repeated actions do not accumulate listeners, timers,
or requests.
**Default assumption:** If no performance budget is given, propose a check with a placeholder
threshold and flag the missing budget rather than asserting a number as if it were agreed.

## UI-015 — Manual test cases are written for what automation cannot judge

**Test levels:** manual
**Rule:** Reserve manual cases for visual correctness, copy and tone, screen-reader experience,
real-device behaviour, third-party integrations that cannot be safely automated, and exploratory
probing of a risky area. Each manual case states preconditions, numbered steps, expected result,
and the data needed.
**Why it matters:** Manual effort is the scarcest testing resource; spending it on what a machine
could assert leaves the subjective gaps uncovered.

---

## Flake-prevention checklist for Playwright cases

An E2E case that fails any row should be rewritten before it enters the plan.

- Locators are role-, label-, or `data-testid`-based (UI-005).
- No fixed sleeps; assertions wait on state (UI-006).
- Test data is unique per run and created by the test (UI-007).
- Authentication uses stored session state, except in login-flow tests (UI-007).
- Network responses the assertion depends on are awaited explicitly.
- The test passes when run alone, in parallel, and repeated back to back.
