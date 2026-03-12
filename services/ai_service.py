import os
import json
import time
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

class AIService:
    def __init__(self):
        # Support for both Google Gemini and OpenAI
        self.google_key = os.environ.get('GOOGLE_API_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
        if self.google_key:
            genai.configure(api_key=self.google_key)
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                print(f"AI Service: Found {len(available_models)} available models.")
                
                # Filter for flash models first, then pro
                # Specifically try to find latest stable flash models, using Gemma first due to Gemini quota issues
                pref = next((m for m in available_models if 'gemma-3-4b' in m.lower()),
                            next((m for m in available_models if 'gemma-3-1b' in m.lower()),
                            next((m for m in available_models if '2.0-flash' in m.lower()),
                            next((m for m in available_models if '2.5-flash' in m.lower()), 
                            next((m for m in available_models if '1.5-flash' in m.lower()), 
                            next((m for m in available_models if 'flash-latest' in m.lower()),
                            next((m for m in available_models if 'flash' in m.lower() and 'lite' not in m.lower()), 
                                 next((m for m in available_models if 'pro' in m.lower()), 
                                      available_models[0]))))))))
                
                self.google_model = genai.GenerativeModel(pref)
                print(f"AI Service: Selected model: {pref}")
            except Exception as e:
                print(f"Gemini Init Error: {e}")
                # Try a safe default
                try:
                    self.google_model = genai.GenerativeModel("gemini-1.5-flash")
                except:
                    self.google_model = None
        else:
            self.google_model = None
            print("AI Service: No Google API Key found")

    def _call_ai(self, system_prompt, user_text, is_json=False):
        """Unified method to call Gemini."""
        if not self.google_key:
            return None

        full_prompt = f"{system_prompt}\n\nContent:\n{user_text}"
        
        try:
            if self.google_model:
                print(f"AI Service: Calling {self.google_model.model_name} (JSON={is_json})... Prompt size: {len(full_prompt)}")
                
                config = None
                if is_json:
                    # Only use JSON mode if NOT using a Gemma model (which hits 400 error)
                    if 'gemma' not in self.google_model.model_name.lower():
                        config = genai.GenerationConfig(response_mime_type="application/json")
                
                # Simple retry logic for 429 (Quota)
                for attempt in range(3):
                    try:
                        response = self.google_model.generate_content(
                            full_prompt,
                            generation_config=config
                        )
                        
                        # Handle safety blocks or empty responses
                        if not response:
                            print("AI Service: Empty response object.")
                            return None
                            
                        try:
                            if response.text:
                                print(f"Gemini raw response (truncated): {response.text[:100]}...")
                                return response.text
                        except Exception as safety_err:
                            print(f"AI Safety Block or Response Access Error: {safety_err}")
                            # Detailed debug for user
                            if hasattr(response, 'candidates') and response.candidates:
                                print(f"Finish Reason: {response.candidates[0].finish_reason}")
                            return None
                            
                    except Exception as e:
                        if ("429" in str(e) or "quota" in str(e).lower()) and attempt < 2:
                            # Increase wait time to 40s to respect free tier and busy periods
                            print(f"AI Service: Quota limit hit (Attempt {attempt+1}). Waiting 40s for reset...")
                            time.sleep(40)
                            continue
                        print(f"AI Request Error: {e}")
                        raise e
            else:
                return None
        except Exception as e:
            print(f"AI Call Critical Error: {e}")
            return None

    def generate_summary(self, text):
        prompt = "Summarize the study material into 3 concise paragraphs for a student."
        try:
            result = self._call_ai(prompt, text)
            return result if result else "Summary generation temporarily unavailable due to AI quota limits."
        except Exception:
            return "Summary generation failed."

    def _clean_json(self, text):
        if not text: return ""
        text = text.strip()
        if text.startswith('```'):
            # Remove leading ```json or ```
            text = text.split('\n', 1)[-1] if '\n' in text else text.strip('`')
            # Remove trailing ```
            if text.endswith('```'): text = text[:-3]
        return text.strip()

    def generate_flashcards(self, text):
        prompt = """Generate 15 detailed flashcards based on the material. 
        You MUST provide exactly 5 cards for each difficulty level: 5 easy, 5 medium, and 5 hard.
        JSON format: {"flashcards": [{"question": "...", "answer": "...", "difficulty": "easy|medium|hard"}]}"""
        result = self._call_ai(prompt, text, is_json=True)
        if not result: return []
        try:
            cleaned = self._clean_json(result)
            data = json.loads(cleaned)
            for key in ['flashcards', 'cards', 'items']:
                if key in data: return data[key]
            if isinstance(data, list): return data
            return []
        except Exception as e:
            print(f"Flashcard Parse Error: {e}\nRaw: {result}")
            return []

    def generate_quizzes(self, text):
        prompt = "Generate 5 MCQs in JSON format: {\"quizzes\": [{\"question\": \"...\", \"options\": [\"...\"], \"correct\": \"...\", \"explanation\": \"...\"}]}"
        result = self._call_ai(prompt, text, is_json=True)
        if not result: return []
        try:
            cleaned = self._clean_json(result)
            data = json.loads(cleaned)
            for key in ['quizzes', 'questions', 'items']:
                if key in data: return data[key]
            if isinstance(data, list): return data
            return []
        except Exception as e:
            print(f"Quiz Parse Error: {e}")
            return []

    def generate_learning_path(self, text):
        prompt = """Generate a comprehensive 5-module learning path based on the content.
        Each module must have a clear title, a detailed 2-sentence description, and an assigned difficulty (easy|medium|hard).
        JSON format: {"path": [{"title": "...", "description": "...", "difficulty": "..."}]}"""
        result = self._call_ai(prompt, text, is_json=True)
        if not result: return []
        try:
            cleaned = self._clean_json(result)
            data = json.loads(cleaned)
            # Support multiple possible keys the AI might use
            for key in ['path', 'learning_path', 'modules', 'steps']:
                if key in data:
                    return data[key]
            # If it's just a top-level list
            if isinstance(data, list): return data
            return []
        except Exception as e:
            print(f"Path Parse Error: {e}\nRaw: {result}")
            return []

    def answer_question(self, material_text, question):
        prompt = f"Answer questions based on this study material: {material_text}"
        return self._call_ai(prompt, question)

    def generate_exam_booster(self, text):
        """Generates rapid revision notes and probable questions with descriptive answers."""
        prompt = """Based on the provided material, generate an Exam Booster set:
        1. Rapid Revision Notes: Exactly 12 high-impact bullet points. 
           EACH point must be on a NEW LINE. Do NOT use HTML tags (like <ul> or <li>) and do NOT use Markdown (like **).
        2. Probable Exam Questions: Exactly 5 descriptive-type questions. 
           For each question, provides a detailed "answer" (2-3 sentences) explaining the concept.
        
        Format your response as a JSON object:
        {
            "revision_notes": "First important point\\nSecond important point\\nThird important point...",
            "probable_questions": [
                {"question": "...", "answer": "...", "topic": "...", "importance": "High/Medium"}
            ]
        }"""
        
        result = self._call_ai(prompt, text, is_json=True)
        if not result:
            return None
            
        try:
            cleaned = self._clean_json(result)
            return json.loads(cleaned)
        except Exception as e:
            print(f"Exam Booster Parse Error: {e}")
            return None
