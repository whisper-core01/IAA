"""Minimal AORATOS data-security lifecycle boundary.

No security capability is implemented yet. This class exists only to make the
activation boundary explicit without coupling AORATOS to business execution.
"""

from __future__ import annotations


class AoratosDataSecurity:
    def __init__(self) -> None:
        self.active = False

    def activate(self) -> None:
        if self.active:
            return
        self.active = True

    def status(self) -> dict[str, str]:
        return {
            "kernel": "AORATOS",
            "lifecycle": "ACTIVE" if self.active else "INACTIVE",
            "data_security": "NOT_IMPLEMENTED",
            "business_logic": "OUT_OF_SCOPE",
        }
