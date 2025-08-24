"""Risk report generation with actionable insights for health communications"""

from typing import Dict, List, Any
from src.agent import Agent, model

class RiskReporter:
    """Generates comprehensive risk reports with actionable recommendations"""
    
    def __init__(self):
        self.report_agent = Agent(
            name="RiskReporter",
            instructions="""You are a health communication risk assessment expert. Your job is to compile comprehensive, actionable risk reports from pipeline analysis results.

Create clear, structured reports that help health communication professionals understand:
1. Overall risk level and key concerns
2. Specific problematic claims and recommended fixes
3. Audience reaction patterns and mitigation strategies
4. Evidence gaps and source recommendations
5. Priority actions for immediate implementation

Use professional, precise language. Focus on actionable insights, not just descriptions.
Provide specific, implementable recommendations.""",
            model=model
        )
    
    async def compile_risk_report(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compile comprehensive risk report from pipeline results"""
        
        # Extract base metrics
        base_metrics = self._calculate_base_metrics(pipeline_result)
        
        # Generate LLM-enhanced analysis
        enhanced_analysis = await self._generate_enhanced_analysis(pipeline_result)
        
        # Compile comprehensive report
        risk_report = {
            'overall_risk_assessment': self._determine_overall_risk(base_metrics),
            'summary_statistics': base_metrics,
            'enhanced_analysis': enhanced_analysis,
            'key_findings': self._extract_key_findings(pipeline_result, base_metrics),
            'recommendations': self._generate_recommendations(pipeline_result, base_metrics),
            'priority_actions': self._prioritize_actions(pipeline_result, base_metrics),
            'evidence_assessment': self._assess_evidence_coverage(pipeline_result),
            'persona_insights': self._analyze_persona_patterns(pipeline_result),
            'countermeasure_effectiveness': self._evaluate_countermeasures(pipeline_result)
        }
        
        return risk_report
    
    def _calculate_base_metrics(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate foundational risk metrics"""
        
        claims = pipeline_result.get('claims', [])
        risk_analysis = pipeline_result.get('risk_analysis', {})
        personas = pipeline_result.get('persona_interpretations', [])
        evidence = pipeline_result.get('evidence_validations', [])
        countermeasures = pipeline_result.get('countermeasures', [])
        
        # Risk distribution
        high_risk_claims = risk_analysis.get('high_risk_claims', [])
        medium_risk_claims = risk_analysis.get('medium_risk_claims', [])
        
        # Persona concern analysis
        high_concern_personas = len([p for p in personas if p.get('concern_level') in ['high', 'medium']])
        
        # Evidence coverage
        well_supported = len([e for e in evidence if e.get('validation_status') in ['well_supported', 'moderately_supported']])
        evidence_coverage_rate = well_supported / len(claims) if claims else 0.0
        
        return {
            'total_claims': len(claims),
            'high_risk_claims': len(high_risk_claims),
            'medium_risk_claims': len(medium_risk_claims),
            'low_risk_claims': len(claims) - len(high_risk_claims) - len(medium_risk_claims),
            'average_risk_score': risk_analysis.get('average_risk_score', 0.0),
            'max_risk_score': risk_analysis.get('max_risk_score', 0.0),
            'personas_analyzed': len(personas),
            'personas_with_concerns': high_concern_personas,
            'evidence_validations': len(evidence),
            'evidence_coverage_rate': evidence_coverage_rate,
            'countermeasures_generated': len(countermeasures),
            'processing_time': pipeline_result.get('processing_time', 0.0)
        }
    
    def _determine_overall_risk(self, metrics: Dict[str, Any]) -> str:
        """Determine overall risk assessment"""
        
        high_risk_claims = metrics['high_risk_claims']
        avg_risk = metrics['average_risk_score']
        personas_concerned = metrics['personas_with_concerns']
        evidence_coverage = metrics['evidence_coverage_rate']
        
        # Multi-factor risk assessment
        if high_risk_claims > 0 or avg_risk >= 0.7:
            return 'high_risk'
        elif avg_risk >= 0.4 or personas_concerned >= 2 or evidence_coverage < 0.5:
            return 'medium_risk'
        else:
            return 'low_risk'
    
    async def _generate_enhanced_analysis(self, pipeline_result: Dict[str, Any]) -> str:
        """Generate LLM-enhanced risk analysis"""
        
        # Prepare context for LLM analysis
        claims_summary = self._summarize_claims(pipeline_result.get('claims', []))
        risk_summary = self._summarize_risk_analysis(pipeline_result.get('risk_analysis', {}))
        persona_summary = self._summarize_persona_reactions(pipeline_result.get('persona_interpretations', []))
        evidence_summary = self._summarize_evidence(pipeline_result.get('evidence_validations', []))
        
        analysis_prompt = f"""
        Analyze this health communication risk assessment and provide expert insights:
        
        CLAIMS IDENTIFIED:
        {claims_summary}
        
        RISK ANALYSIS:
        {risk_summary}
        
        AUDIENCE REACTIONS:
        {persona_summary}
        
        EVIDENCE VALIDATION:
        {evidence_summary}
        
        Provide a comprehensive analysis covering:
        1. Most significant risk factors and their implications
        2. Audience vulnerability patterns and communication gaps
        3. Evidence strengths and weaknesses
        4. Overall communication effectiveness assessment
        5. Strategic recommendations for improvement
        
        Focus on actionable insights for health communication professionals.
        """
        
        try:
            enhanced_analysis = await self.report_agent.run(analysis_prompt)
            return enhanced_analysis
        except Exception as e:
            return f"Enhanced analysis unavailable: {str(e)}"
    
    def _summarize_claims(self, claims: List[Dict[str, Any]]) -> str:
        """Summarize claims for LLM context"""
        if not claims:
            return "No claims detected"
        
        summary = f"Total claims: {len(claims)}\n"
        for i, claim in enumerate(claims[:5], 1):  # Limit to top 5
            summary += f"{i}. {claim.get('text', '')[:100]}... (risk: {claim.get('base_risk_score', 0.0):.2f})\n"
        
        return summary
    
    def _summarize_risk_analysis(self, risk_analysis: Dict[str, Any]) -> str:
        """Summarize risk analysis for LLM context"""
        if not risk_analysis:
            return "No risk analysis available"
        
        return f"""
        Average risk score: {risk_analysis.get('average_risk_score', 0.0):.2f}
        High-risk claims: {risk_analysis.get('risk_distribution', {}).get('high_risk_count', 0)}
        Medium-risk claims: {risk_analysis.get('risk_distribution', {}).get('medium_risk_count', 0)}
        """
    
    def _summarize_persona_reactions(self, personas: List[Dict[str, Any]]) -> str:
        """Summarize persona reactions for LLM context"""
        if not personas:
            return "No persona analysis available"
        
        summary = f"Personas analyzed: {len(personas)}\n"
        for persona in personas:
            concern_level = persona.get('concern_level', 'unknown')
            concerns = len(persona.get('potential_misreading', []))
            summary += f"- {persona.get('persona', 'Unknown')}: {concern_level} concern ({concerns} issues)\n"
        
        return summary
    
    def _summarize_evidence(self, evidence: List[Dict[str, Any]]) -> str:
        """Summarize evidence validation for LLM context"""
        if not evidence:
            return "No evidence validation available"
        
        supported = len([e for e in evidence if e.get('validation_status') == 'well_supported'])
        moderate = len([e for e in evidence if e.get('validation_status') == 'moderately_supported'])
        limited = len([e for e in evidence if e.get('validation_status') == 'limited_support'])
        
        return f"""
        Total validations: {len(evidence)}
        Well supported: {supported}
        Moderately supported: {moderate}
        Limited support: {limited}
        """
    
    def _extract_key_findings(self, pipeline_result: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis"""
        
        findings = []
        
        # High-risk claim findings
        if metrics['high_risk_claims'] > 0:
            findings.append(f"CRITICAL: {metrics['high_risk_claims']} high-risk claims detected requiring immediate revision")
        
        # Evidence coverage findings
        if metrics['evidence_coverage_rate'] < 0.5:
            findings.append(f"EVIDENCE GAP: Only {metrics['evidence_coverage_rate']:.1%} of claims have supporting evidence")
        
        # Persona concern findings
        if metrics['personas_with_concerns'] >= 2:
            findings.append(f"AUDIENCE RISK: {metrics['personas_with_concerns']}/{metrics['personas_analyzed']} audience segments show significant concerns")
        
        # Risk pattern analysis
        risk_analysis = pipeline_result.get('risk_analysis', {})
        all_risk_factors = []
        for claim_risk in risk_analysis.get('claim_risk_scores', []):
            for factor_type, factors in claim_risk.get('risk_factors', {}).items():
                all_risk_factors.extend(factors)
        
        if 'absolutist' in str(all_risk_factors).lower():
            findings.append("LANGUAGE RISK: Absolutist language detected (100%, always, never)")
        
        if 'conspiracy' in str(all_risk_factors).lower():
            findings.append("TRUST RISK: Conspiracy-related concerns identified in audience reactions")
        
        return findings
    
    def _generate_recommendations(self, pipeline_result: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Risk-based recommendations
        if metrics['high_risk_claims'] > 0:
            recommendations.extend([
                "IMMEDIATE: Review and revise all high-risk claims before publication",
                "ADD: Appropriate disclaimers and uncertainty qualifiers to absolutist statements",
                "INCLUDE: Clear citations to authoritative health sources (WHO, CDC, FDA)"
            ])
        
        # Evidence recommendations
        if metrics['evidence_coverage_rate'] < 0.7:
            recommendations.append("STRENGTHEN: Add evidence citations for all unsupported claims")
        
        # Audience recommendations
        if metrics['personas_with_concerns'] >= 2:
            recommendations.extend([
                "ADDRESS: Specific audience concerns through targeted prebunks",
                "SIMPLIFY: Use clearer, less technical language for general audiences"
            ])
        
        # Countermeasure recommendations
        if metrics['countermeasures_generated'] > 0:
            recommendations.append("IMPLEMENT: Use generated countermeasures to address identified risks")
        
        return recommendations
    
    def _prioritize_actions(self, pipeline_result: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize specific actions based on risk level"""
        
        actions = []
        
        # Priority 1: High-risk claims
        risk_analysis = pipeline_result.get('risk_analysis', {})
        for claim_risk in risk_analysis.get('high_risk_claims', []):
            actions.append({
                'priority': 1,
                'action_type': 'revise_claim',
                'description': f"Revise high-risk claim: {claim_risk.get('claim_text', '')[:80]}...",
                'specific_risks': list(claim_risk.get('risk_factors', {}).keys()),
                'urgency': 'immediate'
            })
        
        # Priority 2: Evidence gaps
        evidence_validations = pipeline_result.get('evidence_validations', [])
        for evidence in evidence_validations:
            if evidence.get('validation_status') == 'insufficient_evidence':
                actions.append({
                    'priority': 2,
                    'action_type': 'add_evidence',
                    'description': f"Add evidence for: {evidence.get('claim', '')[:80]}...",
                    'urgency': 'high'
                })
        
        # Priority 3: Implement countermeasures
        countermeasures = pipeline_result.get('countermeasures', [])
        for cm in countermeasures:
            if cm.get('risk_level') == 'high' and cm.get('top_countermeasure'):
                actions.append({
                    'priority': 3,
                    'action_type': 'apply_countermeasure',
                    'description': f"Apply prebunk for: {cm.get('claim', '')[:60]}...",
                    'countermeasure': cm['top_countermeasure']['content'][:150] + "...",
                    'urgency': 'medium'
                })
        
        return sorted(actions, key=lambda x: x['priority'])
    
    def _assess_evidence_coverage(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess evidence coverage quality"""
        
        evidence_validations = pipeline_result.get('evidence_validations', [])
        
        if not evidence_validations:
            return {
                'coverage_level': 'none',
                'assessment': 'No evidence validation performed',
                'gaps': ['All claims lack evidence support']
            }
        
        well_supported = len([e for e in evidence_validations if e.get('validation_status') == 'well_supported'])
        moderately_supported = len([e for e in evidence_validations if e.get('validation_status') == 'moderately_supported'])
        total = len(evidence_validations)
        
        coverage_rate = (well_supported + moderately_supported) / total if total > 0 else 0.0
        
        if coverage_rate >= 0.8:
            coverage_level = 'excellent'
            assessment = 'Strong evidence base with authoritative sources'
        elif coverage_rate >= 0.6:
            coverage_level = 'good'
            assessment = 'Adequate evidence coverage with some gaps'
        elif coverage_rate >= 0.3:
            coverage_level = 'limited'
            assessment = 'Insufficient evidence coverage requiring attention'
        else:
            coverage_level = 'poor'
            assessment = 'Critical evidence gaps requiring immediate action'
        
        gaps = []
        for evidence in evidence_validations:
            if evidence.get('validation_status') in ['insufficient_evidence', 'limited_support']:
                gaps.append(f"Weak evidence for: {evidence.get('claim', '')[:60]}...")
        
        return {
            'coverage_level': coverage_level,
            'coverage_rate': coverage_rate,
            'assessment': assessment,
            'well_supported_count': well_supported,
            'moderately_supported_count': moderately_supported,
            'gaps': gaps[:5]  # Limit to top 5 gaps
        }
    
    def _analyze_persona_patterns(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze persona reaction patterns"""
        
        personas = pipeline_result.get('persona_interpretations', [])
        
        if not personas:
            return {
                'pattern_analysis': 'No persona analysis available',
                'risk_segments': [],
                'common_concerns': []
            }
        
        # Analyze concern patterns
        all_concerns = []
        risk_segments = []
        
        for persona in personas:
            concerns = persona.get('potential_misreading', [])
            all_concerns.extend(concerns)
            
            if persona.get('concern_level') in ['high', 'medium']:
                risk_segments.append({
                    'persona': persona.get('persona', 'Unknown'),
                    'concern_level': persona.get('concern_level'),
                    'key_issues': concerns[:3],  # Top 3 concerns
                    'demographics': persona.get('demographics', 'Not specified')
                })
        
        # Find common concerns
        concern_frequency = {}
        for concern in all_concerns:
            concern_frequency[concern] = concern_frequency.get(concern, 0) + 1
        
        common_concerns = sorted(concern_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_personas_analyzed': len(personas),
            'high_risk_segments': len(risk_segments),
            'pattern_analysis': f"Analyzed {len(personas)} audience segments, {len(risk_segments)} showing significant concerns",
            'risk_segments': risk_segments,
            'common_concerns': [{'concern': c[0], 'frequency': c[1]} for c in common_concerns]
        }
    
    def _evaluate_countermeasures(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate countermeasure effectiveness and coverage"""
        
        countermeasures = pipeline_result.get('countermeasures', [])
        
        if not countermeasures:
            return {
                'coverage': 'none',
                'evaluation': 'No countermeasures generated',
                'recommendations': ['Generate countermeasures for identified risks']
            }
        
        total_countermeasures = sum(len(cm.get('countermeasures', [])) for cm in countermeasures)
        high_quality = sum(1 for cm in countermeasures 
                          if cm.get('top_countermeasure', {}).get('effectiveness_score', 0) >= 0.7)
        
        coverage_rate = len(countermeasures) / len(pipeline_result.get('claims', [])) if pipeline_result.get('claims') else 0.0
        
        return {
            'total_countermeasures': total_countermeasures,
            'claims_with_countermeasures': len(countermeasures),
            'coverage_rate': coverage_rate,
            'high_quality_count': high_quality,
            'evaluation': f"Generated {total_countermeasures} countermeasures for {len(countermeasures)} risky claims",
            'effectiveness_assessment': 'Good' if high_quality >= len(countermeasures) * 0.7 else 'Needs improvement'
        }

# Global instance
risk_reporter = RiskReporter()
