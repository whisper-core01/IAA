# Roadmap

The roadmap is ordered by evidence dependency, not by calendar promise.

## Phase 0 — Foundation

- freeze vocabulary and kernel responsibilities;
- record lineage and non-claims;
- define the first invariants and architecture-decision format;
- establish repository and licensing policy.

## Phase 1 — Contracts

- version neutral shared types and schemas;
- define admission, lifecycle, observability, and failure contracts;
- build conformance fixtures for replaceable organs and components;
- reject business semantics from kernel contracts.

## Phase 2 — Reference skeleton

- implement the smallest kernel boundaries needed to exercise contracts;
- add isolated reference organs without making them mandatory;
- create deterministic integration scenarios;
- publish reproducible test artifacts.

## Phase 3 — Adversarial evaluation

- model compromised organs, hosts, dependencies, and colluding participants;
- compare explicit baselines;
- measure failure and graceful degradation;
- update the threat model from observed evidence.

No phase authorizes security claims that have not passed the gates in
[`VALIDATION.md`](VALIDATION.md).

