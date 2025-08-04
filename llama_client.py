import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()


class LlamaAIClient:
    """Client for interacting with Llama AI API."""
    
    def __init__(self):
        api_key = os.environ.get("LLAMA_API_KEY") or os.environ.get("OPENAI_API_KEY")
        
        if not api_key or api_key.startswith("demo_key"):
            raise ValueError(
                "❌ AI API Key Required!\n\n"
                "To use the AI annotation feature, you need a valid API key:\n"
                "1. Get an OpenAI API key from: https://platform.openai.com/api-keys\n"
                "2. Or get a Llama API key from: https://api.llama.com/\n"
                "3. Edit the .env file and replace 'demo_key_replace_with_real_key' with your actual key\n"
                "4. Restart the application\n\n"
                "The app will work for user registration and profile management without an API key,\n"
                "but PDF annotation requires a valid AI service key."
            )
        
        self.client = OpenAI(
            api_key=api_key,
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
            error_message = str(e)
            
            # Provide more helpful error messages for common issues
            if "401" in error_message or "Authentication" in error_message:
                error_message = (
                    "❌ Invalid API Key!\n\n"
                    "Your AI API key is not valid. Please:\n"
                    "1. Check your API key at: https://platform.openai.com/api-keys\n"
                    "2. Make sure you have credit/quota available\n"
                    "3. Update the .env file with a valid key\n"
                    "4. Restart the application\n\n"
                    f"Original error: {error_message}"
                )
            elif "429" in error_message:
                error_message = (
                    "⏱️ Rate Limit Exceeded!\n\n"
                    "You've hit the API rate limit. Please:\n"
                    "1. Wait a few minutes before trying again\n"
                    "2. Check your API quota at: https://platform.openai.com/usage\n"
                    "3. Consider upgrading your API plan if needed\n\n"
                    f"Original error: {error_message}"
                )
            elif "quota" in error_message.lower():
                error_message = (
                    "💳 Quota Exceeded!\n\n"
                    "Your API quota has been exceeded. Please:\n"
                    "1. Add credits to your account at: https://platform.openai.com/settings/organization/billing\n"
                    "2. Check your usage at: https://platform.openai.com/usage\n"
                    "3. Wait until your quota resets (if on free tier)\n\n"
                    f"Original error: {error_message}"
                )
            
            return {
                "success": False,
                "error": error_message,
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