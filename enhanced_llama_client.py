import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()


class EnhancedLlamaAIClient:
    """Enhanced client for generating section-specific inline annotations."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("LLAMA_API_KEY"),
            base_url="https://api.llama.com/compat/v1/",
        )
        self.model = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    
    def generate_inline_annotations(self, lesson_content: str, parameters: Dict) -> Dict:
        """Generate section-specific annotations optimized for inline placement."""
        
        prompt = self._build_inline_annotation_prompt(lesson_content, parameters)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational consultant specializing in creating concise, actionable inline annotations for lesson plans. Provide brief, specific recommendations that can be easily integrated alongside lesson content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500  # Reduced for more concise annotations
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
    
    def _build_inline_annotation_prompt(self, lesson_content: str, parameters: Dict) -> str:
        """Build prompt optimized for inline annotations."""
        
        custom_guidelines = parameters.get('custom_guidelines', '')
        
        prompt = f"""
Analyze this lesson plan and provide CONCISE, ACTIONABLE annotations that will be placed inline with the lesson content.

ANNOTATION PARAMETERS:
- Focus Areas: {', '.join(parameters.get('focus_areas', []))}
- Pedagogical Approach: {parameters.get('pedagogical_approach', 'Balanced')}
- Student Engagement Level: {parameters.get('engagement_level', 'High')}
- Assessment Type: {parameters.get('assessment_type', 'Formative')}
- Language Focus: {parameters.get('language_focus', 'Spanish')}
- Age Group: {parameters.get('age_group', '5-6 years')}

{f"CUSTOM GUIDELINES: {custom_guidelines}" if custom_guidelines else ""}

LESSON PLAN CONTENT:
{lesson_content}

Provide annotations in the following format. Keep each recommendation to 1-2 sentences maximum for inline placement:

## OBJECTIVES ENHANCEMENT
- [Brief engagement suggestion for objectives]
- [Quick improvement for clarity]

## MATERIALS OPTIMIZATION  
- [Specific resource enhancement]
- [Cost-effective alternative suggestion]

## ACTIVITY DIFFERENTIATION
- [Simple modification for different learners]
- [Quick extension for advanced students]

## ENGAGEMENT BOOSTERS
- [Immediate engagement technique]
- [Interactive element to add]

## ASSESSMENT INTEGRATION
- [Quick formative assessment idea]
- [Simple progress monitoring technique]

## EXTENSION OPPORTUNITIES
- [Brief follow-up activity]
- [Connection to other subjects]

## CULTURAL CONSIDERATIONS
- [Language-specific insight]
- [Cultural relevance enhancement]

## IMPLEMENTATION TIPS
- [Practical classroom management tip]
- [Time-saving suggestion]

Focus on practical, immediately implementable suggestions that teachers can apply without major lesson restructuring.
"""
        return prompt


class SectionSpecificAnnotator:
    """Generate annotations specific to lesson plan sections."""
    
    def __init__(self):
        self.ai_client = EnhancedLlamaAIClient()
    
    def annotate_lesson_sections(self, lesson_sections: Dict, parameters: Dict) -> Dict:
        """Generate targeted annotations for specific lesson sections."""
        
        section_annotations = {}
        
        # Annotate objectives
        if lesson_sections.get('objectives'):
            section_annotations['objectives'] = self._annotate_objectives(
                lesson_sections['objectives'], parameters
            )
        
        # Annotate materials
        if lesson_sections.get('materials'):
            section_annotations['materials'] = self._annotate_materials(
                lesson_sections['materials'], parameters
            )
        
        # Annotate activities
        activities_annotations = []
        for i, activity in enumerate(lesson_sections.get('activities', [])):
            activity_annotation = self._annotate_activity(activity, parameters, i+1)
            activities_annotations.append(activity_annotation)
        section_annotations['activities'] = activities_annotations
        
        # Annotate assessment
        if lesson_sections.get('assessment'):
            section_annotations['assessment'] = self._annotate_assessment(
                lesson_sections['assessment'], parameters
            )
        
        return section_annotations
    
    def _annotate_objectives(self, objectives_text: str, parameters: Dict) -> List[str]:
        """Generate specific annotations for learning objectives."""
        prompt = f"""
Analyze these learning objectives and provide 2-3 brief suggestions:

OBJECTIVES: {objectives_text}

Focus on: {', '.join(parameters.get('focus_areas', []))}

Provide concise suggestions for:
1. Making objectives more measurable/observable
2. Enhancing student engagement with objectives  
3. Connecting to {parameters.get('language_focus', 'language')} development

Keep each suggestion to 1 sentence.
"""
        
        try:
            response = self.ai_client.client.chat.completions.create(
                model=self.ai_client.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip('123.-• ') for s in suggestions if s.strip()][:3]
            
        except Exception as e:
            return [f"Consider making objectives more specific and measurable for {parameters.get('age_group', 'students')}"]
    
    def _annotate_materials(self, materials_text: str, parameters: Dict) -> List[str]:
        """Generate specific annotations for materials list."""
        return [
            "Consider digital alternatives to reduce prep time",
            f"Add manipulatives for {parameters.get('pedagogical_approach', 'hands-on')} learning",
            "Prepare differentiated materials for various learning levels"
        ]
    
    def _annotate_activity(self, activity_text: str, parameters: Dict, activity_num: int) -> List[str]:
        """Generate specific annotations for individual activities."""
        focus_areas = parameters.get('focus_areas', [])
        
        suggestions = [
            f"Add movement/gesture for kinesthetic learners" if 'Phonological' in focus_areas else "Consider adding visual supports",
            f"Include peer interaction opportunities" if parameters.get('engagement_level') == 'High' else "Add individual practice time",
            f"Provide sentence frames for language support" if 'Spanish' in parameters.get('language_focus', '') else "Add vocabulary scaffolding"
        ]
        
        return suggestions[:2]
    
    def _annotate_assessment(self, assessment_text: str, parameters: Dict) -> List[str]:
        """Generate specific annotations for assessment strategies."""
        return [
            f"Use {parameters.get('assessment_type', 'formative')} observation checklist",
            "Include student self-reflection component",
            "Document progress for differentiation planning"
        ]