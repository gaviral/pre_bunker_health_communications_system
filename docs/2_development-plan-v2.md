# Agent Development Plan v2.0: PRE-BUNKER Health Communications System

**Target**: Multi-agent "wind-tunnel" for health communications that simulates audience reactions and prevents misinformation

**Context from v1.0**: Built complete OpenAI Agent SDK system with LLM integration (phi4-mini), tool system, multi-agent orchestration, error handling, and tracing. All foundational components working and tested.

**v2.0 MVP Goal**: Implement the PRE-BUNKER pipeline with 5 core components: Audience Simulator, Claim Extractor, Evidence Gatekeeper, Countermeasure Studio, and Ops Orchestrator.

---

## 🔧 CRITICAL SETUP INFORMATION - READ FIRST

### Environment & Technical Context
- **Working Directory**: `/Users/aviralgarg/code/agent/agent-project/` for all code execution
- **Python Version**: 3.13.7 (already pinned with uv)
- **Package Manager**: Use `uv` for all dependencies: `uv add package-name`
- **Python Execution**: Always use `uv run python` for script execution
- **LLM Setup**: 
  ```bash
  export OPENAI_API_KEY="sk-dummy-for-local"
  # Ensure Ollama is running: ollama run phi4-mini
  ```
- **Git Status**: Clean history with v1.0 complete, ready for v2.0 implementation

### Critical v1.0 Architecture to Leverage
- **Agent Pattern**: `async def run(message)` with integrated tracing and error handling
- **Tool System**: `@function_tool` decorator with automatic schema generation in `src/tools.py`
- **Error Handling**: Comprehensive logging in `src/error_handler.py` with graceful failures
- **Orchestration**: Runner class in `src/runner.py` for sync/async coordination
- **File Structure**: All code in `src/` directory with proper module separation

### Health Domain Critical Requirements
- **Medical Accuracy**: Absolutist language ("always", "never", "100%", "guaranteed") = HIGH RISK
- **Authority Sources with Trust Scores**: 
  - WHO: 0.95 (global health, disease outbreaks, guidelines)
  - CDC: 0.95 (US health policy, disease surveillance, prevention)  
  - Cochrane: 0.90 (systematic reviews, evidence synthesis)
  - FDA: 0.90 (drug approval, medical devices, safety)
  - PubMed: 0.85 (peer-reviewed research)
- **Risk Patterns**: Missing evidence, ambiguous terms, emotional appeals, conspiracy theories
- **Core Persona Types**: Vaccine-hesitant, health-anxious, chronic illness patients, healthcare professionals

### Implementation Success Indicators
- ✅ Each version adds ONE testable component that works independently
- ✅ Health claims properly extracted with confidence scores
- ✅ Different personas generate varied interpretations of same text
- ✅ Evidence validation links claims to authoritative sources  
- ✅ Countermeasures address specific persona concerns with appropriate tone
- ✅ Full pipeline processes health messages end-to-end with human review queue

### Common Pitfalls to Avoid
- ❌ **Don't** make up medical facts - use the provided simulated evidence database
- ❌ **Don't** skip testing between versions - each must work before proceeding
- ❌ **Don't** ignore ultra-minimal token requirement from v1.0 experience
- ❌ **Don't** reinvent v1.0 components - build on existing Agent/tools/runner infrastructure
- ✅ **Do** follow exact version sequence (v1.1 → v1.2 → ... → v2.0)
- ✅ **Do** commit each version with detailed git messages
- ✅ **Do** make intelligent assumptions when stuck and continue to next version

### Testing Strategy for Each Version
1. **Unit Test**: Component works in isolation
2. **Integration Test**: Component works with existing v1.0 infrastructure  
3. **Health Domain Test**: Handles medical content appropriately
4. **Error Test**: Fails gracefully with useful error messages
5. **Commit**: Document what works and any limitations

**Test Execution Protocol**: All test runs MUST log complete output to files using:
```bash
uv run python test_vX_Y.py 2>&1 | tee vX_Y_detailed_log.txt
```
This captures both stdout and stderr for comprehensive debugging and audit trails.

### Final v2.0 Production Deliverable
RESTful API that accepts health communication text and returns:
- **Risk Assessment**: Overall score + breakdown by risk factors
- **Persona Reactions**: How different audiences interpret the message
- **Evidence Validation**: Claims matched to trusted sources with confidence
- **Countermeasures**: Prebunks and clarifications tailored to persona concerns
- **Review Queue**: Human oversight workflow for high-risk content
- **Learning System**: Improves scoring based on reviewer feedback

---

## Development Philosophy for v2.0

### Ultra-Granular Approach
Each version adds ONE minimal, testable component. If implementation becomes complex, break into sub-versions (e.g., v1.1.1, v1.1.2).

### Self-Sufficiency Guidelines
- **Complete Code**: Every version includes full working implementation
- **Domain Knowledge**: Includes medical/health informatics context
- **When Stuck**: Move to next version, document blockers, make intelligent assumptions
- **No External Dependencies**: All necessary information included

### Key Learnings from v1.0 Development
- **Environment**: Use Python 3.13.7 with uv package manager
- **LLM**: phi4-mini via Ollama localhost:11434
- **Architecture**: Agent class with async run(), tool decorator system, Runner orchestration
- **Error Handling**: Comprehensive logging + graceful failures
- **Testing**: Verify each component works before proceeding

## Core Architecture Context

### Foundation from v1.0
```
agent-project/src/
├── agent.py          # Core Agent class + LLM integration
├── tools.py          # @function_tool decorator system  
├── agents.py         # Specialized agent instances
├── runner.py         # Workflow orchestration
├── error_handler.py  # Logging + error management
└── tracing.py        # Execution monitoring
```

### v2.0 Extensions Needed
```
agent-project/src/
├── personas/         # Audience simulation agents
├── claims/          # Claim extraction and risk scoring
├── evidence/        # Source validation and citation
├── countermeasures/ # Prebunk generation
├── orchestration/   # Review and testing pipeline
└── health_kb/       # Health domain knowledge base
```

---

## Version Plan: v1.1 - v2.0

## v1.1: Health Domain Setup
**What**: Health communications domain knowledge and data structures  
**How**: Create health-specific data models, terminology, and basic validation  
**Check**: Health claim types identified, basic medical terms recognized

**Implementation**:
```python
# src/health_kb/medical_terms.py
MEDICAL_ENTITIES = {
    'conditions': ['RSV', 'naloxone', 'COVID-19', 'influenza'],
    'treatments': ['vaccination', 'medication', 'therapy'],
    'organizations': ['WHO', 'CDC', 'FDA', 'Cochrane'],
    'risk_phrases': ['always', 'never', 'guaranteed', '100% effective']
}

# src/health_kb/claim_types.py
class HealthClaim:
    def __init__(self, text, claim_type, confidence):
        self.text = text
        self.claim_type = claim_type  # efficacy, safety, dosage, timing
        self.confidence = confidence
        self.risk_level = 'unknown'
```

**Domain Context**: Health communications require extreme precision. Claims about medical efficacy, safety, and dosing carry high misinterpretation risk.

**Development Status**: 

---

## v1.2: Basic Claim Extraction
**What**: Extract explicit health claims from text using NLP  
**How**: Pattern matching + LLM-based claim identification  
**Check**: Identifies claims like "vaccines are safe" or "naloxone reverses overdoses"

**Implementation**:
```python
# src/claims/extractor.py
@function_tool
def extract_health_claims(text: str) -> str:
    """Extract health claims from communication text"""
    # Pattern-based extraction
    claim_patterns = [
        r'(\w+) is (safe|effective|dangerous)',
        r'(\w+) prevents (\w+)',
        r'(\w+) causes (\w+)',
        r'you should (always|never) (\w+)'
    ]
    
    # LLM-based extraction for complex claims
    claims_agent = Agent(
        name="ClaimsExtractor",
        instructions="Extract factual health claims from text. Format as: CLAIM: [claim text]",
        model=model
    )
    
    result = await claims_agent.run(f"Extract health claims from: {text}")
    return result
```

**Dependencies**: spacy or nltk for NLP, extend existing Agent system

**Development Status**: 

---

## v1.3: Risk Scoring Framework
**What**: Score claims for misinterpretation potential  
**How**: Rule-based scoring + confidence metrics  
**Check**: High-risk phrases flagged, confidence scores assigned

**Implementation**:
```python
# src/claims/risk_scorer.py
class RiskScorer:
    def __init__(self):
        self.high_risk_patterns = [
            'always effective', 'never fails', '100%', 'guaranteed',
            'completely safe', 'no side effects', 'instant cure'
        ]
        self.moderate_risk_patterns = [
            'usually', 'often', 'typically', 'most people'
        ]
    
    def score_claim(self, claim_text):
        risk_score = 0
        
        # Pattern-based scoring
        for pattern in self.high_risk_patterns:
            if pattern.lower() in claim_text.lower():
                risk_score += 0.8
                
        # Ambiguity detection
        ambiguous_terms = ['it', 'this', 'that', 'they']
        ambiguity_count = sum(1 for term in ambiguous_terms if term in claim_text.lower())
        risk_score += ambiguity_count * 0.1
        
        return min(risk_score, 1.0)
```

**Domain Context**: Medical misinformation often uses absolutist language ("always", "never") that oversimplifies complex health topics.

**Development Status**: 

---

## v1.4: Basic Persona Framework
**What**: Define audience personas with demographics and beliefs  
**How**: Structured persona data + simulation prompts  
**Check**: Personas generate different interpretations of same text

**Implementation**:
```python
# src/personas/base_personas.py
class AudiencePersona:
    def __init__(self, name, demographics, health_literacy, beliefs, concerns):
        self.name = name
        self.demographics = demographics
        self.health_literacy = health_literacy  # low, medium, high
        self.beliefs = beliefs
        self.concerns = concerns
        self.interpretation_agent = None
    
    def create_agent(self):
        instructions = f"""
You are {self.name} with {self.demographics}.
Health literacy: {self.health_literacy}
Key beliefs: {self.beliefs}
Main concerns: {self.concerns}

When reading health information, interpret it through your perspective.
Focus on what could be misunderstood or concerning to someone like you.
"""
        self.interpretation_agent = Agent(
            name=f"Persona_{self.name}",
            instructions=instructions,
            model=model
        )

# Default personas for health communications
STANDARD_PERSONAS = [
    AudiencePersona(
        name="SkepticalParent",
        demographics="Parent, 35-45, some college",
        health_literacy="medium",
        beliefs="Questions authority, wants natural solutions",
        concerns="Child safety, long-term effects, government overreach"
    ),
    AudiencePersona(
        name="HealthAnxious",
        demographics="Adult, 25-65, worried about health",
        health_literacy="low",
        beliefs="Every symptom is serious, seeks reassurance",
        concerns="Missing something important, worst-case scenarios"
    )
]
```

**Development Status**: 

---

## v1.5: Persona Interpretation Engine
**What**: Personas interpret health communications and flag concerns  
**How**: Each persona agent processes text and returns interpretations  
**Check**: Different personas produce different readings of same message

**Implementation**:
```python
# src/personas/interpreter.py
class PersonaInterpreter:
    def __init__(self, personas):
        self.personas = personas
        
    async def interpret_message(self, message_text):
        interpretations = []
        
        for persona in self.personas:
            if not persona.interpretation_agent:
                persona.create_agent()
                
            response = await persona.interpretation_agent.run(
                f"How would you interpret this health message? What concerns or questions would you have?\n\nMessage: {message_text}"
            )
            
            interpretations.append({
                'persona': persona.name,
                'interpretation': response,
                'potential_misreading': self.extract_concerns(response)
            })
            
        return interpretations
    
    def extract_concerns(self, interpretation_text):
        # Extract specific concerns or misreadings
        concern_keywords = ['worried', 'scared', 'confused', 'unclear', 'dangerous']
        concerns = []
        for keyword in concern_keywords:
            if keyword in interpretation_text.lower():
                concerns.append(keyword)
        return concerns
```

**Development Status**: 

---

## v1.6: Evidence Source Framework
**What**: Define trusted health information sources  
**How**: Curated source database + authority scoring  
**Check**: Sources ranked by trustworthiness, search capability works

**Implementation**:
```python
# src/evidence/sources.py
class EvidenceSource:
    def __init__(self, name, url_pattern, authority_score, specialties):
        self.name = name
        self.url_pattern = url_pattern
        self.authority_score = authority_score  # 0-1
        self.specialties = specialties
        
TRUSTED_SOURCES = [
    EvidenceSource("WHO", "who.int", 0.95, ["global health", "disease outbreaks", "guidelines"]),
    EvidenceSource("CDC", "cdc.gov", 0.95, ["US health policy", "disease surveillance", "prevention"]),
    EvidenceSource("Cochrane", "cochranelibrary.com", 0.90, ["systematic reviews", "evidence synthesis"]),
    EvidenceSource("FDA", "fda.gov", 0.90, ["drug approval", "medical devices", "safety"]),
    EvidenceSource("PubMed", "pubmed.ncbi.nlm.nih.gov", 0.85, ["peer-reviewed research"]),
    EvidenceSource("Mayo Clinic", "mayoclinic.org", 0.80, ["patient education", "symptoms"])
]

class EvidenceSearcher:
    def __init__(self, sources):
        self.sources = sources
        
    def find_supporting_evidence(self, claim_text):
        # Simulate evidence search (in real implementation, would use APIs)
        relevant_sources = []
        for source in self.sources:
            if any(specialty in claim_text.lower() for specialty in source.specialties):
                relevant_sources.append(source)
        return relevant_sources
```

**Domain Context**: Health information authority is critical. WHO/CDC carry highest trust, peer-reviewed sources are essential.

**Development Status**: 

---

## v1.7: Basic Evidence Validation
**What**: Match claims to evidence sources and validate consistency  
**How**: Search simulation + consistency checking  
**Check**: Claims linked to sources, contradictions flagged

**Implementation**:
```python
# src/evidence/validator.py
class EvidenceValidator:
    def __init__(self, searcher):
        self.searcher = searcher
        self.validation_agent = Agent(
            name="EvidenceValidator",
            instructions="Check if health claims are supported by evidence. Report consistency level.",
            model=model
        )
    
    async def validate_claim(self, claim_text):
        # Find relevant sources
        sources = self.searcher.find_supporting_evidence(claim_text)
        
        # Simulate evidence check (real implementation would query actual APIs)
        validation_prompt = f"""
        Claim: {claim_text}
        Available sources: {[s.name for s in sources]}
        
        Assess:
        1. Is this claim supported by evidence?
        2. Any contradictions or nuances missing?
        3. What additional context is needed?
        """
        
        validation_result = await self.validation_agent.run(validation_prompt)
        
        return {
            'claim': claim_text,
            'sources': sources,
            'validation': validation_result,
            'confidence': self.calculate_confidence(sources)
        }
    
    def calculate_confidence(self, sources):
        if not sources:
            return 0.0
        return sum(s.authority_score for s in sources) / len(sources)
```

**Development Status**: 

---

## v1.8: Countermeasure Generation Framework
**What**: Generate prebunks and clarifications for risky claims  
**How**: Template-based + LLM-generated countermeasures  
**Check**: Prebunks address specific misinterpretations

**Implementation**:
```python
# src/countermeasures/generator.py
class CountermeasureGenerator:
    def __init__(self):
        self.prebunk_agent = Agent(
            name="PrebunkGenerator",
            instructions="Generate clear, evidence-based prebunks for health misinformation risks.",
            model=model
        )
        
        self.templates = {
            'absolutist_claim': "While {treatment} is {generally_effective}, individual results may vary. Consult your healthcare provider about your specific situation.",
            'safety_concern': "{treatment} has been extensively tested and is considered safe for most people. Common side effects include {common_effects}. Serious side effects are rare.",
            'conspiracy_theory': "This recommendation comes from {authority_source} based on {evidence_type}. The decision-making process is transparent and regularly reviewed."
        }
    
    async def generate_countermeasures(self, claim, persona_concerns, evidence):
        countermeasures = []
        
        # Template-based prebunks
        for concern_type, template in self.templates.items():
            if self.matches_concern_type(persona_concerns, concern_type):
                prebunk = self.fill_template(template, claim, evidence)
                countermeasures.append({
                    'type': 'template_prebunk',
                    'concern_type': concern_type,
                    'text': prebunk
                })
        
        # LLM-generated custom prebunks
        custom_prompt = f"""
        Claim: {claim}
        Audience concerns: {persona_concerns}
        Evidence: {evidence}
        
        Generate a clear, brief prebunk that addresses the specific concerns while staying accurate to the evidence.
        """
        
        custom_prebunk = await self.prebunk_agent.run(custom_prompt)
        countermeasures.append({
            'type': 'custom_prebunk',
            'text': custom_prebunk
        })
        
        return countermeasures
```

**Development Status**: 

---

## v1.9: Integration Pipeline
**What**: Connect all components in end-to-end workflow  
**How**: Orchestrate claim extraction → risk scoring → evidence validation → countermeasures  
**Check**: Full pipeline processes health message and outputs risk report

**Implementation**:
```python
# src/orchestration/pipeline.py
class PrebunkerPipeline:
    def __init__(self):
        self.claim_extractor = ClaimExtractor()
        self.risk_scorer = RiskScorer()
        self.persona_interpreter = PersonaInterpreter(STANDARD_PERSONAS)
        self.evidence_validator = EvidenceValidator(EvidenceSearcher(TRUSTED_SOURCES))
        self.countermeasure_generator = CountermeasureGenerator()
    
    async def process_message(self, message_text):
        pipeline_result = {
            'original_message': message_text,
            'claims': [],
            'persona_interpretations': [],
            'evidence_validations': [],
            'countermeasures': [],
            'risk_report': {}
        }
        
        # Step 1: Extract claims
        claims = await self.claim_extractor.extract_health_claims(message_text)
        pipeline_result['claims'] = claims
        
        # Step 2: Score risks
        for claim in claims:
            risk_score = self.risk_scorer.score_claim(claim)
            
        # Step 3: Persona interpretations
        interpretations = await self.persona_interpreter.interpret_message(message_text)
        pipeline_result['persona_interpretations'] = interpretations
        
        # Step 4: Evidence validation
        for claim in claims:
            validation = await self.evidence_validator.validate_claim(claim)
            pipeline_result['evidence_validations'].append(validation)
        
        # Step 5: Generate countermeasures
        for claim in claims:
            if self.is_high_risk(claim):  # Risk score > threshold
                countermeasures = await self.countermeasure_generator.generate_countermeasures(
                    claim, interpretations, pipeline_result['evidence_validations']
                )
                pipeline_result['countermeasures'].extend(countermeasures)
        
        # Step 6: Compile risk report
        pipeline_result['risk_report'] = self.compile_risk_report(pipeline_result)
        
        return pipeline_result
```

**Development Status**: 

---

## v1.10: Risk Report Generation
**What**: Compile findings into actionable risk assessment  
**How**: Structured report with scores, recommendations, and priorities  
**Check**: Clear risk report identifies top concerns and suggested fixes

**Implementation**:
```python
# src/orchestration/risk_reporter.py
class RiskReporter:
    def __init__(self):
        self.report_agent = Agent(
            name="RiskReporter",
            instructions="Compile health communication risk assessment into clear, actionable report.",
            model=model
        )
    
    def compile_risk_report(self, pipeline_result):
        # Calculate overall risk metrics
        high_risk_claims = [c for c in pipeline_result['claims'] if self.is_high_risk(c)]
        total_risk_score = sum(self.get_risk_score(c) for c in pipeline_result['claims'])
        
        # Identify top concerns
        persona_concerns = []
        for interpretation in pipeline_result['persona_interpretations']:
            persona_concerns.extend(interpretation['potential_misreading'])
        
        concern_frequency = {}
        for concern in persona_concerns:
            concern_frequency[concern] = concern_frequency.get(concern, 0) + 1
        
        top_concerns = sorted(concern_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate recommendations
        recommendations = []
        for claim in high_risk_claims:
            recommendations.append(f"HIGH RISK: '{claim}' - Add nuance/caveats")
        
        if not pipeline_result['evidence_validations']:
            recommendations.append("MISSING: No evidence citations found - Add authoritative sources")
        
        risk_report = {
            'overall_risk_score': total_risk_score / len(pipeline_result['claims']) if pipeline_result['claims'] else 0,
            'high_risk_claim_count': len(high_risk_claims),
            'top_concerns': top_concerns,
            'recommendations': recommendations,
            'countermeasures_generated': len(pipeline_result['countermeasures']),
            'evidence_coverage': len(pipeline_result['evidence_validations']) / len(pipeline_result['claims']) if pipeline_result['claims'] else 0
        }
        
        return risk_report
```

**Development Status**: 

---

## v1.11: Basic Web Interface
**What**: Simple web interface to input messages and view results  
**How**: FastAPI + HTML forms for testing  
**Check**: Can submit health message and see full risk report

**Implementation**:
```python
# src/web/app.py
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_message(request: Request, message: str = Form(...)):
    pipeline = PrebunkerPipeline()
    result = await pipeline.process_message(message)
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "message": message,
        "result": result
    })

# templates/index.html
"""
<!DOCTYPE html>
<html>
<head><title>PRE-BUNKER Health Communications</title></head>
<body>
    <h1>Health Message Risk Assessment</h1>
    <form action="/analyze" method="post">
        <textarea name="message" rows="5" cols="50" placeholder="Enter health communication message..."></textarea><br>
        <button type="submit">Analyze</button>
    </form>
</body>
</html>
"""

# templates/results.html - Shows full risk report with claims, persona reactions, countermeasures
```

**Dependencies**: fastapi, jinja2, uvicorn

**Development Status**: 

---

## v1.12: Persona Refinement
**What**: Expand persona set with specific health topics  
**How**: Add domain-specific personas (vaccine hesitant, chronic illness, etc.)  
**Check**: More diverse interpretations captured

**Implementation**:
```python
# src/personas/health_specific.py
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
    )
]
```

**Development Status**: 

---

## v1.13: Advanced Claim Detection
**What**: Detect implicit claims and context-dependent meanings  
**How**: Enhanced NLP with context analysis and implication detection  
**Check**: Catches subtle implications like "natural is better"

**Implementation**:
```python
# src/claims/advanced_extractor.py
class AdvancedClaimExtractor:
    def __init__(self):
        self.implicit_claim_agent = Agent(
            name="ImplicitClaimDetector",
            instructions="Detect implicit health claims, assumptions, and implications in text.",
            model=model
        )
        
        self.implicit_patterns = {
            'natural_fallacy': ['natural', 'organic', 'chemical-free', 'traditional'],
            'appeal_to_authority': ['doctors recommend', 'studies show', 'experts say'],
            'fear_uncertainty_doubt': ['dangerous chemicals', 'unknown effects', 'risky'],
            'false_dichotomy': ['safe alternative', 'natural vs synthetic', 'choose wisely']
        }
    
    async def extract_implicit_claims(self, text):
        explicit_claims = await self.extract_health_claims(text)  # From v1.2
        
        implicit_prompt = f"""
        Analyze this health communication for implicit claims or assumptions:
        
        Text: {text}
        
        Look for:
        1. Unstated assumptions (e.g., "natural is safer")
        2. Implied comparisons (e.g., "better choice" implies alternatives are worse)
        3. Emotional appeals that suggest factual claims
        4. Context that changes meaning of neutral statements
        
        List each implicit claim clearly.
        """
        
        implicit_result = await self.implicit_claim_agent.run(implicit_prompt)
        
        # Pattern-based detection
        pattern_matches = []
        for pattern_type, keywords in self.implicit_patterns.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    pattern_matches.append({
                        'pattern': pattern_type,
                        'keyword': keyword,
                        'implied_claim': self.get_implied_claim(pattern_type, keyword)
                    })
        
        return {
            'explicit_claims': explicit_claims,
            'implicit_claims': implicit_result,
            'pattern_matches': pattern_matches
        }
    
    def get_implied_claim(self, pattern_type, keyword):
        implications = {
            'natural_fallacy': f"'{keyword}' products are inherently safer/better",
            'appeal_to_authority': f"Authority endorsement proves effectiveness",
            'fear_uncertainty_doubt': f"Current treatments/approaches are dangerous",
            'false_dichotomy': f"Only two options exist (this vs dangerous alternative)"
        }
        return implications.get(pattern_type, "Unspecified implication")
```

**Development Status**: 

---

## v1.14: Evidence API Integration (Simulated)
**What**: Integrate with health information APIs for real evidence lookup  
**How**: Create simulated API responses for WHO, CDC, PubMed data  
**Check**: Claims matched with actual evidence snippets

**Implementation**:
```python
# src/evidence/api_integration.py
class HealthAPISimulator:
    """Simulates API responses from health organizations"""
    
    def __init__(self):
        # Simulated evidence database
        self.evidence_db = {
            'vaccination': {
                'source': 'WHO',
                'url': 'https://www.who.int/news-room/feature-stories/detail/the-race-for-a-covid-19-vaccine-explained',
                'snippet': 'Vaccines undergo rigorous safety testing before approval and continue to be monitored.',
                'authority_score': 0.95
            },
            'naloxone': {
                'source': 'CDC',
                'url': 'https://www.cdc.gov/stopoverdose/naloxone/index.html',
                'snippet': 'Naloxone is a life-saving medication that can reverse an opioid overdose.',
                'authority_score': 0.95
            },
            'rsv': {
                'source': 'CDC',
                'url': 'https://www.cdc.gov/rsv/index.html',
                'snippet': 'RSV is a common respiratory virus that usually causes mild, cold-like symptoms.',
                'authority_score': 0.95
            }
        }
    
    async def search_evidence(self, claim_keywords):
        """Simulate API search for evidence"""
        matches = []
        for keyword in claim_keywords:
            for topic, evidence in self.evidence_db.items():
                if keyword.lower() in topic.lower():
                    matches.append(evidence)
        
        return matches

class EnhancedEvidenceValidator:
    def __init__(self):
        self.api_simulator = HealthAPISimulator()
        self.evidence_analysis_agent = Agent(
            name="EvidenceAnalyzer",
            instructions="Analyze whether evidence supports, contradicts, or is neutral to health claims.",
            model=model
        )
    
    async def validate_with_api(self, claim_text):
        # Extract keywords from claim
        keywords = self.extract_keywords(claim_text)
        
        # Search for evidence
        evidence_matches = await self.api_simulator.search_evidence(keywords)
        
        if not evidence_matches:
            return {
                'claim': claim_text,
                'evidence_found': False,
                'validation_status': 'insufficient_evidence',
                'recommendations': ['Add authoritative citations', 'Qualify with "according to available evidence"']
            }
        
        # Analyze evidence vs claim
        analysis_prompt = f"""
        Claim: {claim_text}
        Evidence found: {evidence_matches}
        
        Analysis:
        1. Does evidence support this claim? (Yes/No/Partial)
        2. Any contradictions or missing nuances?
        3. What qualifications should be added?
        """
        
        analysis = await self.evidence_analysis_agent.run(analysis_prompt)
        
        return {
            'claim': claim_text,
            'evidence_found': True,
            'evidence_sources': evidence_matches,
            'analysis': analysis,
            'validation_status': self.determine_status(analysis)
        }
```

**Development Status**: 

---

## v1.15: Countermeasure Optimization
**What**: Generate targeted countermeasures for specific persona concerns  
**How**: Persona-specific prebunk generation with tone matching  
**Check**: Different countermeasures for different audience concerns

**Implementation**:
```python
# src/countermeasures/persona_targeted.py
class PersonaTargetedGenerator:
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
    
    async def generate_targeted_countermeasures(self, claim, persona_interpretations, evidence):
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
                    'format': self.get_recommended_format(persona_name)
                }
        
        return countermeasures
    
    def get_recommended_tone(self, persona_name):
        tone_map = {
            'VaccineHesitant': 'respectful, non-judgmental, evidence-focused',
            'HealthAnxious': 'reassuring, calm, specific',
            'SocialMediaUser': 'engaging, shareable, visual-friendly',
            'ChronicIllness': 'detailed, nuanced, practical'
        }
        return tone_map.get(persona_name, 'professional, clear')
    
    def get_recommended_format(self, persona_name):
        format_map = {
            'VaccineHesitant': 'FAQ format, bullet points',
            'HealthAnxious': 'step-by-step guidance',
            'SocialMediaUser': 'infographic-ready, soundbites',
            'ChronicIllness': 'detailed explanation with caveats'
        }
        return format_map.get(persona_name, 'structured paragraphs')
```

**Development Status**: 

---

## v1.16: A/B Testing Framework
**What**: Framework for testing different message versions  
**How**: Compare original vs prebunked versions with simulated audience reactions  
**Check**: Can generate multiple message variants and score effectiveness

**Implementation**:
```python
# src/orchestration/ab_testing.py
class MessageVariantGenerator:
    def __init__(self):
        self.variant_agent = Agent(
            name="VariantGenerator",
            instructions="Create alternative versions of health messages with different approaches to clarity and risk mitigation.",
            model=model
        )
    
    async def generate_variants(self, original_message, risk_report, countermeasures):
        variants = [{'version': 'original', 'text': original_message}]
        
        # Generate prebunked version
        prebunk_prompt = f"""
        Original message: {original_message}
        Risk issues: {risk_report['recommendations']}
        Countermeasures: {countermeasures}
        
        Create an improved version that:
        1. Maintains the core message
        2. Addresses identified risks
        3. Includes appropriate caveats
        4. Adds evidence citations
        """
        
        prebunked_version = await self.variant_agent.run(prebunk_prompt)
        variants.append({'version': 'prebunked', 'text': prebunked_version})
        
        # Generate conservative version (very cautious)
        conservative_prompt = f"""
        Create a very conservative, heavily qualified version of: {original_message}
        Include maximum caveats, uncertainties, and "consult your doctor" advice.
        """
        
        conservative_version = await self.variant_agent.run(conservative_prompt)
        variants.append({'version': 'conservative', 'text': conservative_version})
        
        return variants

class ABTestSimulator:
    def __init__(self, personas):
        self.personas = personas
        self.persona_interpreter = PersonaInterpreter(personas)
    
    async def test_variants(self, variants):
        test_results = {}
        
        for variant in variants:
            version_name = variant['version']
            message_text = variant['text']
            
            # Test with all personas
            interpretations = await self.persona_interpreter.interpret_message(message_text)
            
            # Score this variant
            concern_count = sum(len(interp['potential_misreading']) for interp in interpretations)
            clarity_score = await self.score_clarity(message_text)
            
            test_results[version_name] = {
                'message': message_text,
                'total_concerns': concern_count,
                'clarity_score': clarity_score,
                'persona_reactions': interpretations,
                'overall_score': self.calculate_overall_score(concern_count, clarity_score)
            }
        
        return test_results
    
    async def score_clarity(self, message_text):
        clarity_agent = Agent(
            name="ClarityScorer",
            instructions="Score message clarity on scale 0-1. Consider readability, ambiguity, and completeness.",
            model=model
        )
        
        clarity_prompt = f"""
        Score this health message for clarity (0.0 to 1.0):
        Message: {message_text}
        
        Consider:
        - Is the main point clear?
        - Are there ambiguous terms?
        - Is the language appropriate for general audience?
        - Are important caveats included?
        
        Return just the score as a decimal.
        """
        
        score_response = await clarity_agent.run(clarity_prompt)
        
        # Extract numeric score (basic parsing)
        try:
            score = float(score_response.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5  # Default if parsing fails
```

**Development Status**: 

---

## v1.17: Performance Metrics
**What**: Implement Misinterpretability@k and other evaluation metrics  
**How**: Quantitative scoring of message improvement  
**Check**: Numerical scores show message quality improvement

**Implementation**:
```python
# src/metrics/evaluation.py
class HealthCommMetrics:
    def __init__(self):
        self.metrics = {}
    
    def misinterpretability_at_k(self, persona_reactions, k=3):
        """
        Misinterpretability@k: Proportion of top-k personas that misinterpret the message
        """
        total_personas = len(persona_reactions)
        if total_personas == 0:
            return 0.0
        
        k = min(k, total_personas)
        
        # Sort personas by severity of misinterpretation
        sorted_reactions = sorted(
            persona_reactions, 
            key=lambda x: len(x['potential_misreading']), 
            reverse=True
        )
        
        # Count how many of top-k have misinterpretations
        misinterpreted_count = 0
        for i in range(k):
            if len(sorted_reactions[i]['potential_misreading']) > 0:
                misinterpreted_count += 1
        
        return misinterpreted_count / k
    
    def evidence_coverage_score(self, claims, evidence_validations):
        """Percentage of claims that have evidence support"""
        if not claims:
            return 1.0
        
        supported_claims = sum(1 for ev in evidence_validations if ev['evidence_found'])
        return supported_claims / len(claims)
    
    def risk_reduction_score(self, original_risk, improved_risk):
        """Improvement in risk score from original to improved version"""
        if original_risk == 0:
            return 0.0
        return max(0.0, (original_risk - improved_risk) / original_risk)
    
    def clarity_improvement_score(self, original_clarity, improved_clarity):
        """Improvement in clarity score"""
        return max(0.0, improved_clarity - original_clarity)
    
    def generate_evaluation_report(self, original_result, improved_result):
        """Generate comprehensive evaluation comparing original vs improved"""
        
        metrics = {
            'misinterpretability_at_3_original': self.misinterpretability_at_k(
                original_result['persona_interpretations'], 3
            ),
            'misinterpretability_at_3_improved': self.misinterpretability_at_k(
                improved_result['persona_interpretations'], 3
            ),
            'evidence_coverage_original': self.evidence_coverage_score(
                original_result['claims'], original_result['evidence_validations']
            ),
            'evidence_coverage_improved': self.evidence_coverage_score(
                improved_result['claims'], improved_result['evidence_validations']
            ),
            'total_risk_score_original': original_result['risk_report']['overall_risk_score'],
            'total_risk_score_improved': improved_result['risk_report']['overall_risk_score']
        }
        
        # Calculate improvement metrics
        metrics['misinterpretability_reduction'] = max(0.0, 
            metrics['misinterpretability_at_3_original'] - metrics['misinterpretability_at_3_improved']
        )
        
        metrics['evidence_improvement'] = max(0.0,
            metrics['evidence_coverage_improved'] - metrics['evidence_coverage_original']
        )
        
        metrics['risk_reduction'] = self.risk_reduction_score(
            metrics['total_risk_score_original'],
            metrics['total_risk_score_improved']
        )
        
        return metrics
```

**Development Status**: 

---

## v1.18: Ops Dashboard
**What**: Management interface for reviewing and approving messages  
**How**: Web dashboard with approval workflow  
**Check**: Can review flagged messages, approve/reject with rationale

**Implementation**:
```python
# src/web/ops_dashboard.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
from datetime import datetime

security = HTTPBasic()

class MessageReviewQueue:
    def __init__(self):
        self.queue = []
        self.reviewed = []
        
    def add_to_queue(self, message_id, original_text, analysis_result, priority='medium'):
        queue_item = {
            'id': message_id,
            'original_text': original_text,
            'analysis': analysis_result,
            'priority': priority,
            'submitted_at': datetime.now().isoformat(),
            'status': 'pending_review',
            'reviewer': None,
            'review_notes': None
        }
        self.queue.append(queue_item)
        return message_id
    
    def get_pending_items(self):
        return [item for item in self.queue if item['status'] == 'pending_review']
    
    def approve_message(self, message_id, reviewer, notes, approved_version):
        for item in self.queue:
            if item['id'] == message_id:
                item['status'] = 'approved'
                item['reviewer'] = reviewer
                item['review_notes'] = notes
                item['approved_version'] = approved_version
                item['reviewed_at'] = datetime.now().isoformat()
                self.reviewed.append(item)
                return True
        return False

review_queue = MessageReviewQueue()

@app.get("/ops/dashboard")
async def ops_dashboard(credentials: HTTPBasicCredentials = Depends(security)):
    # Simple auth check
    if credentials.username != "admin" or credentials.password != "admin":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    pending_items = review_queue.get_pending_items()
    
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>PRE-BUNKER Ops Dashboard</title></head>
    <body>
        <h1>Message Review Queue</h1>
        <p>Pending Review: {len(pending_items)}</p>
        
        {generate_review_items_html(pending_items)}
        
        <h2>Submit New Message for Review</h2>
        <form action="/ops/submit" method="post">
            <textarea name="message" rows="5" cols="80" placeholder="Health message to review..."></textarea><br>
            <select name="priority">
                <option value="low">Low Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="high">High Priority</option>
            </select><br>
            <button type="submit">Submit for Review</button>
        </form>
    </body>
    </html>
    """
    
    return HTMLResponse(dashboard_html)

@app.post("/ops/submit")
async def submit_for_review(message: str = Form(...), priority: str = Form(...)):
    # Process message through pipeline
    pipeline = PrebunkerPipeline()
    analysis_result = await pipeline.process_message(message)
    
    # Add to review queue
    message_id = f"msg_{int(datetime.now().timestamp())}"
    review_queue.add_to_queue(message_id, message, analysis_result, priority)
    
    return {"message": "Submitted for review", "id": message_id}

@app.post("/ops/approve/{message_id}")
async def approve_message(
    message_id: str, 
    reviewer: str = Form(...),
    notes: str = Form(...),
    approved_version: str = Form(...)
):
    success = review_queue.approve_message(message_id, reviewer, notes, approved_version)
    if success:
        return {"message": "Message approved"}
    else:
        raise HTTPException(status_code=404, detail="Message not found")

def generate_review_items_html(items):
    if not items:
        return "<p>No items pending review.</p>"
    
    html = "<div>"
    for item in items:
        risk_score = item['analysis']['risk_report']['overall_risk_score']
        risk_color = "red" if risk_score > 0.7 else "orange" if risk_score > 0.4 else "green"
        
        html += f"""
        <div style="border: 1px solid #ccc; margin: 10px; padding: 10px;">
            <h3>Message ID: {item['id']} 
                <span style="color: {risk_color}">Risk: {risk_score:.2f}</span>
            </h3>
            <p><strong>Original:</strong> {item['original_text'][:200]}...</p>
            <p><strong>High-risk claims:</strong> {item['analysis']['risk_report']['high_risk_claim_count']}</p>
            <p><strong>Concerns:</strong> {item['analysis']['risk_report']['top_concerns']}</p>
            
            <form action="/ops/approve/{item['id']}" method="post">
                <input type="text" name="reviewer" placeholder="Your name" required><br>
                <textarea name="notes" placeholder="Review notes..." rows="2" cols="50"></textarea><br>
                <textarea name="approved_version" placeholder="Approved message version..." rows="3" cols="50"></textarea><br>
                <button type="submit">Approve</button>
            </form>
        </div>
        """
    html += "</div>"
    return html
```

**Development Status**: 

---

## v1.19: Learning System
**What**: Learn from reviewer feedback to improve risk scoring  
**How**: Track approval patterns and adjust scoring weights  
**Check**: Risk scores improve based on human feedback

**Implementation**:
```python
# src/learning/feedback_learner.py
class FeedbackLearner:
    def __init__(self):
        self.feedback_history = []
        self.weight_adjustments = {
            'absolutist_language': 1.0,
            'missing_evidence': 1.0,
            'ambiguous_terms': 1.0,
            'emotional_appeals': 1.0
        }
        
    def record_feedback(self, original_analysis, human_decision, reviewer_notes):
        feedback_record = {
            'original_risk_score': original_analysis['risk_report']['overall_risk_score'],
            'human_approved': human_decision == 'approved',
            'reviewer_notes': reviewer_notes,
            'analysis_features': self.extract_features(original_analysis),
            'timestamp': datetime.now().isoformat()
        }
        
        self.feedback_history.append(feedback_record)
        
        # Update weights based on feedback
        self.update_weights(feedback_record)
    
    def extract_features(self, analysis):
        """Extract features from analysis for learning"""
        features = {}
        
        # Count different types of risky patterns
        claims = analysis.get('claims', [])
        features['absolutist_count'] = sum(1 for claim in claims if any(
            word in claim.lower() for word in ['always', 'never', '100%', 'guaranteed']
        ))
        
        features['missing_evidence'] = 1 if len(analysis.get('evidence_validations', [])) == 0 else 0
        features['high_risk_claims'] = analysis['risk_report']['high_risk_claim_count']
        features['persona_concerns'] = sum(
            len(interp['potential_misreading']) 
            for interp in analysis.get('persona_interpretations', [])
        )
        
        return features
    
    def update_weights(self, feedback_record):
        """Adjust scoring weights based on human feedback"""
        features = feedback_record['analysis_features']
        human_approved = feedback_record['human_approved']
        original_risk = feedback_record['original_risk_score']
        
        # If human approved high-risk message, reduce weight of triggering features
        # If human rejected low-risk message, increase weight of present features
        
        if human_approved and original_risk > 0.7:
            # False positive - reduce weights
            if features['absolutist_count'] > 0:
                self.weight_adjustments['absolutist_language'] *= 0.95
            if features['missing_evidence'] > 0:
                self.weight_adjustments['missing_evidence'] *= 0.95
                
        elif not human_approved and original_risk < 0.3:
            # False negative - increase weights
            if features['absolutist_count'] > 0:
                self.weight_adjustments['absolutist_language'] *= 1.05
            if features['persona_concerns'] > 2:
                self.weight_adjustments['ambiguous_terms'] *= 1.05
    
    def get_adjusted_risk_score(self, base_score, features):
        """Apply learned weights to risk scoring"""
        adjusted_score = base_score
        
        # Apply weight adjustments
        if features.get('absolutist_count', 0) > 0:
            adjusted_score *= self.weight_adjustments['absolutist_language']
        
        if features.get('missing_evidence', 0) > 0:
            adjusted_score *= self.weight_adjustments['missing_evidence']
        
        # Normalize to 0-1 range
        return min(1.0, max(0.0, adjusted_score))
    
    def generate_learning_report(self):
        """Generate report on learning progress"""
        if len(self.feedback_history) < 5:
            return "Insufficient feedback data for learning analysis"
        
        recent_feedback = self.feedback_history[-20:]  # Last 20 decisions
        approval_rate = sum(1 for f in recent_feedback if f['human_approved']) / len(recent_feedback)
        
        avg_risk_approved = sum(
            f['original_risk_score'] for f in recent_feedback if f['human_approved']
        ) / sum(1 for f in recent_feedback if f['human_approved'])
        
        avg_risk_rejected = sum(
            f['original_risk_score'] for f in recent_feedback if not f['human_approved']
        ) / sum(1 for f in recent_feedback if not f['human_approved'])
        
        return {
            'total_feedback_count': len(self.feedback_history),
            'recent_approval_rate': approval_rate,
            'avg_risk_score_approved': avg_risk_approved,
            'avg_risk_score_rejected': avg_risk_rejected,
            'current_weights': self.weight_adjustments,
            'learning_trend': 'improving' if avg_risk_rejected > avg_risk_approved else 'needs_tuning'
        }
```

**Development Status**: 

---

## v2.0: Production Integration
**What**: Full production-ready system with all components integrated  
**How**: Complete system with API endpoints, documentation, monitoring  
**Check**: Can process health communications end-to-end with human oversight

**Implementation**:
```python
# src/production/main_api.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI(title="PRE-BUNKER Health Communications API", version="2.0.0")

class HealthMessage(BaseModel):
    text: str
    priority: str = "medium"
    target_audience: Optional[str] = None
    topic_area: Optional[str] = None

class AnalysisRequest(BaseModel):
    message: HealthMessage
    include_countermeasures: bool = True
    include_variants: bool = False
    require_human_review: bool = True

class AnalysisResponse(BaseModel):
    analysis_id: str
    risk_score: float
    high_risk_claims: list
    persona_reactions: list
    evidence_validation: list
    countermeasures: dict
    recommendations: list
    status: str  # 'analyzed', 'pending_review', 'approved'

# Main production pipeline
production_pipeline = None
review_queue = None
feedback_learner = None

@app.on_event("startup")
async def startup_event():
    global production_pipeline, review_queue, feedback_learner
    
    # Initialize all components
    production_pipeline = PrebunkerPipeline()
    review_queue = MessageReviewQueue()
    feedback_learner = FeedbackLearner()
    
    print("PRE-BUNKER system initialized")

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_health_message(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Main endpoint for analyzing health communications"""
    
    analysis_id = str(uuid.uuid4())
    
    try:
        # Run full pipeline analysis
        pipeline_result = await production_pipeline.process_message(request.message.text)
        
        # Apply learned weights if feedback learner is available
        if feedback_learner:
            features = feedback_learner.extract_features(pipeline_result)
            adjusted_risk = feedback_learner.get_adjusted_risk_score(
                pipeline_result['risk_report']['overall_risk_score'],
                features
            )
            pipeline_result['risk_report']['adjusted_risk_score'] = adjusted_risk
        
        # Generate variants if requested
        variants = []
        if request.include_variants:
            variant_generator = MessageVariantGenerator()
            variants = await variant_generator.generate_variants(
                request.message.text,
                pipeline_result['risk_report'],
                pipeline_result['countermeasures']
            )
        
        # Add to review queue if required or high risk
        status = 'analyzed'
        risk_score = pipeline_result['risk_report'].get('adjusted_risk_score', 
                     pipeline_result['risk_report']['overall_risk_score'])
        
        if request.require_human_review or risk_score > 0.6:
            review_queue.add_to_queue(
                analysis_id, 
                request.message.text, 
                pipeline_result,
                request.message.priority
            )
            status = 'pending_review'
        
        # Prepare response
        response = AnalysisResponse(
            analysis_id=analysis_id,
            risk_score=risk_score,
            high_risk_claims=pipeline_result['claims'],  # Filter for high-risk only
            persona_reactions=pipeline_result['persona_interpretations'],
            evidence_validation=pipeline_result['evidence_validations'],
            countermeasures=pipeline_result['countermeasures'] if request.include_countermeasures else {},
            recommendations=pipeline_result['risk_report']['recommendations'],
            status=status
        )
        
        # Log for monitoring (background task)
        background_tasks.add_task(log_analysis, analysis_id, request, pipeline_result)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "pipeline_ready": production_pipeline is not None,
        "review_queue_size": len(review_queue.get_pending_items()) if review_queue else 0,
        "feedback_history_size": len(feedback_learner.feedback_history) if feedback_learner else 0
    }

@app.get("/metrics")
async def get_metrics():
    """System performance metrics"""
    if feedback_learner:
        learning_report = feedback_learner.generate_learning_report()
        return {
            "system_metrics": learning_report,
            "pipeline_version": "2.0.0",
            "available_personas": len(STANDARD_PERSONAS) + len(HEALTH_SPECIFIC_PERSONAS),
            "available_sources": len(TRUSTED_SOURCES)
        }
    return {"status": "metrics not available"}

async def log_analysis(analysis_id, request, result):
    """Background logging task"""
    # In production, this would log to monitoring system
    print(f"Analysis {analysis_id} completed. Risk score: {result['risk_report']['overall_risk_score']}")

# Documentation endpoint
@app.get("/docs/pipeline")
async def pipeline_documentation():
    return {
        "pipeline_stages": [
            "1. Claim Extraction - Identify health claims in text",
            "2. Risk Scoring - Assess misinterpretation potential", 
            "3. Persona Simulation - Test with different audience types",
            "4. Evidence Validation - Check against authoritative sources",
            "5. Countermeasure Generation - Create prebunks and clarifications"
        ],
        "supported_personas": [p.name for p in STANDARD_PERSONAS + HEALTH_SPECIFIC_PERSONAS],
        "evidence_sources": [s.name for s in TRUSTED_SOURCES],
        "risk_metrics": [
            "Misinterpretability@k",
            "Evidence coverage score", 
            "Persona concern count",
            "Clarity score"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Final System Architecture**:
```
PRE-BUNKER v2.0 Production System
├── API Layer (FastAPI)
├── Pipeline Orchestration
├── Audience Simulation (Multiple Personas)
├── Claim Extraction & Risk Scoring
├── Evidence Validation (WHO/CDC/Cochrane)
├── Countermeasure Generation
├── A/B Testing Framework
├── Human Review Queue
├── Learning & Feedback System
└── Monitoring & Metrics
```

**Deployment Commands**:
```bash
cd agent-project
uv add fastapi uvicorn jinja2 pydantic
export OPENAI_API_KEY="sk-dummy-for-local"
uv run uvicorn src.production.main_api:app --reload --host 0.0.0.0 --port 8000
```

**Development Status**: 

---

## Testing Strategy for v2.0

### Test Cases for Each Component
1. **Health Claims**: "Vaccines are 100% safe" → Should flag absolutist language
2. **Persona Reactions**: Vaccine-hesitant should express different concerns than health-anxious
3. **Evidence Validation**: Claims should link to WHO/CDC sources when available
4. **Countermeasures**: Should generate persona-specific prebunks
5. **Risk Scoring**: High-risk claims should score >0.7, low-risk <0.3

### Integration Tests
- Full pipeline processes sample health messages
- A/B testing compares original vs improved versions
- Human review queue properly flags high-risk content
- Learning system adjusts weights based on feedback

### Production Readiness Checklist
- [ ] All components integrated and tested
- [ ] API endpoints documented and working
- [ ] Error handling for all failure modes
- [ ] Performance monitoring in place
- [ ] Human review workflow operational
- [ ] Feedback learning system functional

---

## Summary

This development plan provides a path from the current v1.0 Agent SDK to a fully functional v2.0 PRE-BUNKER health communications system. Each version builds incrementally toward the final goal while maintaining the ultra-granular approach proven successful in v1.0.

**Key Success Factors**:
- Each version is independently testable
- Health domain expertise embedded throughout
- Complete self-sufficiency for implementation
- Intelligent fallbacks when components fail
- Learning system improves over time

**Expected Timeline**: 19 incremental versions, each taking 1-3 development cycles, leading to production-ready health misinformation prevention system.

**Development Status**: Ready for implementation starting with v1.1
