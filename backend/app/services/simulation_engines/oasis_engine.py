"""OASIS adapter implementing the generic simulation engine interface."""

from __future__ import annotations

from typing import Any, Dict

from .interface import SimulationEngine


class OasisSimulationEngine(SimulationEngine):
    """Adapter placeholder; OASIS lifecycle remains managed by existing endpoints."""

    def prepare(self, simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "simulation_id": simulation_id,
            "engine": "oasis",
            "status": "delegated",
            "message": "Use existing /api/simulation/prepare flow for OASIS simulations.",
        }

    def run(self, simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "simulation_id": simulation_id,
            "engine": "oasis",
            "status": "delegated",
            "message": "Use existing /api/simulation/start flow for OASIS simulations.",
        }

    def get_status(self, simulation_id: str) -> Dict[str, Any]:
        return {
            "simulation_id": simulation_id,
            "engine": "oasis",
            "status": "delegated",
            "message": "Use existing /api/simulation/<id>/run-status flow for OASIS simulations.",
        }

    def get_results(self, simulation_id: str) -> Dict[str, Any]:
        return {
            "simulation_id": simulation_id,
            "engine": "oasis",
            "status": "delegated",
            "message": "Use existing OASIS timeline/actions APIs for detailed results.",
        }
