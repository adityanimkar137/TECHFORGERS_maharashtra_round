import json
import unittest
from pathlib import Path

from app.engine import ReplayEngine


class ReplayEngineTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        path = Path(__file__).parents[1] / "data" / "sample_run.json"
        cls.sample_run = json.loads(
            path.read_text(encoding="utf-8")
        )

    def setUp(self):
        self.engine = ReplayEngine()

    def test_checkpoint_is_created(self):
        checkpoint = self.engine.create_checkpoint(
            self.sample_run,
            3
        )

        self.assertEqual(
            checkpoint["run_id"],
            "RUN-001"
        )

        self.assertEqual(
            checkpoint["step_id"],
            3
        )

        self.assertEqual(
            len(checkpoint["steps_before"]),
            2
        )

    def test_replay_with_bad_value_stays_failed(self):
        replay = self.engine.replay(
            self.sample_run,
            start_step=3,
            modified_outputs={
                3: "bad-value"
            },
        )

        self.assertEqual(
            replay["status"],
            "failed"
        )

    def test_replay_with_corrected_value_succeeds(self):
        replay = self.engine.replay(
            self.sample_run,
            start_step=3,
            modified_outputs={
                3: "₹45999"
            },
        )

        self.assertEqual(
            replay["status"],
            "success"
        )

        self.assertEqual(
            replay["steps"][2]["status"],
            "success"
        )

    def test_comparison_detects_fix(self):
        replay = self.engine.replay(
            self.sample_run,
            start_step=3,
            modified_outputs={
                3: "₹45999"
            },
        )

        comparison = self.engine.compare(
            self.sample_run,
            replay
        )

        self.assertTrue(
            comparison["fixed"]
        )

        self.assertGreater(
            comparison["changed_step_count"],
            0
        )


if __name__ == "__main__":
    unittest.main()
