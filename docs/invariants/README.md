# Invariants

Initial invariants:

- **INV-001:** IRIS, ARGOS, and AORATOS contain no business logic.
- **INV-002:** kernels depend on contracts, never concrete implementations.
- **INV-003:** replacing one admitted organ does not change kernel semantics.
- **INV-004:** an unsupported capability is reported, not silently simulated.
- **INV-005:** ARKE supplies directory content only through its defined Wasm boundary.
- **INV-006:** ARKE does not initiate SOL or compute fractal representations.
- **INV-007:** security claims remain no stronger than reproducible evidence.

Each invariant must later receive a versioned conformance test and an explicit
failure mode.

