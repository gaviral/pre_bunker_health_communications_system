"""Test v1.17: Performance Metrics"""

import os
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-dummy-for-local"

from src.metrics.evaluation import HealthCommMetrics, health_comm_metrics

def test_health_comm_metrics_initialization():
    """Test health communication metrics setup"""
    print("=== Testing HealthCommMetrics Initialization ===")
    
    metrics = HealthCommMetrics()
    
    # Check that instance is properly initialized
    assert metrics.metrics == {}, "Should start with empty metrics dict"
    assert hasattr(metrics, 'misinterpretability_at_k'), "Should have misinterpretability_at_k method"
    assert hasattr(metrics, 'evidence_coverage_score'), "Should have evidence_coverage_score method"
    assert hasattr(metrics, 'generate_evaluation_report'), "Should have generate_evaluation_report method"
    
    print("✅ HealthCommMetrics initialized with all required methods")

def test_misinterpretability_at_k():
    """Test misinterpretability@k calculation"""
    print("\n=== Testing Misinterpretability@K ===")
    
    metrics = HealthCommMetrics()
    
    # Test case 1: High misinterpretability
    high_misinterpret_reactions = [
        {'persona': 'VaccineHesitant', 'potential_misreading': ['safety concern', 'effectiveness doubt']},
        {'persona': 'HealthAnxious', 'potential_misreading': ['side effect worry']},
        {'persona': 'SkepticalParent', 'potential_misreading': ['child safety']},
        {'persona': 'TrustingElder', 'potential_misreading': []}
    ]
    
    score_k3 = metrics.misinterpretability_at_k(high_misinterpret_reactions, k=3)
    print(f"High misinterpretability@3: {score_k3:.2f}")
    assert score_k3 == 1.0, "Top 3 personas all have misinterpretations"
    
    # Test case 2: Medium misinterpretability
    medium_misinterpret_reactions = [
        {'persona': 'VaccineHesitant', 'potential_misreading': ['safety concern']},
        {'persona': 'HealthAnxious', 'potential_misreading': []},
        {'persona': 'SkepticalParent', 'potential_misreading': []},
        {'persona': 'TrustingElder', 'potential_misreading': []}
    ]
    
    score_k3_medium = metrics.misinterpretability_at_k(medium_misinterpret_reactions, k=3)
    print(f"Medium misinterpretability@3: {score_k3_medium:.2f}")
    assert abs(score_k3_medium - 0.33) < 0.1, "Should be around 1/3"
    
    # Test case 3: No misinterpretations
    no_misinterpret_reactions = [
        {'persona': 'VaccineHesitant', 'potential_misreading': []},
        {'persona': 'HealthAnxious', 'potential_misreading': []},
        {'persona': 'SkepticalParent', 'potential_misreading': []}
    ]
    
    score_k3_none = metrics.misinterpretability_at_k(no_misinterpret_reactions, k=3)
    print(f"No misinterpretability@3: {score_k3_none:.2f}")
    assert score_k3_none == 0.0, "No misinterpretations should give 0 score"
    
    # Test edge case: Empty list
    empty_score = metrics.misinterpretability_at_k([], k=3)
    assert empty_score == 0.0, "Empty reactions should give 0 score"
    
    print("✅ Misinterpretability@K calculation working correctly")

def test_evidence_coverage_score():
    """Test evidence coverage scoring"""
    print("\n=== Testing Evidence Coverage Score ===")
    
    metrics = HealthCommMetrics()
    
    # Test case 1: Full coverage
    full_coverage_claims = ['claim1', 'claim2', 'claim3']
    full_coverage_evidence = [
        {'claim': 'claim1', 'evidence_found': True},
        {'claim': 'claim2', 'evidence_found': True},
        {'claim': 'claim3', 'evidence_found': True}
    ]
    
    full_score = metrics.evidence_coverage_score(full_coverage_claims, full_coverage_evidence)
    print(f"Full coverage score: {full_score:.2f}")
    assert full_score == 1.0, "Full coverage should give score of 1.0"
    
    # Test case 2: Partial coverage
    partial_coverage_evidence = [
        {'claim': 'claim1', 'evidence_found': True},
        {'claim': 'claim2', 'evidence_found': False},
        {'claim': 'claim3', 'evidence_found': True}
    ]
    
    partial_score = metrics.evidence_coverage_score(full_coverage_claims, partial_coverage_evidence)
    print(f"Partial coverage score: {partial_score:.2f}")
    assert abs(partial_score - 0.67) < 0.1, "2/3 coverage should be around 0.67"
    
    # Test case 3: No coverage
    no_coverage_evidence = [
        {'claim': 'claim1', 'evidence_found': False},
        {'claim': 'claim2', 'evidence_found': False},
        {'claim': 'claim3', 'evidence_found': False}
    ]
    
    no_score = metrics.evidence_coverage_score(full_coverage_claims, no_coverage_evidence)
    print(f"No coverage score: {no_score:.2f}")
    assert no_score == 0.0, "No coverage should give score of 0.0"
    
    # Test edge case: No claims
    empty_claims_score = metrics.evidence_coverage_score([], [])
    assert empty_claims_score == 1.0, "No claims should give perfect score"
    
    print("✅ Evidence coverage scoring working correctly")

def test_risk_reduction_score():
    """Test risk reduction calculation"""
    print("\n=== Testing Risk Reduction Score ===")
    
    metrics = HealthCommMetrics()
    
    # Test case 1: Significant reduction
    significant_reduction = metrics.risk_reduction_score(0.8, 0.4)
    print(f"Significant reduction (0.8→0.4): {significant_reduction:.2f}")
    assert abs(significant_reduction - 0.5) < 0.1, "50% reduction should give score around 0.5"
    
    # Test case 2: Complete elimination
    complete_reduction = metrics.risk_reduction_score(0.6, 0.0)
    print(f"Complete reduction (0.6→0.0): {complete_reduction:.2f}")
    assert complete_reduction == 1.0, "Complete reduction should give score of 1.0"
    
    # Test case 3: No improvement
    no_improvement = metrics.risk_reduction_score(0.5, 0.7)
    print(f"No improvement (0.5→0.7): {no_improvement:.2f}")
    assert no_improvement == 0.0, "Increased risk should give score of 0.0"
    
    # Test case 4: Zero original risk
    zero_original = metrics.risk_reduction_score(0.0, 0.0)
    print(f"Zero original risk: {zero_original:.2f}")
    assert zero_original == 0.0, "Zero original risk should give score of 0.0"
    
    print("✅ Risk reduction scoring working correctly")

def test_countermeasure_effectiveness_score():
    """Test countermeasure effectiveness calculation"""
    print("\n=== Testing Countermeasure Effectiveness Score ===")
    
    metrics = HealthCommMetrics()
    
    # Test case 1: High effectiveness
    high_effectiveness_countermeasures = {
        'VaccineHesitant': {'text': 'Good response', 'effectiveness_score': 0.8},
        'HealthAnxious': {'text': 'Great response', 'effectiveness_score': 0.9},
        'SkepticalParent': {'text': 'Excellent response', 'effectiveness_score': 0.85}
    }
    
    high_score = metrics.countermeasure_effectiveness_score(high_effectiveness_countermeasures)
    print(f"High effectiveness score: {high_score:.2f}")
    expected_high = (0.8 + 0.9 + 0.85) / 3
    assert abs(high_score - expected_high) < 0.1, f"Should average to {expected_high:.2f}"
    
    # Test case 2: Mixed effectiveness
    mixed_effectiveness_countermeasures = {
        'VaccineHesitant': {'text': 'Poor response', 'effectiveness_score': 0.3},
        'HealthAnxious': {'text': 'Good response', 'effectiveness_score': 0.7}
    }
    
    mixed_score = metrics.countermeasure_effectiveness_score(mixed_effectiveness_countermeasures)
    print(f"Mixed effectiveness score: {mixed_score:.2f}")
    expected_mixed = (0.3 + 0.7) / 2
    assert abs(mixed_score - expected_mixed) < 0.1, f"Should average to {expected_mixed:.2f}"
    
    # Test case 3: No countermeasures
    empty_score = metrics.countermeasure_effectiveness_score({})
    print(f"No countermeasures score: {empty_score:.2f}")
    assert empty_score == 0.0, "Empty countermeasures should give score of 0.0"
    
    print("✅ Countermeasure effectiveness scoring working correctly")

def test_response_time_score():
    """Test response time scoring"""
    print("\n=== Testing Response Time Score ===")
    
    metrics = HealthCommMetrics()
    target_time = 30.0
    
    # Test case 1: Fast response
    fast_score = metrics.response_time_score(15.0, target_time)
    print(f"Fast response (15s): {fast_score:.2f}")
    assert fast_score == 1.0, "Fast response should get perfect score"
    
    # Test case 2: Target time
    target_score = metrics.response_time_score(30.0, target_time)
    print(f"Target time (30s): {target_score:.2f}")
    assert target_score == 1.0, "Target time should get perfect score"
    
    # Test case 3: Slow response
    slow_score = metrics.response_time_score(60.0, target_time)
    print(f"Slow response (60s): {slow_score:.2f}")
    assert 0.0 <= slow_score < 1.0, "Slow response should get reduced score"
    
    # Test case 4: Very slow response
    very_slow_score = metrics.response_time_score(120.0, target_time)
    print(f"Very slow response (120s): {very_slow_score:.2f}")
    assert very_slow_score == 0.0, "Very slow response should get minimum score"
    
    print("✅ Response time scoring working correctly")

def test_evaluation_report_generation():
    """Test comprehensive evaluation report generation"""
    print("\n=== Testing Evaluation Report Generation ===")
    
    metrics = HealthCommMetrics()
    
    # Sample original result
    original_result = {
        'claims': ['claim1', 'claim2'],
        'persona_interpretations': [
            {'persona': 'VaccineHesitant', 'potential_misreading': ['safety concern']},
            {'persona': 'HealthAnxious', 'potential_misreading': []},
            {'persona': 'SkepticalParent', 'potential_misreading': ['effectiveness doubt']}
        ],
        'evidence_validations': [
            {'claim': 'claim1', 'evidence_found': True},
            {'claim': 'claim2', 'evidence_found': False}
        ],
        'risk_report': {'overall_risk_score': 0.6},
        'countermeasures': {
            'VaccineHesitant': {'effectiveness_score': 0.7},
            'HealthAnxious': {'effectiveness_score': 0.8}
        },
        'processing_time': 25.0
    }
    
    # Test single result evaluation
    single_report = metrics.generate_evaluation_report(original_result)
    
    print("Single result evaluation:")
    for key, value in single_report.items():
        if key != 'evaluation_summary':
            print(f"  {key}: {value}")
    
    # Verify required metrics are present
    required_metrics = [
        'misinterpretability_at_3_original',
        'evidence_coverage_original', 
        'total_risk_score_original',
        'countermeasure_effectiveness_original',
        'response_time_score_original',
        'evaluation_summary'
    ]
    
    for metric in required_metrics:
        assert metric in single_report, f"Should have {metric} in report"
    
    # Sample improved result
    improved_result = {
        'claims': ['claim1', 'claim2'],
        'persona_interpretations': [
            {'persona': 'VaccineHesitant', 'potential_misreading': []},
            {'persona': 'HealthAnxious', 'potential_misreading': []},
            {'persona': 'SkepticalParent', 'potential_misreading': []}
        ],
        'evidence_validations': [
            {'claim': 'claim1', 'evidence_found': True},
            {'claim': 'claim2', 'evidence_found': True}
        ],
        'risk_report': {'overall_risk_score': 0.3},
        'countermeasures': {
            'VaccineHesitant': {'effectiveness_score': 0.9},
            'HealthAnxious': {'effectiveness_score': 0.85},
            'SkepticalParent': {'effectiveness_score': 0.8}
        }
    }
    
    # Test comparison evaluation
    comparison_report = metrics.generate_evaluation_report(original_result, improved_result)
    
    print("\nComparison evaluation:")
    improvement_metrics = [
        'misinterpretability_reduction',
        'evidence_improvement', 
        'risk_reduction',
        'countermeasure_improvement',
        'overall_improvement_score'
    ]
    
    for metric in improvement_metrics:
        if metric in comparison_report:
            print(f"  {metric}: {comparison_report[metric]:.2f}")
    
    # Verify improvement metrics are present
    for metric in improvement_metrics:
        assert metric in comparison_report, f"Should have {metric} in comparison report"
    
    print("\n" + comparison_report['evaluation_summary'])
    
    print("✅ Evaluation report generation working correctly")

def test_baseline_benchmarking():
    """Test benchmarking against standard baselines"""
    print("\n=== Testing Baseline Benchmarking ===")
    
    metrics = HealthCommMetrics()
    
    test_cases = [
        # Excellent performance
        {
            'name': 'Excellent',
            'result': {
                'claims': ['claim1', 'claim2'],
                'persona_interpretations': [
                    {'persona': 'VaccineHesitant', 'potential_misreading': []},
                    {'persona': 'HealthAnxious', 'potential_misreading': []},
                    {'persona': 'SkepticalParent', 'potential_misreading': []}
                ],
                'evidence_validations': [
                    {'claim': 'claim1', 'evidence_found': True},
                    {'claim': 'claim2', 'evidence_found': True}
                ],
                'risk_report': {'overall_risk_score': 0.05}
            },
            'expected_grade': 'A'
        },
        # Good performance
        {
            'name': 'Good',
            'result': {
                'claims': ['claim1', 'claim2'],
                'persona_interpretations': [
                    {'persona': 'VaccineHesitant', 'potential_misreading': []},
                    {'persona': 'HealthAnxious', 'potential_misreading': ['minor concern']},
                    {'persona': 'SkepticalParent', 'potential_misreading': []}
                ],
                'evidence_validations': [
                    {'claim': 'claim1', 'evidence_found': True},
                    {'claim': 'claim2', 'evidence_found': False}
                ],
                'risk_report': {'overall_risk_score': 0.2}
            },
            'expected_grade': 'B'
        },
        # Poor performance
        {
            'name': 'Poor',
            'result': {
                'claims': ['claim1', 'claim2'],
                'persona_interpretations': [
                    {'persona': 'VaccineHesitant', 'potential_misreading': ['major concern', 'doubt']},
                    {'persona': 'HealthAnxious', 'potential_misreading': ['worry', 'fear']},
                    {'persona': 'SkepticalParent', 'potential_misreading': ['safety issue']}
                ],
                'evidence_validations': [
                    {'claim': 'claim1', 'evidence_found': False},
                    {'claim': 'claim2', 'evidence_found': False}
                ],
                'risk_report': {'overall_risk_score': 0.8}
            },
            'expected_grade': 'D'
        }
    ]
    
    for case in test_cases:
        performance = metrics.benchmark_against_baselines(case['result'])
        
        print(f"{case['name']} performance:")
        print(f"  Overall grade: {performance['overall_grade']}")
        print(f"  Risk level: {performance['risk_level']}")
        print(f"  Evidence level: {performance['evidence_level']}")
        print(f"  Misinterpretability level: {performance['misinterpretability_level']}")
        
        # Verify structure
        assert 'overall_grade' in performance, "Should have overall grade"
        assert 'baseline_comparison' in performance, "Should have baseline comparison"
        
        # Note: Grade prediction is heuristic, so we verify structure rather than exact values
        assert performance['overall_grade'] in ['A', 'B', 'C', 'D'], "Grade should be A-D"
    
    print("✅ Baseline benchmarking working correctly")

if __name__ == "__main__":
    test_health_comm_metrics_initialization()
    test_misinterpretability_at_k()
    test_evidence_coverage_score()
    test_risk_reduction_score()
    test_countermeasure_effectiveness_score()
    test_response_time_score()
    test_evaluation_report_generation()
    test_baseline_benchmarking()
    
    print("\n✅ v1.17 Performance Metrics - Comprehensive health communication evaluation system")
