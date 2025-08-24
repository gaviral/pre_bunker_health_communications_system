"""Test v1.1: Health Domain Setup"""

from src.health_kb.medical_terms import MEDICAL_ENTITIES, is_medical_term, extract_medical_entities
from src.health_kb.claim_types import HealthClaim, ClaimType, classify_claim_type

def test_medical_terms():
    """Test medical term recognition"""
    print("=== Testing Medical Terms ===")
    
    test_texts = [
        "COVID-19 vaccines are safe and effective",
        "Naloxone can reverse opioid overdoses",
        "The weather is nice today",
        "WHO recommends vaccination for everyone"
    ]
    
    for text in test_texts:
        is_medical = is_medical_term(text)
        entities = extract_medical_entities(text)
        print(f"Text: {text}")
        print(f"  Medical: {is_medical}")
        print(f"  Entities: {entities}")
        print()

def test_claim_types():
    """Test health claim classification"""
    print("=== Testing Claim Types ===")
    
    test_claims = [
        "Vaccines are 100% effective against disease",
        "This medication causes serious side effects",
        "Take 2 tablets daily with food",
        "Exercise prevents heart disease"
    ]
    
    for claim_text in test_claims:
        claim_type = classify_claim_type(claim_text)
        claim = HealthClaim(claim_text, claim_type, 0.8)
        risk_score = claim.calculate_base_risk()
        
        print(f"Claim: {claim_text}")
        print(f"  Type: {claim_type}")
        print(f"  Absolutist: {claim.absolutist_language}")
        print(f"  Risk Score: {risk_score:.2f}")
        print()

if __name__ == "__main__":
    test_medical_terms()
    test_claim_types()
    print("✅ v1.1 Health Domain Setup - Basic functionality working")
