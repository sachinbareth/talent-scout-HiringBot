from typing import Dict, List, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re
from datetime import datetime
from pathlib import Path
from app.utils.config import Config
from app.utils.prompts import Prompts

class DataHandler:
    def __init__(self, storage_path: str = "chatbot_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self._init_session()

    def _init_session(self):
        """Initialize a new session with enhanced data structure"""
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.data = {
            "session_id": self.session_id,
            "candidate": {
                "name": None,
                "original_email": None,
                "anonymized_email": None,
                "tech_stack": [],
                "experience": None,
                "role": None
            },
            "full_conversation": [],
            "technical_qa": [],
            "timestamps": {
                "start": datetime.now().isoformat(),
                "end": None
            },
            "statistics": {
                "total_messages": 0,
                "questions_asked": 0
            }
        }

    def save_to_json(self, final_save: bool = False):
        """Save current session data to JSON file"""
        if final_save:
            self.data["timestamps"]["end"] = datetime.now().isoformat()
        
        filename = f"session_{self.session_id}.json"
        filepath = self.storage_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.get_complete_data(), f, indent=2, ensure_ascii=False)
        return filepath

    def anonymize_email(self, email: str) -> str:
        """Generate anonymized email while preserving original"""
        if not email or "@" not in email:
            return "anonymous@example.com"
        
        self.data["candidate"]["original_email"] = email
        anonymized = f"user{abs(hash(email)) % 10000}@example.com"
        self.data["candidate"]["anonymized_email"] = anonymized
        return anonymized

    def update_info(self, field: str, value: Any):
        """Update candidate info with validation"""
        if field == "name" and value:
            self.data["candidate"]["name"] = self._clean_text(value)
        elif field == "email" and value:
            self.anonymize_email(value)
        elif field == "tech_stack" and value:
            self.data["candidate"]["tech_stack"] = self._parse_tech_stack(value)
        elif field in ["experience", "role"] and value:
            self.data["candidate"][field] = self._clean_text(value)
        
        self.save_to_json()

    def add_conversation(self, user_input: str, response: str, stage: str):
        """Record conversation with metadata, avoiding duplicates"""
        if stage == "technical_questions" and not user_input.strip():
            return
            
        conversation_entry = {
            "stage": stage,
            "user_input": self._clean_text(user_input),
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.data["full_conversation"] or conversation_entry != self.data["full_conversation"][-1]:
            self.data["full_conversation"].append(conversation_entry)
            self.data["statistics"]["total_messages"] += 1
        
            if stage == "technical_questions" and user_input.strip():
                if (not self.data["technical_qa"] or 
                    response != self.data["technical_qa"][-1]["question"]):
                    
                    qa_entry = {
                        "question": response,
                        "answer": user_input,
                        "timestamp": conversation_entry["timestamp"]
                    }
                    self.data["technical_qa"].append(qa_entry)
                    self.data["statistics"]["questions_asked"] += 1
        
        self.save_to_json()

    def get_complete_data(self) -> Dict[str, Any]:
        """Return complete data including original info and Q&A"""
        return {
            "session_id": self.session_id,
            "candidate": {
                "name": self.data["candidate"]["name"],
                "original_email": self.data["candidate"]["original_email"],
                "anonymized_email": self.data["candidate"]["anonymized_email"],
                "tech_stack": self.data["candidate"]["tech_stack"],
                "experience": self.data["candidate"]["experience"],
                "role": self.data["candidate"]["role"]
            },
            "full_conversation": self.data["full_conversation"],
            "technical_qa": self.data["technical_qa"],
            "statistics": self.data["statistics"],
            "timestamps": self.data["timestamps"]
        }

    def _clean_text(self, text: str) -> str:
        """Basic sanitization preserving special characters in answers"""
        if not text:
            return ""
        return re.sub(r'[^\w\s,.!?@-]', '', str(text).strip())

    def _parse_tech_stack(self, tech_input) -> List[str]:
        """Convert tech stack input to clean list"""
        if isinstance(tech_input, str):
            return [self._clean_text(tech) for tech in tech_input.split(",") if tech.strip()]
        elif isinstance(tech_input, list):
            return [self._clean_text(tech) for tech in tech_input if tech]
        return []

    def finalize_session(self):
        """Ensure complete data is saved when conversation ends"""
        self.save_to_json(final_save=True)

class HiringAssistant:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        self.data_handler = DataHandler()
        
        self.candidate_data = {
            "info": {
                "name": None,
                "email": None,
                "tech_stack": [],
                "experience": None,
                "role": None
            },
            "responses": [],
            "questions": []
        }
        self.conversation_history: List = []
        self.stage = "greeting"
        self.user_counter = 0
        self.question_count = 0
        self.total_questions = 5

    def anonymize_email(self, email: str) -> str:
        """Replace real email with anonymized version"""
        return self.data_handler.anonymize_email(email)

    def clean_input(self, text: str) -> str:
        """Basic sanitization of user input"""
        return self.data_handler._clean_text(text)

    def store_response(self, user_input: str, assistant_response: str):
        """Store conversation with anonymized data"""
        cleaned_input = self.clean_input(user_input)
        
        self.candidate_data["responses"].append({
            "raw_input": user_input,
            "cleaned_input": cleaned_input,
            "assistant_response": assistant_response,
            "stage": self.stage
        })

    def extract_info(self, user_input: str) -> bool:
        """Returns True if successful extraction"""
        user_input = self.clean_input(user_input)
        
        if self.stage == "greeting":
            try:
                extract_prompt = ChatPromptTemplate.from_template(
                    "Extract information from: {input}\n\n" + 
                    Prompts.get_extract_prompt()
                )
                
                chain = extract_prompt | self.llm | StrOutputParser()
                result = chain.invoke({"input": user_input})
                
                cleaned = result.strip().strip('`').replace('json\n', '')
                data = json.loads(cleaned)
                
                if data.get("name"):
                    self.candidate_data["info"]["name"] = self.clean_input(data["name"])
                    self.data_handler.update_info("name", data["name"])
                
                if data.get("tech_stack"):
                    if isinstance(data["tech_stack"], str):
                        self.candidate_data["info"]["tech_stack"] = [
                            self.clean_input(t) for t in data["tech_stack"].split(",") if t.strip()
                        ]
                        self.data_handler.update_info("tech_stack", data["tech_stack"])
                    else:
                        self.candidate_data["info"]["tech_stack"] = [
                            self.clean_input(t) for t in data["tech_stack"] 
                            if isinstance(t, str) and t.strip()
                        ]
                        self.data_handler.update_info("tech_stack", data["tech_stack"])
                    return True
                    
            except Exception as e:
                print(f"Extraction error: {e}")
            return False
        
        elif self.stage == "collect_email":
            if "@" in user_input and "." in user_input.split("@")[-1]:
                self.candidate_data["info"]["email"] = self.anonymize_email(user_input)
                self.data_handler.update_info("email", user_input)
                return True
        
        elif self.stage == "collect_experience":
            if user_input.isdigit():
                self.candidate_data["info"]["experience"] = user_input
                self.data_handler.update_info("experience", user_input)
                return True
        
        elif self.stage == "collect_role":
            if user_input.strip():
                self.candidate_data["info"]["role"] = self.clean_input(user_input)
                self.data_handler.update_info("role", user_input)
                return True
                
        return False

    def generate_response(self, user_input: str) -> str:
        """Generate context-aware response with improved data handling"""
        if not user_input.strip():
            response = Prompts.get_system_prompt("greeting")
            self.store_response("", response)
            self.data_handler.add_conversation("", response, "greeting")
            return response
        
        if user_input.lower() in ["bye", "exit", "quit"]:
            response = f"Thank you {self.candidate_data['info'].get('name', '')}! We'll contact you soon."
            self.store_response(user_input, response)
            self.data_handler.add_conversation(user_input, response, "exit")
            self.data_handler.finalize_session()
            return response
        
        extraction_success = self.extract_info(user_input)
        
        if self.stage == "greeting":
            if extraction_success:
                self.stage = "collect_email"
                response = Prompts.get_system_prompt("collect_email")
            else:
                response = "Please provide both name and tech stack together.\nExample: 'John Doe, Python, JavaScript'"
        
        elif self.stage == "collect_email":
            if extraction_success:
                self.stage = "collect_experience"
                response = Prompts.get_system_prompt("collect_experience")
            else:
                response = "Please enter a valid email address (e.g., name@example.com)"
        
        elif self.stage == "collect_experience":
            if extraction_success:
                self.stage = "collect_role"
                response = Prompts.get_system_prompt("collect_role")
            else:
                response = "Please enter a valid number for years of experience"
        
        elif self.stage == "collect_role":
            if extraction_success:
                self.stage = "technical_questions"
                self.question_count = 0
                prompt_template = ChatPromptTemplate.from_template(
                    Prompts.get_system_prompt(self.stage))
                chain = prompt_template | self.llm | StrOutputParser()
                response = chain.invoke({
                    "tech_stack": ", ".join(self.candidate_data["info"]["tech_stack"]),
                    "experience": self.candidate_data["info"]["experience"],
                    "role": self.candidate_data["info"]["role"]
                })
                self.candidate_data["questions"].append(response)
                self.question_count += 1
                self.data_handler.add_conversation("", response, self.stage)
            else:
                response = "Please specify the role you're applying for"
        
        elif self.stage == "technical_questions":
            if self.question_count == self.total_questions - 1:
                if not hasattr(self, 'last_question_shown'):
                    response = Prompts.get_system_prompt("last_question_notice") + "\n\n"
                    prompt_template = ChatPromptTemplate.from_template(
                        Prompts.get_system_prompt(self.stage))
                    chain = prompt_template | self.llm | StrOutputParser()
                    question = chain.invoke({
                        "tech_stack": ", ".join(self.candidate_data["info"]["tech_stack"]),
                        "experience": self.candidate_data["info"]["experience"],
                        "role": self.candidate_data["info"]["role"]
                    })
                    response += question
                    self.candidate_data["questions"].append(question)
                    self.last_question_shown = True
                    return response
                else:
                    self.stage = "complete"
                    response = "Thank you for completing the interview! We'll review your responses and get back to you soon."
            
            elif self.question_count < self.total_questions - 1:
                if not hasattr(self, 'current_question') or user_input.strip():
                    transition = ""
                    if self.question_count > 0 and user_input.strip():
                        transition = Prompts.get_system_prompt("question_transition") + "\n\n"
                    
                    prompt_template = ChatPromptTemplate.from_template(
                        Prompts.get_system_prompt(self.stage))
                    chain = prompt_template | self.llm | StrOutputParser()
                    question = chain.invoke({
                        "tech_stack": ", ".join(self.candidate_data["info"]["tech_stack"]),
                        "experience": self.candidate_data["info"]["experience"],
                        "role": self.candidate_data["info"]["role"]
                    })
                    self.current_question = question
                    self.question_count += 1
                    
                    response = transition + question
                    self.candidate_data["questions"].append(question)
                else:
                    response = self.current_question
            else:
                response = "Thank you for completing the interview! We'll review your responses and get back to you soon."
        
        else:
            response = "I didn't understand that. Please try again."
        
        if user_input.strip() or self.stage != "technical_questions":
            self.store_response(user_input, response)
            self.data_handler.add_conversation(user_input, response, self.stage)
        
        return response

    def get_anonymized_data(self) -> Dict:
        """Return sanitized candidate data for storage/analysis"""
        return self.data_handler.get_complete_data()