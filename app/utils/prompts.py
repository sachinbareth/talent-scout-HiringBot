from typing import Any
class Prompts:
    @staticmethod
    def get_system_prompt(stage: str, question_count: int = 0, total_questions: int = 5) -> str:
        prompts = {
            "greeting": (
                "Welcome to TalentScout Hiring Assistant!\n\n"
                "Please provide:\n"
                "1. Your full name\n"
                "2. Your primary tech stack\n\n"
                "Example: 'John Doe, Python, JavaScript'"
            ),
            "collect_email": "Thank you! What's your professional email address?",
            "collect_experience": "How many years of professional experience do you have?",
            "collect_role": "What specific role are you applying for?",
            "technical_questions": (
                "Generate one technical interview question for a candidate with these skills: {tech_stack}\n"
                "and {experience} years of experience applying for {role} position.\n"
                "The question should be at intermediate difficulty level and question should be1 line to 4 to 5 lines."
            ),
            "question_transition": "Okay, let's move on to the next question.",
            "last_question_notice": "This will be our last question for this interview."
        }
        
        if stage == "technical_questions" and question_count == total_questions - 1:
            return prompts["last_question_notice"] + "\n\n" + prompts[stage]
        
        return prompts[stage]

    @staticmethod
    def get_extract_prompt() -> str:
        return """Extract the following information from this message:
        {input}
        
        Return ONLY a JSON object with these keys:
        - "name" (string)
        - "tech_stack" (array of strings)
        
        Example Output:
        {{"name": "John Doe", "tech_stack": ["Python", "JavaScript"]}}
        
        Rules:
        1. If any information is missing, set the value to null
        2. Do not include any additional text or explanation
        3. Ensure the output is valid JSON"""