"""
Edge AI API Router
Note: Main endpoints are in main.py. This is for modular routing if needed.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import json

router = APIRouter(prefix="/edge", tags=["Edge AI"])

# Services will be injected
_edge_service = None
_swarm_service = None

def set_services(edge_service, swarm_service):
    """Set service dependencies"""
    global _edge_service, _swarm_service
    _edge_service = edge_service
    _swarm_service = swarm_service

@router.post("/submit-report")
async def submit_symptom_report(
    village_id: str = Form(...),
    symptoms: str = Form(...),
    voice: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    metadata: Optional[str] = Form(None)
):
    """
    Submit symptom report from ASHA worker
    """
    if not _edge_service or not _swarm_service:
        raise HTTPException(500, "Services not initialized")
    
    # Parse JSON inputs
    try:
        symptoms_list = json.loads(symptoms)
        metadata_dict = json.loads(metadata) if metadata else {}
    except:
        raise HTTPException(400, "Invalid JSON in symptoms or metadata")
    
    # Process with Edge AI
    edge_result = await _edge_service.normalize_symptoms(symptoms_list, metadata_dict)
    
    # Send to Swarm
    swarm_result = await _swarm_service.process_symptom_report(
        village_id=village_id,
        symptoms=symptoms_list,
        metadata={'edge_analysis': edge_result}
    )
    
    return {
        'status': 'success',
        'village_id': village_id,
        'edge_analysis': edge_result,
        'swarm_response': swarm_result
    }

@router.post("/process-voice")
async def process_voice_only(
    audio: UploadFile = File(...),
    language: str = Form("hi-IN")
):
    """Process voice input only"""
    if not _edge_service:
        raise HTTPException(500, "Edge AI service not initialized")
    
    audio_data = await audio.read()
    result = await _edge_service.process_voice(audio_data)
    
    return result

@router.post("/process-image")
async def process_image_only(image: UploadFile = File(...)):
    """Process image only"""
    if not _edge_service:
        raise HTTPException(500, "Edge AI service not initialized")
    
    image_data = await image.read()
    result = await _edge_service.process_image(image_data)
    
    return result
