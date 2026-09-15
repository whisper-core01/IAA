# Architecture

IAA separates stable semantic ownership from replaceable implementation.

```text
domain use-case
      |
components and organs
      |
versioned contracts
      |
IRIS | ARGOS | AORATOS
      |
integration evidence
```

ARKÉ is the mobile connectivity component beside these boundaries. It connects
researchers with one another or connects people already present in the user's
phone contacts through Reticulum or TCP and the SOL. Its detailed contracts
and data-handling rules remain to be defined before implementation.

The canonical host and isolation topology is frozen in
[`DEPLOYMENT.md`](DEPLOYMENT.md): NixOS boots from a USB key containing a LUKS
partition, and IRIS, ARGOS, and AORATOS each run in a separate, independently
instantiable WASM sandbox.

Detailed runtime flows will be added only after their contracts are frozen.
