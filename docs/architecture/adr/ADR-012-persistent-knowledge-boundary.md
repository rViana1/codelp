# ADR-012 — Persistent Project Knowledge Boundary

**Status:** Accepted

**Date:** 2026-08-14

---

# Context

Codelp progressively evolved from a sequential analysis pipeline into a knowledge-oriented system.

The pipeline currently produces multiple knowledge artifacts:

- Project metadata
- Parsed structures
- Symbol indexes
- Semantic chunks
- Embedding metadata
- Retrieval information

Initially, these artifacts existed only during execution.

Milestone 10 introduced the requirement to persist project knowledge between executions.

Directly integrating persistence into existing pipeline modules would introduce several risks:

- Scanner, Parser, Indexer and Chunker becoming storage-aware.
- Domain models depending on persistence mechanisms.
- Increased coupling between execution lifecycle and storage lifecycle.
- Difficulty replacing storage implementations in the future.
- Increased risk of regressions in already validated pipeline components.

---

# Decision

Persistent Project Knowledge will be introduced through an independent architectural boundary.

The implementation will be divided into incremental milestones:

## Milestone 10.1 — Persistent Knowledge Foundation

Responsible for:

- Defining persistent knowledge models.
- Defining storage abstractions.
- Creating storage adapters.
- Establishing identity preservation rules.
- Validating serialization boundaries.

This milestone must not modify existing pipeline behaviour.

---

## Milestone 10.2 — Pipeline Knowledge Integration

Responsible for:

- Defining persistence points.
- Loading existing project knowledge.
- Updating persisted knowledge after analysis.
- Supporting incremental analysis workflows.

Integration will happen on top of the existing validated pipeline.

---

The Project aggregate remains the source of truth.

Persistence acts as an external knowledge lifecycle mechanism and must not replace the domain model.

---

# Consequences

## Advantages

- Existing pipeline remains stable.
- Persistence can evolve independently.
- Storage implementations remain replaceable.
- Incremental analysis becomes possible without redesigning the architecture.
- Existing identities remain compatible.

## Disadvantages

- Additional integration steps are required.
- Temporary duplication exists between runtime state and persisted knowledge.
- More explicit lifecycle decisions are required.

---

# Alternatives Considered

## Integrate persistence directly into Project

Rejected.

This would make the domain responsible for storage concerns and increase coupling.

## Persist every pipeline result immediately

Rejected.

This would couple execution order with persistence behaviour and make future lifecycle changes harder.

---

# Implementation

Milestone 10.1 establishes the persistent knowledge boundary.

Future milestones will integrate persistence progressively without modifying existing module responsibilities.

---

# Notes

This ADR formalizes the separation between knowledge representation and knowledge persistence.

Future persistence decisions must preserve:

- Project ownership.
- Module boundaries.
- Deterministic identities.
- Storage independence.
