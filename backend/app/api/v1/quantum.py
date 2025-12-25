"""
Quantum API Router
Note: Main endpoints are in main.py. This is for modular routing if needed.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/quantum", tags=["Quantum"])

# Services will be injected
_quantum_service = None
_swarm_service = None

def set_services(quantum_service, swarm_service):
    """Set service dependencies"""
    global _quantum_service, _swarm_service
    _quantum_service = quantum_service
    _swarm_service = swarm_service

@router.post("/analyze")
async def run_quantum_analysis():
    """
    Triggered by swarm consensus
    Runs quantum pattern detection and optimization
    """
    if not _quantum_service or not _swarm_service:
        raise HTTPException(500, "Services not initialized")
    
    # Get swarm data
    swarm_data = _swarm_service.get_network_status()
    
    # Run quantum analysis
    quantum_result = await _quantum_service.analyze_outbreak_pattern(swarm_data)
    
    return quantum_result

@router.get("/insights")
async def get_quantum_insights():
    """Get latest quantum insights"""
    if not _quantum_service or not _swarm_service:
        raise HTTPException(500, "Services not initialized")
    
    swarm_data = _swarm_service.get_network_status()
    return await _quantum_service.analyze_outbreak_pattern(swarm_data)
