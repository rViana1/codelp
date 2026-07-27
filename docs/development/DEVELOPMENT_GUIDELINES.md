# Development Guidelines

This document defines the engineering practices followed during the development of Codelp.

The objective is to keep the project consistent, maintainable and easy to evolve over time.

---

# 1. General Principles

- Prefer readability over cleverness.
- Keep responsibilities small.
- Avoid premature optimisation.
- Design for extension, not speculation.
- Every module should have a single responsibility.

---

# 2. Coding Standards

## Python

- Follow PEP 8.
- Use type hints everywhere.
- Public APIs must be documented.
- Keep functions small whenever possible.
- Prefer composition over inheritance.

---

## Naming

- Classes use PascalCase.
- Functions use snake_case.
- Variables use descriptive names.
- Private members start with "_".

---

## Imports

Imports should be grouped in the following order:

1. Standard Library
2. Third-party packages
3. Internal modules

---

# 3. Architecture

- Avoid circular dependencies.
- Keep modules independent.
- Public interfaces should remain stable.
- Internal implementation may evolve freely.

---

# 4. Testing Strategy

Every new feature should include automated tests.

Testing priority:

1. Unit Tests
2. Integration Tests
3. Regression Tests
4. Performance Tests (when applicable)

Tests should be:

- deterministic
- isolated
- easy to read
- fast

---

# 5. Documentation

Every significant architectural decision must be documented.

The following documents should remain updated:

- ROADMAP
- ARCHITECTURE
- ADRs
- LESSONS_LEARNED

---

# 6. Code Review

Every completed feature should be reviewed before being committed.

Review checklist:

- Correctness
- Readability
- Simplicity
- Maintainability
- Extensibility

---

# 7. Commit Strategy

Each milestone should end with:

- successful tests
- documentation update
- architecture review
- code review
- git commit
- version tag