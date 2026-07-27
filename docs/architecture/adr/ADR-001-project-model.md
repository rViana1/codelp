# ADR-001 — Introduce the Project Domain Model

**Status:** Proposed

**Date:** 2026-07-24

---

# Context

The current architecture produces independent outputs from each processing stage.

For example:

- Scanner produces a ScanResult.
- Parser will produce parsed structures.
- Chunker will produce semantic chunks.
- Embedding Engine will generate vector representations.

If every module exposes its own independent output, higher-level components would need to manage multiple disconnected objects, increasing coupling and making the architecture progressively harder to maintain.

As the number of processing stages grows, this fragmentation becomes increasingly problematic.

---

# Decision

Introduce a central domain entity named `Project`.

The Project entity will represent the complete state of a software repository.

Rather than creating unrelated result objects, every processing stage will enrich the same Project instance.

Conceptually:

Repository

↓

Project

↓

Scanner

↓

Parser

↓

Indexer

↓

Chunker

↓

Embedding Engine

↓

Retriever

↓

Context Builder

---

Each module reads the current Project state, adds new knowledge and returns the updated Project.

---

# Consequences

## Advantages

A single domain model shared across the entire platform.

Lower coupling between modules.

Simpler communication between components.

Clear ownership of project state.

Better scalability as new modules are introduced.

Future persistence becomes straightforward.

Caching becomes significantly easier.

---

## Disadvantages

The Project model will become progressively larger.

Strong attention must be paid to separation of responsibilities inside the domain model.

---

# Alternatives Considered

No alternative was considered sufficiently advantageous to justify maintaining multiple disconnected result models.

The benefits of a unified domain model clearly outweigh the additional complexity of maintaining a richer Project entity.

---

# Implementation

The Project entity will **not** be introduced during Milestone 2.1.

Implementation is planned for Milestone 2.2 after the scanner has been fully stabilised.

---

# Notes

This ADR establishes the Project entity as the central object of the Codelp architecture.

Future architectural decisions should preserve this principle unless a compelling reason emerges.