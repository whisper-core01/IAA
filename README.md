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
| ARKÉ | Mobile connectivity component that connects researchers with one another or connects people already present in the user's phone contacts, through Reticulum or TCP and the SOL. |

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
arke/          ARKÉ mobile connectivity boundary and future implementation
organs/        replaceable organs grouped by owning contract surface
components/    replaceable technical and business components
integration/   conformance, scenarios, fixtures, and end-to-end validation
```

## Evidence status

The initial commit validates only repository structure and doctrine coherence.
No executable security, anonymity, cryptographic, networking, or resilience
claim is made. The evidence gates are defined in [`VALIDATION.md`](VALIDATION.md)
and the initial risk boundary in [`THREAT_MODEL.md`](THREAT_MODEL.md).

## License

IAA is licensed under the GNU Affero General Public License v3.0 only.

