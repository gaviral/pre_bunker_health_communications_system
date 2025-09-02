"""A/B Testing Framework for message variant comparison"""

import asyncio
from typing import Dict, List, Any, Optional
from src.agent import Agent, model
from src.personas.interpreter import PersonaInterpreter

class MessageVariantGenerator:
    """Generate alternative versions of health messages for testing"""
    
    def __init__(self):
        self.variant_agent = Agent(
            name="VariantGenerator",
            instructions="Create alternative versions of health messages with different approaches to clarity and risk mitigation.",
            model=model
        )
    
    async def generate_variants(self, original_message, risk_report, countermeasures):
        """Generate multiple message variants for A/B testing"""
        variants = [{'version': 'original', 'text': original_message}]
        
        # Generate prebunked version
        prebunk_prompt = f"""
        Original message: {original_message}
        Risk issues: {risk_report.get('recommendations', [])}
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
        
        # Generate simplified version (clear and accessible)
        simplified_prompt = f"""
        Create a simplified, easy-to-understand version of: {original_message}
        Use plain language, avoid technical jargon, make it accessible to general audience.
        """
        
        simplified_version = await self.variant_agent.run(simplified_prompt)
        variants.append({'version': 'simplified', 'text': simplified_version})
        
        return variants

class ABTestSimulator:
    """Simulate A/B testing with persona-based reactions"""
    
    def __init__(self, personas=None):
        self.personas = personas
        self.persona_interpreter = PersonaInterpreter(personas) if personas else PersonaInterpreter()
        
        self.clarity_agent = Agent(
            name="ClarityScorer",
            instructions="Score message clarity on scale 0-1. Consider readability, ambiguity, and completeness.",
            model=model
        )
    
    async def test_variants(self, variants):
        """Test all variants and compare results"""
        test_results = {}
        
        for variant in variants:
            version_name = variant['version']
            message_text = variant['text']
            
            # Test with all personas
            interpretations = await self.persona_interpreter.interpret_message(message_text)
            
            # Calculate metrics
            concern_count = sum(len(interp.get('potential_misreading', [])) for interp in interpretations)
            clarity_score = await self.score_clarity(message_text)
            readability_score = self.calculate_readability_score(message_text)
            
            test_results[version_name] = {
                'message': message_text,
                'total_concerns': concern_count,
                'clarity_score': clarity_score,
                'readability_score': readability_score,
                'persona_reactions': interpretations,
                'overall_score': self.calculate_overall_score(concern_count, clarity_score, readability_score),
                'message_length': len(message_text),
                'word_count': len(message_text.split())
            }
        
        return test_results
    
    async def score_clarity(self, message_text):
        """Score message clarity using LLM"""
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
        
        try:
            score_response = await self.clarity_agent.run(clarity_prompt)
            
            # Extract numeric score (basic parsing)
            score = float(score_response.strip())
            return max(0.0, min(1.0, score))
        except (ValueError, TypeError, AttributeError) as e:
            # Fallback to heuristic scoring
            return self.calculate_readability_score(message_text)
    
    def calculate_readability_score(self, message_text):
        """Calculate readability score based on text characteristics"""
        if not message_text:
            return 0.0
        
        words = message_text.split()
        sentences = message_text.count('.') + message_text.count('!') + message_text.count('?')
        if sentences == 0:
            sentences = 1
        
        # Average words per sentence
        avg_words_per_sentence = len(words) / sentences
        
        # Penalize very long sentences more aggressively
        sentence_penalty = max(0, (avg_words_per_sentence - 15) * 0.05)
        
        # Count complex words (>7 characters for stricter assessment)
        complex_words = sum(1 for word in words if len(word) > 7)
        complex_ratio = complex_words / len(words) if words else 0
        
        # Count very complex words (>12 characters)
        very_complex_words = sum(1 for word in words if len(word) > 12)
        very_complex_ratio = very_complex_words / len(words) if words else 0
        
        # Base readability score with more aggressive penalties
        readability = 1.0 - (complex_ratio * 0.6) - (very_complex_ratio * 0.8) - sentence_penalty
        
        return max(0.0, min(1.0, readability))
    
    def calculate_overall_score(self, concern_count, clarity_score, readability_score):
        """Calculate overall effectiveness score"""
        # Lower concerns is better (invert concern score)
        max_expected_concerns = 10  # Assume max 10 concerns
        concern_score = max(0.0, 1.0 - (concern_count / max_expected_concerns))
        
        # Weight the components
        overall = (concern_score * 0.5) + (clarity_score * 0.3) + (readability_score * 0.2)
        
        return round(overall, 2)
    
    def compare_variants(self, test_results):
        """Compare variants and identify the best performing"""
        if not test_results:
            return None
        
        # Rank by overall score
        ranked_variants = sorted(
            test_results.items(), 
            key=lambda x: x[1]['overall_score'], 
            reverse=True
        )
        
        comparison_report = {
            'best_variant': ranked_variants[0][0],
            'rankings': [(name, data['overall_score']) for name, data in ranked_variants],
            'metrics_comparison': {},
            'recommendations': []
        }
        
        # Compare specific metrics
        for metric in ['total_concerns', 'clarity_score', 'readability_score', 'word_count']:
            metric_values = {name: data[metric] for name, data in test_results.items()}
            
            if metric == 'total_concerns':
                # Lower is better for concerns
                best_metric = min(metric_values, key=metric_values.get)
            else:
                # Higher is better for other metrics
                best_metric = max(metric_values, key=metric_values.get)
            
            comparison_report['metrics_comparison'][metric] = {
                'values': metric_values,
                'best_performer': best_metric
            }
        
        # Generate recommendations
        best_variant_name = comparison_report['best_variant']
        best_data = test_results[best_variant_name]
        
        if best_data['total_concerns'] > 5:
            comparison_report['recommendations'].append("Consider further revision to reduce audience concerns")
        
        if best_data['clarity_score'] < 0.7:
            comparison_report['recommendations'].append("Improve message clarity and remove ambiguous language")
        
        if best_data['readability_score'] < 0.6:
            comparison_report['recommendations'].append("Simplify language for better accessibility")
        
        return comparison_report

class ABTestingFramework:
    """Complete A/B testing framework combining generation and simulation"""
    
    def __init__(self, personas=None):
        self.variant_generator = MessageVariantGenerator()
        self.ab_simulator = ABTestSimulator(personas)
    
    async def run_ab_test(self, original_message, risk_report, countermeasures):
        """Run complete A/B test from generation to comparison"""
        
        # Step 1: Generate variants
        variants = await self.variant_generator.generate_variants(
            original_message, risk_report, countermeasures
        )
        
        # Step 2: Test all variants
        test_results = await self.ab_simulator.test_variants(variants)
        
        # Step 3: Compare and analyze
        comparison_report = self.ab_simulator.compare_variants(test_results)
        
        # Step 4: Compile comprehensive results
        ab_test_results = {
            'original_message': original_message,
            'variants_generated': len(variants),
            'variants': variants,
            'test_results': test_results,
            'comparison_report': comparison_report,
            'winner': comparison_report['best_variant'] if comparison_report else None,
            'improvement_achieved': self.calculate_improvement(test_results),
            'recommendations': comparison_report['recommendations'] if comparison_report else []
        }
        
        return ab_test_results
    
    def calculate_improvement(self, test_results):
        """Calculate improvement from original to best variant"""
        if 'original' not in test_results or len(test_results) < 2:
            return 0.0
        
        original_score = test_results['original']['overall_score']
        best_score = max(data['overall_score'] for data in test_results.values())
        
        improvement = best_score - original_score
        return round(improvement, 2)

# Global instance
ab_testing_framework = ABTestingFramework()
