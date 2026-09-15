# Validation

## Current result

The repository validates documentation structure and includes one narrowly
scoped executable experiment: [Collatz Scan](components/argos/engines/collatz/README.md).
Its standard-library verification runs 15 deterministic unit and CPU integration
tests and syntax-checks the optional OpenCL source. OpenCL execution is not
validated when a compatible GPU and driver are absent.

These checks validate bounded software behavior only. Collatz Scan does not
prove the Collatz conjecture, and its results are not IAA runtime, benchmark,
security, anonymity, cryptographic, networking, or resilience evidence.

Historical WHISPER Remote Nerve results belong to that deprecated, unmaintained
prototype and are not carried forward as IAA evidence.

## Evidence gates

Every future capability must pass, as applicable:

1. contract and schema validation;
2. deterministic conformance tests;
3. integration tests across replaceable implementations;
4. negative and adversarial tests;
5. reproducible benchmark capture;
6. documented assumptions and failure conditions;
7. independent review before security wording is promoted.

Results must identify the exact commit, toolchain, configuration, dataset or
seed, command, and raw artifact.

