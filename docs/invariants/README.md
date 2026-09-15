# Invariants

Initial invariants:

- **INV-001:** IRIS, ARGOS, and AORATOS contain no business logic.
- **INV-002:** kernels depend on contracts, never concrete implementations.
- **INV-003:** replacing one admitted organ does not change kernel semantics.
- **INV-004:** an unsupported capability is reported, not silently simulated.
- **INV-005:** ARKÉ is the mobile interface.
- **INV-006:** IRIS performs the matching between researchers or with people
  already present in the user's phone contacts.
- **INV-007:** every ARKÉ ingress and egress crosses a SOL.
- **INV-008:** ARKÉ exchanges use Reticulum or TCP.
- **INV-009:** LoRa is restricted to text messages of at most 100 characters.
- **INV-010:** security claims remain no stronger than reproducible evidence.

The SOL-specific invariants are defined in [`docs/architecture/SOL.md`](../architecture/SOL.md).

Each invariant must later receive a versioned conformance test and an explicit
failure mode.

