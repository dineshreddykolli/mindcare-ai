"""
AI Service for LLM integration (Claude/OpenAI)
Handles sentiment analysis, crisis detection, and text understanding
"""
import anthropic
import openai
from typing import Dict, List, Optional, Tuple
import re
from app.config import settings


class AIService:
    """
    Unified AI service supporting both Anthropic Claude and OpenAI
    """
    
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        
        if self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.LLM_MODEL
        elif self.provider == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.model = settings.LLM_MODEL
        else:
            raise ValueError("No valid AI provider configured")
    
    async def analyze_intake_text(
        self, 
        primary_concern: str, 
        symptoms: Optional[str] = None,
        goals: Optional[str] = None
    ) -> Dict:
        """
        Analyze patient's intake text responses for:
        - Sentiment (positive/negative/neutral)
        - Crisis keywords detection
        - Urgency level
        - Key themes
        """
        
        # Combine all text
        full_text = f"Primary Concern: {primary_concern}\n"
        if symptoms:
            full_text += f"Symptoms: {symptoms}\n"
        if goals:
            full_text += f"Goals: {goals}\n"
        
        # Check for crisis keywords first
        crisis_keywords = self._detect_crisis_keywords(full_text)
        
        # Prepare prompt for LLM
        prompt = f"""Analyze the following mental health intake text and provide:

1. Sentiment score (-1.0 to 1.0): How negative/positive is the overall tone?
2. Urgency level (low/medium/high/critical): Based on severity of concerns
3. Key themes (list 3-5): Main psychological issues or concerns mentioned
4. Crisis indicators (yes/no): Any immediate safety concerns?
5. Brief summary (2-3 sentences): Clinical interpretation

Patient's intake text:
{full_text}

Respond in this exact JSON format:
{{
    "sentiment_score": <float between -1.0 and 1.0>,
    "urgency_level": "<low|medium|high|critical>",
    "key_themes": ["theme1", "theme2", "theme3"],
    "crisis_indicators": <true or false>,
    "summary": "<brief clinical summary>"
}}"""
        
        # Call LLM
        result = await self._call_llm(prompt)
        
        # Parse response
        analysis = self._parse_json_response(result)
        
        # Add detected crisis keywords
        analysis["crisis_keywords_detected"] = crisis_keywords
        analysis["has_crisis_keywords"] = len(crisis_keywords) > 0
        
        return analysis
    
    def _detect_crisis_keywords(self, text: str) -> List[str]:
        """
        Detect crisis-related keywords in text
        """
        text_lower = text.lower()
        detected = []
        
        for keyword in settings.CRISIS_KEYWORDS:
            if keyword.lower() in text_lower:
                detected.append(keyword)
        
        return detected
    
    async def generate_therapist_match_reasoning(
        self,
        patient_info: Dict,
        therapist_info: Dict,
        match_score: float
    ) -> str:
        """
        Generate explanation for why a therapist was matched to a patient
        """
        
        prompt = f"""Explain why this therapist is a good match for this patient.

Patient:
- Primary concern: {patient_info.get('primary_concern', 'Not specified')}
- Risk level: {patient_info.get('risk_level', 'Unknown')}
- Preferences: {patient_info.get('preferences', 'None specified')}

Therapist:
- Name: {therapist_info.get('name')}
- Specialties: {', '.join(therapist_info.get('specialties', []))}
- Languages: {', '.join(therapist_info.get('languages', []))}
- Experience: {therapist_info.get('years_experience', 0)} years
- Accepts high-risk: {therapist_info.get('accepts_high_risk', False)}

Match Score: {match_score}/100

Provide a brief 2-3 sentence explanation for this match that would be helpful for clinic staff."""
        
        result = await self._call_llm(prompt)
        return result.strip()
    
    async def chatbot_response(
        self, 
        conversation_history: List[Dict],
        current_question: str
    ) -> str:
        """
        Generate chatbot response for intake process
        """
        
        system_prompt = """You are a compassionate mental health intake assistant for MindCare AI clinic. 
        
Your role is to:
1. Ask one question at a time to gather information
2. Be empathetic and non-judgmental
3. Collect information about: chief concerns, symptoms, goals, previous treatment, current medications
4. If someone mentions crisis indicators (suicide, self-harm), immediately express concern and recommend crisis resources
5. Keep responses brief and focused (2-3 sentences max)

Do not diagnose or provide treatment advice. Your goal is to gather information for proper triage."""
        
        # Build conversation
        messages = [{"role": "system", "content": system_prompt}]
        for msg in conversation_history:
            messages.append(msg)
        messages.append({"role": "user", "content": current_question})
        
        # Call LLM
        result = await self._call_llm_chat(messages)
        return result
    
    async def _call_llm(self, prompt: str) -> str:
        """
        Call LLM with a single prompt
        """
        if self.provider == "anthropic":
            message = self.client.messages.create(
                model=self.model,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        
        elif self.provider == "openai":
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE
            )
            return response.choices[0].message.content
        
        raise ValueError(f"Unknown provider: {self.provider}")
    
    async def _call_llm_chat(self, messages: List[Dict]) -> str:
        """
        Call LLM with conversation history
        """
        if self.provider == "anthropic":
            # Anthropic requires system message separate
            system_msg = None
            filtered_messages = []
            
            for msg in messages:
                if msg.get("role") == "system":
                    system_msg = msg.get("content")
                else:
                    filtered_messages.append(msg)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                system=system_msg,
                messages=filtered_messages
            )
            return message.content[0].text
        
        elif self.provider == "openai":
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE
            )
            return response.choices[0].message.content
        
        raise ValueError(f"Unknown provider: {self.provider}")
    
    def _parse_json_response(self, response: str) -> Dict:
        """
        Parse JSON from LLM response (handles markdown code blocks)
        """
        import json
        
        # Remove markdown code blocks if present
        response = re.sub(r'```json\n?', '', response)
        response = re.sub(r'```\n?', '', response)
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Return default values if parsing fails
            return {
                "sentiment_score": 0.0,
                "urgency_level": "medium",
                "key_themes": ["Unable to parse"],
                "crisis_indicators": False,
                "summary": "Error parsing AI response"
            }


# Singleton instance
ai_service = AIService()
