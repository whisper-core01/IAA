# IAA

**IRIS · ARGOS · AORATOS**

IAA is an experimental, contract-driven architecture for composing replaceable
software organs and components around three domain-agnostic kernels.

> **Current status: architecture scaffold with bounded reference paths.** This
> repository does not contain a production runtime and must not be presented or
> deployed as a secure communication, booking, or access-control system.

## Lineage

IAA is the architectural successor to the research recorded in
[`whisper-core01/whisper`](https://github.com/whisper-core01/whisper). Whisper
is deprecated, no longer maintained, and remains public only as the historical
origin. IAA starts from a stricter baseline: claims are limited to what the
repository can currently demonstrate.

IAA is not a rename of Whisper, does not erase its history, and does not inherit
its unverified security claims. See [`docs/lineage/WHISPER.md`](docs/lineage/WHISPER.md).

## Kernels and boundary

| Entity | Responsibility |
| --- | --- |
| IRIS | Domain-agnostic kernel and startup owner. It initiates SOL, activates ARGOS and AORATOS, and computes SOL fractal representations. |
| ARGOS | Domain-agnostic fact-production kernel that dispatches work to replaceable scientific, mathematical, or business components. |
| AORATOS | Domain-agnostic data-security kernel. It protects data and has no responsibility for business logic or its execution. |
| SOL | Internal anchoring organ and I/O boundary between raw external flows and canonical, typed, encapsulated flows. |
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
iris/          IRIS boundary, startup, and future implementation
argos/         ARGOS boundary, reference dispatch, and future implementation
aoratos/       AORATOS data-security boundary and future implementation
arke/          ARKÉ mobile interface and future implementation
organs/        replaceable organs grouped by owning contract surface
components/    replaceable technical and business components
integration/   conformance, scenarios, fixtures, and end-to-end validation
```

## Evidence status

[Collatz Scan](components/argos/engines/collatz/README.md) is a bounded numerical
experiment with 15 deterministic software checks. It does **not** prove the
Collatz conjecture and is not evidence for any IAA security property.

[Hotel Reservation](components/argos/business/hotel_reservation/README.md) is a
replaceable business component launched through IRIS. IRIS activates ARGOS and
AORATOS independently; ARGOS alone admits and executes the business component.
Its tests cover only the published finite rules and reference views.

No executable security, anonymity, cryptographic, networking, or resilience
claim is made. The evidence gates are defined in [`VALIDATION.md`](VALIDATION.md)
and the initial risk boundary in [`THREAT_MODEL.md`](THREAT_MODEL.md).

## License

IAA is licensed under the GNU Affero General Public License v3.0 only.
