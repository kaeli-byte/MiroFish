"""Mesa-based renewable fuels market simulation engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import logging
import threading
from typing import Any, Dict, List

from mesa import Agent, Model
from mesa.time import StagedActivation

from .assumption_extractor import ScenarioAssumptionExtractor
from .interface import SimulationEngine


logger = logging.getLogger(__name__)


class ProducerAgent(Agent):
    def __init__(self, unique_id: int, model: "RenewableFuelsMarketModel", capacity: float):
        super().__init__(unique_id, model)
        self.capacity = capacity
        self.output = capacity

    def produce(self):
        self.output = max(0.0, self.capacity * self.random.uniform(0.9, 1.1))
        self.model.supply += self.output


class SupplierAgent(Agent):
    def __init__(self, unique_id: int, model: "RenewableFuelsMarketModel"):
        super().__init__(unique_id, model)
        self.inventory = 0.0

    def distribute(self):
        distributed = self.model.supply * self.random.uniform(0.75, 0.95)
        self.inventory = max(0.0, distributed)
        self.model.available_inventory += self.inventory


class BuyerAgent(Agent):
    def __init__(self, unique_id: int, model: "RenewableFuelsMarketModel", baseline_demand: float):
        super().__init__(unique_id, model)
        self.baseline_demand = baseline_demand
        self.current_demand = baseline_demand

    def demand(self):
        price_sensitivity = max(0.1, 1.0 - (self.model.price - self.model.base_price) * 0.03)
        self.current_demand = max(0.0, self.baseline_demand * price_sensitivity * self.random.uniform(0.9, 1.1))
        self.model.total_demand += self.current_demand


class InvestorAgent(Agent):
    def __init__(self, unique_id: int, model: "RenewableFuelsMarketModel"):
        super().__init__(unique_id, model)
        self.last_flow = 0.0

    def invest(self):
        self.last_flow = self.random.uniform(-2.5, 5.5)
        self.model.capital_pool += self.last_flow
        self.model.investment_flow += self.last_flow


class RegulatorAgent(Agent):
    def __init__(self, unique_id: int, model: "RenewableFuelsMarketModel"):
        super().__init__(unique_id, model)
        self.intensity = 1.0

    def regulate(self):
        imbalance = self.model.available_inventory - self.model.total_demand
        self.intensity = 1.0 + (-imbalance / max(1.0, self.model.total_demand)) * 0.03
        self.intensity = min(1.2, max(0.85, self.intensity))
        self.model.regulation_intensity = self.intensity


class RenewableFuelsMarketModel(Model):
    def __init__(self, scenario: Dict[str, Any]):
        super().__init__()
        self.scenario = scenario
        self.base_price = float(scenario.get("initial_price", 1.8))
        self.price = self.base_price
        self.capital_pool = float(scenario.get("initial_capital", 250.0))
        self.supply = 0.0
        self.available_inventory = 0.0
        self.total_demand = 0.0
        self.investment_flow = 0.0
        self.regulation_intensity = 1.0

        self.schedule = StagedActivation(
            self,
            stage_list=["produce", "distribute", "demand", "invest", "regulate"],
            shuffle=True,
            shuffle_between_stages=False,
        )

        producer_count = int(scenario.get("producers", 5))
        supplier_count = int(scenario.get("suppliers", 3))
        buyer_count = int(scenario.get("buyers", 8))
        investor_count = int(scenario.get("investors", 4))

        uid = 1
        for _ in range(producer_count):
            self.schedule.add(ProducerAgent(uid, self, capacity=float(scenario.get("producer_capacity", 22.0))))
            uid += 1
        for _ in range(supplier_count):
            self.schedule.add(SupplierAgent(uid, self))
            uid += 1
        for _ in range(buyer_count):
            self.schedule.add(BuyerAgent(uid, self, baseline_demand=float(scenario.get("buyer_demand", 12.0))))
            uid += 1
        for _ in range(investor_count):
            self.schedule.add(InvestorAgent(uid, self))
            uid += 1
        self.schedule.add(RegulatorAgent(uid, self))

    def step(self):
        self.supply = 0.0
        self.available_inventory = 0.0
        self.total_demand = 0.0
        self.investment_flow = 0.0

        self.schedule.step()

        imbalance = self.available_inventory - self.total_demand
        demand_ref = max(1.0, self.total_demand)
        self.price *= 1 + (-imbalance / demand_ref) * 0.08
        self.price *= self.regulation_intensity
        self.price = max(0.25, self.price)


@dataclass
class RenewableSimulationState:
    simulation_id: str
    status: str = "created"
    current_step: int = 0
    total_steps: int = 0
    scenario: Dict[str, Any] = field(default_factory=dict)
    assumptions: Dict[str, Any] = field(default_factory=dict)
    metrics: List[Dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class MesaRenewableFuelsEngine(SimulationEngine):
    def __init__(self):
        self._states: Dict[str, RenewableSimulationState] = {}
        self._lock = threading.Lock()

    def _get_state(self, simulation_id: str) -> RenewableSimulationState:
        with self._lock:
            if simulation_id not in self._states:
                self._states[simulation_id] = RenewableSimulationState(simulation_id=simulation_id)
            return self._states[simulation_id]

    def _sanitize_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        sanitized: Dict[str, Any] = dict(scenario)

        int_keys = {"steps", "producers", "suppliers", "buyers", "investors"}
        float_keys = {"initial_price", "initial_capital", "producer_capacity", "buyer_demand"}

        def safe_cast(key: str, cast_type: type[int] | type[float]) -> None:
            if key not in sanitized:
                return

            raw_value = sanitized[key]
            try:
                sanitized[key] = cast_type(raw_value)
            except (TypeError, ValueError) as exc:
                cast_type_name = "int" if cast_type is int else "float"
                raise ValueError(
                    f"_sanitize_scenario failed for key '{key}' with value {raw_value!r}: "
                    f"expected a value castable by {cast_type_name} from "
                    f"{'int_keys' if cast_type is int else 'float_keys'}."
                ) from exc

        for key in int_keys:
            safe_cast(key, int)
        for key in float_keys:
            safe_cast(key, float)

        return sanitized

    def prepare(self, simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        state = self._get_state(simulation_id)
        assumptions = ScenarioAssumptionExtractor.extract(payload.get("report_text", ""))

        with self._lock:
            if state.status == "running":
                raise ValueError("Cannot prepare simulation while it is running.")

            scenario = payload.get("scenario", {})
            if not isinstance(scenario, dict):
                raise ValueError("Scenario must be an object.")

            sanitized_scenario = self._sanitize_scenario(scenario)
            total_steps = int(sanitized_scenario.get("steps", 24))
            if total_steps <= 0:
                raise ValueError("Scenario steps must be greater than 0.")

            state.scenario = sanitized_scenario
            state.assumptions = assumptions
            state.total_steps = total_steps
            state.current_step = 0
            state.metrics = []
            state.error = None
            state.status = "ready"
            state.updated_at = datetime.now().isoformat()
        return self.get_status(simulation_id)

    def _run_background(self, simulation_id: str):
        state = self._get_state(simulation_id)
        try:
            with self._lock:
                scenario = dict(state.scenario)
                total_steps = state.total_steps

            model = RenewableFuelsMarketModel(scenario)
            for step in range(1, total_steps + 1):
                model.step()
                with self._lock:
                    state.current_step = step
                    state.metrics.append(
                        {
                            "step": step,
                            "supply": round(model.supply, 3),
                            "inventory": round(model.available_inventory, 3),
                            "demand": round(model.total_demand, 3),
                            "price": round(model.price, 3),
                            "investment_flow": round(model.investment_flow, 3),
                            "capital_pool": round(model.capital_pool, 3),
                            "regulation_intensity": round(model.regulation_intensity, 3),
                        }
                    )
                    state.updated_at = datetime.now().isoformat()

            with self._lock:
                state.status = "completed"
                state.updated_at = datetime.now().isoformat()
        except Exception as exc:
            logger.exception("Renewable fuels simulation failed for simulation_id=%s", simulation_id)
            with self._lock:
                state.status = "failed"
                state.error = str(exc)
                state.updated_at = datetime.now().isoformat()

    def run(self, simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        state = self._get_state(simulation_id)
        with self._lock:
            if state.status not in {"ready", "completed"}:
                raise ValueError("Simulation must be prepared before running.")
            state.status = "running"
            state.current_step = 0
            state.metrics = []
            state.error = None
            state.updated_at = datetime.now().isoformat()

        threading.Thread(target=self._run_background, args=(simulation_id,), daemon=True).start()
        return self.get_status(simulation_id)

    def get_status(self, simulation_id: str) -> Dict[str, Any]:
        state = self._get_state(simulation_id)
        with self._lock:
            return {
                "simulation_id": simulation_id,
                "engine": "mesa_renewable_fuels",
                "status": state.status,
                "current_step": state.current_step,
                "total_steps": state.total_steps,
                "error": state.error,
                "updated_at": state.updated_at,
            }

    def get_results(self, simulation_id: str) -> Dict[str, Any]:
        state = self._get_state(simulation_id)
        with self._lock:
            if state.status != "completed":
                raise ValueError("Simulation results are only available after completion.")
            latest = state.metrics[-1] if state.metrics else {}
            return {
                "simulation_id": simulation_id,
                "engine": "mesa_renewable_fuels",
                "scenario": state.scenario,
                "assumptions": state.assumptions,
                "status": state.status,
                "summary": {
                    "final_price": latest.get("price"),
                    "final_supply": latest.get("supply"),
                    "final_inventory": latest.get("inventory"),
                    "final_demand": latest.get("demand"),
                    "final_capital_pool": latest.get("capital_pool"),
                },
                "time_series": list(state.metrics),
            }
