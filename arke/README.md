# ARKÉ

ARKÉ is the mobile interface of IAA.

It supports communication between researchers or with people already present
in the user's phone contacts. IRIS performs the matching.

Every external ingress and egress crosses a SOL. The SOL is the internal
anchoring organ and I/O boundary that normalizes, validates, encapsulates, and
publishes flows. ARKÉ does not own those SOL responsibilities.

Exchanges use Reticulum or TCP. LoRa is available only for text messages of at
most 100 characters.

ARKÉ's identity, consent, contact-access, routing, and data-handling contracts
must be defined explicitly before implementation. This document does not assume
a particular mobile framework or runtime.

See [`docs/architecture/SOL.md`](../docs/architecture/SOL.md) for the canonical
SOL definition.

