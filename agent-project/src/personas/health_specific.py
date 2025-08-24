"""Health-specific audience personas for targeted analysis"""

from .base_personas import AudiencePersona

# Health-specific personas for specialized risk assessment
HEALTH_SPECIFIC_PERSONAS = [
    AudiencePersona(
        name="VaccineHesitant",
        demographics="Adult, 30-50, some college, rural/suburban",
        health_literacy="medium",
        beliefs="Natural immunity preferred, distrust pharmaceutical industry",
        concerns="Long-term effects, rushed development, profit motives, religious exemptions"
    ),
    AudiencePersona(
        name="ChronicIllness",
        demographics="Adult, 40-70, managing chronic condition",
        health_literacy="high",
        beliefs="Experience-based knowledge, healthcare advocacy",
        concerns="Drug interactions, condition-specific effects, insurance coverage"
    ),
    AudiencePersona(
        name="HealthcareProfessional",
        demographics="Medical professional, 25-60",
        health_literacy="very high",
        beliefs="Evidence-based practice, professional responsibility",
        concerns="Patient safety, liability, clinical guidelines, resource allocation"
    ),
    AudiencePersona(
        name="SocialMediaUser",
        demographics="Young adult, 18-35, active online",
        health_literacy="variable",
        beliefs="Peer recommendations, influencer trust",
        concerns="Social proof, trending topics, shareable content, fear of missing out"
    ),
    AudiencePersona(
        name="NewParent",
        demographics="Adult, 25-40, first-time or new parent",
        health_literacy="medium to high",
        beliefs="Child safety priority, research everything",
        concerns="Infant safety, developmental impacts, conflicting advice, peer pressure"
    ),
    AudiencePersona(
        name="ElderlyCaregiver",
        demographics="Adult, 45-70, caring for elderly parent",
        health_literacy="medium",
        beliefs="Traditional medicine respect, family responsibility",
        concerns="Polypharmacy, cognitive decline, quality of life, healthcare costs"
    ),
    AudiencePersona(
        name="FitnessEnthusiast",
        demographics="Adult, 20-50, active lifestyle focus",
        health_literacy="medium",
        beliefs="Natural health, performance optimization",
        concerns="Performance impacts, supplement interactions, recovery time, body image"
    ),
    AudiencePersona(
        name="PregnantWoman",
        demographics="Female, 20-40, pregnant or planning pregnancy",
        health_literacy="high during pregnancy",
        beliefs="Extreme caution, evidence-based decisions",
        concerns="Fetal safety, breastfeeding impacts, maternal health, long-term effects"
    )
]

# Combined persona set including base and health-specific
ALL_PERSONAS = None  # Will be populated by get_all_personas()

def get_all_personas():
    """Get combined list of base and health-specific personas"""
    global ALL_PERSONAS
    if ALL_PERSONAS is None:
        from .base_personas import STANDARD_PERSONAS
        ALL_PERSONAS = STANDARD_PERSONAS + HEALTH_SPECIFIC_PERSONAS
    return ALL_PERSONAS

def get_personas_by_topic(topic: str):
    """Get relevant personas for specific health topic"""
    
    topic_lower = topic.lower()
    all_personas = get_all_personas()
    
    # Topic-specific persona mapping
    topic_mappings = {
        'vaccine': ['VaccineHesitant', 'NewParent', 'HealthcareProfessional', 'PregnantWoman'],
        'medication': ['ChronicIllness', 'ElderlyCaregiver', 'HealthcareProfessional', 'PregnantWoman'],
        'pregnancy': ['PregnantWoman', 'NewParent', 'HealthcareProfessional'],
        'elderly': ['ElderlyCaregiver', 'TrustingElder', 'HealthcareProfessional'],
        'children': ['NewParent', 'SkepticalParent', 'HealthcareProfessional'],
        'fitness': ['FitnessEnthusiast', 'BusyProfessional', 'SocialMediaUser'],
        'mental_health': ['HealthAnxious', 'SocialMediaUser', 'HealthcareProfessional'],
        'social_media': ['SocialMediaUser', 'HealthAnxious', 'VaccineHesitant']
    }
    
    # Find matching topics
    relevant_persona_names = set()
    for key, personas in topic_mappings.items():
        if key in topic_lower:
            relevant_persona_names.update(personas)
    
    # If no specific match, use default set
    if not relevant_persona_names:
        relevant_persona_names = {
            'SkepticalParent', 'HealthAnxious', 'TrustingElder', 
            'BusyProfessional', 'HealthcareProfessional'
        }
    
    # Return matching personas
    return [p for p in all_personas if p.name in relevant_persona_names]

def get_persona_by_name(name: str):
    """Get specific persona by name"""
    all_personas = get_all_personas()
    for persona in all_personas:
        if persona.name == name:
            return persona
    return None
