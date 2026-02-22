"""
Risk scoring engine
Calculates patient risk scores based on multiple factors
"""
from typing import Dict, List
from app.config import settings
from app.models.risk import RiskLevel


class RiskScorer:
    """
    Calculate overall risk scores from multiple inputs
    """
    
    # PHQ-9 score interpretation
    PHQ9_RANGES = {
        (0, 4): 5,      # Minimal - 5% contribution
        (5, 9): 15,     # Mild - 15%
        (10, 14): 35,   # moderate - 35%
        (15, 19): 60,   # moderately severe - 60%
        (20, 27): 85    # Severe - 85%
    }
    
    # GAD-7 score interpretation
    GAD7_RANGES = {
        (0, 4): 5,      # Minimal
        (5, 9): 15,     # Mild
        (10, 14): 40,   # moderate
        (15, 21): 70    # Severe
    }
    
    def __init__(self):
        self.critical_threshold = settings.critical_RISK_THRESHOLD
        self.high_threshold = settings.high_RISK_THRESHOLD
        self.moderate_threshold = settings.moderate_RISK_THRESHOLD
    
    def calculate_overall_risk(
        self,
        phq9_score: int,
        gad7_score: int,
        sentiment_score: float,
        crisis_keywords: List[str],
        self_harm_score: int
    ) -> Dict:
        """
        Calculate overall risk score and level
        
        Returns:
            Dict with risk_score (0-100) and risk_level
        """
        
        # Component scores
        phq9_risk = self._score_from_range(phq9_score, self.PHQ9_RANGES)
        gad7_risk = self._score_from_range(gad7_score, self.GAD7_RANGES)
        sentiment_risk = self._sentiment_to_risk(sentiment_score)
        crisis_risk = self._crisis_keyword_risk(crisis_keywords)
        self_harm_risk = self._self_harm_to_risk(self_harm_score)
        
        # Weighted combination
        # higher weights for more direct indicators
        overall_score = (
            phq9_risk * 0.25 +          # 25% weight
            gad7_risk * 0.20 +          # 20% weight
            sentiment_risk * 0.15 +      # 15% weight
            crisis_risk * 0.25 +         # 25% weight (high importance)
            self_harm_risk * 0.15        # 15% weight
        )
        
        # If crisis keywords present, minimum score is 60 (high risk)
        if crisis_keywords and len(crisis_keywords) > 0:
            overall_score = max(overall_score, 60.0)
        
        # If self-harm question scored high, minimum is 70
        if self_harm_score >= 2:  # "More than half the days" or higher
            overall_score = max(overall_score, 70.0)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Determine recommended urgency
        urgency = self._determine_urgency(overall_score, crisis_keywords, self_harm_score)
        
        return {
            "overall_risk_score": round(overall_score, 2),
            "risk_level": risk_level,
            "recommended_urgency": urgency,
            "component_scores": {
                "phq9_risk": round(phq9_risk, 2),
                "gad7_risk": round(gad7_risk, 2),
                "sentiment_risk": round(sentiment_risk, 2),
                "crisis_keyword_risk": round(crisis_risk, 2),
                "self_harm_risk": round(self_harm_risk, 2)
            }
        }
    
    def _score_from_range(self, score: int, ranges: Dict) -> float:
        """Convert a questionnaire score to risk percentage using ranges"""
        for (min_val, max_val), risk in ranges.items():
            if min_val <= score <= max_val:
                return float(risk)
        return 50.0  # Default medium risk if out of range
    
    def _sentiment_to_risk(self, sentiment: float) -> float:
        """
        Convert sentiment score (-1.0 to 1.0) to risk (0-100)
        More negative sentiment = higher risk
        """
        if sentiment is None:
            return 30.0
        
        # Map -1.0 to 1.0 -> 80 to 10
        # Very negative (-1.0) = 80% risk
        # Neutral (0.0) = 45% risk
        # Very positive (1.0) = 10% risk
        risk = 45 + (-sentiment * 35)
        return max(0.0, min(100.0, risk))
    
    def _crisis_keyword_risk(self, keywords: List[str]) -> float:
        """
        Calculate risk based on crisis keywords detected
        """
        if not keywords or len(keywords) == 0:
            return 10.0  # low baseline if no keywords
        
        # Progressive increase based on number of keywords
        keyword_count = len(keywords)
        
        if keyword_count == 1:
            return 60.0
        elif keyword_count == 2:
            return 75.0
        elif keyword_count >= 3:
            return 90.0
        
        return 50.0
    
    def _self_harm_to_risk(self, self_harm_score: int) -> float:
        """
        Convert PHQ-9 self-harm question to risk
        This is question 9: "Thoughts that you would be better off dead or hurting yourself"
        0 = Not at all
        1 = Several days
        2 = More than half the days
        3 = Nearly every day
        """
        if self_harm_score is None:
            return 20.0
        
        mapping = {
            0: 10.0,   # Not at all - low risk
            1: 50.0,   # Several days - moderate risk
            2: 75.0,   # More than half - high risk
            3: 95.0    # Nearly every day - critical risk
        }
        
        return mapping.get(self_harm_score, 50.0)
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level enum"""
        if score >= self.critical_threshold:
            return RiskLevel.critical
        elif score >= self.high_threshold:
            return RiskLevel.high
        elif score >= self.moderate_threshold:
            return RiskLevel.moderate
        else:
            return RiskLevel.low
    
    def _determine_urgency(
        self, 
        score: float, 
        crisis_keywords: List[str],
        self_harm_score: int
    ) -> str:
        """
        Determine recommended urgency for scheduling
        """
        # Immediate if crisis keywords or high self-harm score
        if (crisis_keywords and len(crisis_keywords) > 0) or (self_harm_score and self_harm_score >= 2):
            return "immediate"
        
        # Urgent if critical or high risk
        if score >= self.high_threshold:
            return "urgent"
        
        # Standard for moderate and below
        return "standard"


# Singleton instance
risk_scorer = RiskScorer()
