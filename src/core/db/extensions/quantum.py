"""
Quantum-Ready Preparations - Quantum metadata and simulator bridges.

Defines quantum metadata schema, simulator bridges, curvature-aware
qubit registry, experiment sandbox, and safety guardrails.
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import math
import cmath


class QubitState(Enum):
    """Qubit states."""
    ZERO = "0"
    ONE = "1"
    SUPERPOSITION = "superposition"


@dataclass
class Qubit:
    """Quantum bit with hyperbolic metadata."""
    qubit_id: str
    state: QubitState
    amplitude_0: complex
    amplitude_1: complex
    curvature: float
    position: Optional[Tuple[float, float]] = None  # Hyperbolic coordinates


@dataclass
class QuantumCircuit:
    """Quantum circuit definition."""
    circuit_id: str
    num_qubits: int
    gates: List[Dict[str, Any]]
    measurements: List[int]


@dataclass
class ExperimentResult:
    """Quantum experiment result."""
    experiment_id: str
    circuit_id: str
    measurements: Dict[str, int]  # bitstring -> count
    execution_time_ms: float
    simulator: str


class QuantumRegistry:
    """
    Curvature-aware qubit registry.

    Manages qubit metadata with hyperbolic geometry awareness
    for quantum-classical hybrid computations.
    """

    def __init__(self, curvature: float = -1.0):
        self.curvature = curvature
        self.qubits: Dict[str, Qubit] = {}
        self.circuits: Dict[str, QuantumCircuit] = {}

    def register_qubit(self, qubit_id: str,
                      position: Optional[Tuple[float, float]] = None) -> Qubit:
        """
        Register qubit with hyperbolic position.

        Args:
            qubit_id: Qubit identifier
            position: Hyperbolic coordinates (r, theta)

        Returns:
            Registered Qubit
        """
        qubit = Qubit(
            qubit_id=qubit_id,
            state=QubitState.ZERO,
            amplitude_0=complex(1, 0),
            amplitude_1=complex(0, 0),
            curvature=self.curvature,
            position=position
        )

        self.qubits[qubit_id] = qubit
        return qubit

    def apply_gate(self, qubit_id: str, gate: str, params: Optional[Dict] = None) -> None:
        """
        Apply quantum gate to qubit.

        Args:
            qubit_id: Qubit identifier
            gate: Gate name (H, X, Y, Z, RX, RY, RZ)
            params: Gate parameters
        """
        if qubit_id not in self.qubits:
            return

        qubit = self.qubits[qubit_id]

        if gate == "H":  # Hadamard
            new_amp_0 = (qubit.amplitude_0 + qubit.amplitude_1) / math.sqrt(2)
            new_amp_1 = (qubit.amplitude_0 - qubit.amplitude_1) / math.sqrt(2)
            qubit.amplitude_0 = new_amp_0
            qubit.amplitude_1 = new_amp_1
            qubit.state = QubitState.SUPERPOSITION

        elif gate == "X":  # Pauli-X (NOT)
            qubit.amplitude_0, qubit.amplitude_1 = qubit.amplitude_1, qubit.amplitude_0

        elif gate == "Z":  # Pauli-Z
            qubit.amplitude_1 = -qubit.amplitude_1

        elif gate == "RX" and params and "theta" in params:  # Rotation around X
            theta = params["theta"]
            cos_half = math.cos(theta / 2)
            sin_half = math.sin(theta / 2)

            new_amp_0 = cos_half * qubit.amplitude_0 - 1j * sin_half * qubit.amplitude_1
            new_amp_1 = -1j * sin_half * qubit.amplitude_0 + cos_half * qubit.amplitude_1

            qubit.amplitude_0 = new_amp_0
            qubit.amplitude_1 = new_amp_1

    def measure(self, qubit_id: str) -> str:
        """
        Measure qubit (collapses superposition).

        Args:
            qubit_id: Qubit identifier

        Returns:
            Measurement result ("0" or "1")
        """
        if qubit_id not in self.qubits:
            return "0"

        qubit = self.qubits[qubit_id]

        # Probability of measuring |0⟩
        prob_0 = abs(qubit.amplitude_0) ** 2

        # Simulate measurement
        import random
        result = "0" if random.random() < prob_0 else "1"

        # Collapse state
        if result == "0":
            qubit.amplitude_0 = complex(1, 0)
            qubit.amplitude_1 = complex(0, 0)
            qubit.state = QubitState.ZERO
        else:
            qubit.amplitude_0 = complex(0, 0)
            qubit.amplitude_1 = complex(1, 0)
            qubit.state = QubitState.ONE

        return result

    def geodesic_entanglement(self, qubit1_id: str, qubit2_id: str) -> float:
        """
        Compute entanglement strength based on geodesic distance.

        Args:
            qubit1_id: First qubit ID
            qubit2_id: Second qubit ID

        Returns:
            Entanglement strength (0 to 1)
        """
        if qubit1_id not in self.qubits or qubit2_id not in self.qubits:
            return 0.0

        qubit1 = self.qubits[qubit1_id]
        qubit2 = self.qubits[qubit2_id]

        if not qubit1.position or not qubit2.position:
            return 0.0

        # Compute hyperbolic distance
        r1, theta1 = qubit1.position
        r2, theta2 = qubit2.position

        delta_theta = abs(theta2 - theta1)
        numerator = (r1 - r2)**2 + 4 * r1 * r2 * math.sin(delta_theta / 2)**2
        denominator = (1 - r1**2) * (1 - r2**2)

        if denominator <= 0:
            return 0.0

        distance = math.acosh(1 + 2 * numerator / denominator)

        # Entanglement decays with distance
        return math.exp(-distance)


class QuantumSimulatorBridge:
    """
    Bridge to quantum simulators.

    Provides interface to quantum simulators with safety guardrails
    and experiment sandboxing.
    """

    def __init__(self, simulator: str = "statevector"):
        self.simulator = simulator
        self.registry = QuantumRegistry()
        self.experiments: Dict[str, ExperimentResult] = {}
        self.safety_limits = {
            "max_qubits": 20,
            "max_gates": 1000,
            "max_shots": 10000
        }

    def create_circuit(self, circuit_id: str, num_qubits: int) -> QuantumCircuit:
        """
        Create quantum circuit.

        Args:
            circuit_id: Circuit identifier
            num_qubits: Number of qubits

        Returns:
            Created QuantumCircuit
        """
        if num_qubits > self.safety_limits["max_qubits"]:
            raise ValueError(f"Exceeds max qubits limit: {self.safety_limits['max_qubits']}")

        circuit = QuantumCircuit(
            circuit_id=circuit_id,
            num_qubits=num_qubits,
            gates=[],
            measurements=[]
        )

        self.registry.circuits[circuit_id] = circuit

        # Register qubits
        for i in range(num_qubits):
            self.registry.register_qubit(f"{circuit_id}_q{i}")

        return circuit

    def add_gate(self, circuit_id: str, gate: str, qubits: List[int],
                params: Optional[Dict] = None) -> None:
        """
        Add gate to circuit.

        Args:
            circuit_id: Circuit identifier
            gate: Gate name
            qubits: Target qubit indices
            params: Gate parameters
        """
        if circuit_id not in self.registry.circuits:
            return

        circuit = self.registry.circuits[circuit_id]

        if len(circuit.gates) >= self.safety_limits["max_gates"]:
            raise ValueError(f"Exceeds max gates limit: {self.safety_limits['max_gates']}")

        circuit.gates.append({
            "gate": gate,
            "qubits": qubits,
            "params": params or {}
        })

    def execute(self, circuit_id: str, shots: int = 1024) -> ExperimentResult:
        """
        Execute quantum circuit.

        Args:
            circuit_id: Circuit identifier
            shots: Number of measurement shots

        Returns:
            ExperimentResult
        """
        if circuit_id not in self.registry.circuits:
            raise ValueError(f"Circuit not found: {circuit_id}")

        if shots > self.safety_limits["max_shots"]:
            raise ValueError(f"Exceeds max shots limit: {self.safety_limits['max_shots']}")

        circuit = self.registry.circuits[circuit_id]

        start_time = datetime.now()

        # Simulate circuit execution
        measurements = {}

        for _ in range(shots):
            # Reset qubits
            for i in range(circuit.num_qubits):
                qubit_id = f"{circuit_id}_q{i}"
                if qubit_id in self.registry.qubits:
                    qubit = self.registry.qubits[qubit_id]
                    qubit.amplitude_0 = complex(1, 0)
                    qubit.amplitude_1 = complex(0, 0)
                    qubit.state = QubitState.ZERO

            # Apply gates
            for gate_spec in circuit.gates:
                for qubit_idx in gate_spec["qubits"]:
                    qubit_id = f"{circuit_id}_q{qubit_idx}"
                    self.registry.apply_gate(qubit_id, gate_spec["gate"], gate_spec["params"])

            # Measure
            bitstring = ""
            for i in range(circuit.num_qubits):
                qubit_id = f"{circuit_id}_q{i}"
                bitstring += self.registry.measure(qubit_id)

            measurements[bitstring] = measurements.get(bitstring, 0) + 1

        execution_time = (datetime.now() - start_time).total_seconds() * 1000

        experiment_id = f"exp_{circuit_id}_{int(datetime.now().timestamp())}"

        result = ExperimentResult(
            experiment_id=experiment_id,
            circuit_id=circuit_id,
            measurements=measurements,
            execution_time_ms=execution_time,
            simulator=self.simulator
        )

        self.experiments[experiment_id] = result

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get simulator statistics."""
        return {
            "num_qubits": len(self.registry.qubits),
            "num_circuits": len(self.registry.circuits),
            "num_experiments": len(self.experiments),
            "safety_limits": self.safety_limits
        }
