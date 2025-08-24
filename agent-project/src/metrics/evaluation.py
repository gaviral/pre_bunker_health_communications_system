"""Performance metrics for health communication evaluation"""

from typing import Dict, List, Any, Optional
import statistics

class HealthCommMetrics:
    """Comprehensive health communication evaluation metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def misinterpretability_at_k(self, persona_reactions: List[Dict], k: int = 3) -> float:
        """
        Misinterpretability@k: Proportion of top-k personas that misinterpret the message
        """
        total_personas = len(persona_reactions)
        if total_personas == 0:
            return 0.0
        
        k = min(k, total_personas)
        
        # Sort personas by severity of misinterpretation
        sorted_reactions = sorted(
            persona_reactions, 
            key=lambda x: len(x.get('potential_misreading', [])), 
            reverse=True
        )
        
        # Count how many of top-k have misinterpretations
        misinterpreted_count = 0
        for i in range(k):
            if len(sorted_reactions[i].get('potential_misreading', [])) > 0:
                misinterpreted_count += 1
        
        return misinterpreted_count / k
    
    def evidence_coverage_score(self, claims: List, evidence_validations: List[Dict]) -> float:
        """Percentage of claims that have evidence support"""
        if not claims:
            return 1.0
        
        supported_claims = sum(1 for ev in evidence_validations if ev.get('evidence_found', False))
        return supported_claims / len(claims)
    
    def risk_reduction_score(self, original_risk: float, improved_risk: float) -> float:
        """Improvement in risk score from original to improved version"""
        if original_risk == 0:
            return 0.0
        return max(0.0, (original_risk - improved_risk) / original_risk)
    
    def clarity_improvement_score(self, original_clarity: float, improved_clarity: float) -> float:
        """Improvement in clarity score"""
        return max(0.0, improved_clarity - original_clarity)
    
    def countermeasure_effectiveness_score(self, countermeasures: Dict) -> float:
        """Average effectiveness of generated countermeasures"""
        if not countermeasures:
            return 0.0
        
        effectiveness_scores = []
        for persona, data in countermeasures.items():
            if isinstance(data, dict) and 'effectiveness_score' in data:
                effectiveness_scores.append(data['effectiveness_score'])
        
        return statistics.mean(effectiveness_scores) if effectiveness_scores else 0.0
    
    def persona_coverage_score(self, persona_reactions: List[Dict], available_personas: List) -> float:
        """Percentage of available personas that were analyzed"""
        if not available_personas:
            return 1.0
        
        analyzed_personas = len(persona_reactions)
        return min(1.0, analyzed_personas / len(available_personas))
    
    def claim_detection_recall(self, detected_claims: List, manual_claims: List) -> float:
        """Recall of claim detection (requires manual ground truth)"""
        if not manual_claims:
            return 1.0 if not detected_claims else 0.0
        
        # Simple text-based matching for now
        detected_texts = [str(claim).lower() for claim in detected_claims]
        manual_texts = [str(claim).lower() for claim in manual_claims]
        
        matches = 0
        for manual_claim in manual_texts:
            if any(manual_claim in detected for detected in detected_texts):
                matches += 1
        
        return matches / len(manual_claims)
    
    def response_time_score(self, processing_time: float, target_time: float = 30.0) -> float:
        """Score based on processing time (lower is better)"""
        if processing_time <= target_time:
            return 1.0
        else:
            # Exponential decay after target time
            return max(0.0, 1.0 - ((processing_time - target_time) / target_time))
    
    def generate_evaluation_report(self, original_result: Dict, improved_result: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive evaluation comparing original vs improved"""
        
        metrics = {}
        
        # Basic metrics for original result
        metrics['misinterpretability_at_3_original'] = self.misinterpretability_at_k(
            original_result.get('persona_interpretations', []), 3
        )
        
        metrics['evidence_coverage_original'] = self.evidence_coverage_score(
            original_result.get('claims', []), 
            original_result.get('evidence_validations', [])
        )
        
        risk_report = original_result.get('risk_report', {})
        metrics['total_risk_score_original'] = risk_report.get('overall_risk_score', 0.0)
        
        metrics['countermeasure_effectiveness_original'] = self.countermeasure_effectiveness_score(
            original_result.get('countermeasures', {})
        )
        
        # Processing time if available
        if 'processing_time' in original_result:
            metrics['response_time_score_original'] = self.response_time_score(
                original_result['processing_time']
            )
        
        # If improved result is provided, calculate comparison metrics
        if improved_result:
            metrics['misinterpretability_at_3_improved'] = self.misinterpretability_at_k(
                improved_result.get('persona_interpretations', []), 3
            )
            
            metrics['evidence_coverage_improved'] = self.evidence_coverage_score(
                improved_result.get('claims', []), 
                improved_result.get('evidence_validations', [])
            )
            
            improved_risk_report = improved_result.get('risk_report', {})
            metrics['total_risk_score_improved'] = improved_risk_report.get('overall_risk_score', 0.0)
            
            metrics['countermeasure_effectiveness_improved'] = self.countermeasure_effectiveness_score(
                improved_result.get('countermeasures', {})
            )
            
            # Calculate improvement metrics
            metrics['misinterpretability_reduction'] = max(0.0, 
                metrics['misinterpretability_at_3_original'] - metrics['misinterpretability_at_3_improved']
            )
            
            metrics['evidence_improvement'] = max(0.0,
                metrics['evidence_coverage_improved'] - metrics['evidence_coverage_original']
            )
            
            metrics['risk_reduction'] = self.risk_reduction_score(
                metrics['total_risk_score_original'],
                metrics['total_risk_score_improved']
            )
            
            metrics['countermeasure_improvement'] = max(0.0,
                metrics['countermeasure_effectiveness_improved'] - metrics['countermeasure_effectiveness_original']
            )
            
            # Overall improvement score
            improvement_components = [
                metrics['misinterpretability_reduction'] * 0.3,
                metrics['evidence_improvement'] * 0.2,
                metrics['risk_reduction'] * 0.3,
                metrics['countermeasure_improvement'] * 0.2
            ]
            metrics['overall_improvement_score'] = sum(improvement_components)
        
        # Generate textual summary
        metrics['evaluation_summary'] = self._generate_summary(metrics, improved_result is not None)
        
        return metrics
    
    def _generate_summary(self, metrics: Dict, has_comparison: bool) -> str:
        """Generate human-readable summary of metrics"""
        summary_parts = []
        
        # Original performance
        original_risk = metrics.get('total_risk_score_original', 0)
        original_misinterp = metrics.get('misinterpretability_at_3_original', 0)
        original_evidence = metrics.get('evidence_coverage_original', 0)
        
        summary_parts.append(f"Original message analysis:")
        summary_parts.append(f"  - Risk score: {original_risk:.2f}")
        summary_parts.append(f"  - Misinterpretability@3: {original_misinterp:.2%}")
        summary_parts.append(f"  - Evidence coverage: {original_evidence:.2%}")
        
        if has_comparison:
            risk_reduction = metrics.get('risk_reduction', 0)
            misinterp_reduction = metrics.get('misinterpretability_reduction', 0)
            evidence_improvement = metrics.get('evidence_improvement', 0)
            overall_improvement = metrics.get('overall_improvement_score', 0)
            
            summary_parts.append(f"\nImprovement achieved:")
            summary_parts.append(f"  - Risk reduction: {risk_reduction:.2%}")
            summary_parts.append(f"  - Misinterpretability reduction: {misinterp_reduction:.2%}")
            summary_parts.append(f"  - Evidence improvement: {evidence_improvement:.2%}")
            summary_parts.append(f"  - Overall improvement: {overall_improvement:.2f}")
            
            # Recommendations
            if overall_improvement < 0.1:
                summary_parts.append(f"\n⚠️ Low improvement achieved. Consider more aggressive interventions.")
            elif overall_improvement >= 0.3:
                summary_parts.append(f"\n✅ Significant improvement achieved.")
            else:
                summary_parts.append(f"\n🔄 Moderate improvement. Further optimization recommended.")
        
        return "\n".join(summary_parts)
    
    def benchmark_against_baselines(self, result: Dict) -> Dict[str, Any]:
        """Compare performance against standard baselines"""
        
        risk_score = result.get('risk_report', {}).get('overall_risk_score', 0)
        evidence_coverage = self.evidence_coverage_score(
            result.get('claims', []), 
            result.get('evidence_validations', [])
        )
        misinterpretability = self.misinterpretability_at_k(
            result.get('persona_interpretations', []), 3
        )
        
        # Define baseline thresholds
        baselines = {
            'low_risk_threshold': 0.3,
            'good_evidence_threshold': 0.7,
            'low_misinterpretability_threshold': 0.2,
            'excellent_risk_threshold': 0.1,
            'excellent_evidence_threshold': 0.9,
            'excellent_misinterpretability_threshold': 0.05
        }
        
        performance = {}
        
        # Risk assessment
        if risk_score <= baselines['excellent_risk_threshold']:
            performance['risk_level'] = 'excellent'
        elif risk_score <= baselines['low_risk_threshold']:
            performance['risk_level'] = 'good'
        else:
            performance['risk_level'] = 'needs_improvement'
        
        # Evidence assessment
        if evidence_coverage >= baselines['excellent_evidence_threshold']:
            performance['evidence_level'] = 'excellent'
        elif evidence_coverage >= baselines['good_evidence_threshold']:
            performance['evidence_level'] = 'good'
        else:
            performance['evidence_level'] = 'needs_improvement'
        
        # Misinterpretability assessment
        if misinterpretability <= baselines['excellent_misinterpretability_threshold']:
            performance['misinterpretability_level'] = 'excellent'
        elif misinterpretability <= baselines['low_misinterpretability_threshold']:
            performance['misinterpretability_level'] = 'good'
        else:
            performance['misinterpretability_level'] = 'needs_improvement'
        
        # Overall grade
        levels = [performance['risk_level'], performance['evidence_level'], performance['misinterpretability_level']]
        if all(level == 'excellent' for level in levels):
            performance['overall_grade'] = 'A'
        elif all(level in ['excellent', 'good'] for level in levels):
            performance['overall_grade'] = 'B'
        elif any(level == 'excellent' for level in levels):
            performance['overall_grade'] = 'C'
        else:
            performance['overall_grade'] = 'D'
        
        performance['baseline_comparison'] = {
            'risk_score': risk_score,
            'evidence_coverage': evidence_coverage,
            'misinterpretability_at_3': misinterpretability,
            'baselines_used': baselines
        }
        
        return performance

# Global instance
health_comm_metrics = HealthCommMetrics()
