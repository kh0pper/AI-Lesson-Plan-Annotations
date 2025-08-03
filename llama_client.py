import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()


class LlamaAIClient:
    """Client for interacting with Llama AI API."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("LLAMA_API_KEY"),
            base_url="https://api.llama.com/compat/v1/",
        )
        self.model = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    
    def generate_annotations(self, lesson_content: str, annotation_parameters: Dict) -> Dict:
        """Generate intelligent annotations for lesson plan content."""
        
        prompt = self._build_annotation_prompt(lesson_content, annotation_parameters)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational consultant specializing in Spanish language learning and kindergarten pedagogy. Provide detailed, actionable annotations for lesson plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return {
                "success": True,
                "annotations": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "annotations": None
            }
    
    def _build_annotation_prompt(self, lesson_content: str, parameters: Dict) -> str:
        """Build the prompt for annotation generation."""
        
        custom_guidelines = parameters.get('custom_guidelines', '')
        
        prompt = f"""
Please analyze and annotate this lesson plan with the following parameters:

ANNOTATION PARAMETERS:
- Focus Areas: {', '.join(parameters.get('focus_areas', []))}
- Pedagogical Approach: {parameters.get('pedagogical_approach', 'Balanced')}
- Student Engagement Level: {parameters.get('engagement_level', 'High')}
- Assessment Type: {parameters.get('assessment_type', 'Formative')}
- Differentiation Needs: {parameters.get('differentiation', 'Multi-level')}
- Language Focus: {parameters.get('language_focus', 'Spanish')}
- Age Group: {parameters.get('age_group', '5-6 years')}

{f"CUSTOM GUIDELINES: {custom_guidelines}" if custom_guidelines else ""}

LESSON PLAN CONTENT:
{lesson_content}

Please provide annotations in the following categories:

{self._get_annotation_categories(parameters)}

Provide specific, actionable recommendations that a kindergarten teacher could immediately implement.
"""
        return prompt
    
    def _get_annotation_categories(self, parameters: Dict) -> str:
        """Generate annotation categories based on theme and custom definitions."""
        custom_categories = parameters.get('custom_category_definitions', {})
        
        if custom_categories:
            # Use custom user-defined categories
            categories = []
            for i, (category_key, definition) in enumerate(custom_categories.items(), 1):
                categories.append(f"{i}. **{definition}**: Provide specific insights and recommendations related to: {definition}")
            return "\n\n".join(categories)
        else:
            # Use default predefined categories
            return """1. **Pedagogical Strengths**: What teaching strategies are particularly effective?

2. **Student Engagement Opportunities**: How can student participation be enhanced?

3. **Assessment Suggestions**: Recommended formative and summative assessment strategies.

4. **Differentiation Strategies**: How to accommodate different learning levels and styles.

5. **Resource Optimization**: Suggestions for better use of materials and time.

6. **Extension Activities**: Additional activities to deepen learning.

7. **Areas for Improvement**: Constructive suggestions for enhancement.

8. **Cultural/Linguistic Considerations**: Spanish language learning specific insights."""