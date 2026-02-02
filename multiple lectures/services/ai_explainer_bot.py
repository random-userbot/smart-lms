"""
AI Explanation Chatbot Service
Uses Grok AI to explain teaching scores and provide insights
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logging.warning("Groq not installed. Install with: pip install groq")


class TeachingScoreExplainerBot:
    """AI chatbot to explain teaching scores and provide insights"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the chatbot
        
        Args:
            api_key: Grok/Groq API key (falls back to environment variable)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.client = None
        self.model = "mixtral-8x7b-32768"  # Fast and powerful model
        
        if GROQ_AVAILABLE and self.api_key:
            self.client = Groq(api_key=self.api_key)
            logging.info("✓ Teaching Score Explainer Bot initialized")
        else:
            logging.warning("❌ Groq API not available or API key not found")
    
    def is_available(self) -> bool:
        """Check if the bot is available"""
        return self.client is not None
    
    def _build_context(self, score_data: Dict, activity_summary: Dict) -> str:
        """Build context string from score data and activities with XAI enhancements"""
        
        # Extract key information
        overall_score = score_data.get('overall_score', 0)
        grade = score_data.get('grade', 'N/A')
        calculated_at = score_data.get('calculated_at', 'Unknown')
        
        # Start context with label clarification
        context = f"""
# Teaching Effectiveness Indicator Report

**IMPORTANT**: This is a Teaching Effectiveness INDICATOR based on tracked data, not an absolute measure of teaching quality.

## Overall Indicator
- **Indicator Score:** {overall_score:.1f}/100
- **Grade Equivalent:** {grade}
- **Calculated:** {calculated_at}
"""
        
        # Add confidence interval if available
        if 'confidence_interval' in score_data:
            ci = score_data['confidence_interval']
            confidence_level = score_data.get('confidence_level', 'Unknown')
            context += f"- **Confidence Range:** {ci.get('lower', 0):.1f} - {ci.get('upper', 100):.1f}\n"
            context += f"- **Confidence Level:** {confidence_level}\n"
            context += f"- **Calculation Method:** {score_data.get('calculation_method', 'Weighted Components')}\n"
        
        # Add limitations section
        if 'limitations' in score_data:
            context += "\n## Data Limitations & Constraints\n"
            limitations = score_data['limitations']
            if isinstance(limitations, list):
                for limitation in limitations:
                    severity = limitation.get('severity', 'Unknown')
                    lim_type = limitation.get('type', 'Unknown')
                    explanation = limitation.get('explanation', '')
                    context += f"- **[{severity}] {lim_type}:** {explanation}\n"
            else:
                context += "- No major limitations identified\n"
        
        # Add contextual factors
        if 'contextual_factors' in score_data:
            context += "\n## Contextual Factors\n"
            
            # Course difficulty
            if 'course_difficulty' in score_data['contextual_factors']:
                diff = score_data['contextual_factors']['course_difficulty']
                context += f"### Course Difficulty\n"
                context += f"- **Difficulty Level:** {diff.get('difficulty_level', 'Unknown')}\n"
                context += f"- **Difficulty Score:** {diff.get('difficulty_score', 0):.1f}/100\n"
                context += f"- **Explanation:** {diff.get('explanation', 'N/A')}\n\n"
            
            # Cohort behavior
            if 'cohort_behavior' in score_data['contextual_factors']:
                cohort = score_data['contextual_factors']['cohort_behavior']
                context += f"### Cohort Behavior\n"
                context += f"- **Cohort Size:** {cohort.get('cohort_size', 0)} students\n"
                context += f"- **Engagement Level:** {cohort.get('engagement_level', 'Unknown')}\n"
                context += f"- **Behavior Pattern:** {cohort.get('behavior_pattern', 'Unknown')}\n"
                context += f"- **Participation Rate:** {cohort.get('participation_rate', 0):.1f}%\n"
                context += f"- **Explanation:** {cohort.get('explanation', 'N/A')}\n\n"
        
        # Add normalization/baseline data
        if 'normalization' in score_data:
            context += "\n## Baseline & Historical Comparison\n"
            norm = score_data['normalization']
            
            if 'baseline' in norm and norm['baseline'].get('baseline_available'):
                baseline = norm['baseline']
                context += f"### Course Baseline\n"
                context += f"- **Historical Baseline Score:** {baseline.get('baseline_score', 0):.1f}\n"
                context += f"- **Score Range:** {baseline.get('score_range', {}).get('min', 0):.1f} - {baseline.get('score_range', {}).get('max', 0):.1f}\n"
                context += f"- **Trend:** {baseline.get('trend', 'Unknown')}\n"
                context += f"- **Based on:** {baseline.get('historical_count', 0)} previous evaluations\n\n"
            
            if 'self_comparison' in norm and norm['self_comparison'].get('comparison_available'):
                self_comp = norm['self_comparison']
                context += f"### Teacher Self-Comparison\n"
                context += f"- **Current Score:** {self_comp.get('current_score', 0):.1f}\n"
                context += f"- **Previous Average:** {self_comp.get('previous_average', 0):.1f}\n"
                context += f"- **Improvement:** {self_comp.get('improvement', 0):+.1f} ({self_comp.get('improvement_percentage', 0):+.1f}%)\n"
                context += f"- **Trend:** {self_comp.get('trend', 'Unknown')}\n\n"
        
        # Component scores with detailed data
        context += "\n## Component Scores (Tracked Metrics)\n"
        
        components = score_data.get('components', {})
        for component, data in components.items():
            context += f"### {component.replace('_', ' ').title()}\n"
            context += f"- **Score:** {data.get('score', 0):.1f}/100\n"
            context += f"- **Weight:** {data.get('weight', 0)*100:.0f}%\n"
            context += f"- **Contribution to Overall:** {data.get('contribution', 0):.1f} points\n"
            
            # Add detailed explanation data
            if 'explanation' in data:
                context += "- **Tracked Data:**\n"
                for key, value in data['explanation'].items():
                    context += f"  - {key.replace('_', ' ').title()}: {value}\n"
            
            context += "\n"
        
        # Add ML insights if available
        if 'ml_insights' in score_data and score_data['ml_insights']:
            ml = score_data['ml_insights']
            context += "\n## Machine Learning Insights\n"
            context += f"- **Model Used:** {ml.get('model_used', 'Unknown')}\n"
            context += f"- **Predicted Score:** {ml.get('predicted_score', 0):.1f}\n"
            context += f"- **Confidence Level:** {ml.get('confidence_level', 'Unknown')}\n"
            
            if 'feature_importance' in ml:
                context += "- **Most Important Factors:**\n"
                # Sort by importance
                importance = sorted(ml['feature_importance'].items(), 
                                  key=lambda x: x[1], reverse=True)[:5]
                for feature, value in importance:
                    context += f"  - {feature.replace('_', ' ').title()}: {value:.2%}\n"
            context += "\n"
        
        # Add activity summary if available
        if activity_summary:
            context += "\n## Activity Summary (Raw Data)\n"
            for key, value in activity_summary.items():
                context += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        # Add final disclaimer
        context += "\n## Important Notes\n"
        context += "- All scores are based on TRACKED DATA ONLY from the LMS\n"
        context += "- Missing or incomplete data affects accuracy\n"
        context += "- This is an INDICATOR, not a judgment of teaching ability\n"
        context += "- Consider contextual factors (difficulty, cohort, external factors)\n"
        
        return context
    
    def explain_score(self, score_data: Dict, activity_summary: Optional[Dict] = None) -> str:
        """
        Generate an explanation of the teaching score
        
        Args:
            score_data: Teaching score data
            activity_summary: Optional activity summary
        
        Returns:
            Explanation text
        """
        if not self.is_available():
            return "❌ AI explanation service is not available. Please check API configuration."
        
        context = self._build_context(score_data, activity_summary or {})
        
        system_prompt = """You are an educational analytics expert specialized in explaining Teaching Effectiveness Indicators using Explainable AI (XAI) principles.

STRICT REQUIREMENTS - You MUST follow these rules:

1. **Data-Backed Only**: Every statement MUST reference specific data points from the provided metrics. NEVER speculate or make general assumptions.

2. **Explicit Limitations**: If data is insufficient or missing for any component, explicitly state: "Data for [component] is limited/unavailable."

3. **Reference Tracked Metrics**: Only explain using tracked metrics (engagement, quiz scores, attendance, completion rates, sentiment, resource usage, activity patterns).

4. **No Speculation**: NEVER say things like "you probably...", "students might...", or "this could mean...". Only state what the data shows.

5. **Confidence Levels**: Acknowledge confidence levels and data quality. If sample size is small, mention it.

6. **Contextual Factors**: Reference course difficulty and cohort behavior when available.

7. **Disclaimer**: Always remind that this is a Teaching Effectiveness INDICATOR, not an absolute quality measure.

Format:
- Start with data limitations (if any)
- Cite specific metrics for each statement
- Provide confidence level for interpretations
- End with contextual disclaimer

Your tone should be professional, transparent, and scientifically rigorous."""
        
        user_prompt = f"""Based on the following teaching performance data, provide a comprehensive explanation of the Teaching Effectiveness Indicator.

{context}

IMPORTANT: This is an INDICATOR, not absolute quality. Follow XAI principles.

Provide:
1. **Data Limitations**: State any data insufficiencies upfront
2. **Overall Indicator Summary**: Score with confidence level
3. **Strongest Components**: With specific metrics cited
4. **Improvement Areas**: With specific data points
5. **Contextual Factors**: Course difficulty, cohort behavior impact
6. **Disclaimer**: This is an indicator based on available data

REMEMBER: Every statement must be traceable to the data above. NO speculation.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logging.error(f"Error generating score explanation: {str(e)}")
            return f"❌ Error generating explanation: {str(e)}"
    
    def answer_question(self, question: str, score_data: Dict, 
                       activity_summary: Optional[Dict] = None,
                       conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Answer a specific question about teaching scores
        
        Args:
            question: User's question
            score_data: Teaching score data
            activity_summary: Optional activity summary
            conversation_history: Previous conversation messages
        
        Returns:
            Answer to the question
        """
        if not self.is_available():
            return "❌ AI chatbot is not available. Please check API configuration."
        
        context = self._build_context(score_data, activity_summary or {})
        
        system_prompt = """You are an educational analytics expert helping teachers understand their Teaching Effectiveness Indicators using Explainable AI (XAI) principles.

STRICT XAI REQUIREMENTS:

1. **NO SPECULATION**: Only answer based on provided data. If data is missing, explicitly say so.

2. **Cite Sources**: Every answer must reference specific tracked metrics:
   - Engagement scores
   - Quiz performance data
   - Attendance records
   - Lecture completion rates
   - Sentiment analysis
   - Resource usage
   - Activity patterns

3. **State Limitations**: If insufficient data exists for a complete answer, say: "Based on available data... However, [limitation]."

4. **Confidence Levels**: Qualify statements with confidence ("Data shows...", "Limited data suggests...", "Cannot determine from available data...")

5. **Contextual Awareness**: Consider course difficulty, cohort size, and data recency.

6. **Transparent Explanations**: Explain HOW data leads to conclusions, not just the conclusions.

7. **No Generic Advice**: Recommendations must be tied to specific data gaps or patterns.

Example Good Response:
"Your engagement score is 65/100 based on 45 tracked interactions across 12 students over 4 weeks. This is below the 70+ threshold because: (1) Average session time is 15 minutes vs. target 30 minutes, (2) Only 60% of students completed lectures."

Example Bad Response:
"Your engagement seems low. You should try to make lectures more interesting."

Always end with: "This analysis is based on available tracked data and represents an indicator, not absolute teaching quality."
"""
        
        # Build message history
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the teaching performance data:\n\n{context}"}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logging.error(f"Error answering question: {str(e)}")
            return f"❌ Error generating answer: {str(e)}"
    
    def generate_improvement_plan(self, score_data: Dict, 
                                 activity_summary: Optional[Dict] = None) -> str:
        """
        Generate a personalized improvement plan
        
        Args:
            score_data: Teaching score data
            activity_summary: Optional activity summary
        
        Returns:
            Improvement plan text
        """
        if not self.is_available():
            return "❌ AI service is not available. Please check API configuration."
        
        context = self._build_context(score_data, activity_summary or {})
        
        system_prompt = """You are an educational consultant creating personalized improvement plans for teachers.

Your goal: Create a specific, actionable 30-day improvement plan based on teaching performance data.

The plan should:
1. Prioritize the most impactful improvements
2. Include specific, measurable actions
3. Be realistic and achievable
4. Focus on student outcomes
5. Include timeline and milestones"""
        
        user_prompt = f"""Based on this teaching performance data, create a 30-day improvement plan:

{context}

Format the plan with:
- **Week 1-2:** [Immediate actions]
- **Week 3-4:** [Building on progress]
- **Ongoing:** [Continuous improvements]
- **Success Metrics:** [How to measure improvement]
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logging.error(f"Error generating improvement plan: {str(e)}")
            return f"❌ Error generating plan: {str(e)}"
    
    def compare_with_benchmarks(self, score_data: Dict) -> str:
        """
        Compare score with educational benchmarks
        
        Args:
            score_data: Teaching score data
        
        Returns:
            Comparison analysis
        """
        if not self.is_available():
            return "❌ AI service is not available."
        
        context = self._build_context(score_data, {})
        
        prompt = f"""Based on this teaching performance data:

{context}

Compare this performance with typical educational benchmarks and best practices.

Provide:
1. How this score compares to average teaching performance
2. Which components are above/below typical benchmarks
3. What top-performing teachers do differently
4. Specific areas that match or exceed best practices
5. Industry standards for each component
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an educational benchmarking expert with knowledge of teaching performance standards."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logging.error(f"Error generating benchmark comparison: {str(e)}")
            return f"❌ Error generating comparison: {str(e)}"


# Singleton instance
_bot_instance = None


def get_explainer_bot() -> TeachingScoreExplainerBot:
    """Get singleton explainer bot instance"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = TeachingScoreExplainerBot()
    return _bot_instance
