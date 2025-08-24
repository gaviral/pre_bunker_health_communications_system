"""Health claim classification and data structures"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ClaimType(Enum):
    EFFICACY = "efficacy"  # How well treatment works
    SAFETY = "safety"      # Side effects and risks
    DOSAGE = "dosage"      # Amount and frequency
    TIMING = "timing"      # When to use treatment
    IMPLICATION = "implication"  # Implicit claims and assumptions
    COMPARISON = "comparison"  # Comparing treatments
    CAUSATION = "causation"    # What causes what

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class HealthClaim:
    """Represents a health-related claim extracted from text"""
    text: str
    claim_type: ClaimType
    confidence: float  # 0-1 confidence in extraction
    risk_level: RiskLevel = RiskLevel.LOW
    medical_entities: List[str] = None
    absolutist_language: bool = False
    missing_evidence: bool = True
    
    def __post_init__(self):
        if self.medical_entities is None:
            self.medical_entities = []
        
        # Auto-detect absolutist language
        absolutist_markers = ['always', 'never', '100%', 'guaranteed', 'completely', 'totally', 'absolutely']
        self.absolutist_language = any(marker in self.text.lower() for marker in absolutist_markers)
    
    def calculate_base_risk(self) -> float:
        """Calculate base risk score for this claim"""
        risk_score = 0.0
        
        # Absolutist language increases risk
        if self.absolutist_language:
            risk_score += 0.4
        
        # Missing evidence increases risk
        if self.missing_evidence:
            risk_score += 0.3
        
        # Certain claim types are riskier
        high_risk_types = [ClaimType.SAFETY, ClaimType.EFFICACY, ClaimType.CAUSATION]
        if self.claim_type in high_risk_types:
            risk_score += 0.2
        
        # Medical content inherently has risk
        if self.medical_entities:
            risk_score += 0.1
        
        return min(1.0, risk_score)

# Example claim patterns for different types
CLAIM_PATTERNS = {
    ClaimType.EFFICACY: [
        r'(\w+) (is|are) (effective|works|cures)',
        r'(\w+) (prevents|treats|heals) (\w+)',
        r'(\w+) (success rate|effectiveness)'
    ],
    ClaimType.SAFETY: [
        r'(\w+) (is|are) (safe|dangerous|harmful)',
        r'(\w+) (causes|leads to|results in) (\w+)',
        r'(side effects|adverse reactions|risks) of (\w+)'
    ],
    ClaimType.DOSAGE: [
        r'take (\d+) (\w+) (daily|weekly|monthly)',
        r'(\d+) (mg|ml|units) of (\w+)',
        r'recommended (dose|dosage|amount)'
    ],
    ClaimType.TIMING: [
        r'take (\w+) (before|after|with) (\w+)',
        r'best time to (take|use|administer)',
        r'(\w+) should be (taken|used) (when|if)'
    ]
}

def classify_claim_type(text: str) -> ClaimType:
    """Classify the type of health claim based on text patterns"""
    text_lower = text.lower()
    
    # Check for specific patterns
    import re
    for claim_type, patterns in CLAIM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return claim_type
    
    # Default classification based on keywords
    if any(word in text_lower for word in ['effective', 'works', 'cures', 'prevents', 'treats']):
        return ClaimType.EFFICACY
    elif any(word in text_lower for word in ['safe', 'dangerous', 'side effects', 'risks']):
        return ClaimType.SAFETY
    elif any(word in text_lower for word in ['causes', 'leads to', 'results in']):
        return ClaimType.CAUSATION
    else:
        return ClaimType.EFFICACY  # Default
