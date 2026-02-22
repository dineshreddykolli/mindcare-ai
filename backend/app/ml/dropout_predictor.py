"""
Dropout Prediction ML Model
Predicts likelihood of patient dropping out of therapy
"""
import numpy as np
from typing import Dict, List
import pickle
import os


class DropoutPredictor:
    """
    Machine learning model for predicting patient dropout risk
    
    In production, this would use a trained scikit-learn/XGBoost model
    For MVP, uses heuristic-based prediction
    """
    
    def __init__(self):
        self.model = None
        self.model_version = "1.0.0-heuristic"
        
        # Try to load trained model if exists
        model_path = "app/ml/dropout_model.pkl"
        if os.path.exists(model_path):
            self._load_model(model_path)
    
    def predict_dropout_probability(self, features: Dict) -> Dict:
        """
        Predict dropout probability and identify risk factors
        
        Args:
            features: Dictionary containing:
                - sessions_attended: int
                - sessions_cancelled: int
                - sessions_no_show: int
                - days_since_last_session: int
                - sentiment_trend: float (-1.0 to 1.0)
                - avg_response_time_hours: float
                - has_insurance: bool
                - distance_miles: Optional[float]
        
        Returns:
            Dict with:
                - dropout_probability: float (0-100)
                - risk_factors: List[str]
                - confidence: float (0-100)
        """
        
        if self.model:
            # Use trained model if available
            return self._predict_with_model(features)
        else:
            # Use heuristic approach for MVP
            return self._predict_heuristic(features)
    
    def _predict_heuristic(self, features: Dict) -> Dict:
        """
        Heuristic-based prediction using domain knowledge
        """
        probability = 0.0
        risk_factors = []
        
        # Feature extraction
        sessions_attended = features.get("sessions_attended", 0)
        sessions_cancelled = features.get("sessions_cancelled", 0)
        sessions_no_show = features.get("sessions_no_show", 0)
        days_since_last = features.get("days_since_last_session", 0)
        sentiment_trend = features.get("sentiment_trend", 0.0)
        response_time = features.get("avg_response_time_hours", 24.0)
        
        total_sessions = sessions_attended + sessions_cancelled + sessions_no_show
        
        # 1. Attendance pattern (40% weight)
        if total_sessions > 0:
            attendance_rate = sessions_attended / total_sessions
            
            if attendance_rate < 0.5:
                probability += 40
                risk_factors.append("low attendance rate (<50%)")
            elif attendance_rate < 0.75:
                probability += 25
                risk_factors.append("moderate attendance rate")
            else:
                probability += 5
        
        # 2. No-show pattern (25% weight)
        if sessions_no_show > 0:
            no_show_rate = sessions_no_show / max(total_sessions, 1)
            
            if no_show_rate > 0.3:
                probability += 25
                risk_factors.append("high no-show rate (>30%)")
            elif no_show_rate > 0.1:
                probability += 15
                risk_factors.append("Some no-shows")
        
        # 3. Days since last session (20% weight)
        if days_since_last > 30:
            probability += 20
            risk_factors.append(f"No session in {days_since_last} days")
        elif days_since_last > 14:
            probability += 10
            risk_factors.append("Session gap >2 weeks")
        
        # 4. Sentiment trend (10% weight)
        if sentiment_trend < -0.3:
            probability += 10
            risk_factors.append("Declining sentiment")
        elif sentiment_trend < 0:
            probability += 5
        
        # 5. Response time (5% weight)
        if response_time > 72:
            probability += 5
            risk_factors.append("Slow response to communications")
        
        # Additional risk factors
        
        # Early dropout risk (first 3 sessions)
        if total_sessions <= 3 and sessions_cancelled > 0:
            probability += 15
            risk_factors.append("Early cancellation pattern")
        
        # No recent engagement
        if sessions_attended == 0 and total_sessions > 0:
            probability += 20
            risk_factors.append("Never attended a session")
        
        # Cap at 100
        probability = min(100.0, probability)
        
        # Confidence based on data availability
        confidence = self._calculate_confidence(features)
        
        return {
            "dropout_probability": round(probability, 2),
            "risk_factors": risk_factors,
            "confidence": round(confidence, 2),
            "model_version": self.model_version
        }
    
    def _calculate_confidence(self, features: Dict) -> float:
        """
        Calculate prediction confidence based on feature completeness
        """
        confidence = 100.0
        
        # Reduce confidence if limited data
        total_sessions = (
            features.get("sessions_attended", 0) +
            features.get("sessions_cancelled", 0) +
            features.get("sessions_no_show", 0)
        )
        
        if total_sessions == 0:
            confidence -= 40  # No session history
        elif total_sessions < 3:
            confidence -= 20  # Limited history
        
        if features.get("sentiment_trend") is None:
            confidence -= 10
        
        if features.get("avg_response_time_hours") is None:
            confidence -= 10
        
        return max(20.0, confidence)
    
    def _predict_with_model(self, features: Dict) -> Dict:
        """
        Predict using trained ML model (for future implementation)
        """
        # Placeholder for actual ML model prediction
        # Would convert features to numpy array and call model.predict()
        pass
    
    def _load_model(self, path: str):
        """Load trained model from disk"""
        try:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"Loaded dropout prediction model from {path}")
        except Exception as e:
            print(f"Could not load model: {e}")
            self.model = None
    
    def train_model(self, training_data: List[Dict], labels: List[int]):
        """
        Train the dropout prediction model
        
        Args:
            training_data: List of feature dictionaries
            labels: List of 0/1 indicating dropout (1) or retained (0)
        
        This would be implemented with scikit-learn in production:
        - Feature engineering
        - Train/test split
        - Model selection (Random Forest, XGBoost, etc.)
        - Hyperparameter tuning
        - Model evaluation
        """
        # Placeholder for training logic
        # In production, this would:
        # 1. Process features into numpy arrays
        # 2. Split train/test
        # 3. Train model (e.g., RandomForestClassifier)
        # 4. Evaluate on test set
        # 5. Save model to disk
        pass


# Singleton instance
dropout_predictor = DropoutPredictor()
