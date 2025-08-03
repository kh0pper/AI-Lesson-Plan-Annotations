from typing import Dict, List
from dataclasses import dataclass


@dataclass
class AnnotationParameters:
    """Predefined parameters for lesson plan annotation."""
    
    focus_areas: List[str]
    pedagogical_approach: str
    engagement_level: str
    assessment_type: str
    differentiation: str
    language_focus: str
    age_group: str


class ParameterPresets:
    """Predefined parameter sets for different annotation needs."""
    
    @staticmethod
    def kindergarten_phonics() -> AnnotationParameters:
        """Parameters specifically for kindergarten phonics lessons."""
        return AnnotationParameters(
            focus_areas=[
                "Phonological Awareness",
                "Letter-Sound Correspondence", 
                "Vocabulary Development",
                "Oral Language Skills",
                "Fine Motor Development"
            ],
            pedagogical_approach="Multisensory Learning",
            engagement_level="High Interactive",
            assessment_type="Formative Observation",
            differentiation="Multi-level Support",
            language_focus="Spanish L1 Development",
            age_group="5-6 years"
        )
    
    @staticmethod
    def general_kindergarten() -> AnnotationParameters:
        """General parameters for kindergarten lessons."""
        return AnnotationParameters(
            focus_areas=[
                "Student Engagement",
                "Differentiated Instruction",
                "Assessment Strategies",
                "Classroom Management",
                "Learning Objectives"
            ],
            pedagogical_approach="Play-based Learning",
            engagement_level="High",
            assessment_type="Formative",
            differentiation="Universal Design for Learning",
            language_focus="Spanish Native",
            age_group="5-6 years"
        )
    
    @staticmethod
    def spanish_literacy() -> AnnotationParameters:
        """Parameters for Spanish literacy development."""
        return AnnotationParameters(
            focus_areas=[
                "Reading Comprehension",
                "Phonemic Awareness",
                "Vocabulary Building",
                "Writing Skills",
                "Cultural Context"
            ],
            pedagogical_approach="Balanced Literacy",
            engagement_level="Interactive",
            assessment_type="Authentic Assessment",
            differentiation="Tiered Instruction",
            language_focus="Spanish Language Arts",
            age_group="5-8 years"
        )
    
    @staticmethod
    def custom_parameters(
        focus_areas: List[str] = None,
        pedagogical_approach: str = "Constructivist",
        engagement_level: str = "High",
        assessment_type: str = "Formative",
        differentiation: str = "Multi-level",
        language_focus: str = "Spanish",
        age_group: str = "5-6 years"
    ) -> AnnotationParameters:
        """Create custom annotation parameters."""
        
        if focus_areas is None:
            focus_areas = [
                "Student Learning",
                "Engagement",
                "Assessment",
                "Differentiation"
            ]
        
        return AnnotationParameters(
            focus_areas=focus_areas,
            pedagogical_approach=pedagogical_approach,
            engagement_level=engagement_level,
            assessment_type=assessment_type,
            differentiation=differentiation,
            language_focus=language_focus,
            age_group=age_group
        )
    
    @staticmethod
    def get_available_presets() -> Dict[str, str]:
        """Return available parameter presets with descriptions."""
        return {
            "kindergarten_phonics": "Specialized for K-phonics lessons with multisensory approach",
            "general_kindergarten": "General K-level parameters with play-based learning",
            "spanish_literacy": "Spanish language arts with balanced literacy approach",
            "custom": "User-defined parameters"
        }


def parameters_to_dict(params: AnnotationParameters) -> Dict:
    """Convert AnnotationParameters to dictionary format."""
    return {
        "focus_areas": params.focus_areas,
        "pedagogical_approach": params.pedagogical_approach,
        "engagement_level": params.engagement_level,
        "assessment_type": params.assessment_type,
        "differentiation": params.differentiation,
        "language_focus": params.language_focus,
        "age_group": params.age_group
    }