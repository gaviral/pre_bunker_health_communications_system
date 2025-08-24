"""Persona interpretation engine for analyzing health communications"""

import asyncio
import re
from typing import List, Dict, Any, Optional
from src.personas.base_personas import AudiencePersona, STANDARD_PERSONAS
from src.health_kb.medical_terms import is_medical_term

class PersonaInterpreter:
    """Orchestrates multiple personas to interpret health communications"""
    
    def __init__(self, personas: List[AudiencePersona] = None):
        self.personas = personas or STANDARD_PERSONAS.copy()
        self.concern_keywords = [
            'worried', 'scared', 'confused', 'unclear', 'dangerous',
            'concerning', 'troubling', 'suspicious', 'doubt', 'uncertain',
            'risky', 'harmful', 'misleading', 'false', 'wrong'
        ]
        
        # Ensure all personas have agents created
        for persona in self.personas:
            if not persona.interpretation_agent:
                persona.create_agent()
    
    async def interpret_message(self, message_text: str) -> List[Dict[str, Any]]:
        """Have all personas interpret a health message"""
        
        # Skip non-medical content to save LLM calls
        if not is_medical_term(message_text):
            return []
        
        interpretations = []
        
        # Use asyncio.gather for parallel execution
        async def get_persona_interpretation(persona):
            try:
                response = await persona.interpret_message(message_text)
                concerns = self.extract_concerns(response)
                misreadings = self.extract_misreadings(response)
                emotional_reactions = self.extract_emotional_reactions(response)
                
                return {
                    'persona': persona.name,
                    'demographics': persona.demographics,
                    'health_literacy': persona.health_literacy,
                    'interpretation': response,
                    'potential_misreading': concerns + misreadings,
                    'emotional_reaction': emotional_reactions,
                    'concern_level': self.assess_concern_level(response),
                    'key_issues': self.extract_key_issues(response)
                }
            except Exception as e:
                # Return error info but don't fail the whole operation
                return {
                    'persona': persona.name,
                    'demographics': persona.demographics,
                    'health_literacy': persona.health_literacy,
                    'interpretation': f"Error in interpretation: {str(e)}",
                    'potential_misreading': ['interpretation_error'],
                    'emotional_reaction': ['error'],
                    'concern_level': 'unknown',
                    'key_issues': ['failed_to_process']
                }
        
        # Execute all persona interpretations in parallel
        interpretation_tasks = [get_persona_interpretation(persona) for persona in self.personas]
        interpretations = await asyncio.gather(*interpretation_tasks)
        
        return interpretations
    
    def extract_concerns(self, interpretation_text: str) -> List[str]:
        """Extract specific concerns or worries from interpretation"""
        concerns = []
        text_lower = interpretation_text.lower()
        
        for keyword in self.concern_keywords:
            if keyword in text_lower:
                concerns.append(keyword)
        
        # Look for specific concern patterns
        concern_patterns = [
            r'i (?:am|\'m) (?:worried|concerned|scared) about (.+?)(?:\.|$)',
            r'(?:what|how) about (.+?)\?',
            r'(?:this|that) (?:sounds|seems|looks) (.+?)(?:\.|$)',
            r'(?:i|we) (?:don\'t|dont) (?:trust|believe) (.+?)(?:\.|$)'
        ]
        
        for pattern in concern_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 3:  # Avoid very short matches
                    concerns.append(f"concern_about_{match.strip()[:30]}")
        
        return list(set(concerns))  # Remove duplicates
    
    def extract_misreadings(self, interpretation_text: str) -> List[str]:
        """Extract potential misreadings or misunderstandings"""
        misreadings = []
        text_lower = interpretation_text.lower()
        
        # Patterns that suggest misreading
        misreading_indicators = [
            'i thought', 'i assumed', 'sounds like', 'seems like',
            'probably means', 'i bet', 'must be', 'obviously'
        ]
        
        for indicator in misreading_indicators:
            if indicator in text_lower:
                misreadings.append(f'potential_misreading_{indicator.replace(" ", "_")}')
        
        # Look for absolutist interpretations of nuanced content
        absolutist_interpretations = [
            'always', 'never', 'all', 'none', 'everyone', 'no one',
            'completely', 'totally', 'entirely', 'absolutely'
        ]
        
        for abs_term in absolutist_interpretations:
            if abs_term in text_lower:
                misreadings.append(f'absolutist_thinking_{abs_term}')
        
        return misreadings
    
    def extract_emotional_reactions(self, interpretation_text: str) -> List[str]:
        """Extract emotional reactions from the interpretation"""
        emotions = []
        text_lower = interpretation_text.lower()
        
        emotion_keywords = {
            'fear': ['afraid', 'scared', 'frightened', 'terrified', 'fearful'],
            'anger': ['angry', 'mad', 'furious', 'outraged', 'irritated'],
            'confusion': ['confused', 'puzzled', 'unclear', 'lost', 'bewildered'],
            'skepticism': ['doubt', 'suspicious', 'skeptical', 'questioning', 'unsure'],
            'relief': ['relieved', 'reassured', 'comforted', 'calmed'],
            'excitement': ['excited', 'eager', 'enthusiastic', 'hopeful'],
            'anxiety': ['anxious', 'nervous', 'worried', 'stressed', 'uneasy']
        }
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotions.append(emotion)
                    break  # Only add each emotion once
        
        return emotions
    
    def assess_concern_level(self, interpretation_text: str) -> str:
        """Assess the overall concern level of the interpretation"""
        text_lower = interpretation_text.lower()
        
        high_concern_indicators = [
            'dangerous', 'risky', 'harmful', 'scared', 'terrified',
            'wrong', 'false', 'misleading', 'lies', 'conspiracy'
        ]
        
        medium_concern_indicators = [
            'worried', 'concerned', 'unsure', 'confused', 'questioning',
            'doubt', 'suspicious', 'unclear', 'confusing'
        ]
        
        low_concern_indicators = [
            'reassured', 'confident', 'clear', 'helpful', 'informative',
            'good', 'useful', 'makes sense'
        ]
        
        high_score = sum(1 for indicator in high_concern_indicators if indicator in text_lower)
        medium_score = sum(1 for indicator in medium_concern_indicators if indicator in text_lower)
        low_score = sum(1 for indicator in low_concern_indicators if indicator in text_lower)
        
        if high_score > 0:
            return 'high'
        elif medium_score > low_score:
            return 'medium'
        elif low_score > 0:
            return 'low'
        else:
            return 'neutral'
    
    def extract_key_issues(self, interpretation_text: str) -> List[str]:
        """Extract key issues or topics mentioned in the interpretation"""
        issues = []
        text_lower = interpretation_text.lower()
        
        # Health-related topics
        health_topics = [
            'side effects', 'safety', 'effectiveness', 'dosage', 'timing',
            'children', 'elderly', 'pregnancy', 'allergies', 'interactions',
            'long term', 'short term', 'natural', 'artificial', 'chemicals',
            'government', 'pharmaceutical', 'profit', 'control', 'freedom',
            'research', 'studies', 'evidence', 'proof', 'data'
        ]
        
        for topic in health_topics:
            if topic in text_lower:
                issues.append(topic.replace(' ', '_'))
        
        return list(set(issues))
    
    def analyze_interpretation_patterns(self, interpretations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns across all persona interpretations"""
        if not interpretations:
            return {}
        
        analysis = {
            'total_personas': len(interpretations),
            'concern_distribution': {},
            'common_misreadings': {},
            'emotional_patterns': {},
            'high_concern_personas': [],
            'consensus_issues': [],
            'divergent_views': []
        }
        
        # Analyze concern levels
        concern_counts = {}
        for interp in interpretations:
            concern = interp['concern_level']
            concern_counts[concern] = concern_counts.get(concern, 0) + 1
            
            if concern == 'high':
                analysis['high_concern_personas'].append(interp['persona'])
        
        analysis['concern_distribution'] = concern_counts
        
        # Find common misreadings
        all_misreadings = []
        for interp in interpretations:
            all_misreadings.extend(interp['potential_misreading'])
        
        misreading_counts = {}
        for misreading in all_misreadings:
            misreading_counts[misreading] = misreading_counts.get(misreading, 0) + 1
        
        # Include misreadings mentioned by multiple personas
        analysis['common_misreadings'] = {
            k: v for k, v in misreading_counts.items() if v > 1
        }
        
        # Analyze emotional patterns
        all_emotions = []
        for interp in interpretations:
            all_emotions.extend(interp['emotional_reaction'])
        
        emotion_counts = {}
        for emotion in all_emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        analysis['emotional_patterns'] = emotion_counts
        
        # Find consensus issues (mentioned by multiple personas)
        all_issues = []
        for interp in interpretations:
            all_issues.extend(interp['key_issues'])
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        analysis['consensus_issues'] = [
            issue for issue, count in issue_counts.items() if count >= len(interpretations) // 2
        ]
        
        return analysis

# Global instance
persona_interpreter = PersonaInterpreter()
