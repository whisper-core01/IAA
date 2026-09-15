# AORATOS

AORATOS is the domain-agnostic data-security kernel. It protects data and does
not own, load, select, interpret, or execute business logic.

`security/reference_boundary.py` currently exposes lifecycle status only. It
reports `data_security: NOT_IMPLEMENTED`; no encryption, authentication,
authorization, isolation, retention, or privacy claim is made.

AORATOS is activated by IRIS independently from ARGOS. ARGOS business logic
must never depend on AORATOS for its semantics or execution.
