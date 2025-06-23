# TalentScout – AI Hiring Assistant Chatbot

TalentScout is an AI-powered hiring assistant chatbot that automates initial candidate screening for technical roles. It interacts with candidates in natural language, collects their information, and evaluates their skills by generating relevant technical questions based on their declared tech stack (like Python, React, or AWS).

Built using Python, Streamlit, and Google Gemini, the chatbot maintains context throughout the conversation and guides the candidate through a structured but friendly assessment.

## Features

-  Natural conversation interface
-  Extracts name, experience, and technical stack
-  Dynamically generates tech-specific intermediate questions
-  Maintains session state across turns
-  Clean prompt engineering for accuracy
-  Error handling for incomplete or unclear inputs

## 🛠 Tech Stack

- Python 3.8+
- Streamlit for web interface
- GEMINI API for conversation and question generation
- python-dotenv for environment variable management
- Langchain framework
- Docker for containerized deployment on dockerhub

## 📂 Project Structure
```
talent-scout-HiringBot/
├── app/
│ ├── models/
│ │ ├── init.py
│ │ └── assistant.py
│ ├── ui/
│ │ ├── init.py
│ │ └── Streamlit_app.py
│ └── utils/
│ ├── config.py
│ └── prompts.py
├── chatbot_data/ # Directory for storing chatbot-related data
├── .env # Environment file (excluded from Git)
├── dockerfile # Dockerfile to containerize the app
├── main.py # Entry point for running the Streamlit app
├── requirements.txt # Python dependencies
└── README.md # Project documentation
```

## Technical Implementation
### Core Components
- **Streamlit**: Web interface for chat interactions
- **GOOGLE GEMINI**: Generates conversational responses and technical questions
- **Session State**: Maintains conversation context throughout the chat

### Key Files
- `app`: Main application logic and UI
- `prompts.py`: Contains all LLM prompt templates
- `utils`: Helper functions for input processing
- `requirements.txt`: Lists all Python dependencies

### Prompt Engineering
The system uses carefully designed prompts including:

1. Information Collection:
```python
"Extract from the candidate's message: name (string), experience (string), and tech stack (list) etc. Return as JSON."
```

### Clone the repository

```bash
https://github.com/sachinbareth/talent-scout-HiringBot.git
cd talent-scout-HiringBot
```
### Install dependencies
```bash
pip install -r requirements.txt
```

### Add your GOOGLE API Key
- Create a .env file in the root directory with the following content:
  
  ```bash
  GOOGLE_API_KEY=your_api_key_here
  ```

### Run the App

```bash
streamlit run main.py
```
## Live Demo

You can try out the TalentScout AI Hiring Assistant Chatbot live at the following link:

🔗 [https://talent-scout-hiringbot-is-here.streamlit.app/](https://talent-scout-hiringbot-is-here.streamlit.app/)

No setup required — just open the link in your browser and start interacting with the chatbot.

## Usage Guide
The chatbot will automatically open in your browser. Follow these steps:

1. The bot will greet you and request:
   - Full name
   - Years of experience
   - Technical skills (e.g., Python, React, AWS)

2. Based on your declared skills, it will generate 3-5 technical questions

3. Type "bye" at any time to end the session
  
