# Canonical deployment model

## Host and encrypted medium

IAA's canonical deployment boots **NixOS from a USB key**. The key includes a
**LUKS-encrypted partition**. This is the required deployment topology, not an
optional packaging detail.

LUKS addresses encryption at rest for the partition. Its presence alone does
not establish secure key handling, protection while mounted, secure deletion,
integrity, anonymity, or resistance to a compromised running host.

## Three independently instantiable environments

IRIS, ARGOS, and AORATOS are independently instantiable. Each kernel executes
inside its **own WebAssembly environment and its own sandbox**:

| Instance | Environment | Responsibility |
| --- | --- | --- |
| IRIS | Separate WASM sandbox | Startup and orchestration; initiates SOL and activates ARGOS and AORATOS instances. |
| ARGOS | Separate WASM sandbox | Admits and executes replaceable business, scientific, or mathematical logic. |
| AORATOS | Separate WASM sandbox | Data security only; never loads or executes ARGOS business logic. |

One shared WASM instance for all three kernels is non-conforming. Instance
lifecycle, admission, restart, and failure must remain explicit per kernel.
Cross-kernel exchanges must use versioned contracts rather than merging kernel
responsibilities.

## Public implementation status

The current public Python reference launcher demonstrates responsibility and
activation order only. It runs in one Python process and therefore **does not
implement or prove** the canonical NixOS, USB, LUKS, WASM, or sandbox deployment.

Before the deployment model can be reported as reproduced, the repository must
publish and validate at least:

- the reproducible NixOS configuration and USB build procedure;
- the partition layout and LUKS provisioning procedure, without publishing
  secrets;
- three separate WASM artifacts or module definitions;
- the sandbox configuration and inter-instance contract channels;
- isolation, restart, failure, and sandbox-escape tests.
