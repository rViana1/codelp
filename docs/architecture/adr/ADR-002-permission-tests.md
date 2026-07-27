# ADR-002 — Defer Permission Error Testing Until Mock Infrastructure Exists

**Status:** Accepted

**Date:** 2026-07-24

---

# Context

The ProjectScanner handles PermissionError exceptions by recording the error instead of interrupting the scan.

Although this behaviour is already implemented, reproducing PermissionError reliably in automated tests is highly dependent on the operating system, file system and execution environment.

Tests based on real file permissions would therefore become fragile and potentially inconsistent across platforms.

---

# Decision

Permission-related behaviour will not be tested during Milestone 2.1.

Instead, dedicated tests will be implemented after introducing a mocking framework capable of simulating PermissionError deterministically.

This ensures that automated tests remain stable and platform-independent.

---

# Consequences

## Advantages

Platform-independent test suite.

Deterministic behaviour.

No dependency on operating system permissions.

Improved reliability of continuous integration.

---

## Disadvantages

PermissionError handling is temporarily validated only through implementation review.

Automated verification is postponed.

---

# Implementation

Introduce mock-based tests after the project adopts:

- pytest-mock

or

- unittest.mock

Future tests should simulate PermissionError raised by os.scandir().

---

# Notes

This ADR affects only the testing strategy.

The scanner implementation already supports PermissionError and does not require modification.