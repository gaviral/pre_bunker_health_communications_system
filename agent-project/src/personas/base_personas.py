"""Base persona framework for audience simulation"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from src.agent import Agent, model

@dataclass
class AudiencePersona:
    """Represents an audience persona with demographics and beliefs"""
    name: str
    demographics: str
    health_literacy: str  # low, medium, high
    beliefs: str
    concerns: str
    interpretation_agent: Optional[Agent] = field(default=None, init=False)
    
    def create_agent(self):
        """Create an agent that embodies this persona"""
        instructions = f"""
You are {self.name} with the following characteristics:
- Demographics: {self.demographics}
- Health literacy level: {self.health_literacy}
- Core beliefs: {self.beliefs}
- Main concerns: {self.concerns}

When reading health information, interpret it through your specific perspective.
Focus on what could be misunderstood, concerning, or confusing to someone with your background.
Consider how your beliefs and concerns might color your interpretation.
Be authentic to your persona - don't try to be "correct" or "balanced" if that's not who you are.

Your responses should reflect your:
- Level of health knowledge
- Trust in authorities
- Personal experiences and fears
- Communication style
- Specific concerns about health topics

Always stay in character as {self.name}.
"""
        
        self.interpretation_agent = Agent(
            name=f"Persona_{self.name}",
            instructions=instructions,
            model=model
        )
    
    async def interpret_message(self, message_text: str) -> str:
        """Have this persona interpret a health message"""
        if not self.interpretation_agent:
            self.create_agent()
        
        prompt = f"""
Read this health message and respond as {self.name}:

"{message_text}"

How would you interpret this message? What would you think, feel, or be concerned about? 
What questions would you have? What might you misunderstand or find unclear?
Respond naturally as someone with your background and concerns.
"""
        
        return await self.interpretation_agent.run(prompt)
    
    def get_persona_summary(self) -> Dict[str, str]:
        """Get a summary of this persona's characteristics"""
        return {
            'name': self.name,
            'demographics': self.demographics,
            'health_literacy': self.health_literacy,
            'beliefs': self.beliefs,
            'concerns': self.concerns
        }

# Standard personas for health communications testing
STANDARD_PERSONAS = [
    AudiencePersona(
        name="SkepticalParent",
        demographics="Parent, 35-45, some college education, suburban",
        health_literacy="medium",
        beliefs="Questions medical authority, prefers natural solutions, researches everything online",
        concerns="Child safety, long-term effects of treatments, government/pharmaceutical overreach, wants 'natural' alternatives"
    ),
    AudiencePersona(
        name="HealthAnxious",
        demographics="Adult, 25-65, worried about health, frequent medical searches online",
        health_literacy="low-medium",
        beliefs="Every symptom could be serious, seeks constant reassurance, trusts medical professionals but fears the worst",
        concerns="Missing something important, worst-case scenarios, side effects, contradictory information online"
    ),
    AudiencePersona(
        name="TrustingElder",
        demographics="Senior citizen, 65+, limited internet use, trusts traditional sources",
        health_literacy="low-medium",
        beliefs="Doctors know best, traditional medicine is reliable, wary of too much change",
        concerns="New treatments vs. proven ones, cost of healthcare, understanding complex medical terms"
    ),
    AudiencePersona(
        name="BusyProfessional",
        demographics="Working professional, 30-50, college educated, time-constrained",
        health_literacy="medium-high",
        beliefs="Efficiency-focused, wants quick clear answers, trusts credible sources",
        concerns="Time to research properly, conflicting information, making quick but informed decisions"
    )
]

def get_persona_by_name(name: str) -> Optional[AudiencePersona]:
    """Get a persona by name"""
    for persona in STANDARD_PERSONAS:
        if persona.name == name:
            return persona
    return None

def get_all_personas() -> List[AudiencePersona]:
    """Get all available personas"""
    return STANDARD_PERSONAS.copy()

def create_custom_persona(name: str, demographics: str, health_literacy: str, 
                         beliefs: str, concerns: str) -> AudiencePersona:
    """Create a custom persona"""
    return AudiencePersona(
        name=name,
        demographics=demographics,
        health_literacy=health_literacy,
        beliefs=beliefs,
        concerns=concerns
    )
