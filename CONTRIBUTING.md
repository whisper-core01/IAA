# Contributing

Contributions must preserve the doctrine, explicit boundaries, and factual
status of the project.

Before proposing implementation:

- identify the owning contract and responsibility;
- keep business logic out of IRIS, ARGOS, and AORATOS;
- avoid coupling a kernel to a concrete organ or component;
- add conformance and negative tests with the change;
- record semantic decisions in `docs/decisions/`;
- describe limitations and failure modes;
- never promote an intention or passing demo into an unverified security claim.

Security reports belong in the private channel described by `SECURITY.md`, not
in public issues.

