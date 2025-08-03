// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const lessonPlanText = document.getElementById('lessonPlanText');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('resultsSection');
const annotations = document.getElementById('annotations');

// File upload handling
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Handle file upload
function handleFile(file) {
    const reader = new FileReader();
    
    reader.onload = (e) => {
        lessonPlanText.value = e.target.result;
        
        // Update upload area to show file is loaded
        const uploadContent = uploadArea.querySelector('.upload-content');
        uploadContent.innerHTML = `
            <div class="upload-icon">✅</div>
            <p><strong>File loaded:</strong> ${file.name}</p>
            <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                Choose Different File
            </button>
        `;
    };
    
    reader.readAsText(file);
}

// Analyze lesson plan
analyzeBtn.addEventListener('click', () => {
    const text = lessonPlanText.value.trim();
    
    if (!text) {
        alert('Please upload a file or enter lesson plan text to analyze.');
        return;
    }
    
    showLoading();
    
    // Simulate AI analysis (in a real app, this would call an AI API)
    setTimeout(() => {
        generateAnnotations(text);
    }, 2000);
});

// Show loading state
function showLoading() {
    resultsSection.style.display = 'block';
    annotations.innerHTML = '<div class="loading">Analyzing lesson plan with AI</div>';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Generate mock annotations (in a real app, this would be AI-generated)
function generateAnnotations(text) {
    const mockAnnotations = [
        {
            title: "Learning Objectives Analysis",
            content: "The lesson plan contains clear, measurable learning objectives that align with educational standards. Consider adding more specific success criteria for each objective."
        },
        {
            title: "Engagement Strategies",
            content: "Good use of interactive elements. Suggestion: Add more opportunities for peer collaboration and discussion to increase student engagement."
        },
        {
            title: "Assessment Methods",
            content: "The assessment approach is well-structured. Consider incorporating formative assessment checkpoints throughout the lesson to gauge understanding."
        },
        {
            title: "Differentiation Opportunities",
            content: "The lesson could benefit from more differentiation strategies to accommodate diverse learning styles and abilities. Consider adding visual, auditory, and kinesthetic learning options."
        },
        {
            title: "Time Management",
            content: "The lesson timeline appears realistic. Ensure buffer time is included for transitions and unexpected discussions that may arise."
        },
        {
            title: "Technology Integration",
            content: "Consider incorporating digital tools or multimedia resources to enhance the learning experience and prepare students for digital literacy."
        }
    ];
    
    // Add text-specific insights based on content
    const additionalInsights = analyzeTextContent(text);
    
    const allAnnotations = [...mockAnnotations, ...additionalInsights];
    
    displayAnnotations(allAnnotations);
}

// Simple text analysis for additional insights
function analyzeTextContent(text) {
    const insights = [];
    const wordCount = text.split(/\s+/).length;
    const sentences = text.split(/[.!?]+/).length;
    
    insights.push({
        title: "Content Analysis",
        content: `Your lesson plan contains approximately ${wordCount} words and ${sentences} sentences. This suggests a ${wordCount > 500 ? 'comprehensive' : 'concise'} lesson structure.`
    });
    
    // Check for key educational terms
    const keyTerms = ['objective', 'assessment', 'activity', 'discussion', 'homework', 'evaluation'];
    const foundTerms = keyTerms.filter(term => 
        text.toLowerCase().includes(term)
    );
    
    if (foundTerms.length > 0) {
        insights.push({
            title: "Educational Structure",
            content: `Great! Your lesson plan includes key educational components: ${foundTerms.join(', ')}. This shows good pedagogical structure.`
        });
    }
    
    return insights;
}

// Display annotations in the UI
function displayAnnotations(annotationList) {
    annotations.innerHTML = annotationList.map(annotation => `
        <div class="annotation-item">
            <h3>${annotation.title}</h3>
            <p>${annotation.content}</p>
        </div>
    `).join('');
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Lesson Plan Annotator loaded successfully!');
});