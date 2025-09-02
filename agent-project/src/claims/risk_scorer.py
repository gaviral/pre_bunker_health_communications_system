"""Risk scoring framework for health claims"""

import re
from typing import Dict, List, Tuple
from src.health_kb.claim_types import HealthClaim, ClaimType

class RiskScorer:
    def __init__(self):
        # High-risk language patterns
        self.high_risk_patterns = [
            'always effective', 'never fails', '100%', 'guaranteed',
            'completely safe', 'no side effects', 'instant cure',
            'miracle cure', 'perfect solution', 'zero risk',
            'absolutely safe', 'totally harmless', 'works every time'
        ]
        
        # Moderate-risk patterns that suggest uncertainty but still problematic
        self.moderate_risk_patterns = [
            'usually effective', 'generally safe', 'mostly harmless',
            'rarely causes problems', 'almost always works',
            'typically successful', 'most effective treatment'
        ]
        
        # Low-risk patterns that show appropriate uncertainty
        self.low_risk_patterns = [
            'may help', 'could be beneficial', 'might work',
            'consult your doctor', 'individual results vary',
            'according to studies', 'evidence suggests'
        ]
        
        # Ambiguous terms that increase risk
        self.ambiguous_terms = ['it', 'this', 'that', 'they', 'these', 'those']
        
        # Authority indicators (can be misused)
        self.authority_patterns = [
            r'(?:doctors|experts|scientists|researchers) (?:say|recommend|prove)',
            r'(?:studies|research|trials) (?:show|prove|demonstrate)',
            r'(?:WHO|CDC|FDA|NIH) (?:says|recommends|approves)'
        ]
        
        # Emotional appeal indicators
        self.emotional_patterns = [
            'fear', 'scared', 'worried', 'dangerous', 'deadly',
            'amazing', 'incredible', 'breakthrough', 'revolutionary'
        ]
    
    def score_claim(self, claim_text: str) -> float:
        """Score a single claim for misinterpretation risk"""
        risk_score = 0.0
        claim_lower = claim_text.lower()
        
        # Pattern-based scoring
        for pattern in self.high_risk_patterns:
            if pattern.lower() in claim_lower:
                risk_score += 0.3
        
        for pattern in self.moderate_risk_patterns:
            if pattern.lower() in claim_lower:
                risk_score += 0.2
        
        # Reduce risk for appropriate uncertainty language
        for pattern in self.low_risk_patterns:
            if pattern.lower() in claim_lower:
                risk_score -= 0.1
        
        # Ambiguity detection
        ambiguity_count = sum(1 for term in self.ambiguous_terms if f' {term} ' in f' {claim_lower} ')
        risk_score += ambiguity_count * 0.05
        
        # Authority misuse detection
        authority_count = 0
        for pattern in self.authority_patterns:
            if re.search(pattern, claim_lower):
                authority_count += 1
        risk_score += authority_count * 0.15
        
        # Emotional appeal detection
        emotional_count = sum(1 for pattern in self.emotional_patterns if pattern in claim_lower)
        risk_score += emotional_count * 0.1
        
        # Medical content inherently has some risk
        has_medical_terms = any(
            term.lower() in claim_lower 
            for category in MEDICAL_ENTITIES.values() 
            for term in category
        )
        if has_medical_terms:
            risk_score += 0.1
        
        # Normalize to 0-1 range
        return min(1.0, max(0.0, risk_score))
    
    def score_health_claim(self, health_claim: HealthClaim) -> Dict[str, float]:
        """Score a HealthClaim object with detailed breakdown"""
        base_score = health_claim.calculate_base_risk()
        pattern_score = self.score_claim(health_claim.text)
        
        # Combine scores with weights
        combined_score = (base_score * 0.6) + (pattern_score * 0.4)
        
        # Adjust based on claim type
        type_adjustments = {
            ClaimType.SAFETY: 0.2,      # Safety claims are high-risk
            ClaimType.EFFICACY: 0.15,   # Efficacy claims are medium-high risk
            ClaimType.CAUSATION: 0.15,  # Causation claims are medium-high risk
            ClaimType.DOSAGE: 0.1,      # Dosage claims are medium risk
            ClaimType.TIMING: 0.05,     # Timing claims are lower risk
            ClaimType.COMPARISON: 0.1   # Comparison claims are medium risk
        }
        
        type_adjustment = type_adjustments.get(health_claim.claim_type, 0.0)
        final_score = min(1.0, combined_score + type_adjustment)
        
        return {
            'base_score': base_score,
            'pattern_score': pattern_score,
            'type_adjustment': type_adjustment,
            'final_score': final_score,
            'confidence': health_claim.confidence
        }
    
    def analyze_risk_factors(self, claim_text: str) -> Dict[str, List[str]]:
        """Analyze specific risk factors present in the claim"""
        claim_lower = claim_text.lower()
        factors = {
            'high_risk_language': [],
            'ambiguous_terms': [],
            'authority_appeals': [],
            'emotional_language': [],
            'missing_qualifiers': []
        }
        
        # Find high-risk language
        for pattern in self.high_risk_patterns:
            if pattern.lower() in claim_lower:
                factors['high_risk_language'].append(pattern)
        
        # Find ambiguous terms
        for term in self.ambiguous_terms:
            if f' {term} ' in f' {claim_lower} ':
                factors['ambiguous_terms'].append(term)
        
        # Find authority appeals
        for pattern in self.authority_patterns:
            if re.search(pattern, claim_lower):
                factors['authority_appeals'].append(pattern)
        
        # Find emotional language
        for pattern in self.emotional_patterns:
            if pattern in claim_lower:
                factors['emotional_language'].append(pattern)
        
        # Check for missing qualifiers
        has_qualifiers = any(qualifier in claim_lower for qualifier in [
            'may', 'might', 'could', 'usually', 'often', 'sometimes',
            'consult', 'individual', 'varies', 'depends'
        ])
        
        if not has_qualifiers and any(pattern in claim_lower for pattern in ['effective', 'safe', 'works', 'prevents']):
            factors['missing_qualifiers'].append('No uncertainty qualifiers found')
        
        return {k: v for k, v in factors.items() if v}  # Only return non-empty factors
    
    def calculate_confidence_score(self, claim_text: str, extraction_method: str = 'pattern') -> float:
        """Calculate confidence in the risk assessment"""
        base_confidence = 0.8 if extraction_method == 'pattern' else 0.6
        
        # Higher confidence for longer, more specific claims
        if len(claim_text.split()) > 8:
            base_confidence += 0.1
        
        # Lower confidence for very ambiguous claims
        ambiguity_count = sum(1 for term in self.ambiguous_terms if term in claim_text.lower())
        base_confidence -= ambiguity_count * 0.05
        
        # Higher confidence when medical terms are present
        has_medical = any(
            term.lower() in claim_text.lower()
            for category in MEDICAL_ENTITIES.values()
            for term in category
        )
        if has_medical:
            base_confidence += 0.1
        
        return min(1.0, max(0.2, base_confidence))

# Global instance
risk_scorer = RiskScorer()
