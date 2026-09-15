# Invariants

Initial invariants:

- **INV-001:** IRIS, ARGOS, and AORATOS contain no business logic.
- **INV-002:** kernels depend on contracts, never concrete implementations.
- **INV-003:** replacing one admitted organ does not change kernel semantics.
- **INV-004:** an unsupported capability is reported, not silently simulated.
- **INV-005:** ARKÉ is the mobile interface.
- **INV-006:** IRIS performs the connection, using the SOL, between researchers
  or with people already present in the user's phone contacts.
- **INV-007:** ARKÉ exchanges use Reticulum or TCP.
- **INV-008:** LoRa is restricted to text messages of at most 100 characters.
- **INV-009:** security claims remain no stronger than reproducible evidence.

Each invariant must later receive a versioned conformance test and an explicit
failure mode.

