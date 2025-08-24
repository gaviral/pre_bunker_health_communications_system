"""Test v1.14: Evidence Database Enhancement"""

import os
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-dummy-for-local"

from src.evidence.enhanced_sources import (
    ENHANCED_TRUSTED_SOURCES,
    EnhancedEvidenceSearcher,
    enhanced_evidence_searcher
)
from src.evidence.sources import TRUSTED_SOURCES

def test_enhanced_source_database():
    """Test enhanced trusted sources database"""
    print("=== Testing Enhanced Source Database ===")
    
    # Check that we have significantly more sources
    original_count = len(TRUSTED_SOURCES)
    enhanced_count = len(ENHANCED_TRUSTED_SOURCES)
    
    print(f"Original sources: {original_count}")
    print(f"Enhanced sources: {enhanced_count}")
    
    assert enhanced_count > original_count, f"Enhanced should have more sources than original"
    assert enhanced_count >= 15, f"Should have at least 15 sources, got {enhanced_count}"
    
    # Check diversity of source types
    source_types = set(source.source_type.value for source in ENHANCED_TRUSTED_SOURCES)
    print(f"Source types: {len(source_types)} - {source_types}")
    
    expected_types = {
        'government', 'academic', 'medical_institution',
        'research_organization', 'professional_society'
    }
    
    overlap = source_types & expected_types
    assert len(overlap) >= 4, f"Should have diverse source types, got {overlap}"
    
    print("✅ Enhanced database contains diverse, authoritative sources")

def test_enhanced_searcher_initialization():
    """Test enhanced evidence searcher setup"""
    print("\n=== Testing Enhanced Searcher Initialization ===")
    
    searcher = EnhancedEvidenceSearcher()
    
    # Should use enhanced source set
    assert len(searcher.sources) == len(ENHANCED_TRUSTED_SOURCES), "Should use enhanced sources"
    
    # Check authority scores are reasonable
    scores = [source.authority_score for source in searcher.sources]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    print(f"Authority scores: avg={avg_score:.2f}, max={max_score:.2f}, min={min_score:.2f}")
    
    assert avg_score >= 0.8, "Average authority should be high"
    assert max_score <= 1.0, "No score should exceed 1.0"
    assert min_score >= 0.7, "All sources should be reasonably authoritative"
    
    print("✅ Enhanced searcher initialized with quality sources")

def test_specialty_based_search():
    """Test specialty-based source search"""
    print("\n=== Testing Specialty-Based Search ===")
    
    searcher = EnhancedEvidenceSearcher()
    
    test_specialties = [
        ('vaccine', 'vaccines'),
        ('cancer', 'cancer'),
        ('mental health', 'mental health'),
        ('nutrition', 'nutrition'),
        ('cardiovascular', 'cardiovascular'),
        ('pediatric', 'pediatric')
    ]
    
    for search_term, expected_specialty in test_specialties:
        results = searcher.get_sources_by_specialty(search_term, min_authority_score=0.75)
        
        print(f"'{search_term}' specialty: {len(results)} sources")
        
        if results:
            top_source = results[0]
            print(f"  Top: {top_source.name} (score: {top_source.authority_score})")
            
            # Verify specialty relevance
            specialties_text = ' '.join(top_source.specialties).lower()
            
            # Should be sorted by authority score
            scores = [source.authority_score for source in results]
            assert scores == sorted(scores, reverse=True), "Should be sorted by authority score"
            
            # All should meet minimum authority requirement
            assert all(score >= 0.75 for score in scores), "All should meet minimum authority"
        else:
            print(f"  No sources found for {search_term}")
    
    print("✅ Specialty-based search working")

def test_source_type_filtering():
    """Test filtering by organizational type"""
    print("\n=== Testing Source Type Filtering ===")
    
    searcher = EnhancedEvidenceSearcher()
    
    test_types = [
        'government',
        'academic', 
        'medical_institution',
        'professional_society',
        'research_organization'
    ]
    
    for source_type in test_types:
        results = searcher.get_sources_by_type(source_type)
        
        print(f"Type '{source_type}': {len(results)} sources")
        
        # Verify all results are of correct type
        for source in results:
            assert (source.source_type.value == source_type or 
                   source.source_type.name.lower() == source_type.lower()), f"Source {source.name} has wrong type"
        
        if results:
            example = results[0]
            print(f"  Example: {example.name}")
    
    print("✅ Source type filtering working")

def test_content_type_search():
    """Test content type-based search"""
    print("\n=== Testing Content Type Search ===")
    
    searcher = EnhancedEvidenceSearcher()
    
    test_content_types = [
        'guidelines',
        'research_articles',
        'systematic_reviews',
        'clinical_trials',
        'recommendations'
    ]
    
    for content_type in test_content_types:
        results = searcher.search_by_content_type(content_type)
        
        print(f"Content type '{content_type}': {len(results)} sources")
        
        # Verify all results provide this content type
        for source in results:
            assert content_type in source.typical_content_types, f"Source {source.name} doesn't provide {content_type}"
        
        if results:
            example = results[0]
            print(f"  Example: {example.name}")
    
    print("✅ Content type search working")

def test_top_sources():
    """Test top sources by authority"""
    print("\n=== Testing Top Sources Ranking ===")
    
    searcher = EnhancedEvidenceSearcher()
    
    top_10 = searcher.get_top_sources(limit=10)
    top_5 = searcher.get_top_sources(limit=5)
    
    print(f"Top 10 sources by authority:")
    for i, source in enumerate(top_10, 1):
        print(f"  {i}. {source.name}: {source.authority_score}")
    
    # Verify sorting
    scores = [source.authority_score for source in top_10]
    assert scores == sorted(scores, reverse=True), "Should be sorted by authority score"
    
    # Verify limits work
    assert len(top_10) == 10, "Should return exactly 10 sources"
    assert len(top_5) == 5, "Should return exactly 5 sources"
    
    # Top 5 should be subset of top 10
    top_5_names = {source.name for source in top_5}
    top_10_names = {source.name for source in top_10[:5]}
    assert top_5_names == top_10_names, "Top 5 should match first 5 of top 10"
    
    print("✅ Top sources ranking working")

def test_diversity_analysis():
    """Test source diversity scoring"""
    print("\n=== Testing Source Diversity Analysis ===")
    
    searcher = EnhancedEvidenceSearcher()
    
    # Test with diverse selection
    diverse_sources = [
        searcher.sources[0],  # Likely WHO (international)
        searcher.sources[1],  # Likely CDC (US government)
        searcher.sources[2],  # Likely FDA (US regulatory)
    ]
    
    # Add some international/regional sources if available
    for source in searcher.sources[3:]:
        if ('uk' in source.url_pattern.lower() or 'europa' in source.url_pattern.lower() or 
            'canada' in source.url_pattern.lower()):
            diverse_sources.append(source)
            break
    
    diversity = searcher.get_source_diversity_score(diverse_sources)
    
    print(f"Diversity analysis for {len(diverse_sources)} sources:")
    print(f"  Overall score: {diversity['score']}")
    print(f"  Type diversity: {diversity['type_diversity']}")
    print(f"  Region diversity: {diversity['region_diversity']}")
    print(f"  Specialty diversity: {diversity['specialty_diversity']}")
    print(f"  Types: {diversity['types']}")
    print(f"  Regions: {diversity['regions']}")
    print(f"  Specialties: {diversity['specialties'][:5]}...")  # First 5
    
    # Verify structure
    assert 'score' in diversity, "Should have overall score"
    assert 'types' in diversity, "Should have types list"
    assert 'regions' in diversity, "Should have regions list"
    assert 'specialties' in diversity, "Should have specialties list"
    
    # Score should be reasonable
    assert 0.0 <= diversity['score'] <= 1.0, "Score should be between 0 and 1"
    
    # Test with empty list
    empty_diversity = searcher.get_source_diversity_score([])
    assert empty_diversity['score'] == 0.0, "Empty list should have 0 diversity"
    
    print("✅ Diversity analysis working")

def test_authority_score_distribution():
    """Test authority score distribution and quality"""
    print("\n=== Testing Authority Score Distribution ===")
    
    searcher = EnhancedEvidenceSearcher()
    
    scores = [source.authority_score for source in searcher.sources]
    
    # Statistical analysis
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    # Score distribution
    high_authority = sum(1 for score in scores if score >= 0.9)
    medium_authority = sum(1 for score in scores if 0.8 <= score < 0.9)
    acceptable_authority = sum(1 for score in scores if 0.7 <= score < 0.8)
    
    print(f"Score distribution:")
    print(f"  High authority (≥0.9): {high_authority}")
    print(f"  Medium authority (0.8-0.9): {medium_authority}")
    print(f"  Acceptable authority (0.7-0.8): {acceptable_authority}")
    print(f"  Average: {avg_score:.2f}")
    print(f"  Range: {min_score:.2f} - {max_score:.2f}")
    
    # Quality checks
    assert avg_score >= 0.8, "Average authority should be high"
    assert high_authority >= 3, "Should have several high-authority sources"
    assert min_score >= 0.7, "All sources should be reasonably authoritative"
    
    print("✅ Authority score distribution is high quality")

def test_global_coverage():
    """Test geographic and organizational coverage"""
    print("\n=== Testing Global Coverage ===")
    
    searcher = EnhancedEvidenceSearcher()
    
    # Analyze geographic representation
    regions = set()
    org_types = set()
    
    for source in searcher.sources:
        # Infer regions
        if 'who.int' in source.url_pattern:
            regions.add('International')
        elif any(indicator in source.url_pattern.lower() for indicator in ['uk', 'nhs']):
            regions.add('UK')
        elif 'canada' in source.url_pattern.lower():
            regions.add('Canada')
        elif 'europa' in source.url_pattern.lower():
            regions.add('EU')
        else:
            regions.add('US')
        
        org_types.add(source.type)
    
    print(f"Geographic coverage: {len(regions)} regions")
    print(f"  Regions: {sorted(regions)}")
    
    print(f"Organizational diversity: {len(org_types)} types")
    print(f"  Types: {sorted(org_types)}")
    
    # Should have good global representation
    assert len(regions) >= 3, "Should cover multiple regions"
    assert 'International' in regions, "Should include international sources"
    assert len(org_types) >= 5, "Should have diverse organizational types"
    
    print("✅ Global coverage is comprehensive")

if __name__ == "__main__":
    test_enhanced_source_database()
    test_enhanced_searcher_initialization()
    test_specialty_based_search()
    test_source_type_filtering()
    test_content_type_search()
    test_top_sources()
    test_diversity_analysis()
    test_authority_score_distribution()
    test_global_coverage()
    
    print("\n✅ v1.14 Evidence Database Enhancement - Comprehensive trusted source expansion with advanced search and diversity analysis")
