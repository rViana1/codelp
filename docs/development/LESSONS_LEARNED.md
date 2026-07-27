# Lessons Learned

This document records the most important technical lessons learned during the development of each milestone.

Its goal is to preserve architectural reasoning, successful decisions and future improvements identified during development.

---

# Milestone 2.1 — Project Scanner

## Objective

Implement the first production-ready version of the Project Scanner.

The scanner is responsible for traversing a project directory, applying filtering rules and producing an in-memory representation of the project tree.

---

## What went well

- The scanner remained focused on a single responsibility.
- The project tree representation proved to be simple and expressive.
- Introducing the ScanFilter abstraction made the scanner easily extensible.
- Deterministic ordering simplified both testing and debugging.
- Building the tree during scanning avoided unnecessary post-processing.

---

## Lessons Learned

### Keep responsibilities small

Avoid adding parsing, chunking or indexing responsibilities to the scanner.

The scanner should only discover the project structure.

---

### Deterministic behaviour is extremely valuable

Sorting directories before files and keeping alphabetical ordering makes:

- tests deterministic;
- debugging easier;
- future caching mechanisms more reliable.

---

### Domain models are worth creating early

Using explicit models (`TreeNode` and `ScanResult`) instead of dictionaries provides a much better foundation for future evolution.

---

### Design for extension, not speculation

The `ScanFilter` abstraction allows new filtering strategies without modifying the scanner itself.

Only abstractions with immediate value should be introduced.

---

### Test incrementally

Creating small tests first and gradually increasing complexity made implementation safer and reduced debugging time.

---

## Architectural Decisions Reinforced

- Project tree represented as a graph of `TreeNode` objects.
- Children stored as a dictionary for fast lookup.
- Filtering implemented using the Strategy Pattern.
- Scanner remains independent from parsers, chunkers and indexers.

---

## Future Improvements

- Scanner statistics.
- Incremental scanning.
- Persistent project knowledge.
- Composite scan filters.
- Parallel scanning for very large repositories.

---

## Milestone Result

Status: Completed

Architecture Review: Approved

Code Review: Approved

Tests: Passed

Ready for next milestone.