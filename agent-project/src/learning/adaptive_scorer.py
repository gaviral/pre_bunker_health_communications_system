"""Adaptive risk scorer that incorporates learning"""

from typing import Dict, List, Any
from src.claims.risk_scorer import RiskScorer
from src.learning.feedback_learner import feedback_learner

class AdaptiveRiskScorer(RiskScorer):
    """Risk scorer that adapts based on human feedback"""
    
    def __init__(self):
        super().__init__()
        self.learner = feedback_learner
        self.use_adaptive_scoring = True
    
    def score_claims(self, claims: List, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Score claims with adaptive adjustments"""
        # Score each claim individually using parent class method
        scored_claims = []
        total_risk = 0.0
        
        for claim in claims:
            if isinstance(claim, str):
                claim_text = claim
            else:
                claim_text = getattr(claim, 'text', str(claim))
            
            score = self.score_claim(claim_text)
            scored_claims.append({
                'claim': claim_text,
                'risk_score': score
            })
            total_risk += score
        
        base_result = {
            'claims': scored_claims,
            'overall_risk_score': total_risk / len(claims) if claims else 0.0,
            'high_risk_claims': [c for c in scored_claims if c['risk_score'] > 0.7]
        }
        
        if not self.use_adaptive_scoring:
            return base_result
        
        # Apply learning-based adjustments
        adjusted_result = self._apply_learning_adjustments(base_result, claims)
        
        return adjusted_result
    
    def _apply_learning_adjustments(self, base_result: Dict, claims: List) -> Dict[str, Any]:
        """Apply learned adjustments to risk scoring"""
        # Extract features for learning system
        analysis_features = {
            'claims': claims,
            'risk_report': base_result,
            'evidence_validations': [],  # Would be populated in full pipeline
            'persona_interpretations': [],  # Would be populated in full pipeline
            'countermeasures': {}  # Would be populated in full pipeline
        }
        
        features = self.learner.extract_features(analysis_features)
        
        # Get original overall risk score
        original_score = base_result.get('overall_risk_score', 0.0)
        
        # Apply learned adjustments
        adjusted_score = self.learner.get_adjusted_risk_score(original_score, features)
        
        # Update result with adjusted scores
        adjusted_result = base_result.copy()
        adjusted_result['overall_risk_score'] = adjusted_score
        adjusted_result['learning_adjustment'] = adjusted_score - original_score
        adjusted_result['features_detected'] = features
        adjusted_result['current_weights'] = self.learner.weight_adjustments.copy()
        
        # Adjust individual claim scores proportionally
        if 'claim_scores' in base_result and base_result['claim_scores']:
            adjustment_ratio = adjusted_score / max(0.01, original_score)  # Avoid division by zero
            adjusted_result['claim_scores'] = {
                claim: score * adjustment_ratio 
                for claim, score in base_result['claim_scores'].items()
            }
        
        return adjusted_result
    
    def enable_adaptive_scoring(self):
        """Enable adaptive scoring based on feedback"""
        self.use_adaptive_scoring = True
    
    def disable_adaptive_scoring(self):
        """Disable adaptive scoring (use base scoring only)"""
        self.use_adaptive_scoring = False
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning system status"""
        patterns = self.learner.analyze_feedback_patterns()
        recommendations = self.learner.get_recommendations()
        
        return {
            'adaptive_scoring_enabled': self.use_adaptive_scoring,
            'feedback_count': len(self.learner.feedback_history),
            'current_weights': self.learner.weight_adjustments.copy(),
            'performance_patterns': patterns,
            'recommendations': recommendations,
            'learning_rate': self.learner.learning_rate
        }
    
    def record_human_feedback(self, original_analysis: Dict, human_decision: str, reviewer_notes: str, reviewer_id: str = None):
        """Record human feedback for learning"""
        return self.learner.record_feedback(original_analysis, human_decision, reviewer_notes, reviewer_id)
    
    def reset_learning(self):
        """Reset learning system to initial state"""
        self.learner.feedback_history = []
        self.learner.weight_adjustments = {
            'absolutist_language': 1.0,
            'missing_evidence': 1.0,
            'ambiguous_terms': 1.0,
            'emotional_appeals': 1.0,
            'unsupported_claims': 1.0,
            'persona_concerns': 1.0
        }

# Global adaptive scorer instance
adaptive_risk_scorer = AdaptiveRiskScorer()
