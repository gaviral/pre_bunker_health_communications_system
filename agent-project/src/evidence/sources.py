"""Evidence source framework for health information validation"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum

class SourceType(Enum):
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    MEDICAL_INSTITUTION = "medical_institution"
    RESEARCH_ORGANIZATION = "research_organization"
    PROFESSIONAL_SOCIETY = "professional_society"

@dataclass
class EvidenceSource:
    """Represents a trusted health information source"""
    name: str
    url_pattern: str
    authority_score: float  # 0-1, higher = more authoritative
    specialties: List[str]
    source_type: SourceType
    description: str
    typical_content_types: List[str]
    limitations: List[str] = None
    
    def __post_init__(self):
        if self.limitations is None:
            self.limitations = []
    
    def is_relevant_for_topic(self, topic: str) -> bool:
        """Check if this source is relevant for a given health topic"""
        topic_lower = topic.lower()
        # Check if topic appears in any specialty, or if any specialty appears in topic
        return any(
            specialty.lower() in topic_lower or topic_lower in specialty.lower() 
            for specialty in self.specialties
        )
    
    def get_search_terms(self, claim_text: str) -> List[str]:
        """Extract relevant search terms for this source"""
        # Basic implementation - in practice would be more sophisticated
        terms = []
        claim_lower = claim_text.lower()
        
        for specialty in self.specialties:
            if specialty.lower() in claim_lower:
                terms.append(specialty)
        
        # Extract key medical terms
        medical_keywords = [
            'vaccine', 'vaccination', 'immunization', 'medication', 'treatment',
            'therapy', 'disease', 'infection', 'symptoms', 'side effects',
            'dosage', 'safety', 'efficacy', 'effectiveness', 'prevention'
        ]
        
        for keyword in medical_keywords:
            if keyword in claim_lower:
                terms.append(keyword)
        
        return list(set(terms))

# Trusted health information sources
TRUSTED_SOURCES = [
    EvidenceSource(
        name="World Health Organization (WHO)",
        url_pattern="who.int",
        authority_score=0.95,
        specialties=[
            "global health", "disease outbreaks", "vaccination guidelines",
            "infectious diseases", "health emergencies", "public health policy"
        ],
        source_type=SourceType.GOVERNMENT,
        description="Global health authority providing evidence-based guidance",
        typical_content_types=["guidelines", "fact sheets", "recommendations", "reports"],
        limitations=["May not cover country-specific recommendations", "Focus on global rather than individual guidance"]
    ),
    
    EvidenceSource(
        name="Centers for Disease Control and Prevention (CDC)",
        url_pattern="cdc.gov",
        authority_score=0.95,
        specialties=[
            "US health policy", "disease surveillance", "prevention",
            "vaccination schedules", "infectious diseases", "epidemiology"
        ],
        source_type=SourceType.GOVERNMENT,
        description="US national public health agency",
        typical_content_types=["guidelines", "surveillance data", "recommendations", "fact sheets"],
        limitations=["US-focused", "May not apply to other countries"]
    ),
    
    EvidenceSource(
        name="Cochrane Library",
        url_pattern="cochranelibrary.com",
        authority_score=0.90,
        specialties=[
            "systematic reviews", "evidence synthesis", "meta-analyses",
            "clinical effectiveness", "treatment comparisons"
        ],
        source_type=SourceType.RESEARCH_ORGANIZATION,
        description="High-quality systematic reviews and meta-analyses",
        typical_content_types=["systematic reviews", "meta-analyses", "clinical trials"],
        limitations=["May not have reviews for very new treatments", "Academic language"]
    ),
    
    EvidenceSource(
        name="U.S. Food and Drug Administration (FDA)",
        url_pattern="fda.gov",
        authority_score=0.90,
        specialties=[
            "drug approval", "medical devices", "safety warnings",
            "adverse events", "clinical trials", "regulatory decisions"
        ],
        source_type=SourceType.GOVERNMENT,
        description="US agency regulating medical products",
        typical_content_types=["safety alerts", "drug labels", "approval decisions", "warnings"],
        limitations=["US regulatory focus", "May not cover off-label uses"]
    ),
    
    EvidenceSource(
        name="PubMed/NCBI",
        url_pattern="pubmed.ncbi.nlm.nih.gov",
        authority_score=0.85,
        specialties=[
            "peer-reviewed research", "clinical studies", "basic science",
            "medical literature", "case studies", "clinical trials"
        ],
        source_type=SourceType.ACADEMIC,
        description="Database of peer-reviewed medical literature",
        typical_content_types=["research papers", "clinical trials", "case studies", "reviews"],
        limitations=["Variable quality", "Requires medical expertise to interpret", "May include preliminary studies"]
    ),
    
    EvidenceSource(
        name="Mayo Clinic",
        url_pattern="mayoclinic.org",
        authority_score=0.80,
        specialties=[
            "patient education", "symptoms", "diseases", "treatments",
            "patient care", "health information", "medical conditions"
        ],
        source_type=SourceType.MEDICAL_INSTITUTION,
        description="Trusted medical institution providing patient information",
        typical_content_types=["patient guides", "symptom information", "treatment options"],
        limitations=["Focused on patient education", "May not include latest research"]
    ),
    
    EvidenceSource(
        name="American Academy of Pediatrics (AAP)",
        url_pattern="aap.org",
        authority_score=0.85,
        specialties=[
            "pediatric care", "child health", "vaccination schedules",
            "infant care", "adolescent health", "pediatric guidelines"
        ],
        source_type=SourceType.PROFESSIONAL_SOCIETY,
        description="Professional society for pediatricians",
        typical_content_types=["clinical guidelines", "policy statements", "recommendations"],
        limitations=["Pediatric focus only", "Professional audience"]
    ),
    
    EvidenceSource(
        name="American Medical Association (AMA)",
        url_pattern="ama-assn.org",
        authority_score=0.80,
        specialties=[
            "medical ethics", "professional standards", "health policy",
            "physician guidelines", "medical education"
        ],
        source_type=SourceType.PROFESSIONAL_SOCIETY,
        description="Professional association for physicians",
        typical_content_types=["policy statements", "ethical guidelines", "professional standards"],
        limitations=["Focus on professional practice", "Policy rather than clinical guidance"]
    )
]

class EvidenceSearcher:
    """Handles searching for evidence across trusted sources"""
    
    def __init__(self, sources: List[EvidenceSource] = None):
        self.sources = sources or TRUSTED_SOURCES
        self.source_lookup = {source.name: source for source in self.sources}
    
    def find_relevant_sources(self, claim_text: str, topic_area: str = None) -> List[EvidenceSource]:
        """Find sources relevant to a health claim"""
        relevant_sources = []
        
        for source in self.sources:
            # Check if source specializes in the topic
            if topic_area and source.is_relevant_for_topic(topic_area):
                relevant_sources.append(source)
                continue
            
            # Check if source is relevant based on claim content
            search_terms = source.get_search_terms(claim_text)
            if search_terms:
                relevant_sources.append(source)
        
        # Sort by authority score (highest first)
        relevant_sources.sort(key=lambda s: s.authority_score, reverse=True)
        
        return relevant_sources
    
    def get_source_by_name(self, name: str) -> Optional[EvidenceSource]:
        """Get a specific source by name"""
        return self.source_lookup.get(name)
    
    def get_sources_by_type(self, source_type: SourceType) -> List[EvidenceSource]:
        """Get all sources of a specific type"""
        return [source for source in self.sources if source.source_type == source_type]
    
    def get_highest_authority_sources(self, limit: int = 3) -> List[EvidenceSource]:
        """Get the highest authority sources"""
        sorted_sources = sorted(self.sources, key=lambda s: s.authority_score, reverse=True)
        return sorted_sources[:limit]
    
    def assess_source_credibility(self, url: str) -> Dict[str, Any]:
        """Assess credibility of a given URL"""
        for source in self.sources:
            if source.url_pattern in url.lower():
                return {
                    'source_name': source.name,
                    'authority_score': source.authority_score,
                    'source_type': source.source_type.value,
                    'credibility_level': self.get_credibility_level(source.authority_score),
                    'specialties': source.specialties,
                    'limitations': source.limitations
                }
        
        # Unknown source
        return {
            'source_name': 'Unknown',
            'authority_score': 0.0,
            'source_type': 'unknown',
            'credibility_level': 'unverified',
            'specialties': [],
            'limitations': ['Source not in trusted database']
        }
    
    def get_credibility_level(self, score: float) -> str:
        """Convert authority score to credibility level"""
        if score >= 0.9:
            return 'very_high'
        elif score >= 0.8:
            return 'high'
        elif score >= 0.7:
            return 'medium'
        elif score >= 0.5:
            return 'low'
        else:
            return 'very_low'
    
    def generate_source_summary(self) -> Dict[str, Any]:
        """Generate summary of available sources"""
        summary = {
            'total_sources': len(self.sources),
            'by_type': {},
            'authority_distribution': {},
            'specialty_coverage': set(),
            'highest_authority': []
        }
        
        # Count by type
        for source in self.sources:
            source_type = source.source_type.value
            summary['by_type'][source_type] = summary['by_type'].get(source_type, 0) + 1
            
            # Collect specialties
            summary['specialty_coverage'].update(source.specialties)
        
        # Authority distribution
        for source in self.sources:
            level = self.get_credibility_level(source.authority_score)
            summary['authority_distribution'][level] = summary['authority_distribution'].get(level, 0) + 1
        
        # Convert set to list for JSON serialization
        summary['specialty_coverage'] = list(summary['specialty_coverage'])
        
        # Highest authority sources
        summary['highest_authority'] = [
            {'name': s.name, 'score': s.authority_score} 
            for s in self.get_highest_authority_sources(5)
        ]
        
        return summary

# Global instance
evidence_searcher = EvidenceSearcher()
