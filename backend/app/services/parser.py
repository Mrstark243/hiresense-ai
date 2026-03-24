import fitz  # PyMuPDF
import re

class ResumeParser:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extracts text from a PDF file."""
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"Error extracting text: {e}")
        return text

    @staticmethod
    def clean_text(text: str) -> str:
        """Cleans extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove special characters but keep punctuation
        # text = re.sub(r'[^\w\s\.,;:\-\(\)@]', '', text)
        return text

    @staticmethod
    def segment_sections(text: str) -> dict:
        """Rudimentary segmentation of resume sections."""
        sections = {
            "contact": "",
            "summary": "",
            "experience": "",
            "education": "",
            "skills": "",
            "projects": "",
            "other": ""
        }
        
        # Simple keyword-based segmentation
        keywords = {
            "summary": ["summary", "profile", "objective"],
            "experience": ["experience", "work history", "employment", "professional background"],
            "education": ["education", "academic", "degree"],
            "skills": ["skills", "technical skills", "competencies", "technologies"],
            "projects": ["projects", "personal projects", "portfolio"],
            "other": ["certifications", "awards", "languages", "interests"]
        }
        
        # This is a very basic implementation. For production, more advanced NLP or regex would be used.
        # Here we just keep the whole text for RAG to handle.
        sections["full_text"] = text
        return sections
