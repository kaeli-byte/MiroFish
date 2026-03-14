"""Domain-neutral simulation engine interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class SimulationEngine(ABC):
    """Unified interface for all simulation engines."""

    @abstractmethod
    def prepare(self, simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare required data/config before execution."""

    @abstractmethod
    def run(self, simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Start or execute a simulation run."""

    @abstractmethod
    def get_status(self, simulation_id: str) -> Dict[str, Any]:
        """Return current execution status."""

    @abstractmethod
    def get_results(self, simulation_id: str) -> Dict[str, Any]:
        """Return simulation outputs in JSON-serializable form."""
