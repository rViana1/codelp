---

# Milestone 2.2 — Project Domain Model

## Objective

Introduce the central `Project` aggregate root and integrate the scanner with the domain model without breaking the existing scanner API.

This milestone established the architectural foundation for all future modules (Parser, Indexer, Chunker, Embeddings and Retrieval).

---

## What Went Well

- The `Project` aggregate created a clear central source of truth.
- Separating metadata, configuration and statistics improved cohesion.
- Timezone-aware UTC handling was introduced from the beginning.
- The scanner was integrated without breaking backwards compatibility.
- Existing scanner tests continued to pass unchanged.
- Integration tests validated the interaction between the scanner and the domain.

---

## Lessons Learned

### Domain First Simplifies Evolution

Introducing a dedicated domain model early makes future modules significantly easier to design.

Instead of connecting modules directly, every module enriches the same `Project` instance.

---

### Preserve Stable APIs When Evolving Architecture

The original `scan()` API remained untouched.

Adding a new `scan_project()` method was safer than replacing the existing contract.

Incremental architectural evolution is usually less risky than disruptive redesign.

---

### Rich Domain Models Need Clear Boundaries

The domain should store knowledge, not implementation details.

The scanner owns `TreeNode`; the domain stores a serialization-safe representation of the tree.

Keeping this boundary explicit prevents accidental coupling.

---

### Circular References Become a Real Problem Quickly

The `parent` reference in `TreeNode` created circular serialization issues.

Navigation models and persistence models are often different concerns.

A dedicated serialization step solved the problem while preserving navigation capabilities.

---

### Default Factories Prevent Shared Mutable State

Pydantic `Field(default_factory=...)` was essential for sets, lists and nested models.

This avoided shared mutable state between `Project` instances.

---

### Timezone Awareness Should Be Decided Early

Using `datetime.now(timezone.utc)` from the beginning prevents future migration problems.

Timezone-aware timestamps should be the default for all persistent project data.

---

### Package Structure Matters

The integration tests revealed that a clear package root and a configured `pytest.ini` are necessary for reliable imports.

Import strategy should be defined early and applied consistently across the project.

---

## Architectural Decisions Reinforced

- `Project` is the Aggregate Root.
- The domain depends on no application modules.
- Application modules may depend on the domain.
- Scanner enriches the `Project` instead of communicating with future modules.
- Tree serialization excludes parent references.
- Backwards compatibility is preserved during architectural evolution.

---

## Future Improvements Identified

### Domain

- Dedicated `ProjectTree` domain model.
- Stronger validation rules.
- Immutable metadata sections.

### Scanner Integration

- Make `scan_project()` the primary public API.
- Incremental tree updates.
- Change tracking between scans.

### Knowledge Persistence

- Persist serialized trees.
- Store scan snapshots.
- Track repository evolution over time.

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed (17 automated tests)

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

Ready for Milestone 3 — Parser.


---

# Milestone 3 — Python Parser

## Objective

Implement the first production-ready parser capable of transforming Python source files into structured knowledge integrated with the Project aggregate.

The parser extracts imports, top-level functions, classes and methods while remaining independent from Scanner internals.

---

## What Went Well

- The parser architecture remained highly modular.
- Separating detection, parsing, visitors and orchestration simplified testing.
- The dual API (`parse_file` and `parse_project`) proved consistent with the Scanner architecture.
- AST visitors avoided large monolithic parsing logic.
- Diagnostics propagation allowed project parsing to continue even when some files could not be parsed.
- Integration with the Project aggregate required minimal changes to the existing architecture.

---

## Lessons Learned

### Keep Extraction Separate from Traversal

Using dedicated AST visitors made symbol extraction easier to understand, test and evolve.

Traversal logic and extraction logic should remain independent.

---

### Top-Level Functions and Methods Are Different Concepts

A generic `visit_FunctionDef` initially risked extracting class methods as top-level functions.

Being explicit about extraction boundaries prevents symbol duplication and simplifies future indexing.

---

### A Minimal Symbol Model Is Often Enough

Only names and ownership information were required to unlock the next milestone.

Decorators, docstrings, line ranges and inheritance can be added later without changing the overall architecture.

---

### Domain APIs and Technical APIs Serve Different Purposes

`parse_file()` is ideal for unit tests and debugging.

`parse_project()` is ideal for orchestration and domain enrichment.

Maintaining both APIs increases flexibility without adding significant complexity.

---

### Unsupported Languages Should Produce Diagnostics, Not Failures

Repositories are frequently multi-language.

Recording diagnostics instead of raising exceptions keeps the pipeline robust while preserving visibility of what was not analysed.

---

### Ownership Information Becomes Important Earlier Than Expected

Adding `class_name` to `MethodSymbol` is a small change with significant future value for indexing, references and navigation.

---

### Determinism Must Be Preserved Across the Pipeline

The parser preserves the deterministic ordering already established by the Scanner.

Stable ordering is important for testing, caching and future persistent project knowledge.

---

## Architectural Decisions Reinforced

- Project remains the Aggregate Root.
- Parser does not depend on Scanner internals.
- Visitors implement symbol extraction.
- Technical and domain APIs coexist.
- Diagnostics are propagated through the Project aggregate.
- Symbol extraction remains intentionally minimal.

---

## Future Improvements Identified

### Symbol Metadata

- decorators
- docstrings
- line ranges
- async functions
- class inheritance

### Indexing Support

- stable symbol identifiers
- fully-qualified names
- cross-file references

### Multi-language Parsing

- JavaScript
- TypeScript
- C#
- Java

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed (11 parser tests, 28 total tests)

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

Ready for Milestone 4 — Indexer.

---

# Milestone 4 — Stable Symbol Index

## Objective

Implement the first navigable project index capable of transforming parsed knowledge into deterministic and query-efficient structures integrated with the Project aggregate.

The indexer builds stable identifiers for functions, classes and methods while preserving deterministic behaviour across the entire pipeline.

---

## What Went Well

- Stable identifiers proved simple and highly effective.
- Separating builders from orchestration kept the indexer focused.
- Dictionary-based indexes simplified lookup logic.
- Deterministic ordering made tests and debugging easier.
- Integration with the existing Project aggregate required minimal architectural changes.
- The full pipeline remained consistent from Scanner to Indexer.

---

## Lessons Learned

### Human-Readable Identifiers Are Extremely Valuable

Identifiers such as:

```text
src/models/user.py::User.login
```

are easy to debug, serialize, log and reason about.

Readability is often more valuable than compactness in early architecture stages.

---

### The Indexer Should Own Identity

The parser should describe structure, not identity.

Moving identifier generation to the Indexer preserves a clean separation between extraction and navigation concerns.

---

### Relative Paths Matter

Using project-relative POSIX paths avoids machine-specific identifiers and keeps indexes portable across environments.

---

### Determinism Must Be Explicit

Relying on upstream ordering is fragile.

The Indexer now sorts files, functions, classes, methods and imports explicitly, making reproducibility a property of the component itself.

---

### Dictionaries Are the Right Default for Knowledge Graphs

Using dictionaries keyed by stable identifiers immediately enables efficient navigation and prepares the architecture for future reference graphs.

---

### Avoid Premature Navigation Optimizations

`FileEntry` stores only symbol identifiers rather than full symbol objects.

This keeps the model lightweight and avoids duplication until a measurable performance or usability need appears.

---

## Architectural Decisions Reinforced

- Project remains the Aggregate Root.
- Parser does not generate stable identifiers.
- Indexer owns symbol identity.
- Deterministic indexing is mandatory.
- Query structures are optimized for lookup, not serialization convenience.
- Cross-file references are intentionally deferred.

---

## Future Improvements Identified

### Reference Graph

- cross-file symbol references
- import resolution
- call graph
- inheritance graph

### Semantic Indexing

- fully-qualified names
- module resolution
- symbol aliases
- generic type information

### Retrieval

- symbol-to-file navigation helpers
- derived views
- ranking metadata

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed (12 indexing tests, 40 total tests)

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

Ready for Milestone 5 — Chunker.


---

# Milestone 5 — Chunker

## Objective

Transform indexed project knowledge into deterministic semantic chunks suitable for embeddings, retrieval and LLM context generation.

The Chunker is responsible for preserving semantic boundaries while extracting the exact source code associated with functions, classes and methods.

---

## What Went Well

- Symbol-based chunking produced clear and predictable chunk boundaries.
- Exact source extraction preserved the original formatting and indentation.
- Reusing stable symbol identifiers avoided introducing a second identity system.
- Deterministic ordering simplified testing and future embedding synchronization.
- Separating extractors, builders and orchestration kept responsibilities clear.
- Full pipeline tests detected regressions introduced by parser model changes.

---

## Lessons Learned

### Stable Identity Should Flow Through the Pipeline

The most important architectural decision was deriving chunk identifiers directly from symbol identifiers.

A single identity chain:

```text
Source File
    ↓
Parser Symbol
    ↓
Indexer Symbol ID
    ↓
Chunk ID
```

greatly simplifies embeddings, retrieval, persistence and incremental updates.

---

### Exact Source Extraction Is More Important Than Pretty Formatting

The chunker must preserve the exact text from the source file.

Any normalization of whitespace, indentation or line endings would make future embeddings and diagnostics less reliable.

---

### Parser Metadata Enables Downstream Features

Adding `start_line` and `end_line` to parser symbols unlocked precise chunk extraction.

This reinforced the idea that parser metadata should be designed with downstream consumers in mind.

---

### Deterministic Ordering Prevents Hidden Instability

Explicit sorting of:

- files;
- functions;
- classes;
- methods;

eliminated non-deterministic behaviour and made chunk IDs and ordering reproducible across executions.

---

### Integration Tests Catch Real Regressions

The most valuable regression was not in the Chunker itself, but in older Indexer tests that instantiated parser models manually.

End-to-end pipeline tests proved essential for detecting compatibility issues between milestones.

---

### Keep Chunking Semantic Before Optimizing Retrieval

The first implementation intentionally prioritised semantic coherence over retrieval optimisation.

Future features such as token-based chunking, overlap or hybrid chunking should be introduced only after retrieval behaviour is measurable.

---

## Architectural Decisions Reinforced

- Chunk IDs are derived from symbol IDs.
- Semantic chunk boundaries are the default strategy.
- Exact source text is preserved.
- Deterministic ordering is mandatory.
- The Chunker remains independent from the AST and the Scanner.

---

## Future Improvements Identified

### Chunking

- Token-based chunking.
- Large-symbol splitting.
- Overlapping windows.
- Hybrid semantic + token chunking.
- Language-specific chunking strategies.

### Retrieval

- Parent-child chunk relationships.
- Context expansion around chunks.
- Retrieval-aware chunk metadata.

### Performance

- Lazy source extraction.
- Incremental chunk regeneration.
- Chunk hashing for cache invalidation.

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

Ready for Milestone 6 — Embeddings.

# Milestone 6 — Embedding Engine

## Provider Abstraction

Embedding generation should not be coupled to a concrete provider.

Using an explicit provider contract allows:

- replacing embedding implementations;
- testing without external dependencies;
- supporting multiple providers in the future;
- keeping orchestration logic independent.

The Embedding Engine depends on the provider abstraction, not on provider implementations.

---

## Stable Embedding Identity

Embeddings should not introduce a new independent identity system.

The identity chain remains:

Source File

↓

Symbol ID

↓

Chunk ID

↓

Embedding.chunk_id

Reusing chunk identity simplifies:

- navigation;
- caching strategies;
- incremental updates;
- vector store synchronization.

---

## Deterministic Testing

External AI services should not be required to validate embedding behaviour.

A deterministic fake provider provides:

- reproducible tests;
- stable vectors;
- dependency-free validation;
- predictable pipeline behaviour.

This keeps architectural validation independent from external providers.

---

## Domain Flexibility

The embedding domain should not assume fixed vector dimensions.

Vector size belongs to the provider metadata.

This allows future support for different embedding models without changing the domain model.

---

## Storage Boundaries

The first embedding storage implementation should remain simple.

An in-memory store is sufficient to validate:

- embedding persistence boundaries;
- lookup behaviour;
- insertion ordering;
- future vector store interfaces.

Persistent storage should only be introduced when retrieval requirements justify the additional complexity.

---

## Project Pipeline Integration

Each processing stage should enrich the Project aggregate without creating direct dependencies between stages.

The current pipeline remains:

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

Future Retrieval

This preserves modularity and allows each stage to evolve independently.


---

# Milestone 7 — Retrieval Engine

## Objective

Transform generated embeddings into searchable project knowledge through a deterministic retrieval layer.

The Retrieval Engine introduces semantic search capabilities while preserving the architectural boundaries established by previous milestones.

---

## What Went Well

- Retrieval remained independent from embedding generation.
- Vector storage was abstracted behind a dedicated contract.
- The Retriever depends on retrieval behaviour rather than concrete storage implementations.
- Stable chunk identity flowed correctly from embeddings into retrieval results.
- Deterministic ranking made retrieval behaviour predictable and testable.
- Project integration followed the existing aggregate enrichment pattern.
- Diagnostics propagation remained consistent with previous pipeline stages.

---

## Lessons Learned

### Retrieval Should Not Own Query Generation

The Retriever should not know how queries are converted into vectors.

Keeping query vector generation outside the Retriever allows future integration with different embedding providers without changing retrieval logic.

---

### Vector Storage Must Remain Replaceable

The retrieval layer should depend on a storage contract rather than a concrete implementation.

The initial in-memory store is enough for validation, while the architecture remains prepared for future vector databases.

---

### Similarity Calculation Needs Explicit Boundaries

Similarity behaviour should be isolated from retrieval orchestration.

Separating cosine similarity from ranking logic makes future strategies possible, such as:

- hybrid retrieval;
- metadata filtering;
- alternative ranking algorithms.

---

### Determinism Is a Retrieval Requirement

Retrieval results must be reproducible.

Explicit ordering rules are required when multiple embeddings have similar scores.

Deterministic ranking improves:

- testing;
- debugging;
- caching;
- user confidence.

---

### Identity Preservation Enables Knowledge Navigation

Retrieval should return references to existing project knowledge, not create new identities.

The identity chain remains:

```text
Source File
    ↓
Symbol ID
    ↓
Chunk ID
    ↓
Embedding.chunk_id
    ↓
RetrievalResult.chunk_id
    ↓
ContextChunk.chunk_id
```

---

# Milestone 8 — Context Builder

## Objective

Transform retrieval results into structured context suitable for future LLM consumption.

The Context Builder introduces the final preparation layer between project knowledge retrieval and external consumers, while preserving architectural independence from LLM providers.

---

## What Went Well

- The Context Builder remained independent from LLM providers.
- Retrieval results were transformed into a structured `PromptContext` model.
- Chunk identity was preserved from retrieval results into generated context.
- The existing Project aggregate enrichment pattern was reused successfully.
- Diagnostics propagation remained consistent with previous pipeline stages.
- Deterministic ordering was preserved from retrieval results into final context generation.
- Existing architecture boundaries remained unchanged.

---

## Lessons Learned

### Context Generation Should Not Belong to Retrieval

The Retriever is responsible for finding relevant knowledge.

The Context Builder is responsible for preparing that knowledge for consumption.

Keeping these responsibilities separate allows retrieval strategies and context generation strategies to evolve independently.

---

### Context Must Preserve Original Knowledge Identity

The Context Builder should not create new identities.

The identity chain remains:

```text
Source File
    ↓
Symbol ID
    ↓
Chunk ID
    ↓
Embedding.chunk_id
    ↓
RetrievalResult.chunk_id
    ↓
ContextChunk.chunk_id
```

Preserving identity enables future navigation, diagnostics and incremental updates.

---

### Structured Context Is Preferable to Raw Text Concatenation

A structured `PromptContext` model provides a clear boundary between project knowledge and future consumers.

This allows future features such as:

- token management;
- context compression;
- prompt templates;
- multiple LLM providers.

without changing retrieval or domain models.

---

### Diagnostics Are Better Than Silent Data Loss

When retrieved chunks cannot be resolved, the Context Builder should not fail the entire pipeline.

Missing knowledge should be recorded through diagnostics while allowing processing to continue.

---

### Deterministic Context Ordering Is Essential

The same retrieval results should always produce the same context.

Stable ordering improves:

- testing;
- reproducibility;
- future caching;
- prompt consistency.

---

### Token Management Should Be Introduced Separately

The first Context Builder implementation focuses on structure and identity preservation.

Token counting, compression and context window optimisation should be introduced only when real LLM integration requirements exist.

---

## Architectural Decisions Reinforced

- Context Builder depends on retrieval output, not retrieval implementation.
- Context generation is independent from LLM providers.
- Project remains the Aggregate Root.
- Chunk identity flows through the complete knowledge pipeline.
- Structured context is preferred over unstructured text generation.
- Missing knowledge produces diagnostics instead of failures.

---

## Future Improvements Identified

### Context Management

- Token counting.
- Context window optimisation.
- Context compression.
- Priority-based chunk selection.
- Parent-child context expansion.

---

### LLM Integration

- Prompt templates.
- Multiple LLM providers.
- Streaming responses.
- Conversation context management.

---

### Knowledge Persistence

- Persist generated contexts.
- Store context history.
- Incremental context regeneration.

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed (8 context tests, 103 total tests)

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

Ready for Milestone 9 — MCP Integration.

---

---

# Milestone 7.1 — Vector Store Lifecycle Management

## Objective

Introduce a dedicated vector store lifecycle management layer after the completion of the Retrieval and Context Builder milestones.

This milestone was introduced as an architectural correction after reviewing the evolution of the knowledge pipeline.

The initial Retrieval implementation correctly introduced the VectorStore abstraction, but further architectural analysis revealed that vector store ownership and lifecycle management required a dedicated responsibility.

The goal was to separate:

- vector storage lifecycle;
- retrieval behaviour;
- future persistence strategies.

This change prepares the architecture for future persistent vector databases without coupling retrieval logic to storage management.

---

## Reason for Introduction After Milestone 8

This milestone represents an architectural refinement rather than a planned pipeline stage.

During the implementation of the Retrieval and Context Builder layers, the architecture evolved and exposed a missing responsibility boundary.

The original retrieval design successfully isolated similarity search from concrete storage implementations, but the lifecycle of vector stores was still owned too closely by retrieval orchestration.

Further review identified that future requirements such as:

- persistent vector databases;
- project knowledge persistence;
- incremental updates;
- storage replacement strategies;

would require an explicit owner for vector store management.

Instead of introducing storage concerns into existing milestones, a dedicated milestone was created to correct the responsibility boundary while preserving the completed work.

This demonstrates the importance of continuous architecture review during incremental development.

---

## What Went Well

- The architecture review identified the missing responsibility before persistent storage integration.
- Existing Retrieval and Context Builder behaviour remained unchanged.
- Vector storage lifecycle was successfully separated from retrieval logic.
- The new `VectorStoreManager` introduced a clear ownership boundary.
- The Retriever remained independent from concrete storage implementations.
- Existing project domain boundaries were preserved.
- Future persistent vector database integration became possible without redesigning retrieval behaviour.

---

## Lessons Learned

### Architecture Must Evolve With New Knowledge

Early architectural decisions are based on available requirements and understanding.

As the platform grows, new responsibilities may emerge that were not visible initially.

The important principle is not avoiding change, but introducing changes that improve boundaries without breaking existing behaviour.

---

### A Storage Abstraction Needs a Lifecycle Owner

Introducing `VectorStore` as an interface solved replacement concerns, but it did not define who owns:

- creation;
- registration;
- replacement;
- removal.

The `VectorStoreManager` provides that missing ownership.

---

### Retrieval Should Consume Knowledge, Not Manage Storage

The Retriever should answer:

"Which embeddings are relevant?"

It should not answer:

"How are vector stores created and maintained?"

Keeping these concerns separate improves modularity and future extensibility.

---

### Refactoring Completed Milestones Can Be Necessary

The existing Retrieval implementation was functional and fully tested.

However, architectural quality sometimes requires revisiting previous assumptions.

The change was performed through a controlled refactor with regression validation rather than through redesign.

---

### Persistent Storage Should Be Introduced Only After Boundaries Are Stable

Introducing a real vector database before defining lifecycle ownership would couple infrastructure decisions too early.

The in-memory implementation was enough to validate the architecture first.

---

## Architectural Decisions Reinforced

- Vector store lifecycle belongs to a dedicated application service.
- Retriever depends only on the VectorStore contract.
- Storage implementations remain replaceable.
- Project domain remains independent from persistence concerns.
- Future vector databases can replace the current implementation without changing retrieval behaviour.

---

## Future Improvements Identified

### Vector Storage

- Persistent vector database implementation.
- Storage migration strategy.
- Vector indexing optimisation.
- Distributed storage support.

### Knowledge Persistence

- Persist project knowledge state.
- Synchronise embeddings with project changes.
- Incremental vector updates.

### Retrieval

- Metadata filtering.
- Hybrid retrieval.
- Advanced ranking strategies.

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed (108 automated tests)

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

---

# Milestone 9 — MCP Integration

## Objective

Introduce Model Context Protocol (MCP) as an external interface layer capable of exposing Codelp project knowledge and capabilities to external tools while preserving the existing architectural boundaries.

This milestone establishes the foundation for future IDE integrations, AI assistants and external development tools without coupling the domain model or internal processing pipeline to the MCP protocol.

---

## What Went Well

- MCP integration was introduced without modifying the Project aggregate design.
- The existing knowledge pipeline remained independent from external protocol concerns.
- MCP resources provided a structured way to expose project information.
- MCP tools provided a controlled way to execute project-related operations.
- Application services remained responsible for business logic while MCP acted as an adaptation layer.
- Tool execution was separated from tool registration and definition.
- Resource and tool registries provided an extensible foundation for future capabilities.
- Architecture boundary tests prevented MCP from depending on internal implementation details.
- Existing functionality remained stable after introducing the MCP layer.

---

## Lessons Learned

### External Protocols Should Be Introduced Through Adapter Layers

MCP should not influence the internal architecture of the platform.

The protocol acts as an external interface and should adapt existing application capabilities rather than introduce new business logic.

The dependency direction remains:

External Consumer

↓

MCP

↓

Application Services

↓

Domain

---

### Resources and Tools Represent Different Concepts

Resources expose structured project information.

Tools execute project-related operations.

Keeping these responsibilities separate avoids mixing data access with execution behaviour and provides clearer extension points.

---

### MCP Should Delegate, Not Duplicate Logic

MCP components should not contain domain or application logic.

They should delegate operations to existing services, ensuring that the same business rules are reused regardless of the consumer.

---

### External Consumers Should Not Affect Domain Design

The Project aggregate remains the source of truth.

The domain should not know that MCP exists or how external tools consume project knowledge.

This keeps the platform independent from specific protocols and integrations.

---

### Registries Enable Incremental Capability Growth

Tool and resource registries provide a simple extension mechanism.

New capabilities can be added without modifying the MCP server core, reducing coupling and improving maintainability.

---

### Architecture Tests Are Essential for Boundary Validation

Architecture tests proved valuable for ensuring that MCP remained isolated from internal implementation details.

Automated boundary validation prevents architectural erosion as new integrations are introduced.

---

## Architectural Decisions Reinforced

- MCP belongs to the application/interface boundary.
- The domain remains independent from external protocols.
- Resources expose structured knowledge without duplicating business logic.
- Tools delegate execution to application services.
- MCP contracts define communication boundaries, not business rules.
- External integrations should be replaceable without changing the core architecture.

---

## Future Improvements Identified

### MCP Integration

- Implement complete MCP protocol transport support.
- Add dynamic capability discovery.
- Support additional MCP resources and tools.
- Introduce authentication and access control mechanisms.

---

### Knowledge Exposure

- Expose project dependency information.
- Expose symbol navigation capabilities.
- Expose project evolution history.
- Add project analysis and impact exploration tools.

---

### Developer Experience

- IDE integration.
- AI assistant integration.
- CLI MCP client support.

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed (175 automated tests)

Code Review: Approved

Architecture Review: Approved

Documentation: Completed

Ready for Milestone 10 — Production Ready.

---

# Milestone 10.1 — Persistent Project Knowledge Boundary

## Objective

Introduce the architectural foundation required for persistent project knowledge without coupling storage concerns to the existing analysis pipeline.

This milestone represents the first step towards persistent Codelp knowledge.

The original Milestone 10 combined multiple large objectives:

- persistent project knowledge;
- external integrations;
- production readiness;
- configuration;
- plugin system;
- release preparation.

During architecture review, persistent knowledge was identified as a foundational capability that required independent design before production features could be introduced.

The milestone was separated to reduce architectural risk, preserve the completed pipeline and allow persistence concerns to evolve independently.

---

## Reason for Separation from Milestone 10

Persistent project knowledge introduces a fundamental architectural capability.

Unlike previous milestones that enriched the `Project` aggregate during a single execution, persistence requires Codelp to answer new questions:

- what project knowledge should survive between executions;
- who owns persisted state;
- how identities are reconstructed;
- how existing knowledge is loaded and updated;
- how storage remains independent from the domain.

Introducing these concerns together with external integrations and production features would increase complexity and make architectural validation harder.

A dedicated milestone was created to establish the persistence boundary first.

This allows future milestones to build on a stable foundation without modifying previous architectural decisions.

---

## What Went Well

- The existing Project aggregate remained unchanged as the source of truth.
- Persistence concerns were introduced without coupling storage to domain models.
- Existing pipeline responsibilities were preserved.
- Storage abstractions allowed future implementations without architectural changes.
- Deterministic identities created a strong foundation for future incremental analysis.
- Previous milestones remained stable and regression tests continued passing.
- The architecture review identified persistence boundaries before introducing real storage systems.

---

## Lessons Learned

### Persistence Should Be Designed Around Existing Domain Boundaries

Persistent storage should not become the source of truth.

The `Project` aggregate remains responsible for representing project knowledge.

Persistence is only a mechanism to store and restore that knowledge.

---

### Stable Identity Is a Requirement Before Persistence

Persistent knowledge depends on being able to recognise the same entity across executions.

The identity chain established in previous milestones:

```text
Source File
    ↓
Symbol ID
    ↓
Chunk ID
    ↓
Embedding Identity
```

provides the foundation required for future restoration and incremental updates.

---

### Storage Abstraction Should Exist Before Storage Technology

Choosing a database before defining ownership and lifecycle responsibilities would couple the architecture to infrastructure decisions too early.

The correct order is:

```text
Domain boundary

↓

Storage abstraction

↓

Lifecycle definition

↓

Concrete implementation
```

---

### Milestone Boundaries Should Follow Architectural Responsibility

Milestones are not only delivery checkpoints.

They are also architectural boundaries.

Separating Persistent Project Knowledge from Production Readiness allows each concern to be validated independently.

---

### Incremental Evolution Is Safer Than Large Architectural Changes

The completed pipeline from Scanner to MCP remained untouched.

The persistence work was introduced as an additional capability instead of modifying existing responsibilities.

This reduces regression risk and preserves previous architectural investments.

---

## Architectural Decisions Reinforced

- Project remains the Aggregate Root.
- Persistence must remain outside the domain.
- Storage implementations must be replaceable.
- Existing pipeline modules remain responsible only for knowledge generation.
- Persistent knowledge lifecycle requires an explicit architectural boundary.
- Deterministic identities are mandatory for future incremental analysis.

---

## Future Improvements Identified

### Persistent Knowledge

- Complete project metadata persistence.
- Persist file identities.
- Persist symbol identities.
- Persist chunk identities.
- Persist embedding metadata.
- Persist retrieval metadata.
- Knowledge versioning.

---

### Incremental Analysis

- Detect project changes.
- Identify affected files.
- Rebuild only invalidated knowledge.
- Synchronise changed embeddings.
- Preserve unchanged identities.

---

### Storage

- Validate serialization strategy.
- Handle corrupted knowledge state.
- Introduce persistent storage backend.
- Support knowledge migration between versions.

---

## Milestone Result

Status: Completed

Implementation: Completed

Architecture Review: Completed

Documentation: Updated

Prepared for Milestone 10.2 — Pipeline Knowledge Integration.

---

# Milestone 10.2 — Pipeline Knowledge Integration

## Objective

Integrate persistent project knowledge into the existing analysis pipeline while preserving existing module responsibilities and architectural boundaries.

This milestone connects the Persistent Project Knowledge capability with the execution lifecycle without making persistence a responsibility of individual pipeline components.

The goal was to establish:

- knowledge preparation before analysis;
- knowledge persistence after analysis;
- lifecycle ownership independent from storage implementation;
- compatibility with the existing Scanner → Parser → Indexer → Chunker → Embedding → Retrieval → Context pipeline.

---

## What Went Well

- Persistent knowledge integration was introduced without modifying existing pipeline responsibilities.
- The Project aggregate remained the source of truth during execution.
- Knowledge lifecycle management was isolated into a dedicated service.
- Existing analysis stages remained unaware of persistence concerns.
- Storage implementations remained replaceable through existing abstractions.
- The pipeline continued to preserve deterministic behaviour.
- Existing regression tests remained valid after lifecycle integration.
- Architecture boundary tests successfully prevented persistence concerns from leaking into unrelated modules.

---

## Lessons Learned

### Lifecycle Ownership Should Be Explicit

Persistence requires clear ownership of when knowledge is:

- loaded;
- prepared;
- updated;
- persisted.

Introducing a dedicated lifecycle service avoided spreading persistence decisions across multiple pipeline stages.

---

### The Pipeline Should Not Know About Storage

The analysis pipeline should coordinate knowledge generation, not persistence details.

The correct dependency direction remains:

```text
Pipeline
↓
Knowledge Lifecycle
↓
Knowledge Storage Abstraction
↓
Storage Implementation
```


This keeps future storage migrations independent from pipeline evolution.

---

### Optional Capabilities Should Preserve Existing Behaviour

Persistent knowledge integration was introduced as an additional capability.

The pipeline continues to operate correctly when persistence services are not provided.

This avoids forcing infrastructure concerns into the core execution flow.

---

### Architecture Tests Protect Long-Term Design

Functional tests validate behaviour.

Architecture tests validate boundaries.

Both are required to prevent future changes from accidentally coupling:

- domain;
- pipeline;
- persistence;
- storage implementations.

---

### Compatibility Is More Valuable Than Immediate Optimisation

The first integration focused on establishing correct ownership and boundaries.

Optimisations such as:

- selective restoration;
- incremental updates;
- partial pipeline execution;

remain future concerns after the architecture is stable.

---

## Architectural Decisions Reinforced

- Project remains the Aggregate Root.
- Pipeline modules remain responsible only for knowledge generation.
- Persistence lifecycle belongs to a dedicated application service.
- Storage remains replaceable through abstraction.
- Domain remains independent from persistence concerns.
- Existing deterministic identity strategy is preserved.

---

## Future Improvements Identified

### Incremental Analysis

- Detect changed project components.
- Reuse persisted knowledge.
- Invalidate affected knowledge selectively.
- Rebuild only required pipeline stages.

### Knowledge Evolution

- Persist file identities.
- Persist symbol identities.
- Persist chunk identities.
- Persist embedding metadata.
- Persist retrieval metadata.
- Introduce knowledge versioning.

### Storage

- Improve persistence backend capabilities.
- Add migration strategies.
- Handle incompatible knowledge versions.

---

## Milestone Result

Status: Completed

Implementation: Completed

Tests: Passed

Architecture Review: Completed

Code Review: Completed

Documentation: Completed

Ready for Milestone 10.3 — Incremental Analysis Foundation.

---

# Milestone 10.3 — Knowledge Persistence Foundation

## Objective

Establish the complete persistent knowledge foundation required for Codelp to preserve project understanding between executions.

This milestone transformed persistence from an architectural concept into a complete lifecycle capability while preserving the existing Project-centric architecture.

The objective was to ensure that project knowledge could be:

- represented;
- stored;
- validated;
- restored;
- evolved;

without coupling persistence concerns to the domain or analysis pipeline.

---

## What Went Well

- Persistent knowledge was introduced without modifying the Project aggregate responsibility.
- Runtime state and persisted state remained clearly separated.
- The complete knowledge lifecycle was implemented successfully.
- Stable identities were preserved across persistence cycles.
- Schema versioning created a foundation for future migrations.
- Storage implementations remained replaceable.
- Round-trip persistence validated knowledge equivalence between executions.
- Architecture validation confirmed existing boundaries remained intact.

---

## Lessons Learned

### Persistence Is a Lifecycle, Not a Storage Feature

Persistent knowledge requires more than saving objects.

A complete lifecycle must define:

- loading;
- validation;
- restoration;
- analysis;
- updating;
- persistence.

---

### The Runtime Domain Must Remain the Source of Truth

Persisted knowledge is a representation of project state, not the owner of project behaviour.

The Project aggregate remains responsible for runtime decisions.

---

### Identity Preservation Is Fundamental

Persistent systems require stable identities.

The existing identity chain:

Source File

↓

Symbol ID

↓

Chunk ID

↓

Embedding Identity

↓

Retrieval Identity

must remain deterministic across executions.

---

### Schema Versioning Should Exist Before Migrations Are Needed

Persistent data evolves over time.

Defining schema compatibility boundaries early prevents future migrations from becoming uncontrolled changes.

---

### Architecture Tests Protect Persistence Boundaries

Persistence introduces a high risk of accidental coupling.

Automated architecture tests ensure that storage concerns do not leak into domain and pipeline components.

---

## Architectural Decisions Reinforced

- Project remains Aggregate Root.
- Persistent knowledge is separate from runtime state.
- Domain remains independent from persistence.
- Storage remains replaceable.
- Lifecycle management belongs to application boundaries.
- Persistence must not bypass application services.

---

## Future Improvements Identified

### Incremental Analysis

- File content hashing.
- Change detection.
- Knowledge invalidation.
- Partial pipeline execution.
- Incremental updates.

### Knowledge Evolution

- Knowledge migration strategies.
- Historical project evolution.
- Knowledge graph relationships.

---

## Milestone Result

Status: Completed

Implementation: Completed

Architecture Review: Completed

Documentation: Completed

Tests: Passed (300 automated tests)

Prepared for Milestone 10.4 — Incremental Knowledge & Change Detection.