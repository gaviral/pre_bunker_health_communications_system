"""Basic evidence validation for health claims"""

import asyncio
from typing import List, Dict, Any, Optional
from src.evidence.sources import EvidenceSearcher, TRUSTED_SOURCES, EvidenceSource
from src.agent import Agent, model
from src.health_kb.claim_types import HealthClaim

class EvidenceValidator:
    """Validates health claims against trusted evidence sources"""
    
    def __init__(self, searcher: EvidenceSearcher = None):
        self.searcher = searcher or EvidenceSearcher(TRUSTED_SOURCES)
        
        # Create specialized agent for evidence validation
        self.validation_agent = Agent(
            name="EvidenceValidator",
            instructions="""You are an evidence validation expert. Your job is to assess whether health claims are supported by evidence from trusted sources.

For each claim, analyze:
1. Is this claim supported by the available evidence sources?
2. Are there any contradictions or important nuances missing?
3. What additional context or qualifications should be added?
4. How confident can we be in this claim based on the source authority?

Provide clear, factual assessments. Use phrases like:
- "Supported by evidence" / "Not supported" / "Partially supported"
- "High confidence" / "Medium confidence" / "Low confidence"
- "Additional context needed: [specific context]"
- "Important limitation: [limitation]"

Be precise and avoid speculation. Focus on what the evidence actually shows.""",
            model=model
        )
    
    async def validate_claim(self, claim_text: str, topic_area: str = None) -> Dict[str, Any]:
        """Validate a single claim against evidence sources"""
        
        # Find relevant sources
        relevant_sources = self.searcher.find_relevant_sources(claim_text, topic_area)
        
        # Create validation context
        validation_context = self._create_validation_context(claim_text, relevant_sources)
        
        # Get LLM validation assessment
        try:
            validation_result = await self.validation_agent.run(validation_context)
        except Exception as e:
            validation_result = f"Validation error: {str(e)}"
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(relevant_sources, claim_text)
        
        # Analyze source coverage
        source_analysis = self._analyze_source_coverage(relevant_sources, claim_text)
        
        return {
            'claim': claim_text,
            'relevant_sources': [self._source_to_dict(source) for source in relevant_sources],
            'source_count': len(relevant_sources),
            'highest_authority': max([s.authority_score for s in relevant_sources]) if relevant_sources else 0.0,
            'average_authority': sum([s.authority_score for s in relevant_sources]) / len(relevant_sources) if relevant_sources else 0.0,
            'validation_assessment': validation_result,
            'confidence_score': confidence_score,
            'source_coverage': source_analysis,
            'validation_status': self._determine_validation_status(confidence_score, len(relevant_sources))
        }
    
    async def validate_health_claim(self, health_claim: HealthClaim) -> Dict[str, Any]:
        """Validate a HealthClaim object"""
        
        # Extract topic area from medical entities
        topic_area = None
        if health_claim.medical_entities:
            topic_area = health_claim.medical_entities[0]  # Use first medical entity as topic
        
        validation_result = await self.validate_claim(health_claim.text, topic_area)
        
        # Add claim-specific information
        validation_result.update({
            'claim_type': health_claim.claim_type.value,
            'claim_confidence': health_claim.confidence,
            'medical_entities': health_claim.medical_entities,
            'absolutist_language': health_claim.absolutist_language,
            'missing_evidence_flag': health_claim.missing_evidence
        })
        
        return validation_result
    
    def _create_validation_context(self, claim_text: str, sources: List[EvidenceSource]) -> str:
        """Create context prompt for LLM validation"""
        
        if not sources:
            return f"""
Claim to validate: "{claim_text}"

No relevant trusted sources found for this claim.
Please assess: Is this claim verifiable? What type of evidence would be needed?
"""
        
        source_info = []
        for source in sources[:5]:  # Limit to top 5 sources
            source_info.append(f"- {source.name} (Authority: {source.authority_score}) - Specializes in: {', '.join(source.specialties[:3])}")
        
        sources_text = '\n'.join(source_info)
        
        return f"""
Claim to validate: "{claim_text}"

Relevant trusted sources available:
{sources_text}

Please assess this claim based on what these authoritative sources would likely say.
Consider the authority level and specialization of each source.
"""
    
    def _calculate_confidence_score(self, sources: List[EvidenceSource], claim_text: str) -> float:
        """Calculate confidence score for validation"""
        if not sources:
            return 0.0
        
        # Base confidence from source authority
        avg_authority = sum(s.authority_score for s in sources) / len(sources)
        
        # Bonus for multiple sources
        source_bonus = min(0.2, len(sources) * 0.05)
        
        # Penalty for very broad or vague claims
        specificity_score = self._assess_claim_specificity(claim_text)
        
        # Bonus for specific medical terms
        medical_term_bonus = 0.1 if any(term in claim_text.lower() for term in [
            'vaccine', 'medication', 'treatment', 'therapy', 'dosage', 'mg', 'ml'
        ]) else 0.0
        
        confidence = avg_authority + source_bonus + (specificity_score * 0.1) + medical_term_bonus
        
        return min(1.0, max(0.0, confidence))
    
    def _assess_claim_specificity(self, claim_text: str) -> float:
        """Assess how specific and concrete a claim is"""
        specificity_indicators = [
            'mg', 'ml', 'daily', 'weekly', 'doses', 'study', 'trial',
            'percent', '%', 'effective', 'clinical', 'patients'
        ]
        
        vague_indicators = [
            'it', 'this', 'that', 'they', 'some', 'many', 'often', 'usually'
        ]
        
        claim_lower = claim_text.lower()
        
        specific_count = sum(1 for indicator in specificity_indicators if indicator in claim_lower)
        vague_count = sum(1 for indicator in vague_indicators if indicator in claim_lower)
        
        # Score from 0 to 1, higher is more specific
        specificity = (specific_count - vague_count * 0.5) / 5  # Normalize roughly
        
        return max(0.0, min(1.0, specificity))
    
    def _analyze_source_coverage(self, sources: List[EvidenceSource], claim_text: str) -> Dict[str, Any]:
        """Analyze how well sources cover the claim"""
        if not sources:
            return {
                'coverage_level': 'none',
                'source_types': [],
                'authority_levels': [],
                'coverage_gaps': ['No relevant sources found']
            }
        
        # Analyze source types
        source_types = list(set(source.source_type.value for source in sources))
        
        # Analyze authority levels
        authority_levels = []
        for source in sources:
            if source.authority_score >= 0.9:
                authority_levels.append('very_high')
            elif source.authority_score >= 0.8:
                authority_levels.append('high')
            elif source.authority_score >= 0.7:
                authority_levels.append('medium')
            else:
                authority_levels.append('low')
        
        authority_levels = list(set(authority_levels))
        
        # Determine coverage level
        if len(sources) >= 3 and 'very_high' in authority_levels:
            coverage_level = 'excellent'
        elif len(sources) >= 2 and 'high' in authority_levels:
            coverage_level = 'good'
        elif len(sources) >= 1 and any(level in authority_levels for level in ['high', 'very_high']):
            coverage_level = 'adequate'
        else:
            coverage_level = 'limited'
        
        # Identify potential gaps
        coverage_gaps = []
        if 'government' not in source_types:
            coverage_gaps.append('No government sources (WHO, CDC, FDA)')
        if 'research_organization' not in source_types and 'academic' not in source_types:
            coverage_gaps.append('No peer-reviewed research sources')
        if len(sources) < 2:
            coverage_gaps.append('Limited number of sources for verification')
        
        return {
            'coverage_level': coverage_level,
            'source_types': source_types,
            'authority_levels': authority_levels,
            'coverage_gaps': coverage_gaps if coverage_gaps else ['No significant gaps identified']
        }
    
    def _determine_validation_status(self, confidence_score: float, source_count: int) -> str:
        """Determine overall validation status"""
        if confidence_score >= 0.8 and source_count >= 2:
            return 'well_supported'
        elif confidence_score >= 0.6 and source_count >= 1:
            return 'moderately_supported'
        elif confidence_score >= 0.3:
            return 'limited_support'
        else:
            return 'insufficient_evidence'
    
    def _source_to_dict(self, source: EvidenceSource) -> Dict[str, Any]:
        """Convert EvidenceSource to dictionary"""
        return {
            'name': source.name,
            'authority_score': source.authority_score,
            'source_type': source.source_type.value,
            'specialties': source.specialties,
            'url_pattern': source.url_pattern
        }
    
    async def validate_multiple_claims(self, claims: List[str]) -> List[Dict[str, Any]]:
        """Validate multiple claims in parallel"""
        validation_tasks = [self.validate_claim(claim) for claim in claims]
        return await asyncio.gather(*validation_tasks)
    
    def generate_validation_summary(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of multiple validation results"""
        if not validation_results:
            return {'error': 'No validation results provided'}
        
        total_claims = len(validation_results)
        well_supported = sum(1 for r in validation_results if r['validation_status'] == 'well_supported')
        moderately_supported = sum(1 for r in validation_results if r['validation_status'] == 'moderately_supported')
        limited_support = sum(1 for r in validation_results if r['validation_status'] == 'limited_support')
        insufficient_evidence = sum(1 for r in validation_results if r['validation_status'] == 'insufficient_evidence')
        
        avg_confidence = sum(r['confidence_score'] for r in validation_results) / total_claims
        avg_source_count = sum(r['source_count'] for r in validation_results) / total_claims
        
        return {
            'total_claims': total_claims,
            'validation_distribution': {
                'well_supported': well_supported,
                'moderately_supported': moderately_supported,
                'limited_support': limited_support,
                'insufficient_evidence': insufficient_evidence
            },
            'average_confidence': avg_confidence,
            'average_source_count': avg_source_count,
            'overall_assessment': self._determine_overall_assessment(well_supported, moderately_supported, total_claims)
        }
    
    def _determine_overall_assessment(self, well_supported: int, moderately_supported: int, total: int) -> str:
        """Determine overall assessment of all claims"""
        support_ratio = (well_supported + moderately_supported) / total
        
        if support_ratio >= 0.8:
            return 'strong_evidence_base'
        elif support_ratio >= 0.6:
            return 'moderate_evidence_base'
        elif support_ratio >= 0.4:
            return 'weak_evidence_base'
        else:
            return 'poor_evidence_base'

# Global instance
evidence_validator = EvidenceValidator()
