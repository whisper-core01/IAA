# ARGOS

ARGOS is the domain-agnostic fact-production kernel. Scientific, mathematical,
and business implementations are external, replaceable components admitted by
contract.

`runtime/reference_kernel.py` admits a selected business component and
dispatches commands after activation by IRIS. ARGOS does not start itself and
does not know hotel, restaurant, cleaning, or magnetic-key rules before the
replaceable component is admitted.

ARGOS has no business-execution dependency on AORATOS. AORATOS protects data;
it does not load, select, or execute ARGOS business logic.

ARGOS owns fact-production semantics, not a particular component implementation.
