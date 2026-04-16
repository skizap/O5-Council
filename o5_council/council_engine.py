from __future__ import annotations

import json
import re
from collections import Counter
from typing import Callable

from o5_council.models import AgentConfig, CouncilSignal, FinalRunResult, MemberResponse, RoundSummary
from o5_council.openrouter_client import OpenRouterClient

SIGNAL_PATTERN = re.compile(r"<o5_signal>\s*(\{.*?\})\s*</o5_signal>", re.DOTALL)
ProgressCallback = Callable[[str, dict], None]
CancelCheck = Callable[[], bool]


class CouncilRunCancelled(RuntimeError):
    pass


class CouncilEngine:
    def __init__(
        self,
        client: OpenRouterClient,
        council: list[AgentConfig],
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_check: CancelCheck | None = None,
    ) -> None:
        self.client = client
        self.council = council
        self.progress_callback = progress_callback or (lambda _event, _payload: None)
        self.cancel_check = cancel_check or (lambda: False)

    def run(
        self,
        *,
        task_mode: str,
        prompt: str,
        context: str,
        max_rounds: int,
        consensus_target: int,
    ) -> FinalRunResult:
        rounds: list[RoundSummary] = []

        for round_number in range(1, max_rounds + 1):
            self._ensure_not_cancelled()
            self._emit(
                "status",
                {
                    "message": f"Starting round {round_number} of {max_rounds}.",
                    "round_number": round_number,
                },
            )
            review_packet = self._build_review_packet(rounds)
            member_responses: list[MemberResponse] = []

            for agent in self.council:
                self._ensure_not_cancelled()
                self._emit(
                    "status",
                    {
                        "message": f"Requesting {agent.name} using model {agent.model}.",
                        "agent_name": agent.name,
                        "round_number": round_number,
                    },
                )
                member_response = self._collect_member_response(
                    agent=agent,
                    task_mode=task_mode,
                    prompt=prompt,
                    context=context,
                    round_number=round_number,
                    review_packet=review_packet,
                )
                member_responses.append(member_response)
                self._emit(
                    "member_response",
                    {
                        "response": member_response,
                        "round_number": round_number,
                    },
                )

            round_summary = self._summarize_round(
                round_number=round_number,
                member_responses=member_responses,
                consensus_target=consensus_target,
            )
            rounds.append(round_summary)
            self._emit(
                "round_complete",
                {
                    "summary": round_summary,
                    "round_number": round_number,
                },
            )
            if round_summary.consensus_reached:
                break

        final_markdown, synthesized_by = self._synthesize_final_answer(
            task_mode=task_mode,
            prompt=prompt,
            context=context,
            rounds=rounds,
        )
        final_majority_option = rounds[-1].majority_option if rounds else "undetermined"
        return FinalRunResult(
            task_mode=task_mode,
            prompt=prompt,
            context=context,
            rounds=rounds,
            final_markdown=final_markdown,
            consensus_reached=rounds[-1].consensus_reached if rounds else False,
            final_majority_option=final_majority_option,
            synthesized_by=synthesized_by,
        )

    def _collect_member_response(
        self,
        *,
        agent: AgentConfig,
        task_mode: str,
        prompt: str,
        context: str,
        round_number: int,
        review_packet: str,
    ) -> MemberResponse:
        messages = self._build_member_messages(
            agent=agent,
            task_mode=task_mode,
            prompt=prompt,
            context=context,
            round_number=round_number,
            review_packet=review_packet,
        )
        response_data = self.client.chat_completion(
            model=agent.model,
            messages=messages,
            temperature=agent.temperature,
        )
        raw_text = self.client.extract_text(response_data)
        cleaned_content, signal = self._extract_signal(raw_text)
        return MemberResponse(
            agent_name=agent.name,
            role=agent.role,
            model=agent.model,
            round_number=round_number,
            content=cleaned_content,
            signal=signal,
            raw_response=response_data,
        )

    def _build_member_messages(
        self,
        *,
        agent: AgentConfig,
        task_mode: str,
        prompt: str,
        context: str,
        round_number: int,
        review_packet: str,
    ) -> list[dict[str, str]]:
        system_prompt = (
            "You are a member of the O5 Council, a five-model deliberative panel. "
            f"Your role is {agent.role}. Produce rigorous, practical reasoning in markdown. "
            "Be concise but substantive. You must end your answer with an XML-wrapped JSON signal block exactly in this form: "
            "<o5_signal>{\"preferred_option\": \"short label\", \"confidence\": 0, \"consensus_ready\": false, \"key_risks\": [\"risk one\"]}</o5_signal>. "
            "The confidence value must be an integer between 0 and 100. The preferred option must be a short reusable label."
        )

        if round_number == 1:
            user_prompt = (
                f"Task mode: {task_mode}\n\n"
                f"User request:\n{prompt.strip()}\n\n"
                f"Additional context:\n{context.strip() or 'No additional context provided.'}\n\n"
                "Write your answer with the following sections: Overview, Recommendation, Rationale, Risks, and Next Steps."
            )
        else:
            user_prompt = (
                f"Task mode: {task_mode}\n\n"
                f"Original user request:\n{prompt.strip()}\n\n"
                f"Additional context:\n{context.strip() or 'No additional context provided.'}\n\n"
                f"Council review packet from previous rounds:\n{review_packet}\n\n"
                "Revise your position in light of the other members' views. Identify convergence and unresolved disagreements. "
                "Use the same sections as before and update your final signal block to reflect your current stance."
            )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _build_review_packet(self, rounds: list[RoundSummary]) -> str:
        if not rounds:
            return "No previous council output is available."

        latest_round = rounds[-1]
        sections: list[str] = [
            f"Latest round: {latest_round.round_number}",
            f"Majority option: {latest_round.majority_option}",
            f"Ready count: {latest_round.ready_count}",
            f"Majority count: {latest_round.majority_count}",
            "Member positions:",
        ]
        for response in latest_round.member_responses:
            excerpt = self._truncate(response.content, 900)
            sections.append(
                "\n".join(
                    [
                        f"- Member: {response.agent_name}",
                        f"  Role: {response.role}",
                        f"  Model: {response.model}",
                        f"  Preferred option: {response.signal.preferred_option}",
                        f"  Confidence: {response.signal.confidence}",
                        f"  Consensus ready: {response.signal.consensus_ready}",
                        f"  Key risks: {', '.join(response.signal.key_risks) or 'None stated'}",
                        f"  Position excerpt: {excerpt}",
                    ]
                )
            )
        return "\n".join(sections)

    def _summarize_round(
        self,
        *,
        round_number: int,
        member_responses: list[MemberResponse],
        consensus_target: int,
    ) -> RoundSummary:
        option_counter = Counter(
            response.signal.preferred_option.strip().lower() or "undeclared"
            for response in member_responses
        )
        majority_option, majority_count = option_counter.most_common(1)[0]
        ready_count = sum(1 for response in member_responses if response.signal.consensus_ready)
        consensus_reached = ready_count >= consensus_target and majority_count >= consensus_target
        return RoundSummary(
            round_number=round_number,
            member_responses=member_responses,
            majority_option=majority_option,
            ready_count=ready_count,
            majority_count=majority_count,
            consensus_reached=consensus_reached,
        )

    def _synthesize_final_answer(
        self,
        *,
        task_mode: str,
        prompt: str,
        context: str,
        rounds: list[RoundSummary],
    ) -> tuple[str, str]:
        lead_agent = self.council[0]
        synthesis_prompt = self._build_synthesis_prompt(task_mode=task_mode, prompt=prompt, context=context, rounds=rounds)

        try:
            response_data = self.client.chat_completion(
                model=lead_agent.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the chair of the O5 Council. Synthesize the council record into a final markdown report. "
                            "Preserve nuance, identify dissent where relevant, and end with a clear action plan."
                        ),
                    },
                    {"role": "user", "content": synthesis_prompt},
                ],
                temperature=0.4,
            )
            return self.client.extract_text(response_data), lead_agent.model
        except Exception:
            fallback = self._build_fallback_synthesis(task_mode=task_mode, prompt=prompt, rounds=rounds)
            return fallback, f"{lead_agent.model} (fallback local summary)"

    def _build_synthesis_prompt(
        self,
        *,
        task_mode: str,
        prompt: str,
        context: str,
        rounds: list[RoundSummary],
    ) -> str:
        round_sections: list[str] = []
        for summary in rounds:
            round_sections.append(
                f"Round {summary.round_number}: majority_option={summary.majority_option}, majority_count={summary.majority_count}, ready_count={summary.ready_count}, consensus_reached={summary.consensus_reached}"
            )
            for response in summary.member_responses:
                round_sections.append(
                    "\n".join(
                        [
                            f"Member: {response.agent_name}",
                            f"Role: {response.role}",
                            f"Model: {response.model}",
                            f"Preferred option: {response.signal.preferred_option}",
                            f"Confidence: {response.signal.confidence}",
                            f"Consensus ready: {response.signal.consensus_ready}",
                            f"Key risks: {', '.join(response.signal.key_risks) or 'None stated'}",
                            f"Content:\n{response.content}",
                        ]
                    )
                )

        return (
            f"Task mode: {task_mode}\n\n"
            f"Original prompt:\n{prompt.strip()}\n\n"
            f"Additional context:\n{context.strip() or 'No additional context provided.'}\n\n"
            "Using the council records below, produce a final markdown report with these sections: Executive Summary, Areas of Agreement, Areas of Disagreement, Recommended Plan, Risks and Mitigations, and Immediate Next Steps.\n\n"
            + "\n\n".join(round_sections)
        )

    def _build_fallback_synthesis(
        self,
        *,
        task_mode: str,
        prompt: str,
        rounds: list[RoundSummary],
    ) -> str:
        latest_round = rounds[-1]
        agreement_lines = [
            f"- Majority option: **{latest_round.majority_option}**",
            f"- Majority count: **{latest_round.majority_count}** of **{len(latest_round.member_responses)}**",
            f"- Consensus ready votes: **{latest_round.ready_count}**",
        ]
        dissent = [
            f"- {response.agent_name} supported **{response.signal.preferred_option}** with confidence **{response.signal.confidence}**."
            for response in latest_round.member_responses
            if response.signal.preferred_option != latest_round.majority_option
        ]
        if not dissent:
            dissent = ["- No substantial dissent remained in the final round."]

        return (
            f"# O5 Council Final Report\n\n"
            f"## Executive Summary\n\n"
            f"The council completed a **{task_mode}** run for the following request: {prompt.strip()}\n\n"
            f"## Areas of Agreement\n\n"
            + "\n".join(agreement_lines)
            + "\n\n## Areas of Disagreement\n\n"
            + "\n".join(dissent)
            + "\n\n## Recommended Plan\n\n"
            + latest_round.member_responses[0].content
            + "\n\n## Risks and Mitigations\n\n"
            + "\n".join(
                f"- {risk}"
                for response in latest_round.member_responses
                for risk in response.signal.key_risks
            )
            + "\n\n## Immediate Next Steps\n\n"
            "1. Review the majority recommendation.\n2. Examine any dissenting views.\n3. Convert the plan into an execution checklist or formal document as needed.\n"
        )

    def _extract_signal(self, response_text: str) -> tuple[str, CouncilSignal]:
        match = SIGNAL_PATTERN.search(response_text)
        if not match:
            return response_text.strip(), CouncilSignal()

        signal_json = match.group(1)
        cleaned = SIGNAL_PATTERN.sub("", response_text).strip()
        try:
            payload = json.loads(signal_json)
        except json.JSONDecodeError:
            return cleaned, CouncilSignal()

        preferred_option = str(payload.get("preferred_option", "undeclared")).strip() or "undeclared"
        try:
            confidence = int(payload.get("confidence", 50))
        except (TypeError, ValueError):
            confidence = 50
        confidence = max(0, min(100, confidence))
        consensus_ready = bool(payload.get("consensus_ready", False))
        key_risks_raw = payload.get("key_risks", [])
        if isinstance(key_risks_raw, list):
            key_risks = [str(item).strip() for item in key_risks_raw if str(item).strip()]
        else:
            key_risks = []
        return cleaned, CouncilSignal(
            preferred_option=preferred_option,
            confidence=confidence,
            consensus_ready=consensus_ready,
            key_risks=key_risks,
        )

    def _emit(self, event: str, payload: dict) -> None:
        self.progress_callback(event, payload)

    def _ensure_not_cancelled(self) -> None:
        if self.cancel_check():
            raise CouncilRunCancelled("The council run was cancelled.")

    @staticmethod
    def _truncate(text: str, length: int) -> str:
        compact = " ".join(text.split())
        if len(compact) <= length:
            return compact
        return compact[: length - 1].rstrip() + "…"
