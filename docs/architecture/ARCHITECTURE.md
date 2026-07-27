# Codelp Architecture

> **Version:** 1.0  
> **Status:** Draft  
> **Last Updated:** Milestone 2.1

---

# 1. Purpose

The purpose of this document is to describe the architecture of the Codelp platform.

It defines the major system components, their responsibilities, how they interact, and the engineering principles that guide the evolution of the project.

This document is intentionally technology-independent whenever possible. It focuses on architectural decisions rather than implementation details.

---

# 2. Vision

Codelp is designed to transform a software repository into structured knowledge.

Instead of treating source code as plain text, Codelp progressively enriches the information extracted from the project until it becomes a searchable, navigable and AI-ready knowledge base.

Every stage of the architecture contributes to that transformation.

---

# 3. Architecture Principles

The architecture follows a small set of non-negotiable principles.

## Single Responsibility

Every module has one clear responsibility.

No module should perform work belonging to another component.

---

## Modularity

Every component should be replaceable without requiring changes to unrelated modules.

---

## Extensibility

Support for new programming languages, embedding providers or storage engines must be added through extension rather than modification.

---

## Determinism

The same repository must always produce the same internal representation.

Independent executions should generate identical results.

---

## Testability

Public behaviour must always be validated through automated tests.

Private implementation details are not tested directly.

---

## Documentation

Important engineering decisions must be documented through ADRs.

---

# 4. High-Level Architecture

Repository

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

Knowledge Store

↓

Retriever

↓

Context Builder

↓

LLM

Each module enriches the project representation without knowing the internal implementation of later modules.

---

# 5. Core Components

## Scanner

Responsible for discovering the repository.

Responsibilities

- discover files
- discover directories
- ignore configured paths
- build the project tree

Output

ScanResult

---

## Parser

Responsible for understanding source code.

Responsibilities

- parse files
- detect programming language
- extract imports
- extract classes
- extract methods
- extract functions

Output

ParsedProject

---

## Indexer

Responsible for organising project knowledge.

Responsibilities

- symbol index
- dependency index
- file index
- reference index

Output

ProjectIndex

---

## Chunker

Responsible for preparing semantic chunks.

Responsibilities

- preserve context
- generate chunk metadata
- optimise chunk boundaries

Output

Chunks

---

## Embedding Engine

Responsible for generating vector representations.

Responsibilities

- embedding generation
- cache
- batching

Output

Embeddings

---

## Retriever

Responsible for semantic search.

Responsibilities

- similarity search
- ranking
- filtering

---

## Context Builder

Responsible for constructing prompts.

Responsibilities

- retrieve information
- merge context
- enforce token limits

Output

LLM Context

---

# 6. Domain Model

The central entity of the architecture is the Project.

Every module enriches the same Project instance.

Project

├── metadata

├── scan

├── parser

├── index

├── chunks

├── embeddings

├── diagnostics

└── statistics

No module communicates directly with another module.

Communication always happens through the Project model.

---

# 7. Data Flow

Repository

↓

Scanner

↓

Project

↓

Parser

↓

Project

↓

Indexer

↓

Project

↓

Chunker

↓

Project

↓

Embedding Engine

↓

Project

↓

Retriever

↓

Context Builder

↓

LLM

---

# 8. Dependency Rules

Allowed dependencies

Scanner → Models

Parser → Models

Indexer → Models

Chunker → Models

Retriever → Models

Forbidden dependencies

Scanner → Parser

Parser → Chunker

Chunker → Retriever

Retriever → Scanner

No module should depend on a future processing stage.

---

# 9. Layered Architecture

Presentation

↓

Application

↓

Domain

↓

Infrastructure

Scanner belongs to the Infrastructure layer.

The Project model belongs to the Domain layer.

Business rules belong to the Domain layer.

External APIs belong to the Infrastructure layer.

---

# 10. Testing Strategy

Every module must include automated tests.

Priority

1. Public API

2. Business rules

3. Regression tests

Implementation details should not be tested directly.

---

# 11. Performance Goals

Future milestones should optimise

- incremental scanning
- caching
- lazy loading
- parallel parsing
- embedding batching

Performance optimisations should never compromise determinism.

---

# 12. Extensibility

The architecture must support

- multiple programming languages

- multiple embedding providers

- multiple LLM providers

- multiple vector databases

without changing the core architecture.

---

# 13. Architecture Decision Records

Major engineering decisions are documented separately.

Current ADRs

ADR-001 Project Model

ADR-002 Permission Tests

Future ADRs

Plugin System

Cache

Configuration

Language Support

Incremental Scanner

---

# 14. Future Evolution

Future architectural improvements include

- Project entity

- Plugin system

- Incremental scanning

- Remote repository support

- Distributed indexing

- Streaming parser

- Parallel chunking

- Multi-language parsing

---

# 15. Engineering Philosophy

Codelp is designed as an engineering platform rather than a collection of utilities.

The architecture favours maintainability, modularity and deterministic behaviour over short-term implementation speed.

Every new feature should strengthen the architecture rather than increase technical debt.