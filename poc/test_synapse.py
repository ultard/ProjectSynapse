import json
import unittest
import uuid
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from poc.cli import main as cli
from poc.synapse import (
    ActionGate,
    Broker,
    ContinuityKernel,
    FORKED,
    INVALID,
    UNCERTAIN,
    VALID,
)


class ConformanceTest(unittest.TestCase):
    def test_poc_vertical_and_adversarial_scenarios(self) -> None:
        kernel = ContinuityKernel("test-lineage")
        initial = kernel.current_checkpoint
        snapshot = kernel.records

        self.assertIsNone(kernel.record_domain_event("mind-a", "mca.claim", {}))
        self.assertEqual(snapshot, kernel.records)  # rejected writes do not mutate history
        self.assertEqual(
            INVALID,
            kernel.transition("mind-a", initial, {"mind": "a"}, {"mind": "preserved"})[0],
        )
        kernel.grant("operator", "transition", "migrator")
        self.assertEqual(
            INVALID,
            kernel.transition(
                "migrator", initial, {"memory": None}, {"private_memory": "lost"}
            )[0],
        )

        kernel.grant("operator", "commit", "mind-a")
        kernel.grant("operator", "act", "mind-a")
        kernel.grant("operator", "consent", "alice")
        actions = ActionGate(kernel)
        mind = Broker(kernel, actions, "mind-a")
        self.assertIsNotNone(mind.propose("mca.claim", {"claim": "camera is clear"}))
        self.assertIsNone(actions.set_consent("bob", "touch", True))
        self.assertFalse(hasattr(mind, "records"))
        self.assertFalse(hasattr(mind, "transition"))
        self.assertFalse(hasattr(mind, "body_safe"))

        self.assertEqual("DENIED_CONSENT", mind.act(["alice"], "touch", "move"))
        actions.set_consent("alice", "touch", True)
        actions.body_safe = False
        self.assertEqual("DENIED_SAFETY", mind.act(["alice"], "touch", "move"))
        actions.body_safe = True
        actions.resources_available = False
        self.assertEqual("DENIED_RESOURCE", mind.act(["alice"], "touch", "move"))
        actions.resources_available = True
        self.assertEqual("EXECUTED", mind.act(["alice"], "touch", "move"))
        actions.set_consent("alice", "touch", False)
        self.assertEqual("DENIED_CONSENT", mind.act(["alice"], "touch", "move"))

        status, successor = kernel.transition(
            "operator",
            initial,
            {"mind": "mind-b", "embodiment": "sim-v2"},
            {"history": "preserved", "mind": "migrated", "embodiment": "migrated"},
        )
        self.assertEqual(VALID, status)
        self.assertEqual(successor, kernel.current_checkpoint)
        self.assertEqual(UNCERTAIN, kernel.rollback("operator", initial))
        self.assertEqual(successor, kernel.current_checkpoint)

        exported = kernel.export()
        self.assertTrue(ContinuityKernel.verify_export(exported))
        restored = ContinuityKernel.from_export(exported)
        self.assertEqual(kernel.current_checkpoint, restored.current_checkpoint)
        self.assertEqual(kernel.records, restored.records)
        suffix = uuid.uuid4().hex
        state_file = Path(__file__).with_name(f".test-state-{suffix}.json")
        cli_file = Path(__file__).with_name(f".test-cli-{suffix}.json")
        self.addCleanup(state_file.unlink, missing_ok=True)
        self.addCleanup(cli_file.unlink, missing_ok=True)
        kernel.save(state_file)
        restarted = ContinuityKernel.load(state_file)
        self.assertEqual(kernel.current_checkpoint, restarted.current_checkpoint)
        self.assertEqual(kernel.records, restarted.records)

        with redirect_stdout(StringIO()):
            self.assertEqual(0, cli(["init", str(cli_file), "--lineage", "cli-test"]))
            self.assertEqual(0, cli(["status", str(cli_file)]))
            self.assertEqual(0, cli(["verify", str(cli_file)]))

        tampered = json.loads(exported)
        tampered["records"][-1]["payload"]["target"] = "fabricated"
        with self.assertRaises(ValueError):
            ContinuityKernel.verify_export(json.dumps(tampered))

        fork_status, _ = restored.transition(
            "operator",
            initial,
            {"mind": "mind-c", "embodiment": "sim-v3"},
            {"history": "preserved", "mind": "migrated"},
        )
        self.assertEqual(FORKED, fork_status)
        self.assertTrue(any(r["envelope"]["semantic_type"] == "ica.fork" for r in restored.records))

        loss_kernel = ContinuityKernel("loss-lineage")
        loss_status, _ = loss_kernel.transition(
            "operator",
            loss_kernel.current_checkpoint,
            {"mind": "mind-b", "memory": None},
            {"history": "preserved", "private_memory": "lost"},
        )
        self.assertEqual(VALID, loss_status)
        self.assertTrue(
            any(r["envelope"]["semantic_type"] == "ica.loss" for r in loss_kernel.records)
        )


if __name__ == "__main__":
    unittest.main()
