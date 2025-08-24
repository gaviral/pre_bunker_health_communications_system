"""Persona-targeted countermeasure generation for specific audience concerns"""

from typing import Dict, List, Any
from src.agent import Agent, model

class PersonaTargetedGenerator:
    """Generate targeted countermeasures for specific persona concerns"""
    
    def __init__(self):
        self.generators = {}
        
        # Create specialized agents for different persona types
        self.generators['VaccineHesitant'] = Agent(
            name="VaccineHesitantCountermeasures",
            instructions="Generate respectful, evidence-based responses to vaccine concerns. Acknowledge fears while providing facts.",
            model=model
        )
        
        self.generators['HealthAnxious'] = Agent(
            name="AnxietyCountermeasures", 
            instructions="Generate reassuring, clear responses for health-anxious individuals. Focus on what's normal and when to seek help.",
            model=model
        )
        
        self.generators['SocialMediaUser'] = Agent(
            name="SocialMediaCountermeasures",
            instructions="Generate shareable, engaging content that counters misinformation. Use clear visuals and memorable facts.",
            model=model
        )
        
        self.generators['ChronicIllness'] = Agent(
            name="ChronicIllnessCountermeasures",
            instructions="Generate detailed, nuanced responses for people managing chronic conditions. Include practical considerations and caveats.",
            model=model
        )
        
        self.generators['SkepticalParent'] = Agent(
            name="ParentCountermeasures",
            instructions="Generate family-focused responses that address parental concerns about child safety and long-term effects.",
            model=model
        )
        
        self.generators['HealthcareProfessional'] = Agent(
            name="ProfessionalCountermeasures",
            instructions="Generate evidence-based, clinical responses suitable for healthcare professionals with citations and technical details.",
            model=model
        )
    
    async def generate_targeted_countermeasures(self, claim, persona_interpretations, evidence):
        """Generate persona-specific countermeasures for a claim"""
        countermeasures = {}
        
        for interpretation in persona_interpretations:
            persona_name = interpretation['persona']
            concerns = interpretation['potential_misreading']
            
            if persona_name in self.generators:
                generator = self.generators[persona_name]
                
                prompt = f"""
                Original claim: {claim}
                Persona concerns: {concerns}
                Evidence: {evidence}
                
                Generate a countermeasure that:
                1. Addresses specific concerns of {persona_name}
                2. Uses appropriate tone and language level
                3. Provides actionable next steps
                4. Maintains empathy while being factual
                """
                
                countermeasure = await generator.run(prompt)
                countermeasures[persona_name] = {
                    'text': countermeasure,
                    'tone': self.get_recommended_tone(persona_name),
                    'format': self.get_recommended_format(persona_name),
                    'concerns_addressed': concerns,
                    'effectiveness_score': self.calculate_effectiveness_score(countermeasure, concerns)
                }
        
        return countermeasures
    
    def get_recommended_tone(self, persona_name):
        """Get recommended tone for specific persona"""
        tone_map = {
            'VaccineHesitant': 'respectful, non-judgmental, evidence-focused',
            'HealthAnxious': 'reassuring, calm, specific',
            'SocialMediaUser': 'engaging, shareable, visual-friendly',
            'ChronicIllness': 'detailed, nuanced, practical',
            'SkepticalParent': 'understanding, family-focused, safety-oriented',
            'HealthcareProfessional': 'clinical, evidence-based, technical',
            'TrustingElder': 'respectful, clear, authoritative',
            'BusyProfessional': 'concise, actionable, time-efficient'
        }
        return tone_map.get(persona_name, 'professional, clear')
    
    def get_recommended_format(self, persona_name):
        """Get recommended format for specific persona"""
        format_map = {
            'VaccineHesitant': 'FAQ format, bullet points',
            'HealthAnxious': 'step-by-step guidance',
            'SocialMediaUser': 'infographic-ready, soundbites',
            'ChronicIllness': 'detailed explanation with caveats',
            'SkepticalParent': 'family-friendly Q&A',
            'HealthcareProfessional': 'clinical summary with references',
            'TrustingElder': 'clear instructions, simple language',
            'BusyProfessional': 'executive summary, key points'
        }
        return format_map.get(persona_name, 'structured paragraphs')
    
    def calculate_effectiveness_score(self, countermeasure_text, concerns):
        """Calculate effectiveness score based on concern coverage"""
        if not concerns or not countermeasure_text:
            return 0.0
        
        countermeasure_lower = countermeasure_text.lower()
        addressed_concerns = 0
        
        for concern in concerns:
            # Improved keyword matching - check for partial matches
            concern_words = concern.lower().split()
            concern_addressed = False
            
            # Check if any concern word or root appears in countermeasure
            for word in concern_words:
                if len(word) >= 3:  # Only check meaningful words
                    # Check exact match or if word is contained in countermeasure
                    if word in countermeasure_lower or any(word in cm_word for cm_word in countermeasure_lower.split()):
                        concern_addressed = True
                        break
            
            if concern_addressed:
                addressed_concerns += 1
        
        # Base score on concern coverage (minimum 0.3 if any concerns addressed)
        if addressed_concerns > 0:
            coverage_score = max(0.3, addressed_concerns / len(concerns))
        else:
            coverage_score = 0.0
        
        # Bonus for length (more comprehensive response)
        length_bonus = min(0.15, len(countermeasure_text) / 500)
        
        # Bonus for specific helpful phrases
        helpful_phrases = ['evidence', 'studies', 'research', 'doctor', 'consult', 'talk to', 'consider', 'safe', 'effective']
        phrase_bonus = min(0.25, sum(0.03 for phrase in helpful_phrases if phrase in countermeasure_lower))
        
        total_score = min(1.0, coverage_score + length_bonus + phrase_bonus)
        return round(total_score, 2)
    
    def get_all_supported_personas(self):
        """Get list of all personas with dedicated generators"""
        return list(self.generators.keys())
    
    async def batch_generate_countermeasures(self, claims_and_interpretations):
        """Generate countermeasures for multiple claims efficiently"""
        all_countermeasures = {}
        
        for claim_data in claims_and_interpretations:
            claim = claim_data['claim']
            interpretations = claim_data['persona_interpretations']
            evidence = claim_data.get('evidence', 'No specific evidence provided')
            
            claim_countermeasures = await self.generate_targeted_countermeasures(
                claim, interpretations, evidence
            )
            
            all_countermeasures[claim] = claim_countermeasures
        
        return all_countermeasures

# Global instance
persona_targeted_generator = PersonaTargetedGenerator()
