# Validation

## Current result

The repository includes two bounded executable demonstrations:

- Collatz Scan runs 15 deterministic software checks. These finite calculations
  do not prove the Collatz conjecture.
- Hotel Reservation runs deterministic rule and integration checks covering
  independent IRIS activation of ARGOS and AORATOS, ARGOS manifest admission, contract rejection,
  deposits, availability, cleaning exclusion, cancellations, VIP upgrades,
  magnetic-key windows, planning output, and fictitious customer history.

These checks validate only the published reference behavior. They do not
establish a production runtime or any security, anonymity, cryptographic,
networking, privacy, physical-access, or resilience property.

Historical WHISPER results belong to that deprecated, unmaintained prototype
and are not carried forward as IAA evidence.

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
