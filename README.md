# IAA

**IRIS · ARGOS · AORATOS**

IAA is an experimental, contract-driven architecture for composing replaceable
software organs and components around three domain-agnostic kernels.

> **Current status: architecture scaffold.** This repository does not yet
> contain a production runtime and must not be presented or deployed as a
> secure communication system.

## Lineage

IAA is the architectural successor to the research recorded in
[`whisper-core01/whisper`](https://github.com/whisper-core01/whisper). Whisper is deprecated, no longer maintained, and remains public only as the
historical origin. IAA starts from a stricter baseline:
claims are limited to what the repository can currently demonstrate.

IAA is not a rename of Whisper, does not erase its history, and does not inherit
its unverified security claims. See [`docs/lineage/WHISPER.md`](docs/lineage/WHISPER.md).

## Kernels and boundary

| Entity | Responsibility |
| --- | --- |
| IRIS | Domain-agnostic kernel that initiates SOL and computes their fractal representations. |
| ARGOS | Domain-agnostic kernel that produces facts through replaceable scientific and mathematical engines. |
| AORATOS | Domain-agnostic infrastructure kernel; isolation, execution, storage, and security capabilities are external organs admitted by contract. |
| SOL | Internal anchoring organ and I/O boundary between raw external flows and canonical, typed, encapsulated Whisper flows. |
| ARKÉ | Mobile interface for communication between researchers or with people in the user's phone contacts. IRIS performs the matching. Every ingress and egress crosses a SOL. Exchanges use Reticulum or TCP; LoRa is limited to text messages of at most 100 characters. |

The canonical SOL definition is documented in [`docs/architecture/SOL.md`](docs/architecture/SOL.md).

## Founding rules

- Doctrine precedes implementation.
- Each organ has one explicit responsibility.
- IRIS, ARGOS, and AORATOS contain no business logic.
- Kernels depend on contracts, never concrete implementations.
- Organs and components remain replaceable without changing kernel semantics.
- Invariants are explicit, versioned, and testable.
- Security and resilience claims require reproducible evidence.

## Repository map

```text
docs/          doctrine, invariants, architecture, contracts, decisions, glossary
shared/        cross-kernel contracts and neutral types
iris/          IRIS boundary and future implementation
argos/         ARGOS boundary and future implementation
aoratos/       AORATOS boundary and future implementation
arke/          ARKÉ mobile interface and future implementation
organs/        replaceable organs grouped by owning contract surface
components/    replaceable technical and business components
integration/   conformance, scenarios, fixtures, and end-to-end validation
```

## Evidence status

Repository structure and doctrine coherence remain the only IAA-wide evidence.
[Collatz Scan](components/argos/engines/collatz/README.md) adds a narrowly scoped,
executable ARGOS experiment with 15 deterministic software checks. It does
**not** prove the Collatz conjecture and is not evidence for any IAA security
property.

No executable security, anonymity, cryptographic, networking, or resilience
claim is made. The evidence gates are defined in [`VALIDATION.md`](VALIDATION.md)
and the initial risk boundary in [`THREAT_MODEL.md`](THREAT_MODEL.md).

## License

IAA is licensed under the GNU Affero General Public License v3.0 only.

