"""Integration pipeline orchestrating all PRE-BUNKER components end-to-end"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.claims.extractor import ClaimExtractor
from src.claims.risk_scorer import RiskScorer
from src.personas.interpreter import PersonaInterpreter
from src.personas.base_personas import STANDARD_PERSONAS
from src.evidence.validator import EvidenceValidator
from src.countermeasures.generator import CountermeasureGenerator
from src.health_kb.claim_types import HealthClaim, ClaimType, classify_claim_type
from src.health_kb.medical_terms import extract_medical_entities

class PrebunkerPipeline:
    """Main pipeline orchestrating the complete PRE-BUNKER analysis workflow"""
    
    def __init__(self, personas: List = None):
        # Initialize all components
        self.claim_extractor = ClaimExtractor()
        self.risk_scorer = RiskScorer()
        self.persona_interpreter = PersonaInterpreter(personas or STANDARD_PERSONAS)
        self.evidence_validator = EvidenceValidator()
        self.countermeasure_generator = CountermeasureGenerator()
        
        # Pipeline configuration
        self.config = {
            'max_claims_to_process': 10,  # Prevent overwhelming the pipeline
            'min_risk_score_for_countermeasures': 0.3,
            'parallel_processing': True,
            'include_countermeasures': True,
            'detailed_logging': True
        }
    
    async def process_message(self, message_text: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a health message through the complete PRE-BUNKER pipeline"""
        
        # Merge options with defaults
        opts = {**self.config, **(options or {})}
        
        # Initialize result structure
        pipeline_result = {
            'original_message': message_text,
            'processing_timestamp': datetime.now().isoformat(),
            'pipeline_version': '1.9',
            'claims': [],
            'risk_analysis': {},
            'persona_interpretations': [],
            'evidence_validations': [],
            'countermeasures': [],
            'risk_report': {},
            'processing_time': 0.0,
            'pipeline_status': 'processing'
        }
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Extract claims from the message
            if opts['detailed_logging']:
                print(f"[Pipeline] Step 1: Extracting claims from message...")
            
            extracted_claims = await self._extract_claims(message_text, opts)
            pipeline_result['claims'] = extracted_claims
            
            if not extracted_claims:
                pipeline_result.update({
                    'pipeline_status': 'completed_no_claims',
                    'processing_time': asyncio.get_event_loop().time() - start_time
                })
                return pipeline_result
            
            # Step 2: Risk analysis
            if opts['detailed_logging']:
                print(f"[Pipeline] Step 2: Analyzing risk for {len(extracted_claims)} claims...")
            
            risk_analysis = await self._analyze_risk(extracted_claims, opts)
            pipeline_result['risk_analysis'] = risk_analysis
            
            # Step 3: Persona interpretations (in parallel with evidence validation)
            if opts['detailed_logging']:
                print(f"[Pipeline] Step 3: Getting persona interpretations...")
            
            # Step 4: Evidence validation (in parallel with persona interpretations)
            if opts['detailed_logging']:
                print(f"[Pipeline] Step 4: Validating evidence...")
            
            if opts['parallel_processing']:
                # Run persona interpretation and evidence validation in parallel
                persona_task = self._get_persona_interpretations(message_text, opts)
                evidence_task = self._validate_evidence(extracted_claims, opts)
                
                persona_interpretations, evidence_validations = await asyncio.gather(
                    persona_task, evidence_task
                )
            else:
                # Run sequentially
                persona_interpretations = await self._get_persona_interpretations(message_text, opts)
                evidence_validations = await self._validate_evidence(extracted_claims, opts)
            
            pipeline_result['persona_interpretations'] = persona_interpretations
            pipeline_result['evidence_validations'] = evidence_validations
            
            # Step 5: Generate countermeasures for high-risk claims
            if opts['include_countermeasures']:
                if opts['detailed_logging']:
                    print(f"[Pipeline] Step 5: Generating countermeasures...")
                
                countermeasures = await self._generate_countermeasures(
                    extracted_claims, persona_interpretations, evidence_validations, risk_analysis, opts
                )
                pipeline_result['countermeasures'] = countermeasures
            
            # Step 6: Compile comprehensive risk report
            if opts['detailed_logging']:
                print(f"[Pipeline] Step 6: Compiling risk report...")
            
            risk_report = self._compile_risk_report(pipeline_result)
            pipeline_result['risk_report'] = risk_report
            
            # Finalize
            pipeline_result.update({
                'pipeline_status': 'completed_success',
                'processing_time': asyncio.get_event_loop().time() - start_time
            })
            
        except Exception as e:
            pipeline_result.update({
                'pipeline_status': 'error',
                'error_message': str(e),
                'processing_time': asyncio.get_event_loop().time() - start_time
            })
            
            if opts['detailed_logging']:
                print(f"[Pipeline] Error: {str(e)}")
        
        return pipeline_result
    
    async def _extract_claims(self, message_text: str, opts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and classify health claims"""
        
        # Use the synchronous method for pattern-based extraction
        health_claims = self.claim_extractor.extract_and_classify_claims(message_text)
        
        # Limit claims if too many
        if len(health_claims) > opts['max_claims_to_process']:
            health_claims = health_claims[:opts['max_claims_to_process']]
        
        # Convert to detailed format
        extracted_claims = []
        for claim in health_claims:
            claim_dict = {
                'text': claim.text,
                'type': claim.claim_type.value,
                'confidence': claim.confidence,
                'medical_entities': claim.medical_entities,
                'absolutist_language': claim.absolutist_language,
                'base_risk_score': claim.calculate_base_risk()
            }
            extracted_claims.append(claim_dict)
        
        return extracted_claims
    
    async def _analyze_risk(self, claims: List[Dict[str, Any]], opts: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk for all claims"""
        
        risk_analysis = {
            'claim_risk_scores': [],
            'high_risk_claims': [],
            'medium_risk_claims': [],
            'low_risk_claims': [],
            'average_risk_score': 0.0,
            'max_risk_score': 0.0,
            'risk_distribution': {}
        }
        
        total_risk = 0.0
        
        for claim in claims:
            # Score the claim text
            text_risk_score = self.risk_scorer.score_claim(claim['text'])
            
            # Combine with base risk score
            combined_risk = (claim['base_risk_score'] * 0.6) + (text_risk_score * 0.4)
            
            # Analyze risk factors
            risk_factors = self.risk_scorer.analyze_risk_factors(claim['text'])
            
            claim_risk = {
                'claim_text': claim['text'],
                'base_risk_score': claim['base_risk_score'],
                'text_risk_score': text_risk_score,
                'combined_risk_score': combined_risk,
                'risk_factors': risk_factors,
                'risk_level': self._categorize_risk_level(combined_risk)
            }
            
            risk_analysis['claim_risk_scores'].append(claim_risk)
            
            # Categorize by risk level
            if combined_risk >= 0.7:
                risk_analysis['high_risk_claims'].append(claim_risk)
            elif combined_risk >= 0.4:
                risk_analysis['medium_risk_claims'].append(claim_risk)
            else:
                risk_analysis['low_risk_claims'].append(claim_risk)
            
            total_risk += combined_risk
        
        # Calculate summary statistics
        if claims:
            risk_analysis['average_risk_score'] = total_risk / len(claims)
            risk_analysis['max_risk_score'] = max(r['combined_risk_score'] for r in risk_analysis['claim_risk_scores'])
        
        # Risk distribution
        risk_analysis['risk_distribution'] = {
            'high_risk_count': len(risk_analysis['high_risk_claims']),
            'medium_risk_count': len(risk_analysis['medium_risk_claims']),
            'low_risk_count': len(risk_analysis['low_risk_claims'])
        }
        
        return risk_analysis
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk score into level"""
        if risk_score >= 0.7:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    async def _get_persona_interpretations(self, message_text: str, opts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get interpretations from all personas"""
        
        try:
            interpretations = await self.persona_interpreter.interpret_message(message_text)
            return interpretations
        except Exception as e:
            if opts['detailed_logging']:
                print(f"[Pipeline] Persona interpretation error: {str(e)}")
            return []
    
    async def _validate_evidence(self, claims: List[Dict[str, Any]], opts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate evidence for all claims"""
        
        evidence_validations = []
        
        for claim in claims:
            try:
                validation = await self.evidence_validator.validate_claim(claim['text'])
                evidence_validations.append(validation)
            except Exception as e:
                if opts['detailed_logging']:
                    print(f"[Pipeline] Evidence validation error for claim '{claim['text'][:50]}...': {str(e)}")
                
                # Add placeholder validation
                evidence_validations.append({
                    'claim': claim['text'],
                    'validation_status': 'error',
                    'error_message': str(e),
                    'confidence_score': 0.0
                })
        
        return evidence_validations
    
    async def _generate_countermeasures(self, claims: List[Dict[str, Any]], 
                                      persona_interpretations: List[Dict[str, Any]],
                                      evidence_validations: List[Dict[str, Any]],
                                      risk_analysis: Dict[str, Any],
                                      opts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate countermeasures for risky claims"""
        
        countermeasures = []
        
        # Focus on high and medium risk claims
        risky_claims = (risk_analysis['high_risk_claims'] + 
                       risk_analysis['medium_risk_claims'])
        
        for risk_claim in risky_claims:
            claim_text = risk_claim['claim_text']
            
            # Find corresponding evidence validation
            evidence = {}
            for ev in evidence_validations:
                if ev['claim'] == claim_text:
                    evidence = ev
                    break
            
            # Extract persona concerns for this claim
            persona_concerns = []
            for interpretation in persona_interpretations:
                persona_concerns.extend(interpretation.get('potential_misreading', []))
            
            # Remove duplicates
            persona_concerns = list(set(persona_concerns))
            
            try:
                claim_countermeasures = await self.countermeasure_generator.generate_countermeasures(
                    claim_text, persona_concerns, evidence
                )
                
                countermeasures.append({
                    'claim': claim_text,
                    'risk_level': risk_claim['risk_level'],
                    'risk_score': risk_claim['combined_risk_score'],
                    'countermeasures': claim_countermeasures,
                    'top_countermeasure': claim_countermeasures[0] if claim_countermeasures else None
                })
                
            except Exception as e:
                if opts['detailed_logging']:
                    print(f"[Pipeline] Countermeasure generation error for '{claim_text[:50]}...': {str(e)}")
                
                countermeasures.append({
                    'claim': claim_text,
                    'risk_level': risk_claim['risk_level'],
                    'risk_score': risk_claim['combined_risk_score'],
                    'countermeasures': [],
                    'error_message': str(e)
                })
        
        return countermeasures
    
    def _compile_risk_report(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compile comprehensive risk report from all pipeline results"""
        
        risk_report = {
            'overall_risk_assessment': 'unknown',
            'summary_statistics': {},
            'key_findings': [],
            'recommendations': [],
            'priority_actions': []
        }
        
        # Overall risk assessment
        risk_analysis = pipeline_result.get('risk_analysis', {})
        avg_risk = risk_analysis.get('average_risk_score', 0.0)
        high_risk_count = risk_analysis.get('risk_distribution', {}).get('high_risk_count', 0)
        
        if avg_risk >= 0.7 or high_risk_count > 0:
            risk_report['overall_risk_assessment'] = 'high_risk'
        elif avg_risk >= 0.4:
            risk_report['overall_risk_assessment'] = 'medium_risk'
        else:
            risk_report['overall_risk_assessment'] = 'low_risk'
        
        # Summary statistics
        risk_report['summary_statistics'] = {
            'total_claims': len(pipeline_result.get('claims', [])),
            'high_risk_claims': high_risk_count,
            'average_risk_score': avg_risk,
            'personas_with_concerns': len([p for p in pipeline_result.get('persona_interpretations', []) 
                                         if p.get('concern_level') in ['high', 'medium']]),
            'evidence_coverage': len([e for e in pipeline_result.get('evidence_validations', []) 
                                    if e.get('validation_status') in ['well_supported', 'moderately_supported']]),
            'countermeasures_generated': len(pipeline_result.get('countermeasures', []))
        }
        
        # Key findings
        if high_risk_count > 0:
            risk_report['key_findings'].append(f"Found {high_risk_count} high-risk claims requiring immediate attention")
        
        # Check for common risk patterns
        all_risk_factors = []
        for claim_risk in risk_analysis.get('claim_risk_scores', []):
            for factor_type, factors in claim_risk.get('risk_factors', {}).items():
                all_risk_factors.extend(factors)
        
        if 'absolutist' in str(all_risk_factors).lower():
            risk_report['key_findings'].append("Absolutist language detected (100%, always, never)")
        
        if 'conspiracy' in str(all_risk_factors).lower():
            risk_report['key_findings'].append("Conspiracy-related concerns identified")
        
        # Recommendations
        if risk_report['overall_risk_assessment'] == 'high_risk':
            risk_report['recommendations'].extend([
                "Review and revise high-risk claims before publication",
                "Add appropriate disclaimers and qualifications",
                "Include authoritative source citations"
            ])
        
        if risk_report['summary_statistics']['evidence_coverage'] < len(pipeline_result.get('claims', [])):
            risk_report['recommendations'].append("Add evidence citations for unsupported claims")
        
        # Priority actions
        for countermeasure_result in pipeline_result.get('countermeasures', []):
            if countermeasure_result.get('risk_level') == 'high':
                if countermeasure_result.get('top_countermeasure'):
                    risk_report['priority_actions'].append({
                        'claim': countermeasure_result['claim'][:100] + "...",
                        'action': 'apply_prebunk',
                        'prebunk': countermeasure_result['top_countermeasure']['content'][:200] + "..."
                    })
        
        return risk_report
    
    def get_pipeline_summary(self, pipeline_result: Dict[str, Any]) -> str:
        """Generate a human-readable summary of pipeline results"""
        
        status = pipeline_result.get('pipeline_status', 'unknown')
        processing_time = pipeline_result.get('processing_time', 0.0)
        
        if status == 'completed_no_claims':
            return f"✅ No health claims detected in message (processed in {processing_time:.2f}s)"
        
        elif status == 'error':
            error_msg = pipeline_result.get('error_message', 'Unknown error')
            return f"❌ Pipeline error: {error_msg} (failed after {processing_time:.2f}s)"
        
        elif status == 'completed_success':
            risk_report = pipeline_result.get('risk_report', {})
            stats = risk_report.get('summary_statistics', {})
            
            risk_level = risk_report.get('overall_risk_assessment', 'unknown')
            risk_emoji = {'high_risk': '🔴', 'medium_risk': '🟡', 'low_risk': '🟢'}.get(risk_level, '⚪')
            
            summary = f"{risk_emoji} Risk Assessment: {risk_level.replace('_', ' ').title()}\n"
            summary += f"📊 Claims: {stats.get('total_claims', 0)} total, {stats.get('high_risk_claims', 0)} high-risk\n"
            summary += f"🎭 Personas: {len(pipeline_result.get('persona_interpretations', []))} analyzed\n"
            summary += f"📚 Evidence: {stats.get('evidence_coverage', 0)} claims validated\n"
            summary += f"🛡️ Countermeasures: {stats.get('countermeasures_generated', 0)} generated\n"
            summary += f"⏱️ Processed in {processing_time:.2f} seconds"
            
            return summary
        
        else:
            return f"⚪ Pipeline status: {status}"

# Global instance for easy import
prebunker_pipeline = PrebunkerPipeline()
