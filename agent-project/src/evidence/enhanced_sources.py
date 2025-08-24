"""Enhanced evidence database with expanded trusted sources"""

from .sources import EvidenceSource, EvidenceSearcher, SourceType

# Enhanced trusted sources database - simplified for v1.14
ENHANCED_TRUSTED_SOURCES = [
    # Core international sources
    EvidenceSource(
        name="World Health Organization",
        url_pattern="who.int",
        authority_score=0.95,
        specialties=["global health", "disease outbreaks", "health guidelines", "pandemic response"],
        source_type=SourceType.GOVERNMENT,
        description="Global health authority",
        typical_content_types=["guidelines", "reports", "fact_sheets"]
    ),
    
    EvidenceSource(
        name="Centers for Disease Control and Prevention",
        url_pattern="cdc.gov", 
        authority_score=0.95,
        specialties=["US public health", "disease surveillance", "prevention", "vaccines"],
        source_type=SourceType.GOVERNMENT,
        description="US national public health agency",
        typical_content_types=["guidelines", "surveillance_data", "recommendations"]
    ),
    
    EvidenceSource(
        name="FDA",
        url_pattern="fda.gov",
        authority_score=0.90,
        specialties=["drug approval", "medical devices", "food safety"],
        source_type=SourceType.GOVERNMENT,
        description="US regulatory agency",
        typical_content_types=["approvals", "safety_alerts", "guidelines"]
    ),
    
    # Additional international sources
    EvidenceSource(
        name="European Medicines Agency",
        url_pattern="ema.europa.eu",
        authority_score=0.90,
        specialties=["drug approval", "pharmacovigilance", "medical devices"],
        source_type=SourceType.GOVERNMENT,
        description="EU regulatory agency",
        typical_content_types=["approval_decisions", "safety_updates"]
    ),
    
    EvidenceSource(
        name="NHS",
        url_pattern="nhs.uk",
        authority_score=0.87,
        specialties=["UK healthcare", "clinical guidance", "patient information"],
        source_type=SourceType.MEDICAL_INSTITUTION,
        description="UK national health service",
        typical_content_types=["clinical_guidelines", "patient_resources"]
    ),
    
    # Research sources
    EvidenceSource(
        name="PubMed Central", 
        url_pattern="ncbi.nlm.nih.gov/pmc",
        authority_score=0.85,
        specialties=["peer-reviewed research", "biomedical literature"],
        source_type=SourceType.RESEARCH_ORGANIZATION,
        description="Biomedical research database",
        typical_content_types=["research_papers", "systematic_reviews"]
    ),
    
    EvidenceSource(
        name="Cochrane Library",
        url_pattern="cochranelibrary.com",
        authority_score=0.92,
        specialties=["systematic reviews", "evidence synthesis"],
        source_type=SourceType.RESEARCH_ORGANIZATION,
        description="Evidence-based medicine organization",
        typical_content_types=["systematic_reviews", "meta_analyses"]
    ),
    
    EvidenceSource(
        name="Nature Medicine",
        url_pattern="nature.com/nm",
        authority_score=0.88,
        specialties=["medical research", "translational medicine"],
        source_type=SourceType.ACADEMIC,
        description="High-impact medical journal",
        typical_content_types=["research_articles", "reviews"]
    ),
    
    EvidenceSource(
        name="New England Journal of Medicine",
        url_pattern="nejm.org",
        authority_score=0.90,
        specialties=["clinical medicine", "medical research"],
        source_type=SourceType.ACADEMIC,
        description="Premier medical journal",
        typical_content_types=["research_articles", "case_reports"]
    ),
    
    EvidenceSource(
        name="The Lancet",
        url_pattern="thelancet.com",
        authority_score=0.89,
        specialties=["global health", "public health", "medical research"],
        source_type=SourceType.ACADEMIC,
        description="Leading medical journal",
        typical_content_types=["research_articles", "commentary"]
    ),
    
    # Professional organizations
    EvidenceSource(
        name="American Medical Association",
        url_pattern="ama-assn.org",
        authority_score=0.82,
        specialties=["medical practice", "ethics", "professional standards"],
        source_type=SourceType.PROFESSIONAL_SOCIETY,
        description="US physician organization",
        typical_content_types=["guidelines", "position_statements"]
    ),
    
    EvidenceSource(
        name="American Academy of Pediatrics",
        url_pattern="aap.org",
        authority_score=0.85,
        specialties=["pediatric health", "child development", "vaccines"],
        source_type=SourceType.PROFESSIONAL_SOCIETY,
        description="Pediatric professional organization",
        typical_content_types=["clinical_guidelines", "policy_statements"]
    ),
    
    # Disease-specific organizations
    EvidenceSource(
        name="American Cancer Society",
        url_pattern="cancer.org",
        authority_score=0.83,
        specialties=["cancer prevention", "cancer treatment"],
        source_type=SourceType.MEDICAL_INSTITUTION,
        description="Cancer advocacy organization",
        typical_content_types=["guidelines", "patient_information"]
    ),
    
    EvidenceSource(
        name="American Heart Association",
        url_pattern="heart.org",
        authority_score=0.84,
        specialties=["cardiovascular health", "stroke prevention"],
        source_type=SourceType.MEDICAL_INSTITUTION,
        description="Cardiovascular health organization",
        typical_content_types=["guidelines", "recommendations"]
    ),
    
    EvidenceSource(
        name="National Institute of Mental Health",
        url_pattern="nimh.nih.gov",
        authority_score=0.86,
        specialties=["mental health research", "psychiatric disorders"],
        source_type=SourceType.GOVERNMENT,
        description="US mental health research agency",
        typical_content_types=["research_findings", "clinical_trials"]
    ),
]

class EnhancedEvidenceSearcher(EvidenceSearcher):
    """Enhanced evidence searcher with expanded source database"""
    
    def __init__(self):
        super().__init__()
        self.sources = ENHANCED_TRUSTED_SOURCES
    
    def get_sources_by_specialty(self, specialty: str, min_authority_score: float = 0.7) -> list:
        """Get sources filtered by specialty and minimum authority score"""
        
        specialty_lower = specialty.lower()
        matching_sources = []
        
        for source in self.sources:
            if (source.authority_score >= min_authority_score and
                any(specialty_lower in spec.lower() or spec.lower() in specialty_lower 
                    for spec in source.specialties)):
                matching_sources.append(source)
        
        return sorted(matching_sources, key=lambda x: x.authority_score, reverse=True)
    
    def get_sources_by_type(self, source_type: str) -> list:
        """Get sources by organizational type"""
        return [source for source in self.sources 
                if source.source_type.value == source_type or source.source_type.name.lower() == source_type.lower()]
    
    def get_top_sources(self, limit: int = 10) -> list:
        """Get top sources by authority score"""
        return sorted(self.sources, key=lambda x: x.authority_score, reverse=True)[:limit]
    
    def search_by_content_type(self, content_type: str) -> list:
        """Find sources that provide specific content types"""
        return [source for source in self.sources 
                if content_type in source.typical_content_types]
    
    def get_source_diversity_score(self, selected_sources: list) -> dict:
        """Calculate diversity metrics for selected sources"""
        
        if not selected_sources:
            return {'score': 0.0, 'details': 'No sources selected'}
        
        # Analyze diversity
        types = set(source.source_type.value for source in selected_sources)
        specialties = set()
        
        for source in selected_sources:
            specialties.update(source.specialties)
        
        # Calculate diversity score
        type_diversity = len(types) / 5  # 5 main types
        specialty_diversity = min(len(specialties) / 10, 1.0)
        
        overall_score = (type_diversity + specialty_diversity) / 2
        
        return {
            'score': round(overall_score, 2),
            'type_diversity': len(types),
            'specialty_diversity': len(specialties),
            'types': list(types),
            'specialties': list(specialties)[:10]
        }

# Global instance
enhanced_evidence_searcher = EnhancedEvidenceSearcher()