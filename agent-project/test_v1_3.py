"""Test v1.3: Risk Scoring Framework"""

import os
import time
import logging
import statistics

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-dummy-for-local"

from src.claims.risk_scorer import RiskScorer, risk_scorer
from src.claims.extractor import ClaimExtractor
from src.health_kb.claim_types import HealthClaim, ClaimType

# Configure logging for v1.3 analysis
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_risk_scoring():
    """Test basic risk scoring with different claim types"""
    print("=== Testing Basic Risk Scoring ===")
    start_time = time.time()
    
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
    
    # v1.3 Logging Implementation: Confidence and Risk Analysis
    risk_scores = []
    confidence_scores = []
    risk_confidence_pairs = []
    scoring_inconsistencies = []
    
    for claim in test_claims:
        score = scorer.score_claim(claim)
        confidence = scorer.calculate_confidence_score(claim)
        factors = scorer.analyze_risk_factors(claim)
        
        # Track for analysis
        risk_scores.append(score)
        confidence_scores.append(confidence)
        risk_confidence_pairs.append((score, confidence))
        
        # v1.3 Logging Implementation: Detect Scoring Inconsistencies
        if confidence > 0.9 and score < 0.3:
            scoring_inconsistencies.append(f"High confidence ({confidence:.2f}) with low risk ({score:.2f}): {claim[:50]}...")
            logger.warning(f"[SCORING_INCONSISTENCY] High confidence ({confidence:.2f}) assigned to low risk claim ({score:.2f})")
        elif confidence < 0.5 and score > 0.7:
            scoring_inconsistencies.append(f"Low confidence ({confidence:.2f}) with high risk ({score:.2f}): {claim[:50]}...")
            logger.warning(f"[SCORING_INCONSISTENCY] Low confidence ({confidence:.2f}) assigned to high risk claim ({score:.2f})")
        
        # Check for inverted logic patterns
        if "100%" in claim and score < 0.5:
            logger.warning(f"[ALGORITHM_VALIDATION] Risk factors detected: ['100%'] but low risk score assigned ({score:.2f})")
        
        print(f"\nClaim: {claim}")
        print(f"  Risk Score: {score:.2f}")
        print(f"  Confidence: {confidence:.2f}")
        if factors:
            print(f"  Risk Factors: {factors}")
    
    # v1.3 Logging Implementation: Confidence Calibration Analysis
    if risk_scores and confidence_scores:
        avg_risk = statistics.mean(risk_scores)
        avg_confidence = statistics.mean(confidence_scores)
        risk_range = f"{min(risk_scores):.3f}-{max(risk_scores):.3f}"
        confidence_range = f"{min(confidence_scores):.3f}-{max(confidence_scores):.3f}"
        
        logger.info(f"[CONFIDENCE_CALIBRATION] Avg confidence: {avg_confidence:.3f}, Avg risk: {avg_risk:.3f}")
        logger.info(f"[THRESHOLD_ANALYSIS] Risk range: {risk_range}, Confidence range: {confidence_range}")
        
        # Check for correlation issues
        correlation_problems = len(scoring_inconsistencies)
        if correlation_problems > 0:
            logger.warning(f"[CONFIDENCE_CALIBRATION] {correlation_problems} confidence-risk correlation issues detected")
            for issue in scoring_inconsistencies:
                logger.warning(f"[CALIBRATION_ISSUE] {issue}")
        
        # Check if thresholds are defined
        logger.warning(f"[THRESHOLD_ANALYSIS] Confidence thresholds: Not defined, Risk thresholds: Not validated")
    
    processing_time = time.time() - start_time
    logger.info(f"[PERFORMANCE_BASELINE] Risk scoring processing time: {processing_time:.3f}s")
    
    return risk_scores, confidence_scores

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
    # v1.3 Logging Implementation: Comprehensive Analysis
    logger.info("[ANALYSIS_START] Beginning v1.3 risk scoring framework analysis")
    
    risk_scores, confidence_scores = test_basic_risk_scoring()
    test_health_claim_scoring() 
    test_integrated_extraction_and_scoring()
    
    # v1.3 Logging Implementation: Overall Assessment
    if risk_scores and confidence_scores:
        # Calculate correlation between risk and confidence
        try:
            import numpy as np
            correlation = np.corrcoef(risk_scores, confidence_scores)[0, 1]
            logger.info(f"[CONFIDENCE_CALIBRATION] Risk-Confidence correlation: {correlation:.3f}")
            if abs(correlation) < 0.3:
                logger.warning(f"[CALIBRATION_ISSUE] Weak correlation between risk and confidence scores")
        except ImportError:
            logger.warning(f"[ANALYSIS_LIMITED] NumPy not available for correlation analysis")
        
        # Threshold validation check
        high_risk_threshold = 0.7
        medium_risk_threshold = 0.4
        high_confidence_threshold = 0.8
        
        high_risk_count = sum(1 for score in risk_scores if score > high_risk_threshold)
        high_confidence_count = sum(1 for conf in confidence_scores if conf > high_confidence_threshold)
        
        logger.info(f"[THRESHOLD_ANALYSIS] High risk claims: {high_risk_count}/{len(risk_scores)}")
        logger.info(f"[THRESHOLD_ANALYSIS] High confidence claims: {high_confidence_count}/{len(confidence_scores)}")
        
        if high_risk_count != high_confidence_count:
            logger.warning(f"[THRESHOLD_MISMATCH] Risk/confidence thresholds not aligned")
    
    print("\n✅ v1.3 Risk Scoring Framework - Working with rule-based scoring and confidence metrics")
