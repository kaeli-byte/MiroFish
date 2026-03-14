"""Registry for selecting simulation engines."""

from __future__ import annotations

from typing import Dict

from .interface import SimulationEngine
from .mesa_renewable_fuels_engine import MesaRenewableFuelsEngine
from .oasis_engine import OasisSimulationEngine


class SimulationEngineRegistry:
    def __init__(self):
        self._engines: Dict[str, SimulationEngine] = {
            "oasis": OasisSimulationEngine(),
            "mesa_renewable_fuels": MesaRenewableFuelsEngine(),
        }

    def get(self, engine_name: str) -> SimulationEngine:
        if engine_name not in self._engines:
            raise ValueError(f"Unsupported simulation engine: {engine_name}")
        return self._engines[engine_name]

    def list_engines(self):
        return list(self._engines.keys())
