"""Countermeasure generation framework for health misinformation prebunks"""

import asyncio
from typing import List, Dict, Any, Optional
from src.agent import Agent, model
from src.health_kb.claim_types import HealthClaim, ClaimType
from src.evidence.sources import EvidenceSource

class CountermeasureGenerator:
    """Generates prebunks and clarifications for risky health claims"""
    
    def __init__(self):
        # Specialized agent for generating prebunks
        self.prebunk_agent = Agent(
            name="PrebunkGenerator",
            instructions="""You are a health communication expert specializing in creating clear, evidence-based prebunks for health misinformation.

Your job is to generate proactive clarifications that address potential misinterpretations before they spread.

Guidelines:
1. Be clear and factual, avoid complex medical jargon
2. Address specific concerns directly without repeating the misinformation
3. Provide context and nuance where needed
4. Include credible sources when available
5. Maintain empathetic but authoritative tone
6. Focus on what IS true rather than just saying what's false

For each prebunk, include:
- Clear statement of the accurate information
- Brief explanation of why misunderstandings occur
- What people should know/do instead
- Reference to authoritative sources when relevant

Keep prebunks concise but complete.""",
            model=model
        )
        
        # Template-based prebunks for common issues
        self.prebunk_templates = {
            'absolutist_claim': {
                'template': "While {treatment} is {generally_effective}, individual results may vary. {additional_context} Consult your healthcare provider about your specific situation.",
                'triggers': ["100%", "always", "never", "guaranteed", "completely"],
                'description': "Address absolutist language with appropriate nuance"
            },
            'safety_concern': {
                'template': "{treatment} has been extensively tested and is considered safe for most people. {safety_details} Common side effects include {common_effects}. Serious side effects are rare but possible.",
                'triggers': ["completely safe", "no side effects", "perfectly safe"],
                'description': "Provide balanced safety information"
            },
            'conspiracy_theory': {
                'template': "This recommendation comes from {authority_source} based on {evidence_type}. The decision-making process is transparent and regularly reviewed by independent experts. {additional_context}",
                'triggers': ["conspiracy", "control", "hidden agenda", "cover-up"],
                'description': "Address conspiracy concerns with transparency"
            },
            'natural_fallacy': {
                'template': "Both natural and synthetic treatments can be effective and safe when properly tested. {treatment} has undergone rigorous testing regardless of its origin. What matters is the evidence, not whether something is 'natural'.",
                'triggers': ["natural is better", "natural is safer", "chemicals are bad"],
                'description': "Address natural fallacy misconceptions"
            },
            'missing_evidence': {
                'template': "Current evidence from {sources} indicates {evidence_summary}. More research may provide additional insights, but current recommendations are based on the best available evidence.",
                'triggers': ['no evidence', 'unproven', 'experimental'],
                'description': "Clarify evidence status"
            }
        }
    
    async def generate_countermeasures(self, claim: str, persona_concerns: List[str], 
                                     evidence_validation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate countermeasures for a specific claim and its concerns"""
        
        countermeasures = []
        
        # Generate template-based prebunks
        template_prebunks = self._generate_template_prebunks(claim, persona_concerns, evidence_validation)
        countermeasures.extend(template_prebunks)
        
        # Generate custom LLM-based prebunk
        try:
            custom_prebunk = await self._generate_custom_prebunk(claim, persona_concerns, evidence_validation)
            countermeasures.append(custom_prebunk)
        except Exception as e:
            # Fallback if LLM fails
            countermeasures.append({
                'type': 'custom_prebunk',
                'content': f"Error generating custom prebunk: {str(e)}",
                'confidence': 0.0,
                'effectiveness_score': 0.0
            })
        
        # Score and rank countermeasures
        for countermeasure in countermeasures:
            if 'effectiveness_score' not in countermeasure:
                countermeasure['effectiveness_score'] = self._score_countermeasure_effectiveness(
                    countermeasure, claim, persona_concerns
                )
        
        # Sort by effectiveness
        countermeasures.sort(key=lambda x: x['effectiveness_score'], reverse=True)
        
        return countermeasures
    
    def _generate_template_prebunks(self, claim: str, persona_concerns: List[str], 
                                   evidence_validation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prebunks using predefined templates"""
        
        template_prebunks = []
        claim_lower = claim.lower()
        
        for template_type, template_config in self.prebunk_templates.items():
            # Check if any triggers match the claim
            if any(trigger in claim_lower for trigger in template_config['triggers']):
                
                # Fill template with context
                filled_template = self._fill_template(
                    template_config['template'], 
                    claim, 
                    evidence_validation,
                    template_type
                )
                
                template_prebunks.append({
                    'type': 'template_prebunk',
                    'template_type': template_type,
                    'content': filled_template,
                    'description': template_config['description'],
                    'confidence': 0.8,  # High confidence for template-based
                    'triggers_matched': [t for t in template_config['triggers'] if t in claim_lower]
                })
        
        return template_prebunks
    
    def _fill_template(self, template: str, claim: str, evidence_validation: Dict[str, Any], 
                      template_type: str) -> str:
        """Fill a template with specific content for the claim"""
        
        # Extract treatment/topic from claim
        treatment = self._extract_treatment_from_claim(claim)
        
        # Get authority sources
        authority_source = "health authorities"
        if evidence_validation.get('relevant_sources'):
            top_source = evidence_validation['relevant_sources'][0]
            authority_source = top_source['name']
        
        # Template-specific filling
        if template_type == 'absolutist_claim':
            generally_effective = "generally effective" if "effective" in claim.lower() else "helpful for many people"
            additional_context = "Effectiveness can depend on individual factors, timing, and proper use."
            
            return template.format(
                treatment=treatment,
                generally_effective=generally_effective,
                additional_context=additional_context
            )
        
        elif template_type == 'safety_concern':
            safety_details = "Safety data comes from extensive clinical trials and ongoing monitoring."
            common_effects = "mild reactions at the injection site, temporary fatigue, or mild fever"
            
            return template.format(
                treatment=treatment,
                safety_details=safety_details,
                common_effects=common_effects
            )
        
        elif template_type == 'conspiracy_theory':
            evidence_type = "peer-reviewed research and clinical data"
            additional_context = "Multiple independent organizations review this evidence."
            
            return template.format(
                authority_source=authority_source,
                evidence_type=evidence_type,
                additional_context=additional_context
            )
        
        elif template_type == 'missing_evidence':
            sources = authority_source
            evidence_summary = "the treatment shows beneficial effects with acceptable safety profile"
            
            return template.format(
                sources=sources,
                evidence_summary=evidence_summary
            )
        
        # Default case
        return template.format(
            treatment=treatment,
            authority_source=authority_source
        )
    
    def _extract_treatment_from_claim(self, claim: str) -> str:
        """Extract the main treatment/topic from a claim"""
        
        # Common health terms to look for
        health_terms = [
            'vaccine', 'vaccination', 'immunization', 'shot',
            'medication', 'medicine', 'drug', 'treatment', 'therapy',
            'supplement', 'vitamin', 'herb', 'remedy'
        ]
        
        claim_lower = claim.lower()
        words = claim_lower.split()
        
        # Look for health terms
        for term in health_terms:
            if term in claim_lower:
                return term
        
        # Look for specific medical entities
        medical_entities = [
            'covid-19', 'coronavirus', 'flu', 'influenza', 'rsv',
            'acetaminophen', 'ibuprofen', 'aspirin', 'insulin',
            'antibiotic', 'vitamin c', 'vitamin d'
        ]
        
        for entity in medical_entities:
            if entity in claim_lower:
                return entity
        
        # Fallback - use first noun-like word
        for word in words[1:4]:  # Skip first word, check next few
            if len(word) > 3 and word.isalpha():
                return word
        
        return "this treatment"
    
    async def _generate_custom_prebunk(self, claim: str, persona_concerns: List[str], 
                                     evidence_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom prebunk using LLM"""
        
        # Prepare context for LLM
        context_prompt = f"""
        Original claim: "{claim}"
        
        Audience concerns identified: {persona_concerns}
        
        Evidence validation summary:
        - Sources found: {evidence_validation.get('source_count', 0)}
        - Validation status: {evidence_validation.get('validation_status', 'unknown')}
        - Confidence score: {evidence_validation.get('confidence_score', 0.0)}
        
        Generate a clear, evidence-based prebunk that:
        1. Addresses the specific concerns without repeating misinformation
        2. Provides accurate, nuanced information
        3. Uses empathetic but authoritative tone
        4. Includes actionable guidance
        5. Is approximately 2-3 sentences
        
        Focus on what people should know and do, not just what's wrong.
        """
        
        custom_prebunk_text = await self.prebunk_agent.run(context_prompt)
        
        return {
            'type': 'custom_prebunk',
            'content': custom_prebunk_text,
            'confidence': evidence_validation.get('confidence_score', 0.5),
            'context_used': {
                'persona_concerns': persona_concerns,
                'evidence_status': evidence_validation.get('validation_status'),
                'source_count': evidence_validation.get('source_count', 0)
            }
        }
    
    def _score_countermeasure_effectiveness(self, countermeasure: Dict[str, Any], 
                                          claim: str, persona_concerns: List[str]) -> float:
        """Score the potential effectiveness of a countermeasure"""
        
        effectiveness = 0.0
        content = countermeasure.get('content', '').lower()
        
        # Base score from confidence
        effectiveness += countermeasure.get('confidence', 0.5) * 0.3
        
        # Bonus for addressing specific concerns
        concerns_addressed = 0
        for concern in persona_concerns:
            if concern.lower() in content:
                concerns_addressed += 1
        
        if persona_concerns:
            effectiveness += (concerns_addressed / len(persona_concerns)) * 0.3
        
        # Bonus for including authority references
        authority_terms = ['who', 'cdc', 'fda', 'research', 'study', 'clinical', 'evidence']
        authority_mentions = sum(1 for term in authority_terms if term in content)
        effectiveness += min(0.2, authority_mentions * 0.05)
        
        # Bonus for actionable guidance
        action_terms = ['consult', 'talk to', 'discuss', 'contact', 'visit', 'call']
        if any(term in content for term in action_terms):
            effectiveness += 0.1
        
        # Penalty for being too long or too short
        word_count = len(content.split())
        if word_count < 10:
            effectiveness -= 0.1  # Too short
        elif word_count > 100:
            effectiveness -= 0.1  # Too long
        
        # Template type bonuses
        if countermeasure.get('type') == 'template_prebunk':
            effectiveness += 0.1  # Templates are reliable
        
        return min(1.0, max(0.0, effectiveness))
    
    async def generate_multiple_countermeasures(self, claims_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate countermeasures for multiple claims in parallel"""
        
        async def process_claim_data(data):
            claim = data.get('claim', '')
            concerns = data.get('persona_concerns', [])
            evidence = data.get('evidence_validation', {})
            
            countermeasures = await self.generate_countermeasures(claim, concerns, evidence)
            
            return {
                'claim': claim,
                'countermeasures': countermeasures,
                'top_countermeasure': countermeasures[0] if countermeasures else None
            }
        
        tasks = [process_claim_data(data) for data in claims_data]
        return await asyncio.gather(*tasks)
    
    def get_countermeasure_summary(self, countermeasures_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of countermeasure generation results"""
        
        if not countermeasures_results:
            return {'error': 'No countermeasure results provided'}
        
        total_claims = len(countermeasures_results)
        total_countermeasures = sum(len(r['countermeasures']) for r in countermeasures_results)
        
        # Count by type
        type_counts = {}
        effectiveness_scores = []
        
        for result in countermeasures_results:
            for cm in result['countermeasures']:
                cm_type = cm.get('type', 'unknown')
                type_counts[cm_type] = type_counts.get(cm_type, 0) + 1
                effectiveness_scores.append(cm.get('effectiveness_score', 0.0))
        
        avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0.0
        
        # Count high-quality countermeasures
        high_quality = sum(1 for score in effectiveness_scores if score >= 0.7)
        
        return {
            'total_claims_processed': total_claims,
            'total_countermeasures_generated': total_countermeasures,
            'average_countermeasures_per_claim': total_countermeasures / total_claims if total_claims else 0,
            'countermeasure_types': type_counts,
            'average_effectiveness_score': avg_effectiveness,
            'high_quality_countermeasures': high_quality,
            'quality_rate': high_quality / total_countermeasures if total_countermeasures else 0.0
        }

# Global instance
countermeasure_generator = CountermeasureGenerator()
