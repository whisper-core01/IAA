# Contracts

Contracts are the only permitted dependency surface between kernels, organs,
and components.

Every contract must define:

- stable identity and semantic version;
- inputs, outputs, and forbidden data;
- lifecycle and failure behavior;
- capability negotiation and unsupported states;
- observability without leaking protected content;
- conformance fixtures and compatibility policy.

Source-specific or business-specific semantics must remain in adapters or
components, not in the shared contract.

