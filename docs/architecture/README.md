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

ARKÉ is the mobile interface. IRIS performs the connection, using the SOL,
between researchers or with people already present in the user's phone
contacts. Exchanges use Reticulum or TCP. LoRa is restricted to text messages
of at most 100 characters. Detailed identity, consent, contact-access, routing,
and data-handling contracts remain to be defined before implementation.

Detailed runtime flows will be added only after their contracts are frozen.

