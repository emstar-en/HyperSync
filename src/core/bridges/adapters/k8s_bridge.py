"""
Kubernetes Bridge

Integrates HyperSync with Kubernetes clusters for placement advice and workload sync.
"""

from typing import Dict, List, Optional, Any
import requests
import json
from datetime import datetime

from hypersync.bridges.base_bridge import (
    OrchestratorBridge,
    BridgeConfig,
    BridgeType,
    BridgeStatus,
    PlacementAdvice,
    WorkloadMapping
)


class KubernetesBridge(OrchestratorBridge):
    """
    Kubernetes integration bridge.

    Modes:
    - Scheduler Extender: Provide placement advice to K8s scheduler
    - Admission Controller: Validate and mutate pod specs
    - Operator: Watch and sync workload state
    """

    def __init__(self, config: BridgeConfig):
        super().__init__(config)
        self.api_client = None
        self.mode = config.options.get("mode", "scheduler_extender")
        self.namespace_filter = config.options.get("namespace_filter", [])
        self.label_selector = config.options.get("label_selector", {})

    def connect(self) -> bool:
        """Connect to Kubernetes API server."""
        try:
            # Initialize API client
            endpoint = self.config.endpoint
            token = self.config.credentials.get("token")
            ca_cert = self.config.credentials.get("ca_cert")

            # Test connection
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{endpoint}/api/v1/namespaces",
                headers=headers,
                verify=ca_cert if ca_cert else False,
                timeout=10
            )

            if response.status_code == 200:
                self.status = BridgeStatus.CONNECTED
                return True
            else:
                self.status = BridgeStatus.ERROR
                return False

        except Exception as e:
            print(f"K8s connection error: {e}")
            self.status = BridgeStatus.ERROR
            return False

    def disconnect(self) -> bool:
        """Disconnect from Kubernetes."""
        self.api_client = None
        self.status = BridgeStatus.DISCONNECTED
        return True

    def get_workloads(self) -> List[Dict[str, Any]]:
        """Get all pods from Kubernetes."""
        if self.status != BridgeStatus.CONNECTED:
            return []

        try:
            endpoint = self.config.endpoint
            token = self.config.credentials.get("token")
            headers = {"Authorization": f"Bearer {token}"}

            # Get pods
            if self.namespace_filter:
                # Get from specific namespaces
                pods = []
                for ns in self.namespace_filter:
                    response = requests.get(
                        f"{endpoint}/api/v1/namespaces/{ns}/pods",
                        headers=headers,
                        verify=False,
                        timeout=10
                    )
                    if response.status_code == 200:
                        pods.extend(response.json().get("items", []))
            else:
                # Get from all namespaces
                response = requests.get(
                    f"{endpoint}/api/v1/pods",
                    headers=headers,
                    verify=False,
                    timeout=10
                )
                if response.status_code == 200:
                    pods = response.json().get("items", [])
                else:
                    pods = []

            # Filter by labels if specified
            if self.label_selector:
                pods = [p for p in pods if self._matches_labels(p, self.label_selector)]

            return [self._convert_pod_to_workload(p) for p in pods]

        except Exception as e:
            print(f"Error getting K8s workloads: {e}")
            return []

    def get_workload(self, workload_id: str) -> Optional[Dict[str, Any]]:
        """Get specific pod from Kubernetes."""
        if self.status != BridgeStatus.CONNECTED:
            return None

        try:
            # Parse workload_id as namespace/name
            if '/' in workload_id:
                namespace, name = workload_id.split('/', 1)
            else:
                namespace = "default"
                name = workload_id

            endpoint = self.config.endpoint
            token = self.config.credentials.get("token")
            headers = {"Authorization": f"Bearer {token}"}

            response = requests.get(
                f"{endpoint}/api/v1/namespaces/{namespace}/pods/{name}",
                headers=headers,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                pod = response.json()
                return self._convert_pod_to_workload(pod)
            else:
                return None

        except Exception as e:
            print(f"Error getting K8s workload {workload_id}: {e}")
            return None

    def provide_placement_advice(self, workload_spec: Dict[str, Any]) -> PlacementAdvice:
        """
        Provide placement advice for Kubernetes pod.

        Called by K8s scheduler extender.
        """
        # Extract pod requirements
        pod_name = workload_spec.get("metadata", {}).get("name", "unknown")
        namespace = workload_spec.get("metadata", {}).get("namespace", "default")

        # Extract resource requirements
        containers = workload_spec.get("spec", {}).get("containers", [])
        total_cpu = 0
        total_memory = 0

        for container in containers:
            resources = container.get("resources", {}).get("requests", {})
            cpu = resources.get("cpu", "0")
            memory = resources.get("memory", "0")

            # Parse CPU (e.g., "2" or "2000m")
            if cpu.endswith('m'):
                total_cpu += int(cpu[:-1]) / 1000
            else:
                total_cpu += float(cpu)

            # Parse memory (e.g., "4Gi" or "4096Mi")
            if memory.endswith('Gi'):
                total_memory += float(memory[:-2]) * 1024
            elif memory.endswith('Mi'):
                total_memory += float(memory[:-2])

        # Extract node selector and affinity
        node_selector = workload_spec.get("spec", {}).get("nodeSelector", {})
        affinity = workload_spec.get("spec", {}).get("affinity", {})

        # TODO: Call HyperSync placement engine
        # For now, return mock advice
        advice = PlacementAdvice(
            workload_id=f"{namespace}/{pod_name}",
            recommended_node="node-1",
            coordinates=[0.5, 0.3, 0.2],
            distance=0.45,
            confidence=0.85,
            reasoning=f"Optimal placement for {total_cpu} CPU, {total_memory}Mi memory",
            alternatives=[
                {"node": "node-2", "distance": 0.52, "confidence": 0.78},
                {"node": "node-3", "distance": 0.58, "confidence": 0.72}
            ]
        )

        # Generate receipt
        self.generate_receipt(
            operation="placement_advice",
            workload_id=f"{namespace}/{pod_name}",
            status="success",
            placement_advice=advice,
            metadata={
                "cpu": total_cpu,
                "memory": total_memory,
                "node_selector": node_selector
            }
        )

        return advice

    def sync_workload_state(self, workload_id: str, state: Dict[str, Any]) -> bool:
        """Sync workload state to Kubernetes."""
        if self.status != BridgeStatus.CONNECTED:
            return False

        try:
            # Parse workload_id
            if '/' in workload_id:
                namespace, name = workload_id.split('/', 1)
            else:
                namespace = "default"
                name = workload_id

            endpoint = self.config.endpoint
            token = self.config.credentials.get("token")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # Update pod annotations with HyperSync state
            patch = {
                "metadata": {
                    "annotations": {
                        "hypersync.io/state": json.dumps(state),
                        "hypersync.io/synced-at": datetime.utcnow().isoformat()
                    }
                }
            }

            response = requests.patch(
                f"{endpoint}/api/v1/namespaces/{namespace}/pods/{name}",
                headers=headers,
                json=patch,
                verify=False,
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            print(f"Error syncing K8s workload {workload_id}: {e}")
            return False

    def _convert_pod_to_workload(self, pod: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Kubernetes pod to HyperSync workload spec."""
        metadata = pod.get("metadata", {})
        spec = pod.get("spec", {})
        status = pod.get("status", {})

        return {
            "id": f"{metadata.get('namespace', 'default')}/{metadata.get('name')}",
            "name": metadata.get("name"),
            "namespace": metadata.get("namespace", "default"),
            "labels": metadata.get("labels", {}),
            "annotations": metadata.get("annotations", {}),
            "node": spec.get("nodeName"),
            "phase": status.get("phase"),
            "containers": spec.get("containers", []),
            "resources": self._extract_resources(spec),
            "created_at": metadata.get("creationTimestamp")
        }

    def _extract_resources(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Extract resource requirements from pod spec."""
        containers = spec.get("containers", [])
        total_requests = {"cpu": 0, "memory": 0}
        total_limits = {"cpu": 0, "memory": 0}

        for container in containers:
            resources = container.get("resources", {})

            # Requests
            requests = resources.get("requests", {})
            cpu = requests.get("cpu", "0")
            memory = requests.get("memory", "0")

            if cpu.endswith('m'):
                total_requests["cpu"] += int(cpu[:-1]) / 1000
            else:
                total_requests["cpu"] += float(cpu) if cpu else 0

            if memory.endswith('Gi'):
                total_requests["memory"] += float(memory[:-2]) * 1024
            elif memory.endswith('Mi'):
                total_requests["memory"] += float(memory[:-2])

            # Limits
            limits = resources.get("limits", {})
            cpu = limits.get("cpu", "0")
            memory = limits.get("memory", "0")

            if cpu.endswith('m'):
                total_limits["cpu"] += int(cpu[:-1]) / 1000
            else:
                total_limits["cpu"] += float(cpu) if cpu else 0

            if memory.endswith('Gi'):
                total_limits["memory"] += float(memory[:-2]) * 1024
            elif memory.endswith('Mi'):
                total_limits["memory"] += float(memory[:-2])

        return {
            "requests": total_requests,
            "limits": total_limits
        }

    def _matches_labels(self, pod: Dict[str, Any], selector: Dict[str, str]) -> bool:
        """Check if pod matches label selector."""
        pod_labels = pod.get("metadata", {}).get("labels", {})
        return all(pod_labels.get(k) == v for k, v in selector.items())

    def scheduler_extender_filter(self, pod: Dict[str, Any], nodes: List[str]) -> List[str]:
        """
        Filter nodes for scheduler extender.

        Called by K8s scheduler to filter feasible nodes.
        """
        # Get placement advice
        advice = self.provide_placement_advice(pod)

        # Return nodes sorted by HyperSync recommendation
        recommended = advice.recommended_node
        alternatives = [alt["node"] for alt in advice.alternatives]

        # Prioritize recommended node
        filtered = []
        if recommended in nodes:
            filtered.append(recommended)

        # Add alternatives
        for alt in alternatives:
            if alt in nodes and alt not in filtered:
                filtered.append(alt)

        # Add remaining nodes
        for node in nodes:
            if node not in filtered:
                filtered.append(node)

        return filtered

    def scheduler_extender_prioritize(self, pod: Dict[str, Any], nodes: List[str]) -> Dict[str, int]:
        """
        Prioritize nodes for scheduler extender.

        Returns node scores (0-100).
        """
        advice = self.provide_placement_advice(pod)

        scores = {}
        recommended = advice.recommended_node

        # Score recommended node highest
        if recommended in nodes:
            scores[recommended] = 100

        # Score alternatives
        for alt in advice.alternatives:
            node = alt["node"]
            if node in nodes:
                confidence = alt.get("confidence", 0.5)
                scores[node] = int(confidence * 100)

        # Score remaining nodes
        for node in nodes:
            if node not in scores:
                scores[node] = 50  # Default score

        return scores
