"""Custom exceptions for Orchestration Service"""


class OrchestrationError(Exception):
    """Base exception for orchestration service"""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ContainerError(OrchestrationError):
    """Exception for container-related errors"""

    def __init__(self, message: str, container_id: str = None, details: dict = None):
        self.container_id = container_id
        super().__init__(message, details)


class NamespaceError(OrchestrationError):
    """Exception for namespace-related errors"""

    def __init__(self, message: str, namespace: str = None, details: dict = None):
        self.namespace = namespace
        super().__init__(message, details)


class KubernetesError(OrchestrationError):
    """Exception for Kubernetes-related errors"""

    def __init__(self, message: str, resource: str = None, details: dict = None):
        self.resource = resource
        super().__init__(message, details)
