import json
from pathlib import Path
import sys
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT))

from argos.runtime.reference_kernel import AdmissionError
from iris.runtime.reference_launcher import IrisLauncher


class ArgosIntegrationTest(unittest.TestCase):
    def scenario(self):
        return json.loads((PACKAGE_ROOT / "demo" / "argos-scenario.json").read_text(encoding="utf-8"))

    def test_iris_activates_argos_and_aoratos_independently_then_runs_scenario(self):
        result = IrisLauncher().execute(PACKAGE_ROOT, self.scenario())
        self.assertEqual(["IRIS", "ARGOS", "AORATOS"], result["activation_order"])
        self.assertEqual("OUT_OF_SCOPE", result["aoratos"]["business_logic"])
        self.assertEqual("NOT_IMPLEMENTED", result["aoratos"]["data_security"])
        self.assertEqual("NOT_IMPLEMENTED", result["sol"]["status"])
        self.assertEqual("IAA.ARGOS.BUSINESS.RESULT.v1", result["argos"]["contract"])
        self.assertEqual("hotel-reservation", result["argos"]["component_id"])
        reservation = result["argos"]["results"][0]["result"]["reservation"]
        self.assertEqual("DELUXE", reservation["assigned_category"])
        self.assertEqual(2640, reservation["key_duration_minutes"])
        customer = result["argos"]["results"][3]["result"]
        self.assertEqual("Restaurant démo A", customer["restaurant_history"][0]["restaurant"])

    def test_argos_has_no_aoratos_business_dependency(self):
        launcher = IrisLauncher()
        launcher.activate()
        self.assertFalse(hasattr(launcher.argos, "_aoratos"))

    def test_iris_activation_is_idempotent(self):
        launcher = IrisLauncher()
        launcher.activate()
        launcher.activate()
        self.assertEqual(["IRIS", "ARGOS", "AORATOS"], launcher.activation_order)

    def test_argos_rejects_contract_mismatch(self):
        envelope = self.scenario()
        envelope["contract"] = "WRONG"
        with self.assertRaisesRegex(AdmissionError, "contract mismatch"):
            IrisLauncher().execute(PACKAGE_ROOT, envelope)

    def test_argos_rejects_component_identity_mismatch(self):
        envelope = self.scenario()
        envelope["component_id"] = "other-component"
        with self.assertRaisesRegex(AdmissionError, "component_id mismatch"):
            IrisLauncher().execute(PACKAGE_ROOT, envelope)


if __name__ == "__main__":
    unittest.main()
