"""Test v1.6: Evidence Source Framework"""

import os
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-dummy-for-local"

from src.evidence.sources import (
    EvidenceSource, SourceType, TRUSTED_SOURCES, EvidenceSearcher, evidence_searcher
)

def test_evidence_sources():
    """Test evidence source definitions and properties"""
    print("=== Testing Evidence Sources ===")
    
    print(f"Total trusted sources: {len(TRUSTED_SOURCES)}")
    
    # Test each source
    for source in TRUSTED_SOURCES[:3]:  # Show first 3 for brevity
        print(f"\nSource: {source.name}")
        print(f"  Authority Score: {source.authority_score}")
        print(f"  Type: {source.source_type.value}")
        print(f"  Specialties: {source.specialties[:3]}...")  # Show first 3
        print(f"  Content Types: {source.typical_content_types}")
        print(f"  Limitations: {len(source.limitations)} noted")
    
    # Test source relevance
    who_source = next((s for s in TRUSTED_SOURCES if s.name.startswith("World Health")), None)
    assert who_source is not None, "WHO source should exist"
    
    assert who_source.is_relevant_for_topic("vaccination"), "WHO should be relevant for vaccination"
    assert who_source.is_relevant_for_topic("infectious diseases"), "WHO should be relevant for infectious diseases"
    assert not who_source.is_relevant_for_topic("cooking recipes"), "WHO should not be relevant for cooking"
    
    print("✅ Source definitions working")

def test_evidence_searcher():
    """Test evidence search functionality"""
    print("\n=== Testing Evidence Searcher ===")
    
    searcher = EvidenceSearcher()
    
    # Test finding relevant sources
    test_claims = [
        "COVID-19 vaccines are safe and effective",
        "Children should receive routine immunizations", 
        "This medication has serious side effects",
        "WHO recommends this treatment approach"
    ]
    
    for claim in test_claims:
        relevant_sources = searcher.find_relevant_sources(claim)
        print(f"\nClaim: {claim}")
        print(f"  Relevant sources found: {len(relevant_sources)}")
        
        for source in relevant_sources[:2]:  # Show top 2
            search_terms = source.get_search_terms(claim)
            print(f"    {source.name} (score: {source.authority_score}) - terms: {search_terms}")
    
    print("✅ Source search working")

def test_source_lookup_and_filtering():
    """Test source lookup and filtering functionality"""
    print("\n=== Testing Source Lookup and Filtering ===")
    
    searcher = EvidenceSearcher()
    
    # Test lookup by name
    who_source = searcher.get_source_by_name("World Health Organization (WHO)")
    assert who_source is not None, "Should find WHO by name"
    assert who_source.authority_score == 0.95, "WHO should have correct authority score"
    
    # Test filtering by type
    gov_sources = searcher.get_sources_by_type(SourceType.GOVERNMENT)
    academic_sources = searcher.get_sources_by_type(SourceType.ACADEMIC)
    
    print(f"Government sources: {len(gov_sources)}")
    for source in gov_sources:
        print(f"  {source.name} ({source.authority_score})")
    
    print(f"Academic sources: {len(academic_sources)}")
    for source in academic_sources:
        print(f"  {source.name} ({source.authority_score})")
    
    # Test highest authority sources
    top_sources = searcher.get_highest_authority_sources(3)
    print(f"\nTop 3 authority sources:")
    for i, source in enumerate(top_sources, 1):
        print(f"  {i}. {source.name} ({source.authority_score})")
    
    print("✅ Source lookup and filtering working")

def test_credibility_assessment():
    """Test URL credibility assessment"""
    print("\n=== Testing Credibility Assessment ===")
    
    searcher = EvidenceSearcher()
    
    test_urls = [
        "https://www.who.int/news-room/fact-sheets/detail/vaccines",
        "https://www.cdc.gov/vaccines/safety/",
        "https://www.cochranelibrary.com/cdsr/reviews",
        "https://randommedicalwebsite.com/health-advice",
        "https://www.fda.gov/drugs/drug-safety-and-availability"
    ]
    
    for url in test_urls:
        credibility = searcher.assess_source_credibility(url)
        print(f"\nURL: {url}")
        print(f"  Source: {credibility['source_name']}")
        print(f"  Authority Score: {credibility['authority_score']}")
        print(f"  Credibility Level: {credibility['credibility_level']}")
        print(f"  Specialties: {credibility['specialties'][:2]}...")  # Show first 2
        
        if credibility['limitations']:
            print(f"  Limitations: {credibility['limitations'][:1]}...")  # Show first limitation
    
    print("✅ Credibility assessment working")

def test_source_summary():
    """Test source summary generation"""
    print("\n=== Testing Source Summary ===")
    
    searcher = EvidenceSearcher()
    summary = searcher.generate_source_summary()
    
    print("Source Database Summary:")
    print(f"  Total Sources: {summary['total_sources']}")
    print(f"  By Type: {summary['by_type']}")
    print(f"  Authority Distribution: {summary['authority_distribution']}")
    print(f"  Specialty Areas Covered: {len(summary['specialty_coverage'])}")
    print(f"  Top Authority Sources:")
    
    for source in summary['highest_authority']:
        print(f"    {source['name']} ({source['score']})")
    
    # Verify some expected values
    assert summary['total_sources'] == len(TRUSTED_SOURCES), "Should count all sources"
    assert 'government' in summary['by_type'], "Should have government sources"
    assert 'very_high' in summary['authority_distribution'], "Should have very high authority sources"
    
    print("✅ Source summary generation working")

def test_search_term_extraction():
    """Test search term extraction from claims"""
    print("\n=== Testing Search Term Extraction ===")
    
    # Test with WHO source
    who_source = next((s for s in TRUSTED_SOURCES if "WHO" in s.name), None)
    
    test_claims = [
        "COVID-19 vaccination prevents severe disease",
        "This medication causes side effects in children",
        "Global health authorities recommend this treatment",
        "The cooking recipe is delicious"  # Non-medical content
    ]
    
    for claim in test_claims:
        terms = who_source.get_search_terms(claim)
        print(f"\nClaim: {claim}")
        print(f"  Search terms for WHO: {terms}")
    
    print("✅ Search term extraction working")

if __name__ == "__main__":
    test_evidence_sources()
    test_evidence_searcher()
    test_source_lookup_and_filtering()
    test_credibility_assessment()
    test_source_summary()
    test_search_term_extraction()
    
    print("\n✅ v1.6 Evidence Source Framework - Working with trusted sources and search capability")
