"""Medical terminology and entities for health communications analysis"""

MEDICAL_ENTITIES = {
    'conditions': ['RSV', 'naloxone', 'COVID-19', 'influenza', 'diabetes', 'hypertension', 'asthma', 'arthritis'],
    'treatments': ['vaccination', 'medication', 'therapy', 'surgery', 'immunization', 'antibiotic', 'insulin'],
    'organizations': ['WHO', 'CDC', 'FDA', 'Cochrane', 'NIH', 'Mayo Clinic', 'WebMD'],
    'risk_phrases': ['always', 'never', 'guaranteed', '100% effective', 'completely safe', 'no side effects', 'instant cure'],
    'uncertainty_markers': ['usually', 'often', 'typically', 'most people', 'generally', 'may', 'might', 'could']
}

MEDICAL_SPECIALTIES = {
    'cardiology': ['heart', 'cardiac', 'cardiovascular', 'blood pressure', 'cholesterol'],
    'oncology': ['cancer', 'tumor', 'chemotherapy', 'radiation', 'metastasis'],
    'immunology': ['vaccine', 'immunity', 'allergic', 'autoimmune', 'antibody'],
    'infectious_disease': ['virus', 'bacteria', 'infection', 'contagious', 'outbreak'],
    'pediatrics': ['children', 'infant', 'adolescent', 'growth', 'development']
}

def is_medical_term(text: str) -> bool:
    """Check if text contains medical terminology"""
    text_lower = text.lower()
    for category, terms in MEDICAL_ENTITIES.items():
        for term in terms:
            if term.lower() in text_lower:
                return True
    return False

def extract_medical_entities(text: str) -> dict:
    """Extract medical entities from text"""
    text_lower = text.lower()
    found_entities = {}
    
    for category, terms in MEDICAL_ENTITIES.items():
        found_entities[category] = []
        for term in terms:
            if term.lower() in text_lower:
                found_entities[category].append(term)
    
    return {k: v for k, v in found_entities.items() if v}
