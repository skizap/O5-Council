from __future__ import annotations

import unittest

from o5_council.council_engine import CouncilEngine
from o5_council.models import AgentConfig, CouncilSignal, MemberResponse


class DummyClient:
    def chat_completion(self, **kwargs):  # pragma: no cover - not used in these tests
        raise NotImplementedError

    def extract_text(self, response_data):  # pragma: no cover - not used in these tests
        raise NotImplementedError


class CouncilEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        council = [AgentConfig(name="O5-1", role="Chair", model="demo-model")]
        self.engine = CouncilEngine(DummyClient(), council)

    def test_extract_signal_returns_clean_text_and_structured_signal(self) -> None:
        text = (
            "## Recommendation\n\nAdopt phased procurement.\n"
            '<o5_signal>{"preferred_option": "phased procurement", "confidence": 82, '
            '"consensus_ready": true, "key_risks": ["procurement delay"]}</o5_signal>'
        )
        cleaned, signal = self.engine._extract_signal(text)
        self.assertIn("Adopt phased procurement.", cleaned)
        self.assertEqual(signal.preferred_option, "phased procurement")
        self.assertEqual(signal.confidence, 82)
        self.assertTrue(signal.consensus_ready)
        self.assertEqual(signal.key_risks, ["procurement delay"])

    def test_summarize_round_detects_consensus(self) -> None:
        responses = [
            MemberResponse(
                agent_name=f"O5-{index}",
                role="Member",
                model="demo",
                round_number=1,
                content="Test",
                signal=CouncilSignal(
                    preferred_option="balanced modernization",
                    confidence=80,
                    consensus_ready=True,
                    key_risks=[],
                ),
            )
            for index in range(1, 4)
        ]
        responses.extend(
            [
                MemberResponse(
                    agent_name="O5-4",
                    role="Member",
                    model="demo",
                    round_number=1,
                    content="Test",
                    signal=CouncilSignal(
                        preferred_option="air-first posture",
                        confidence=66,
                        consensus_ready=False,
                        key_risks=[],
                    ),
                ),
                MemberResponse(
                    agent_name="O5-5",
                    role="Member",
                    model="demo",
                    round_number=1,
                    content="Test",
                    signal=CouncilSignal(
                        preferred_option="balanced modernization",
                        confidence=72,
                        consensus_ready=True,
                        key_risks=[],
                    ),
                ),
            ]
        )

        summary = self.engine._summarize_round(
            round_number=1,
            member_responses=responses,
            consensus_target=3,
        )
        self.assertEqual(summary.majority_option, "balanced modernization")
        self.assertEqual(summary.majority_count, 4)
        self.assertEqual(summary.ready_count, 4)
        self.assertTrue(summary.consensus_reached)


if __name__ == "__main__":
    unittest.main()
