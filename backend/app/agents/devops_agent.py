from typing import Any
from .base import Agent


class DevOpsAgent(Agent):
    """Handles CI/CD, Docker, Kubernetes, and deployment queries."""

    @property
    def name(self) -> str:
        return "DevOpsAgent"

    def handle(self, message: str) -> dict[str, Any]:
        answer = (
            "For CI/CD we use GitHub Actions. Docker images are built with multi-stage builds "
            "and deployed to a Kubernetes cluster on EKS. "
            "Use 'kubectl' to manage pods and services. "
            "Our deployment process: push to main → GitHub Actions builds image → pushes to ECR → deploys to EKS."
        )
        return {"agent": self.name, "answer": answer}
