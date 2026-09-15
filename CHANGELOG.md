# Changelog

All notable changes to IAA will be documented here.

## Unreleased

- Documented the canonical NixOS-on-USB deployment with a LUKS partition and
  three independently instantiable WASM sandboxes, one each for IRIS, ARGOS,
  and AORATOS. The Python reference path is explicitly not evidence that this
  deployment is implemented.
- Added an IRIS reference launcher that activates ARGOS and AORATOS
  independently for canonical fixture scenarios. ARGOS alone admits and
  executes business logic; AORATOS remains restricted to data security.
  Executable SOL normalization remains explicitly unimplemented.
- Added the Hotel Reservation business component with deterministic booking,
  deposit, cancellation, VIP upgrade, cleaning, and magnetic-key rules.
- Added generated room planning and fictitious customer views with stay
  duration, birthday, and restaurant reservation history.
- Published Collatz Scan as an experimental ARGOS engine with runnable CPU
  sources, bounded datasets, provenance hashes, and 15 deterministic checks.
  These checks do not prove the Collatz conjecture.
- Created the public IAA architecture scaffold.
- Declared the WHISPER lineage without inheriting unverified claims.
- Added doctrine, responsibility boundaries, threat model, roadmap, validation
  gates, contribution rules, and AGPL-3.0-only licensing.
- Corrected ARKÉ as the mobile interface. IRIS performs the matching; every
  ingress and egress crosses a SOL; exchanges use Reticulum or TCP; LoRa is
  limited to text messages of at most 100 characters.
- Added the canonical SOL definition, its internal organs, protocols, types,
  flows, and non-negotiable invariants.
