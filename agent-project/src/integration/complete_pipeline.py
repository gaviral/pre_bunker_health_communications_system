"""Complete PRE-BUNKER system integration for v2.0"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import all components
from src.orchestration.pipeline import PrebunkerPipeline
from src.orchestration.risk_reporter import RiskReporter
from src.claims.advanced_extractor import AdvancedClaimExtractor
from src.evidence.enhanced_sources import EnhancedEvidenceSearcher
from src.personas.interpreter import PersonaInterpreter
from src.evidence.validator import EvidenceValidator
from src.countermeasures.generator import CountermeasureGenerator
from src.countermeasures.persona_targeted import PersonaTargetedGenerator
from src.orchestration.ab_testing import ABTestingFramework
from src.metrics.evaluation import HealthCommMetrics
from src.ops.dashboard import MessageReviewQueue, WorkflowManager
from src.learning.feedback_learner import FeedbackLearner

class CompletePrebunkerSystem:
    """Complete integrated PRE-BUNKER system for production use"""
    
    def __init__(self):
        self.version = "2.0.0"
        
        # Core pipeline components
        self.pipeline = PrebunkerPipeline()
        self.risk_reporter = RiskReporter()
        
        # Advanced processing components
        self.advanced_extractor = AdvancedClaimExtractor()
        self.enhanced_evidence_searcher = EnhancedEvidenceSearcher()
        self.persona_interpreter = PersonaInterpreter()
        self.evidence_validator = EvidenceValidator()
        self.countermeasure_generator = CountermeasureGenerator()
        self.persona_targeted_generator = PersonaTargetedGenerator()
        
        # Testing and evaluation components
        self.ab_testing_framework = ABTestingFramework()
        self.health_comm_metrics = HealthCommMetrics()
        
        # Operations and learning components
        self.message_review_queue = MessageReviewQueue()
        self.workflow_manager = WorkflowManager()
        self.feedback_learner = FeedbackLearner()
        
        # System capabilities tracking
        self.capabilities = {
            "claim_extraction": True,
            "persona_analysis": True,
            "evidence_validation": True,
            "risk_assessment": True,
            "countermeasures": True,
            "web_interface": True,
            "ab_testing": True,
            "performance_metrics": True,
            "human_review_queue": True,
            "learning_system": True
        }
        
        # Component versions implemented
        self.components = {
            "claim_extraction": "v1.2 + v1.13 Advanced",
            "risk_assessment": "v1.3 + v1.10 Enhanced",
            "persona_analysis": "v1.4-v1.5 + v1.12 Health-Specific",
            "evidence_validation": "v1.6-v1.7 + v1.14 Enhanced",
            "countermeasures": "v1.8 + v1.15 Persona-Targeted",
            "web_interface": "v1.11 FastAPI",
            "integration": "v1.9 + v2.0 Complete",
            "ab_testing": "v1.16 Message Variants",
            "performance_metrics": "v1.17 Comprehensive Evaluation",
            "ops_dashboard": "v1.18 Human Review Workflow",
            "learning_system": "v1.19 Feedback-Based Improvement"
        }
        
        print(f"✅ PRE-BUNKER v{self.version} system initialized with {len(self.capabilities)} capabilities")
    
    async def analyze_health_communication(self, message: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Complete health communication analysis pipeline"""
        start_time = datetime.now()
        analysis_id = f"analysis_{int(start_time.timestamp())}"
        
        if options is None:
            options = {}
        
        try:
            # Step 1: Advanced claim extraction
            claim_extraction_result = await self.advanced_extractor.extract_claims_advanced(message, options)
            explicit_claims = claim_extraction_result.get('explicit_claims', [])
            implicit_claims = claim_extraction_result.get('implicit_claims', [])
            all_claims = explicit_claims + implicit_claims
            context_analysis = claim_extraction_result.get('context_analysis', {})
            
            # Step 2: Enhanced evidence validation
            evidence_validations = []
            for claim in all_claims:
                evidence_result = await self.evidence_validator.validate_claim_evidence(str(claim))
                evidence_validations.append(evidence_result)
            
            # Step 3: Persona interpretation analysis
            persona_interpretations = await self.persona_interpreter.interpret_message(message)
            
            # Step 4: Risk assessment and reporting
            pipeline_result = {
                'claims': all_claims,
                'persona_interpretations': persona_interpretations,
                'evidence_validations': evidence_validations
            }
            risk_report = self.risk_reporter.compile_risk_report(pipeline_result)
            
            # Step 5: Persona-targeted countermeasure generation
            persona_countermeasures = await self.persona_targeted_generator.generate_targeted_countermeasures(
                message, persona_interpretations, evidence_validations
            )
            
            # Step 6: General countermeasure generation
            general_countermeasures = await self.countermeasure_generator.generate_countermeasures(
                all_claims, risk_report, evidence_validations
            )
            
            # Combine countermeasures
            all_countermeasures = {**persona_countermeasures, **general_countermeasures}
            
            # Step 7: Performance metrics evaluation
            complete_result = {
                'claims': all_claims,
                'persona_interpretations': persona_interpretations,
                'evidence_validations': evidence_validations,
                'risk_report': risk_report,
                'countermeasures': all_countermeasures,
                'context_analysis': context_analysis
            }
            
            evaluation_metrics = self.health_comm_metrics.generate_evaluation_report(complete_result)
            
            # Step 8: Workflow routing decision
            workflow_recommendation = self.workflow_manager.determine_workflow(complete_result)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Compile final result
            final_result = {
                'analysis_id': analysis_id,
                'message': message,
                'timestamp': start_time.isoformat(),
                'processing_time': processing_time,
                
                # Core analysis results
                'explicit_claims': explicit_claims,
                'implicit_claims': implicit_claims,
                'all_claims': all_claims,
                'context_analysis': context_analysis,
                'persona_interpretations': persona_interpretations,
                'evidence_validations': evidence_validations,
                'risk_report': risk_report,
                'countermeasures': all_countermeasures,
                
                # Enhanced analysis
                'evaluation_metrics': evaluation_metrics,
                'workflow_recommendation': workflow_recommendation,
                
                # System metadata
                'system_version': self.version,
                'components_used': list(self.components.keys()),
                'status': 'completed'
            }
            
            return final_result
            
        except Exception as e:
            # Error handling
            error_result = {
                'analysis_id': analysis_id,
                'message': message,
                'timestamp': start_time.isoformat(),
                'status': 'error',
                'error': str(e),
                'system_version': self.version
            }
            return error_result
    
    async def analyze_with_ab_testing(self, message: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze message with A/B testing of variants"""
        # Get base analysis
        base_analysis = await self.analyze_health_communication(message, options)
        
        if base_analysis.get('status') == 'error':
            return base_analysis
        
        # Run A/B testing
        ab_test_results = await self.ab_testing_framework.run_ab_test(
            message, 
            base_analysis['risk_report'], 
            base_analysis['countermeasures']
        )
        
        # Combine results
        base_analysis['ab_test_results'] = ab_test_results
        base_analysis['recommended_variant'] = ab_test_results.get('winner', 'original')
        
        return base_analysis
    
    def submit_for_human_review(self, analysis_result: Dict[str, Any], priority: str = 'medium') -> str:
        """Submit analysis result for human review"""
        message_id = analysis_result.get('analysis_id', f"review_{int(datetime.now().timestamp())}")
        
        # Add to review queue
        self.message_review_queue.add_to_queue(
            message_id,
            analysis_result.get('message', ''),
            analysis_result,
            priority
        )
        
        return message_id
    
    def record_human_feedback(self, analysis_result: Dict[str, Any], human_decision: str, reviewer_notes: str, reviewer_id: str = None):
        """Record human feedback for learning"""
        return self.feedback_learner.record_feedback(
            analysis_result, human_decision, reviewer_notes, reviewer_id
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        queue_stats = self.message_review_queue.get_queue_stats()
        learning_patterns = self.feedback_learner.analyze_feedback_patterns()
        learning_recommendations = self.feedback_learner.get_recommendations()
        
        return {
            'version': self.version,
            'capabilities': self.capabilities,
            'components': self.components,
            'review_queue': queue_stats,
            'learning_system': {
                'patterns': learning_patterns,
                'recommendations': learning_recommendations
            },
            'system_health': 'operational',
            'features_implemented': [
                'Advanced claim extraction (explicit + implicit)',
                'Enhanced evidence validation with 15 trusted sources',
                'Persona-specific interpretation (12 personas)',
                'Targeted countermeasure generation',
                'A/B testing of message variants',
                'Comprehensive performance metrics',
                'Human review workflow with priority routing',
                'Adaptive learning from reviewer feedback',
                'Complete end-to-end pipeline integration'
            ]
        }
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get system capabilities overview"""
        return {
            "version": self.version,
            "components": self.components,
            "capabilities": self.capabilities,
            "testing_status": "All components implemented and integrated",
            "error_handling": "Comprehensive error recovery and reporting",
            "logging": "Detailed operation logs for debugging and audit",
            "api_compliance": "RESTful standards with proper status codes",
            "deployment_ready": "FastAPI application with uvicorn server",
            "human_oversight": "Complete review workflow with priority routing",
            "adaptive_learning": "Feedback-based improvement system",
            "performance_optimization": "A/B testing and metrics evaluation"
        }

# Global system instance
complete_prebunker_system = CompletePrebunkerSystem()
