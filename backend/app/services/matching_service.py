"""
Therapist-Patient Matching Service
Uses AI to match patients with optimal therapists
"""
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.models.therapist import Therapist
from app.models.risk import RiskLevel


class TherapistMatcher:
    """
    Match patients with therapists based on multiple criteria
    """
    
    def find_best_matches(
        self,
        db: Session,
        patient_data: Dict,
        top_n: int = 3
    ) -> List[Tuple[Therapist, float, str]]:
        """
        Find best therapist matches for a patient
        
        Args:
            db: Database session
            patient_data: Patient information including:
                - risk_level: RiskLevel
                - primary_concern: str
                - preferred_language: str
                - preferred_gender: Optional[str]
            top_n: Number of top matches to return
        
        Returns:
            List of (Therapist, match_score, reasoning) tuples
        """
        
        # Get all active therapists with capacity
        therapists = db.query(Therapist).filter(
            Therapist.active == True
        ).all()
        
        # Score each therapist
        scored_therapists = []
        for therapist in therapists:
            score, reasoning = self._calculate_match_score(therapist, patient_data)
            scored_therapists.append((therapist, score, reasoning))
        
        # Sort by score descending
        scored_therapists.sort(key=lambda x: x[1], reverse=True)
        
        return scored_therapists[:top_n]
    
    def _calculate_match_score(
        self,
        therapist: Therapist,
        patient_data: Dict
    ) -> Tuple[float, str]:
        """
        Calculate match score between therapist and patient
        
        Returns:
            (score from 0-100, reasoning text)
        """
        score = 0.0
        reasons = []
        
        # 1. Capacity check (40 points)
        if not therapist.has_capacity:
            score += 0
            reasons.append("❌ No current capacity")
            # Early return for no capacity
            return (0.0, "; ".join(reasons))
        else:
            capacity_score = (therapist.capacity_remaining / therapist.max_caseload) * 40
            score += capacity_score
            reasons.append(f"✓ {therapist.capacity_remaining} slots available")
        
        # 2. Risk level compatibility (25 points)
        risk_level = patient_data.get("risk_level")
        if risk_level in [RiskLevel.high, RiskLevel.critical]:
            if therapist.accepts_high_risk:
                score += 25
                reasons.append("✓ Accepts high-risk patients")
            else:
                score += 0
                reasons.append("❌ Does not accept high-risk patients")
        else:
            score += 15  # All therapists can handle low/moderate
            reasons.append("✓ Risk level compatible")
        
        # 3. Specialty match (20 points)
        primary_concern = patient_data.get("primary_concern", "").lower()
        specialty_match = self._match_specialty(primary_concern, therapist.specialties)
        
        if specialty_match:
            score += 20
            reasons.append(f"✓ Specialty match: {specialty_match}")
        else:
            score += 5
            reasons.append("○ General practice")
        
        # 4. Language preference (10 points)
        preferred_lang = patient_data.get("preferred_language", "English")
        if preferred_lang in therapist.languages:
            score += 10
            reasons.append(f"✓ Speaks {preferred_lang}")
        else:
            score += 0
            reasons.append(f"○ {preferred_lang} not available")
        
        # 5. Experience bonus (5 points)
        if therapist.years_experience and therapist.years_experience >= 10:
            score += 5
            reasons.append(f"✓ {therapist.years_experience}+ years experience")
        elif therapist.years_experience and therapist.years_experience >= 5:
            score += 3
            reasons.append(f"✓ {therapist.years_experience} years experience")
        
        reasoning = "; ".join(reasons)
        return (round(score, 2), reasoning)
    
    def _match_specialty(self, concern: str, specialties: List[str]) -> str:
        """
        Match patient concern keywords to therapist specialties
        """
        # Keyword mappings
        specialty_keywords = {
            "anxiety": ["anxiety", "anxious", "panic", "worry", "fear", "phobia"],
            "depression": ["depression", "depressed", "sad", "hopeless", "suicide"],
            "trauma": ["trauma", "ptsd", "abuse", "assault", "violence"],
            "addiction": ["addiction", "substance", "alcohol", "drug", "drinking"],
            "family": ["family", "parent", "child", "sibling"],
            "couples": ["relationship", "marriage", "partner", "couples"],
            "eating_disorders": ["eating", "anorexia", "bulimia", "binge"],
            "child": ["child", "teen", "adolescent", "young"]
        }
        
        concern_lower = concern.lower()
        
        for specialty in specialties:
            keywords = specialty_keywords.get(specialty, [])
            for keyword in keywords:
                if keyword in concern_lower:
                    return specialty
        
        return None


# Singleton instance
therapist_matcher = TherapistMatcher()
