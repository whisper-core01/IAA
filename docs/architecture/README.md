# Architecture

IAA separates stable semantic ownership from replaceable implementation.

```text
domain use-case
      |
components and organs
      |
versioned contracts
      |
IRIS | ARGOS | AORATOS
      |
integration evidence
```

ARKÉ is the mobile interface for communication between researchers or with
people already present in the user's phone contacts. IRIS performs the
matching. Every external ingress and egress crosses a SOL, the internal
anchoring organ that normalizes, validates, encapsulates, and publishes flows.
Exchanges use Reticulum or TCP. LoRa is restricted to text messages of at most
100 characters.

```text
mobile peer
  <-> ARKÉ (Reticulum | TCP | LoRa text <= 100 characters)
  <-> SOL (canonical ingress / egress)
  <-> IRIS (matching)
```

See [`SOL.md`](SOL.md) for the canonical SOL definition. Detailed identity,
consent, contact-access, routing, and data-handling contracts remain to be
defined before implementation.

Detailed runtime flows will be added only after their contracts are frozen.

