# Invariants

Initial invariants:

- **INV-001:** IRIS, ARGOS, and AORATOS contain no business logic.
- **INV-002:** kernels depend on contracts, never concrete implementations.
- **INV-003:** replacing one admitted organ does not change kernel semantics.
- **INV-004:** an unsupported capability is reported, not silently simulated.
- **INV-005:** ARKÉ is intended for mobile platforms.
- **INV-006:** ARKÉ connects researchers with one another or connects people
  already present in the user's phone contacts.
- **INV-007:** ARKÉ connections use Reticulum or TCP together with the SOL.
- **INV-008:** security claims remain no stronger than reproducible evidence.

Each invariant must later receive a versioned conformance test and an explicit
failure mode.

