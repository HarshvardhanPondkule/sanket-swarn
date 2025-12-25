"""
Swarm API Router
Note: Main endpoints are in main.py. This is for modular routing if needed.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/swarm", tags=["Swarm"])

# Service will be injected
_swarm_service = None

def set_swarm_service(service):
    """Set the swarm service dependency"""
    global _swarm_service
    _swarm_service = service

@router.get("/agents")
async def get_agents():
    """Get all swarm agents status"""
    if not _swarm_service:
        raise HTTPException(500, "Swarm service not initialized")
    return _swarm_service.get_network_status()

@router.get("/anomalies/{village_id}")
async def detect_anomalies(village_id: str):
    """Check if village agent detected anomalies"""
    if not _swarm_service:
        raise HTTPException(500, "Swarm service not initialized")
    
    agent = _swarm_service.orchestrator.agents.get(village_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    return {
        'village': agent.village_name,
        'outbreak_belief': agent.outbreak_belief,
        'risk_level': agent.risk_level,
        'symptom_count': len(agent.symptom_history)
    }
