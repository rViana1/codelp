# ADR-010 — Vector Store Lifecycle Management

## Status

Accepted

## Date

2026-08-12

---

## Context

Codelp requires semantic retrieval capabilities over project knowledge.

Initially, retrieval operations interacted directly with vector storage during the retrieval workflow. This approach was acceptable for the initial implementation but created coupling between retrieval behaviour and storage lifecycle.

This introduced the following limitations:

- Retrieval logic depended on vector storage management details.
- Vector store lifecycle was not explicitly controlled.
- Future migration to persistent vector databases would require changes in retrieval components.

As Codelp evolves, vector storage must become an independent application concern.

The architecture needs to support:

- multiple vector storage implementations;
- future persistent vector databases;
- project-specific vector store lifecycle management;
- preservation of Retriever simplicity.

---

## Decision

A dedicated Vector Store lifecycle management layer was introduced.

The architecture now separates responsibilities:

RetrievalService

    |

    v

VectorStoreManager

    |

    v

VectorStoreFactory

    |

    v

VectorStore implementation


### VectorStoreManager

Responsible for:

- registering project vector stores;
- retrieving project vector stores;
- removing project vector stores;
- managing vector storage lifecycle.

### VectorStoreFactory

Responsible for:

- creating vector store implementations;
- hiding concrete storage creation details;
- enabling future storage replacement.

### VectorStore

Remains the abstraction consumed by retrieval components.

The Retriever does not know:

- how vector stores are created;
- where vectors are stored;
- how storage lifecycle is managed.

---

## Consequences

### Positive consequences

- Retrieval becomes independent from storage implementation.
- Persistent vector databases can be introduced without modifying Retriever behaviour.
- Vector storage lifecycle is explicitly managed.
- Application responsibilities are better separated.
- Future storage integrations become easier.

### Negative consequences

- Additional application layer introduced.
- More components must be coordinated.
- Factory abstraction exists before persistent storage is required.

---

## Alternatives Considered

### Keep vector storage inside RetrievalService

Rejected.

Reasons:

- Retrieval would remain coupled to storage lifecycle.
- Future storage replacement would require retrieval changes.

### Let Retriever manage vector storage

Rejected.

Reasons:

- Retriever should only perform similarity search.
- Storage lifecycle is not part of retrieval responsibility.

### Introduce persistent vector database immediately

Rejected.

Reasons:

- Current requirements do not require persistence.
- The abstraction should exist before adding infrastructure complexity.

---

## Implementation Details

Implemented components:

backend/app/vectorstore/

- __init__.py
- factory.py
- inmemory.py
- interfaces.py
- manager.py
- models.py


Integration:

RetrievalService

    |

    +--> VectorStoreManager

              |

              +--> VectorStoreFactory

                         |

                         +--> InMemoryVectorStore


---

## Validation

The implementation was validated through:

- VectorStoreManager tests;
- project registration tests;
- project retrieval tests;
- missing store handling tests;
- retrieval regression tests;
- complete pipeline regression tests.

Test status:

108 passed

---

## Result

Codelp now has an extensible vector storage architecture where retrieval remains independent from storage lifecycle and implementation details.

Future vector database integrations can be introduced without changing Retriever behaviour.
EOF
