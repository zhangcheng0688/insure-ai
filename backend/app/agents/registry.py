"""Agent registry - provides access to all insurance AI agents."""
from typing import Optional
from backend.app.agents.base import BaseInsuranceAgent
from backend.app.agents.claims_agent import ClaimsAgent
from backend.app.agents.underwriting_agent import UnderwritingAgent
from backend.app.agents.new_business_agent import NewBusinessAgent
from backend.app.agents.policy_issuance_agent import PolicyIssuanceAgent
from backend.app.agents.servicing_agent import ServicingAgent
from backend.app.agents.renewal_agent import RenewalAgent


AGENT_CLASSES = {
    "claims": ClaimsAgent,
    "underwriting": UnderwritingAgent,
    "new_business": NewBusinessAgent,
    "policy_issuance": PolicyIssuanceAgent,
    "servicing": ServicingAgent,
    "renewal": RenewalAgent,
}


def get_agent(stage: str, provider: Optional[str] = None, model: Optional[str] = None) -> BaseInsuranceAgent:
    """Get an agent instance by stage name."""
    agent_cls = AGENT_CLASSES.get(stage)
    if not agent_cls:
        raise ValueError(f"Unknown stage: {stage}. Available: {list(AGENT_CLASSES.keys())}")
    return agent_cls(provider=provider, model=model)


def list_agents() -> list[dict]:
    """List all available agents with their metadata."""
    result = []
    for stage, agent_cls in AGENT_CLASSES.items():
        # Instantiate just to get info
        instance = agent_cls()
        result.append(instance.get_info())
    return result


def get_agent_info(stage: str) -> dict:
    """Get metadata for a specific agent."""
    agent = get_agent(stage)
    return agent.get_info()
