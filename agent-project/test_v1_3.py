"""Test v1.3: Risk Scoring Framework"""

import os
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-dummy-for-local"

from src.claims.risk_scorer import RiskScorer, risk_scorer
from src.claims.extractor import ClaimExtractor
from src.health_kb.claim_types import HealthClaim, ClaimType

def test_basic_risk_scoring():
    """Test basic risk scoring with different claim types"""
    print("=== Testing Basic Risk Scoring ===")
    
    test_claims = [
        # High-risk claims
        "This vaccine is 100% safe and guaranteed to work",
        "Natural remedies never have side effects and always cure diseases",
        "Doctors say this miracle cure works every time",
        
        # Medium-risk claims  
        "Vaccines are usually effective in preventing disease",
        "Most people find this treatment helpful",
        "Studies show this medication typically works",
        
        # Low-risk claims
        "This medication may help reduce symptoms in some patients",
        "Consult your doctor before starting any new treatment",
        "Individual results may vary with this therapy"
    ]
    
    scorer = RiskScorer()
    
    for claim in test_claims:
        score = scorer.score_claim(claim)
        confidence = scorer.calculate_confidence_score(claim)
        factors = scorer.analyze_risk_factors(claim)
        
        print(f"\nClaim: {claim}")
        print(f"  Risk Score: {score:.2f}")
        print(f"  Confidence: {confidence:.2f}")
        if factors:
            print(f"  Risk Factors: {factors}")

def test_health_claim_scoring():
    """Test scoring with HealthClaim objects"""
    print("\n=== Testing HealthClaim Scoring ===")
    
    # Create some test health claims
    test_health_claims = [
        HealthClaim(
            text="COVID-19 vaccines are 100% effective and completely safe",
            claim_type=ClaimType.SAFETY,
            confidence=0.9
        ),
        HealthClaim(
            text="Take 2mg of this medication daily as needed",
            claim_type=ClaimType.DOSAGE,
            confidence=0.8
        ),
        HealthClaim(
            text="This treatment may help reduce symptoms according to clinical studies",
            claim_type=ClaimType.EFFICACY,
            confidence=0.7
        )
    ]
    
    scorer = RiskScorer()
    
    for claim in test_health_claims:
        score_breakdown = scorer.score_health_claim(claim)
        
        print(f"\nClaim: {claim.text}")
        print(f"  Type: {claim.claim_type}")
        print(f"  Base Score: {score_breakdown['base_score']:.2f}")
        print(f"  Pattern Score: {score_breakdown['pattern_score']:.2f}")
        print(f"  Type Adjustment: {score_breakdown['type_adjustment']:.2f}")
        print(f"  Final Score: {score_breakdown['final_score']:.2f}")
        print(f"  Confidence: {score_breakdown['confidence']:.2f}")

def test_integrated_extraction_and_scoring():
    """Test integration of claim extraction with risk scoring"""
    print("\n=== Testing Integrated Extraction + Scoring ===")
    
    test_text = """
    The new RSV vaccine is 100% effective and completely safe for all patients.
    It prevents all respiratory infections and has no side effects whatsoever.
    Doctors guarantee this breakthrough treatment works every time.
    However, you should consult your healthcare provider before vaccination.
    """
    
    # Extract claims
    extractor = ClaimExtractor()
    health_claims = extractor.extract_and_classify_claims(test_text)
    
    print(f"Text: {test_text.strip()}")
    print(f"Claims Found: {len(health_claims)}")
    
    # Score each claim
    scorer = RiskScorer()
    total_risk = 0.0
    high_risk_count = 0
    
    for i, claim in enumerate(health_claims):
        score_breakdown = scorer.score_health_claim(claim)
        risk_factors = scorer.analyze_risk_factors(claim.text)
        
        print(f"\n  Claim {i+1}: {claim.text}")
        print(f"    Final Risk Score: {score_breakdown['final_score']:.2f}")
        print(f"    Risk Level: {'HIGH' if score_breakdown['final_score'] > 0.7 else 'MEDIUM' if score_breakdown['final_score'] > 0.4 else 'LOW'}")
        
        if risk_factors:
            print(f"    Risk Factors: {list(risk_factors.keys())}")
        
        total_risk += score_breakdown['final_score']
        if score_breakdown['final_score'] > 0.7:
            high_risk_count += 1
    
    if health_claims:
        avg_risk = total_risk / len(health_claims)
        print(f"\n  Summary:")
        print(f"    Average Risk Score: {avg_risk:.2f}")
        print(f"    High-Risk Claims: {high_risk_count}/{len(health_claims)}")
        print(f"    Overall Assessment: {'HIGH RISK' if avg_risk > 0.7 or high_risk_count > 0 else 'MEDIUM RISK' if avg_risk > 0.4 else 'LOW RISK'}")

if __name__ == "__main__":
    test_basic_risk_scoring()
    test_health_claim_scoring()
    test_integrated_extraction_and_scoring()
    print("\n✅ v1.3 Risk Scoring Framework - Working with rule-based scoring and confidence metrics")
