"""Learning system for feedback-based improvement"""

from datetime import datetime
from typing import Dict, List, Any, Optional

class FeedbackLearner:
    """Learn from reviewer feedback to improve risk scoring"""
    
    def __init__(self):
        self.feedback_history = []
        self.weight_adjustments = {
            'absolutist_language': 1.0,
            'missing_evidence': 1.0,
            'ambiguous_terms': 1.0,
            'emotional_appeals': 1.0,
            'unsupported_claims': 1.0,
            'persona_concerns': 1.0
        }
        self.learning_rate = 0.05
        self.min_feedback_for_adjustment = 5
        
    def record_feedback(self, original_analysis: Dict, human_decision: str, reviewer_notes: str, reviewer_id: str = None):
        """Record human feedback for learning"""
        feedback_record = {
            'original_risk_score': original_analysis.get('risk_report', {}).get('overall_risk_score', 0.0),
            'human_approved': human_decision == 'approved',
            'human_decision': human_decision,  # approved, rejected, revision_requested
            'reviewer_notes': reviewer_notes,
            'reviewer_id': reviewer_id,
            'analysis_features': self.extract_features(original_analysis),
            'timestamp': datetime.now().isoformat(),
            'message_id': original_analysis.get('message_id', 'unknown')
        }
        
        self.feedback_history.append(feedback_record)
        
        # Update weights based on feedback if we have enough data
        if len(self.feedback_history) >= self.min_feedback_for_adjustment:
            self.update_weights(feedback_record)
        
        return len(self.feedback_history) - 1  # Return feedback index
    
    def extract_features(self, analysis: Dict) -> Dict[str, Any]:
        """Extract features from analysis for learning"""
        features = {}
        
        # Count different types of risky patterns
        claims = analysis.get('claims', [])
        
        # Absolutist language detection
        absolutist_words = ['always', 'never', '100%', 'guaranteed', 'completely', 'totally', 'absolutely']
        features['absolutist_count'] = sum(1 for claim in claims if any(
            word in str(claim).lower() for word in absolutist_words
        ))
        
        # Evidence availability
        evidence_validations = analysis.get('evidence_validations', [])
        features['missing_evidence'] = 1 if len(evidence_validations) == 0 else 0
        features['evidence_found_ratio'] = sum(1 for ev in evidence_validations if ev.get('evidence_found', False)) / max(1, len(evidence_validations))
        
        # Risk indicators from risk report
        risk_report = analysis.get('risk_report', {})
        features['high_risk_claims'] = risk_report.get('high_risk_claim_count', 0)
        features['overall_risk_score'] = risk_report.get('overall_risk_score', 0.0)
        
        # Persona concern analysis
        persona_interpretations = analysis.get('persona_interpretations', [])
        features['persona_concerns'] = sum(
            len(interp.get('potential_misreading', [])) 
            for interp in persona_interpretations
        )
        features['concerned_personas'] = sum(
            1 for interp in persona_interpretations 
            if len(interp.get('potential_misreading', [])) > 0
        )
        
        # Countermeasure effectiveness
        countermeasures = analysis.get('countermeasures', {})
        if countermeasures:
            effectiveness_scores = [
                cm.get('effectiveness_score', 0) 
                for cm in countermeasures.values() 
                if isinstance(cm, dict) and 'effectiveness_score' in cm
            ]
            features['avg_countermeasure_effectiveness'] = statistics.mean(effectiveness_scores) if effectiveness_scores else 0.0
        else:
            features['avg_countermeasure_effectiveness'] = 0.0
        
        # Message characteristics
        features['claim_count'] = len(claims)
        features['countermeasure_count'] = len(countermeasures)
        
        return features
    
    def update_weights(self, feedback_record: Dict):
        """Adjust scoring weights based on human feedback"""
        features = feedback_record['analysis_features']
        human_approved = feedback_record['human_approved']
        human_decision = feedback_record['human_decision']
        original_risk = feedback_record['original_risk_score']
        
        # Determine if this was a false positive or false negative
        false_positive = human_approved and original_risk > 0.6  # System said high risk, human approved
        false_negative = (human_decision in ['rejected', 'revision_requested']) and original_risk < 0.4  # System said low risk, human rejected
        
        if false_positive:
            # Reduce weights for features that contributed to over-scoring
            self._adjust_weights_down(features)
        elif false_negative:
            # Increase weights for features that should have scored higher
            self._adjust_weights_up(features)
        
        # Ensure weights stay within reasonable bounds
        self._constrain_weights()
    
    def _adjust_weights_down(self, features: Dict):
        """Reduce weights when system over-scored"""
        if features['absolutist_count'] > 0:
            self.weight_adjustments['absolutist_language'] = max(0.5, 
                self.weight_adjustments['absolutist_language'] * (1 - self.learning_rate))
        
        if features['missing_evidence'] > 0:
            self.weight_adjustments['missing_evidence'] = max(0.5,
                self.weight_adjustments['missing_evidence'] * (1 - self.learning_rate))
        
        if features['persona_concerns'] > 5:
            self.weight_adjustments['persona_concerns'] = max(0.5,
                self.weight_adjustments['persona_concerns'] * (1 - self.learning_rate))
    
    def _adjust_weights_up(self, features: Dict):
        """Increase weights when system under-scored"""
        if features['absolutist_count'] > 0:
            self.weight_adjustments['absolutist_language'] = min(2.0,
                self.weight_adjustments['absolutist_language'] * (1 + self.learning_rate))
        
        if features['missing_evidence'] > 0:
            self.weight_adjustments['missing_evidence'] = min(2.0,
                self.weight_adjustments['missing_evidence'] * (1 + self.learning_rate))
        
        if features['persona_concerns'] > 3:
            self.weight_adjustments['persona_concerns'] = min(2.0,
                self.weight_adjustments['persona_concerns'] * (1 + self.learning_rate))
    
    def _constrain_weights(self):
        """Keep weights within reasonable bounds"""
        for key in self.weight_adjustments:
            self.weight_adjustments[key] = max(0.3, min(2.5, self.weight_adjustments[key]))
    
    def get_adjusted_risk_score(self, original_risk_score: float, features: Dict) -> float:
        """Apply learned adjustments to risk score"""
        adjustment_factor = 1.0
        
        # Apply feature-based adjustments
        if features.get('absolutist_count', 0) > 0:
            adjustment_factor *= self.weight_adjustments['absolutist_language']
        
        if features.get('missing_evidence', 0) > 0:
            adjustment_factor *= self.weight_adjustments['missing_evidence']
        
        if features.get('persona_concerns', 0) > 5:
            adjustment_factor *= self.weight_adjustments['persona_concerns']
        
        # Apply adjustment with bounds
        adjusted_score = original_risk_score * adjustment_factor
        return max(0.0, min(1.0, adjusted_score))
    
    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in feedback history"""
        if not self.feedback_history:
            return {'error': 'No feedback data available'}
        
        total_feedback = len(self.feedback_history)
        approved_count = sum(1 for fb in self.feedback_history if fb['human_approved'])
        rejected_count = sum(1 for fb in self.feedback_history if fb['human_decision'] == 'rejected')
        revision_count = sum(1 for fb in self.feedback_history if fb['human_decision'] == 'revision_requested')
        
        # Calculate accuracy metrics
        approval_rate = approved_count / total_feedback
        false_positive_rate = sum(1 for fb in self.feedback_history 
                                if fb['human_approved'] and fb['original_risk_score'] > 0.6) / total_feedback
        false_negative_rate = sum(1 for fb in self.feedback_history 
                                if not fb['human_approved'] and fb['original_risk_score'] < 0.4) / total_feedback
        
        # Analyze feature patterns
        feature_analysis = {}
        for feature_name in ['absolutist_count', 'missing_evidence', 'persona_concerns']:
            feature_values = [fb['analysis_features'].get(feature_name, 0) for fb in self.feedback_history]
            if feature_values:
                feature_analysis[feature_name] = {
                    'average': statistics.mean(feature_values),
                    'correlation_with_approval': self._calculate_correlation(
                        feature_values, 
                        [fb['human_approved'] for fb in self.feedback_history]
                    )
                }
        
        # Recent performance (last 20 feedback items)
        recent_feedback = self.feedback_history[-20:] if len(self.feedback_history) >= 20 else self.feedback_history
        recent_approval_rate = sum(1 for fb in recent_feedback if fb['human_approved']) / len(recent_feedback)
        
        return {
            'total_feedback_count': total_feedback,
            'approval_rate': round(approval_rate, 3),
            'rejection_rate': round(rejected_count / total_feedback, 3),
            'revision_rate': round(revision_count / total_feedback, 3),
            'false_positive_rate': round(false_positive_rate, 3),
            'false_negative_rate': round(false_negative_rate, 3),
            'recent_approval_rate': round(recent_approval_rate, 3),
            'current_weights': self.weight_adjustments.copy(),
            'feature_analysis': feature_analysis,
            'learning_effectiveness': round(abs(recent_approval_rate - 0.5), 3)  # Distance from random
        }
    
    def _calculate_correlation(self, x: List[float], y: List[bool]) -> float:
        """Simple correlation calculation"""
        if not x or not y or len(x) != len(y):
            return 0.0
        
        # Convert booleans to floats
        y_float = [1.0 if val else 0.0 for val in y]
        
        if len(set(x)) <= 1 or len(set(y_float)) <= 1:
            return 0.0  # No variance
        
        # Simple Pearson correlation
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y_float)
        sum_xy = sum(x[i] * y_float[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y_float[i] ** 2 for i in range(n))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return round(numerator / denominator, 3)
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for improving the system"""
        recommendations = []
        
        if len(self.feedback_history) < self.min_feedback_for_adjustment:
            recommendations.append(f"Collect more feedback data ({len(self.feedback_history)}/{self.min_feedback_for_adjustment} minimum)")
            return recommendations
        
        patterns = self.analyze_feedback_patterns()
        
        if patterns['false_positive_rate'] > 0.2:
            recommendations.append("High false positive rate: Consider reducing risk scoring sensitivity")
        
        if patterns['false_negative_rate'] > 0.2:
            recommendations.append("High false negative rate: Consider increasing risk scoring sensitivity")
        
        if patterns['approval_rate'] < 0.3:
            recommendations.append("Low approval rate: Review risk scoring criteria and thresholds")
        
        if patterns['approval_rate'] > 0.8:
            recommendations.append("High approval rate: Consider stricter risk assessment criteria")
        
        # Weight-specific recommendations
        for weight_name, weight_value in self.weight_adjustments.items():
            if weight_value < 0.6:
                recommendations.append(f"Weight '{weight_name}' is low ({weight_value:.2f}): Consider manual review of this feature")
            elif weight_value > 1.8:
                recommendations.append(f"Weight '{weight_name}' is high ({weight_value:.2f}): This feature may be over-weighted")
        
        if not recommendations:
            recommendations.append("System performance appears balanced based on current feedback")
        
        return recommendations
    
    def save_learning_state(self, filepath: str):
        """Save learning state to file"""
        state = {
            'weight_adjustments': self.weight_adjustments,
            'feedback_history': self.feedback_history,
            'learning_rate': self.learning_rate,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_learning_state(self, filepath: str):
        """Load learning state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.weight_adjustments = state.get('weight_adjustments', self.weight_adjustments)
            self.feedback_history = state.get('feedback_history', [])
            self.learning_rate = state.get('learning_rate', 0.05)
            
            return True
        except FileNotFoundError:
            return False

# Global instance
feedback_learner = FeedbackLearner()
