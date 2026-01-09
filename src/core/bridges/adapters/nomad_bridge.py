"""
Nomad Bridge - HashiCorp Nomad integration
"""

from typing import Dict, List, Optional, Any
import requests

from hypersync.bridges.base_bridge import (
    OrchestratorBridge,
    BridgeConfig,
    BridgeStatus,
    PlacementAdvice
)


class NomadBridge(OrchestratorBridge):
    """HashiCorp Nomad integration bridge."""

    def __init__(self, config: BridgeConfig):
        super().__init__(config)
        self.api_client = None

    def connect(self) -> bool:
        """Connect to Nomad API."""
        try:
            endpoint = self.config.endpoint
            token = self.config.credentials.get("token", "")

            headers = {"X-Nomad-Token": token} if token else {}
            response = requests.get(
                f"{endpoint}/v1/status/leader",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                self.status = BridgeStatus.CONNECTED
                return True
            else:
                self.status = BridgeStatus.ERROR
                return False
        except Exception as e:
            print(f"Nomad connection error: {e}")
            self.status = BridgeStatus.ERROR
            return False

    def disconnect(self) -> bool:
        """Disconnect from Nomad."""
        self.status = BridgeStatus.DISCONNECTED
        return True

    def get_workloads(self) -> List[Dict[str, Any]]:
        """Get all jobs from Nomad."""
        if self.status != BridgeStatus.CONNECTED:
            return []

        try:
            endpoint = self.config.endpoint
            token = self.config.credentials.get("token", "")
            headers = {"X-Nomad-Token": token} if token else {}

            response = requests.get(
                f"{endpoint}/v1/jobs",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                jobs = response.json()
                return [self._convert_job_to_workload(j) for j in jobs]
            return []
        except Exception as e:
            print(f"Error getting Nomad workloads: {e}")
            return []

    def get_workload(self, workload_id: str) -> Optional[Dict[str, Any]]:
        """Get specific job from Nomad."""
        if self.status != BridgeStatus.CONNECTED:
            return None

        try:
            endpoint = self.config.endpoint
            token = self.config.credentials.get("token", "")
            headers = {"X-Nomad-Token": token} if token else {}

            response = requests.get(
                f"{endpoint}/v1/job/{workload_id}",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                job = response.json()
                return self._convert_job_to_workload(job)
            return None
        except Exception as e:
            print(f"Error getting Nomad workload {workload_id}: {e}")
            return None

    def provide_placement_advice(self, workload_spec: Dict[str, Any]) -> PlacementAdvice:
        """Provide placement advice for Nomad job."""
        job_id = workload_spec.get("ID", "unknown")

        # Extract resource requirements
        task_groups = workload_spec.get("TaskGroups", [])
        total_cpu = sum(
            task.get("Resources", {}).get("CPU", 0)
            for tg in task_groups
            for task in tg.get("Tasks", [])
        )
        total_memory = sum(
            task.get("Resources", {}).get("MemoryMB", 0)
            for tg in task_groups
            for task in tg.get("Tasks", [])
        )

        # Mock placement advice
        advice = PlacementAdvice(
            workload_id=job_id,
            recommended_node="nomad-client-1",
            coordinates=[0.4, 0.5, 0.3],
            distance=0.38,
            confidence=0.88,
            reasoning=f"Optimal for {total_cpu} MHz CPU, {total_memory}MB memory",
            alternatives=[
                {"node": "nomad-client-2", "distance": 0.42, "confidence": 0.82}
            ]
        )

        self.generate_receipt(
            operation="placement_advice",
            workload_id=job_id,
            status="success",
            placement_advice=advice
        )

        return advice

    def sync_workload_state(self, workload_id: str, state: Dict[str, Any]) -> bool:
        """Sync workload state to Nomad."""
        # Nomad doesn't support arbitrary metadata sync
        # Could use job meta or tags
        return True

    def _convert_job_to_workload(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Nomad job to HyperSync workload spec."""
        return {
            "id": job.get("ID"),
            "name": job.get("Name"),
            "namespace": job.get("Namespace", "default"),
            "type": job.get("Type"),
            "status": job.get("Status"),
            "task_groups": job.get("TaskGroups", []),
            "created_at": job.get("SubmitTime")
        }
