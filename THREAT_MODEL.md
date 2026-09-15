# Threat model

## Status

This is the initial threat-model boundary for an architecture scaffold. It is
not evidence that any threat is currently mitigated.

## Assets considered

- contract integrity and version identity;
- kernel semantic stability;
- organ admission decisions;
- isolation boundaries;
- provenance of components and evidence;
- mobile contact data and connection metadata handled by ARKÉ;
- confidentiality, integrity, and availability of future payloads and metadata.

## Adversaries to model

- a malicious or compromised organ;
- a compromised host or execution environment;
- colluding network participants;
- a dependency or supply-chain attacker;
- an observer correlating timing, volume, identity, or topology;
- a contributor introducing an incompatible semantic change.

## Initial non-claims

IAA currently provides no demonstrated:

- encryption, key exchange, anonymity, or metadata confidentiality;
- secure deletion or protected persistence;
- network-path independence or Sybil resistance;
- sandbox escape resistance;
- protection from a compromised host;
- formal proof of any runtime property.

## Required evidence before a claim

A claim must name its scope, adversary, assumptions, test method, result,
failure threshold, and reproducible artifact. A design intention, diagram, unit
test, or successful demonstration is not by itself a security proof.

