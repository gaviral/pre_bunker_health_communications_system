"""Basic claim extraction using pattern matching and LLM assistance"""

import re
from typing import List, Dict, Any
from src.tools import function_tool
from src.agent import Agent, model
from src.health_kb.medical_terms import extract_medical_entities, is_medical_term
from src.health_kb.claim_types import HealthClaim, ClaimType, classify_claim_type

class ClaimExtractor:
    def __init__(self):
        self.claim_patterns = [
            # Efficacy patterns
            r'(\w+) (?:is|are) (?:effective|safe|dangerous|harmful|good|bad)',
            r'(\w+) (?:prevents|treats|cures|heals|causes) (\w+)',
            r'(\w+) (?:works|helps|stops|reduces)',
            r'(\w+) (?:success rate|effectiveness|efficacy)',
            
            # Safety patterns  
            r'(\w+) (?:side effects|adverse reactions|risks)',
            r'(\w+) (?:causes|leads to|results in) (\w+)',
            r'(?:safe|dangerous|risky|harmful) (?:to use|for) (\w+)',
            
            # Dosage patterns
            r'take (\d+) (\w+) (?:daily|weekly|monthly|times)',
            r'(\d+) (?:mg|ml|units|doses) of (\w+)',
            r'recommended (?:dose|dosage|amount) (?:of|for) (\w+)',
            
            # Timing patterns
            r'take (\w+) (?:before|after|with) (\w+)',
            r'best time to (?:take|use|administer) (\w+)',
            r'(\w+) should be (?:taken|used) (?:when|if|during)',
            
            # Authority patterns
            r'(?:WHO|CDC|FDA|doctors|experts|studies) (?:recommend|say|show|prove) (?:that )?(\w+)',
            r'according to (?:WHO|CDC|FDA|research|studies), (\w+)',
            
            # Comparison patterns
            r'(\w+) (?:is better than|works better than|safer than) (\w+)',
            r'compared to (\w+), (\w+) (?:is|has)',
            
            # Absolutist claims
            r'(\w+) (?:always|never|100%|guaranteed|completely|totally) (\w+)',
            r'(?:all|every|no) (\w+) (?:will|can|should) (\w+)'
        ]
    
    def extract_pattern_claims(self, text: str) -> List[str]:
        """Extract claims using regex patterns"""
        claims = []
        text_lower = text.lower()
        
        for pattern in self.claim_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                # Extract the full sentence containing the match
                start = max(0, text.rfind('.', 0, match.start()) + 1)
                end = text.find('.', match.end())
                if end == -1:
                    end = len(text)
                
                claim_sentence = text[start:end].strip()
                if claim_sentence and len(claim_sentence) > 10:  # Filter very short matches
                    claims.append(claim_sentence)
        
        return list(set(claims))  # Remove duplicates
    
    @function_tool
    async def extract_health_claims(self, text: str) -> str:
        """Extract health claims from communication text using patterns and LLM"""
        
        # First, extract using patterns
        pattern_claims = self.extract_pattern_claims(text)
        
        # Only use LLM for medical texts to avoid unnecessary calls
        llm_claims = []
        if is_medical_term(text):
            # Create specialized claims extraction agent
            claims_agent = Agent(
                name="ClaimsExtractor",
                instructions="""Extract factual health claims from text. 
                
                Look for statements that make assertions about:
                - Treatment effectiveness or safety
                - Medical recommendations or warnings
                - Cause-and-effect relationships in health
                - Dosing or usage instructions
                - Comparisons between treatments
                
                Format each claim as: CLAIM: [exact claim text]
                Only extract claims that are specific and factual.
                Ignore general health advice or vague statements.""",
                model=model
            )
            
            llm_response = await claims_agent.run(f"Extract health claims from: {text}")
            
            # Parse LLM response for claims
            for line in llm_response.split('\n'):
                if line.strip().startswith('CLAIM:'):
                    claim_text = line.replace('CLAIM:', '').strip()
                    if claim_text:
                        llm_claims.append(claim_text)
        
        # Combine and deduplicate claims
        all_claims = pattern_claims + llm_claims
        unique_claims = []
        for claim in all_claims:
            # Simple deduplication based on significant word overlap
            is_duplicate = False
            for existing in unique_claims:
                common_words = set(claim.lower().split()) & set(existing.lower().split())
                if len(common_words) >= 3:  # Significant overlap
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_claims.append(claim)
        
        return '\n'.join([f"CLAIM: {claim}" for claim in unique_claims])

    def extract_and_classify_claims(self, text: str) -> List[HealthClaim]:
        """Extract claims and create HealthClaim objects"""
        # This would normally be async, but for testing we'll make a sync version
        pattern_claims = self.extract_pattern_claims(text)
        
        health_claims = []
        for claim_text in pattern_claims:
            # Classify the claim
            claim_type = classify_claim_type(claim_text)
            
            # Extract medical entities
            entities = extract_medical_entities(claim_text)
            medical_entities = []
            for category, terms in entities.items():
                medical_entities.extend(terms)
            
            # Create HealthClaim object
            health_claim = HealthClaim(
                text=claim_text,
                claim_type=claim_type,
                confidence=0.8,  # Default confidence for pattern-based extraction
                medical_entities=medical_entities
            )
            
            health_claims.append(health_claim)
        
        return health_claims

# Global instance for use in tools
claim_extractor = ClaimExtractor()
