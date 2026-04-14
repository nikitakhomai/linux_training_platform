"""Kubernetes client wrapper"""

from typing import Optional, Dict, Any, List
import logging
import os

logger = logging.getLogger(__name__)


class KubernetesClient:
    """Kubernetes API client"""

    def __init__(self):
        self.available = False
        self._init_client()

    def _init_client(self):
        """Initialize Kubernetes client"""
        try:
            # Check if running in cluster
            if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount"):
                from kubernetes import client, config

                config.load_incluster_config()
                self.available = True
                logger.info("Kubernetes client initialized (in-cluster)")
            else:
                # Try kubeconfig for development
                try:
                    from kubernetes import client, config

                    config.load_kube_config()
                    self.available = True
                    logger.info("Kubernetes client initialized (kubeconfig)")
                except:
                    logger.warning("Kubernetes not available, using Docker fallback")
                    self.available = False

        except ImportError:
            logger.warning("Kubernetes Python client not installed")
            self.available = False
        except Exception as e:
            logger.error(f"Kubernetes initialization error: {e}")
            self.available = False

    def is_available(self) -> bool:
        """Check if Kubernetes is available"""
        return self.available

    async def create_pod(
        self,
        namespace: str,
        pod_name: str,
        image: str,
        memory_limit: str = "512Mi",
        cpu_limit: str = "500m",
    ) -> Dict[str, Any]:
        """Create a pod in Kubernetes"""
        if not self.available:
            raise RuntimeError("Kubernetes not available")

        from kubernetes import client

        try:
            # Create pod specification
            pod_spec = client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name=pod_name,
                        image=image,
                        command=["sleep", "infinity"],
                        resources=client.V1ResourceRequirements(
                            limits={"memory": memory_limit, "cpu": cpu_limit}
                        ),
                    )
                ],
                restart_policy="Never",
            )

            pod = client.V1Pod(
                metadata=client.V1ObjectMeta(name=pod_name), spec=pod_spec
            )

            # Create pod
            v1 = client.CoreV1Api()
            await asyncio.to_thread(
                v1.create_namespaced_pod, namespace=namespace, body=pod
            )

            return {
                "namespace": namespace,
                "pod_name": pod_name,
                "access_method": "kubectl",
                "command": f"kubectl exec -it -n {namespace} {pod_name} -- /bin/bash",
            }

        except Exception as e:
            logger.error(f"Pod creation failed: {e}")
            raise

    async def delete_pod(self, namespace: str, pod_name: str):
        """Delete a pod"""
        if not self.available:
            return

        from kubernetes import client

        try:
            v1 = client.CoreV1Api()
            await asyncio.to_thread(
                v1.delete_namespaced_pod, name=pod_name, namespace=namespace
            )
            logger.info(f"Deleted pod {pod_name} in namespace {namespace}")
        except Exception as e:
            logger.error(f"Pod deletion failed: {e}")

    async def get_pod_status(self, namespace: str, pod_name: str) -> Optional[str]:
        """Get pod status"""
        if not self.available:
            return None

        from kubernetes import client

        try:
            v1 = client.CoreV1Api()
            pod = await asyncio.to_thread(
                v1.read_namespaced_pod, name=pod_name, namespace=namespace
            )
            return pod.status.phase
        except:
            return None

    async def get_pod_metrics(self, namespace: str, pod_name: str) -> Dict[str, Any]:
        """Get pod metrics"""
        # This would use metrics API
        return {
            "cpu_usage": 0.5,
            "memory_usage": 128 * 1024 * 1024,
            "network_rx": 1024,
            "network_tx": 512,
            "uptime_seconds": 3600,
        }


import asyncio
