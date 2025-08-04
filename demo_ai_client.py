#!/usr/bin/env python3
"""
Demo AI client that provides sample annotations when no real API key is available.
This allows users to test the application without needing actual API keys.
"""

from typing import Dict
import json
import time


class DemoAIClient:
    """Demo client that provides sample annotations for testing."""
    
    def __init__(self):
        self.demo_mode = True
    
    def generate_annotations(self, lesson_content: str, annotation_parameters: Dict) -> Dict:
        """Generate sample annotations for demonstration purposes."""
        
        # Simulate processing time
        time.sleep(2)
        
        # Sample annotation content based on typical lesson plan analysis
        sample_annotations = """
### 1. **Pedagogical Strengths**

• **Clear learning objectives**: The lesson plan demonstrates well-defined, age-appropriate goals for kindergarten Spanish phonics
• **Structured progression**: Activities build systematically from recognition to production
• **Multi-sensory approach**: Incorporates visual, auditory, and kinesthetic learning elements

### 2. **Student Engagement Opportunities**

• **Interactive games**: Include more hands-on phonetic games and movement activities
• **Peer collaboration**: Add partner work for practicing letter sounds together  
• **Technology integration**: Consider using educational apps or interactive whiteboards for sound recognition

### 3. **Differentiation Strategies**

• **Visual supports**: Provide picture cards and visual cues for different learning styles
• **Scaffolding**: Offer varying levels of support for students at different phonetic awareness stages
• **Multiple modalities**: Include tactile letter tracing and musical phonics songs

### 4. **Assessment Suggestions**

• **Formative checks**: Implement quick sound recognition checks throughout the lesson
• **Portfolio evidence**: Collect samples of student work for ongoing assessment
• **Observational rubrics**: Use simple checklists to track individual student progress

### 5. **Areas for Improvement**

• **Time management**: Consider breaking complex activities into shorter segments
• **Material preparation**: Ensure all visual aids and manipulatives are ready before class
• **Transition planning**: Add clear signals and routines for moving between activities

### 6. **Resource Optimization**

• **Cultural connections**: Incorporate familiar Spanish songs or rhymes from students' backgrounds
• **Home-school links**: Provide take-home materials for family practice
• **Community resources**: Connect with Spanish-speaking community members as classroom helpers

### 7. **Extension Activities**

• **Creative expression**: Add art projects that incorporate letter sounds and vocabulary
• **Real-world connections**: Include activities that relate phonics to students' daily experiences
• **Technology enhancement**: Use apps that provide immediate feedback on pronunciation

### 8. **Cultural/Linguistic Considerations**

• **Bilingual scaffolding**: Support students transitioning between Spanish and English phonetic systems
• **Cultural relevance**: Ensure examples and contexts reflect students' cultural backgrounds
• **Family engagement**: Provide materials in both languages for home support
"""
        
        return {
            "success": True,
            "annotations": sample_annotations,
            "usage": {
                "prompt_tokens": 850,
                "completion_tokens": 450,
                "total_tokens": 1300
            },
            "demo_mode": True,
            "demo_message": "🎭 DEMO MODE: These are sample annotations. For real AI analysis, add your OpenAI API key to the .env file."
        }


def create_ai_client():
    """Factory function to create appropriate AI client based on available API keys."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.environ.get("LLAMA_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    # Always use real AI client - no demo mode fallback
    from llama_client import LlamaAIClient
    return LlamaAIClient()