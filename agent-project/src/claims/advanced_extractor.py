"""Advanced claim detection with implicit claims and context analysis"""

import re
from typing import List, Dict, Any, Tuple
from src.agent import Agent, model
from src.health_kb.claim_types import HealthClaim, ClaimType
from .extractor import ClaimExtractor

class AdvancedClaimExtractor(ClaimExtractor):
    """Enhanced claim extractor with implicit claim detection and context analysis"""
    
    def __init__(self):
        super().__init__()
        
        # Implicit claim detection agent
        self.implicit_claim_agent = Agent(
            name="ImplicitClaimDetector",
            instructions="""You are an expert at detecting implicit health claims, assumptions, and implications in text.

Your task is to identify:
1. IMPLICIT CLAIMS: Unstated assumptions or implications (e.g., "natural is better" implies manufactured treatments are inferior)
2. CONTEXTUAL MEANINGS: Claims that depend on context or comparison
3. IMPLIED CAUSATION: Suggested cause-and-effect relationships without explicit statement
4. AUTHORITY IMPLICATIONS: Implied endorsements or expert approval
5. STATISTICAL IMPLICATIONS: Misleading use of numbers or percentages

For each implicit claim found, provide:
- The implicit claim text
- What it implies or assumes
- Why it could be misleading
- Confidence level (0.0-1.0)

Focus on health-related implications that could mislead audiences.""",
            model=model
        )
        
        # Context analysis agent
        self.context_agent = Agent(
            name="ContextAnalyzer", 
            instructions="""You are an expert at analyzing the context and framing of health communications.

Your task is to identify:
1. FRAMING EFFECTS: How information is presented to influence interpretation
2. COMPARATIVE CLAIMS: Implicit comparisons without proper context
3. TEMPORAL IMPLICATIONS: Time-based assumptions or urgency
4. AUDIENCE TARGETING: Implicit appeals to specific groups
5. EMOTIONAL FRAMING: Language designed to evoke specific emotional responses

Analyze how the context might change the meaning or impact of health claims.""",
            model=model
        )
        
        # Enhanced pattern matching for implicit claims
        self.implicit_patterns = [
            # Natural vs artificial implications
            (r'\b(natural|organic|pure)\b.*(?:is|are)\s+(?:better|safer|healthier)', 'natural_superiority'),
            (r'\b(chemical|artificial|synthetic|processed)\b.*(?:is|are)\s+(?:bad|harmful|dangerous)', 'artificial_inferiority'),
            
            # Time-based implications
            (r'\b(ancient|traditional|time-tested)\b.*(?:wisdom|knowledge|remedy)', 'historical_authority'),
            (r'\b(modern|new|latest)\b.*(?:medicine|treatment|science)', 'novelty_authority'),
            
            # Comparison implications
            (r'\b(?:unlike|compared to|instead of)\b.*(?:drugs|medication|treatment)', 'implicit_comparison'),
            (r'\bwithout.*(?:side effects|risks|chemicals)', 'risk_free_implication'),
            
            # Authority implications
            (r'\b(?:doctors|experts|scientists)\s+(?:don\'t want you to know|hide|suppress)', 'conspiracy_authority'),
            (r'\b(?:big pharma|pharmaceutical companies)\b.*(?:profit|money|greed)', 'profit_motive'),
            
            # Statistical implications
            (r'\b(\d+)%.*(?:of people|patients|cases)\b', 'statistical_generalization'),
            (r'\bstudies show\b(?!\s+that)', 'vague_study_reference'),
            
            # Causal implications
            (r'\b(?:leads to|causes|results in|linked to)\b', 'causal_implication'),
            (r'\b(?:associated with|correlated with)\b', 'correlation_implication')
        ]
    
    async def extract_claims_advanced(self, text: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract explicit and implicit claims with context analysis"""
        
        options = options or {}
        
        # Get explicit claims from base extractor
        base_result = await self.extract_claims(text, options)
        explicit_claims = base_result.get('claims', [])
        
        # Extract implicit claims
        implicit_claims = await self._extract_implicit_claims(text)
        
        # Analyze context and framing
        context_analysis = await self._analyze_context(text)
        
        # Detect patterns indicating implicit claims
        pattern_implications = self._detect_implicit_patterns(text)
        
        # Combine all findings
        all_claims = explicit_claims + implicit_claims
        
        return {
            'explicit_claims': explicit_claims,
            'implicit_claims': implicit_claims,
            'pattern_implications': pattern_implications,
            'context_analysis': context_analysis,
            'all_claims': all_claims,
            'total_claim_count': len(all_claims),
            'implicit_claim_count': len(implicit_claims),
            'pattern_count': len(pattern_implications)
        }
    
    async def _extract_implicit_claims(self, text: str) -> List[Dict[str, Any]]:
        """Use LLM to detect implicit claims and assumptions"""
        
        analysis_prompt = f"""
        Analyze this health communication text for implicit claims and assumptions:
        
        TEXT: "{text}"
        
        Identify implicit health claims that are not explicitly stated but are implied or assumed. 
        For each implicit claim, provide:
        1. The implicit claim
        2. What it implies or assumes
        3. Why it could be misleading
        4. Confidence level (0.0-1.0)
        
        Return findings in this format:
        IMPLICIT CLAIM: [claim text]
        IMPLIES: [what it implies]
        MISLEADING BECAUSE: [why problematic]
        CONFIDENCE: [0.0-1.0]
        ---
        """
        
        try:
            response = await self.implicit_claim_agent.run(analysis_prompt)
            return self._parse_implicit_claims_response(response)
        except Exception as e:
            print(f"Error in implicit claim extraction: {e}")
            return []
    
    def _parse_implicit_claims_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured implicit claims"""
        
        claims = []
        sections = response.split('---')
        
        for section in sections:
            if 'IMPLICIT CLAIM:' in section:
                try:
                    lines = section.strip().split('\n')
                    claim_data = {}
                    
                    for line in lines:
                        if line.startswith('IMPLICIT CLAIM:'):
                            claim_data['text'] = line.replace('IMPLICIT CLAIM:', '').strip()
                        elif line.startswith('IMPLIES:'):
                            claim_data['implication'] = line.replace('IMPLIES:', '').strip()
                        elif line.startswith('MISLEADING BECAUSE:'):
                            claim_data['misleading_reason'] = line.replace('MISLEADING BECAUSE:', '').strip()
                        elif line.startswith('CONFIDENCE:'):
                            try:
                                claim_data['confidence'] = float(line.replace('CONFIDENCE:', '').strip())
                            except ValueError:
                                claim_data['confidence'] = 0.5
                    
                    if claim_data.get('text'):
                        claim_data.update({
                            'claim_type': ClaimType.IMPLICATION.value,
                            'extraction_method': 'llm_implicit',
                            'is_implicit': True,
                            'base_risk_score': min(0.8, claim_data.get('confidence', 0.5) + 0.3)  # Implicit claims generally higher risk
                        })
                        claims.append(claim_data)
                        
                except Exception as e:
                    print(f"Error parsing implicit claim section: {e}")
                    continue
        
        return claims
    
    async def _analyze_context(self, text: str) -> Dict[str, Any]:
        """Analyze context and framing effects"""
        
        context_prompt = f"""
        Analyze the context and framing of this health communication:
        
        TEXT: "{text}"
        
        Identify:
        1. FRAMING EFFECTS: How is information presented to influence interpretation?
        2. EMOTIONAL LANGUAGE: What emotional responses is the text trying to evoke?
        3. TARGET AUDIENCE: Who is this message targeting?
        4. URGENCY INDICATORS: Any sense of time pressure or urgency?
        5. AUTHORITY APPEALS: What authorities or expertise is referenced?
        6. RISK FRAMING: How are risks/benefits presented?
        
        Provide analysis of how context might affect interpretation.
        """
        
        try:
            response = await self.context_agent.run(context_prompt)
            return {
                'raw_analysis': response,
                'framing_detected': 'framing' in response.lower() or 'presents' in response.lower(),
                'emotional_language': 'emotion' in response.lower() or 'fear' in response.lower(),
                'urgency_detected': 'urgent' in response.lower() or 'immediate' in response.lower(),
                'authority_appeals': 'authority' in response.lower() or 'expert' in response.lower()
            }
        except Exception as e:
            print(f"Error in context analysis: {e}")
            return {'error': str(e)}
    
    def _detect_implicit_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Detect patterns that indicate implicit claims"""
        
        implications = []
        text_lower = text.lower()
        
        for pattern, implication_type in self.implicit_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            
            for match in matches:
                implications.append({
                    'pattern_type': implication_type,
                    'matched_text': match.group(),
                    'start_position': match.start(),
                    'end_position': match.end(),
                    'implication': self._get_implication_description(implication_type),
                    'risk_level': self._assess_pattern_risk(implication_type)
                })
        
        return implications
    
    def _get_implication_description(self, pattern_type: str) -> str:
        """Get description of what the pattern implies"""
        
        descriptions = {
            'natural_superiority': 'Implies natural products are inherently better than manufactured ones',
            'artificial_inferiority': 'Implies artificial/chemical products are inherently harmful',
            'historical_authority': 'Appeals to tradition as evidence of effectiveness',
            'novelty_authority': 'Appeals to newness as evidence of superiority',
            'implicit_comparison': 'Makes comparison without providing complete context',
            'risk_free_implication': 'Implies absence of risks without proper qualification',
            'conspiracy_authority': 'Implies medical establishment is hiding information',
            'profit_motive': 'Suggests profit motive undermines medical advice',
            'statistical_generalization': 'Uses statistics without proper context or methodology',
            'vague_study_reference': 'References studies without specific citation',
            'causal_implication': 'Suggests causation which may not be established',
            'correlation_implication': 'References correlation which may be misinterpreted as causation'
        }
        
        return descriptions.get(pattern_type, 'Unknown implication pattern')
    
    def _assess_pattern_risk(self, pattern_type: str) -> str:
        """Assess risk level of implication pattern"""
        
        high_risk_patterns = [
            'conspiracy_authority', 'risk_free_implication', 
            'causal_implication', 'statistical_generalization'
        ]
        
        medium_risk_patterns = [
            'natural_superiority', 'artificial_inferiority',
            'implicit_comparison', 'vague_study_reference'
        ]
        
        if pattern_type in high_risk_patterns:
            return 'high'
        elif pattern_type in medium_risk_patterns:
            return 'medium'
        else:
            return 'low'
    
    def get_claim_complexity_score(self, claims_result: Dict[str, Any]) -> float:
        """Calculate complexity score based on explicit/implicit claim ratio"""
        
        explicit_count = len(claims_result.get('explicit_claims', []))
        implicit_count = len(claims_result.get('implicit_claims', []))
        pattern_count = len(claims_result.get('pattern_implications', []))
        
        if explicit_count == 0:
            return 1.0 if (implicit_count + pattern_count) > 0 else 0.0
        
        # Higher ratio of implicit to explicit indicates more complex messaging
        complexity_ratio = (implicit_count + pattern_count * 0.5) / explicit_count
        return min(1.0, complexity_ratio)

# Global instance
advanced_claim_extractor = AdvancedClaimExtractor()
