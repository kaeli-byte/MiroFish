"""Extract renewable-fuels scenario assumptions from reports."""

from __future__ import annotations

from typing import Any, Dict, List

from ...utils.llm_client import LLMClient
from ...utils.logger import get_logger

logger = get_logger("mirofish.renewables.assumptions")


class ScenarioAssumptionExtractor:
    """GraphRAG/LLM-assisted extraction used only during scenario ingestion."""

    @staticmethod
    def extract(report_text: str) -> Dict[str, Any]:
        if not report_text:
            return {
                "source": "none",
                "assumptions": [],
            }

        try:
            client = LLMClient()
            response = client.chat_json(
                [
                    {
                        "role": "system",
                        "content": (
                            "You extract structured scenario assumptions for a renewable fuels market simulation. "
                            "Return JSON with key assumptions as a list of objects: "
                            "{name, value, unit, rationale}."
                        ),
                    },
                    {
                        "role": "user",
                        "content": report_text[:12000],
                    },
                ],
                temperature=0.1,
                max_tokens=1200,
            )

            assumptions: List[Dict[str, Any]] = response.get("assumptions", [])
            if not isinstance(assumptions, list):
                assumptions = []

            return {
                "source": "llm",
                "assumptions": assumptions,
            }
        except Exception as exc:
            logger.warning(f"LLM assumption extraction failed, fallback to heuristic mode: {exc}")
            return {
                "source": "heuristic",
                "assumptions": [
                    {
                        "name": "report_summary",
                        "value": report_text[:200],
                        "unit": "text",
                        "rationale": "Fallback summary due to unavailable LLM extraction.",
                    }
                ],
            }
