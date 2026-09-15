# ARGOS business scenario contract v1

`IAA.ARGOS.BUSINESS.SCENARIO.v1` is the first executable reference contract
between the domain-agnostic ARGOS kernel and a replaceable business component.

## Activation

The user launches IRIS. IRIS activates ARGOS and AORATOS independently. ARGOS
admits and executes the business component. AORATOS is responsible only for
data security and neither loads nor interprets business logic.

IRIS is also responsible for initiating SOL. Executable SOL normalization does
not exist in this reference path yet, so the launcher accepts canonical fixture
input only and reports `SOL: NOT_IMPLEMENTED` in its result.

## Input envelope

```json
{
  "contract": "IAA.ARGOS.BUSINESS.SCENARIO.v1",
  "component_id": "hotel-reservation",
  "configuration": {},
  "commands": []
}
```

The component is admitted only when the envelope and `component.json` declare
the same contract and component identity. Commands are dispatched in array
order to one scenario-local component session.

## Output envelope

The IRIS result identifies the activation order, the exact SOL limitation, and
the nested `IAA.ARGOS.BUSINESS.RESULT.v1` result. JSON keys are sorted for
reproducibility.

## Current boundary

This is not a persistent runtime. The admitted Python entrypoint executes with
the launcher's process permissions. Raw-input normalization, network services,
durable storage, concurrency control, and executable AORATOS data-security
capabilities are not implemented.
