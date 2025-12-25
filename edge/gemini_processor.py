import google.generativeai as genai
from PIL import Image
import io
import json
from typing import Dict, List, Optional
import base64

class GeminiProcessor:
    """
    Gemini Multimodal Processor for Edge AI
    Processes voice, images, and text from ASHA workers
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.text_model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
    
    async def process_voice(self, audio_data: bytes, language: str = "hi-IN") -> Dict:
        """
        Process voice input in local dialects
        
        Args:
            audio_data: Raw audio bytes
            language: Language code (hi-IN for Hindi, etc.)
        
        Returns:
            Dict with transcription and extracted symptoms
        """
        try:
            # In production, use Gemini's audio processing
            # For now, simulate with text prompt
            prompt = """
            Transcribe this audio and extract medical symptoms.
            
            Expected input: Patient describing symptoms in Hindi/local language
            
            Return JSON:
            {
                "transcription": "original text",
                "language_detected": "language code",
                "symptoms_extracted": ["symptom1", "symptom2"],
                "confidence": 0.0-1.0
            }
            """
            
            # Simulated response for demo
            # In production: response = await self.text_model.generate_content([prompt, audio_data])
            
            return {
                'transcription': 'मुझे बुखार और सिर दर्द है (I have fever and headache)',
                'language_detected': 'Hindi',
                'symptoms_extracted': ['fever', 'headache'],
                'confidence': 0.92
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'transcription': '',
                'symptoms_extracted': []
            }
    
    async def process_image(self, image_data: bytes) -> Dict:
        """
        Analyze medical images using Gemini Vision
        
        Args:
            image_data: Raw image bytes (JPEG, PNG)
        
        Returns:
            Dict with image analysis results
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            prompt = """
            Analyze this medical/environmental image:
            
            1. Identify visible symptoms (rashes, lesions, skin conditions)
            2. Assess severity (mild/moderate/severe)
            3. Identify environmental hazards (standing water, mosquito breeding sites)
            4. Suggest possible conditions
            
            Return JSON format:
            {
                "detected_conditions": ["condition1", "condition2"],
                "environmental_hazards": ["hazard1"],
                "severity": "mild/moderate/severe",
                "confidence": 0.0-1.0,
                "recommendations": ["action1", "action2"]
            }
            """
            
            response = self.vision_model.generate_content([prompt, image])
            
            # Parse response
            result = self._parse_gemini_response(response.text)
            
            return result
        
        except Exception as e:
            return {
                'error': str(e),
                'detected_conditions': [],
                'environmental_hazards': []
            }
    
    async def normalize_symptoms(self, symptoms: List[str], context: Dict) -> Dict:
        """
        Normalize and categorize symptoms using Gemini
        
        Args:
            symptoms: List of symptom strings
            context: Additional context (location, demographics, etc.)
        
        Returns:
            Dict with normalized symptoms and categorization
        """
        try:
            prompt = f"""
            Normalize and categorize these symptoms:
            Symptoms: {', '.join(symptoms)}
            Context: {json.dumps(context)}
            
            Return JSON:
            {{
                "normalized_symptoms": ["standardized_symptom1", "symptom2"],
                "category": "disease_category",
                "urgency_score": 0.0-1.0,
                "possible_conditions": ["condition1", "condition2"],
                "recommended_tests": ["test1", "test2"]
            }}
            
            Categories: vector_borne_disease, water_borne_disease, respiratory_infection, etc.
            """
            
            response = self.text_model.generate_content(prompt)
            result = self._parse_gemini_response(response.text)
            
            return result
        
        except Exception as e:
            return {
                'error': str(e),
                'normalized_symptoms': symptoms,
                'category': 'unknown',
                'urgency_score': 0.5
            }
    
    def _parse_gemini_response(self, text: str) -> Dict:
        """
        Parse Gemini response text to JSON
        """
        try:
            # Remove markdown code blocks if present
            text = text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except:
            # Fallback if JSON parsing fails
            return {'raw_response': text}