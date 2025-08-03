# Contributing to AI Lesson Plan Annotator

Thank you for your interest in contributing to the AI Lesson Plan Annotator! This document provides guidelines for contributing to the project.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/AI-Lesson-Plan-Annotations.git
   cd AI-Lesson-Plan-Annotations
   ```
3. **Set up development environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Create required directories**
   ```bash
   mkdir -p uploads downloads
   ```
5. **Copy environment file**
   ```bash
   cp .env.example .env
   # Add your API key to .env
   ```

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Testing
- Test your changes locally before submitting
- Run the test script: `python test_server.py`
- Ensure the web interface works properly
- Test with different PDF files if possible

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Include relevant emojis for clarity
- Example: `✨ Add support for new annotation parameters`

## 🛠️ Areas for Contribution

### High Priority
- **Additional Language Support**: Extend beyond Spanish to other languages
- **More Annotation Presets**: Add presets for different grade levels and subjects
- **Improved PDF Processing**: Better text extraction and layout preservation
- **Enhanced UI/UX**: Improve the web interface and user experience

### Medium Priority
- **API Endpoints**: Create REST API for programmatic access
- **Batch Processing**: Support for processing multiple files at once
- **Export Formats**: Add support for other output formats (Word, etc.)
- **User Authentication**: Add user accounts and file management

### Low Priority
- **Performance Optimization**: Improve processing speed and memory usage
- **Advanced Analytics**: Add usage statistics and insights
- **Mobile Responsiveness**: Improve mobile web interface
- **Docker Support**: Add containerization for easy deployment

## 🐛 Bug Reports

When reporting bugs, please include:
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Error messages (if any)
- Your environment (OS, Python version, etc.)
- Sample files (if relevant and not sensitive)

## 💡 Feature Requests

For new features, please:
- Check if the feature already exists or is planned
- Describe the use case and benefits
- Provide examples or mockups if helpful
- Consider implementation complexity

## 🔧 Technical Architecture

### Core Components
- **Flask Web App** (`app.py`): Main web interface
- **Lesson Annotator** (`lesson_annotator.py`): Core processing logic
- **PDF Extractor** (`pdf_extractor.py`): PDF text extraction
- **AI Client** (`llama_client.py`): Integration with Llama AI
- **PDF Annotator** (`pdf_annotator.py`): Generate annotated PDFs
- **Parameters** (`annotation_parameters.py`): Configuration management

### File Structure
```
├── app.py                    # Flask web application
├── lesson_annotator.py      # Core annotation logic
├── pdf_extractor.py         # PDF processing
├── llama_client.py          # AI integration
├── pdf_annotator.py         # PDF generation
├── annotation_parameters.py # Configuration
├── templates/               # HTML templates
├── static/                  # CSS, JS files
└── requirements.txt         # Dependencies
```

## 📝 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, well-documented code
   - Test thoroughly
   - Update documentation if needed

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "✨ Add your feature description"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Provide a clear title and description
   - Link any related issues
   - Include screenshots for UI changes
   - List any breaking changes

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Report any inappropriate behavior

## 📞 Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the README.md for setup and usage

## 🎯 Beginner-Friendly Tasks

Looking for your first contribution? Try these:
- Improve documentation and examples
- Add more preset configurations
- Enhance error messages and user feedback
- Write additional test cases
- Fix typos and formatting issues

Thank you for contributing to make lesson plan annotation better for educators! 🎓