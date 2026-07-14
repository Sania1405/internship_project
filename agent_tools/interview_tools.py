import json
from typing import Dict, Any

def grade_technical_answer(concept_asked: str, user_answer_transcript: str) -> str:
    """
    A simulated tool that the LLM will call to 'grade' the candidate's answer.
    In a real app, this might do semantic similarity checks or keyword hits.
    Here, we instruct the LLM to provide its own grading rationale via the parameters, 
    and we format the output.
    """
    # Simply log it to a JSON file for HR to review later
    record = {
        "concept": concept_asked,
        "transcript": user_answer_transcript,
        "status": "Submitted for HR Review"
    }
    
    with open("candidate_evaluations.json", "a") as f:
        f.write(json.dumps(record) + "\n")
        
    return f"Successfully saved the evaluation for the concept '{concept_asked}'. Please proceed to the next question or conclude the interview."

def query_job_description(query: str) -> str:
    """
    The LLM will use this tool if the candidate asks a question about the job, 
    like "What does a typical day look like?"
    """
    # Dummy data for testing before ChromaDB is wired up
    dummy_data = {
        "salary": "The starting salary for the Backend Engineering Intern role is $8,000 per month.",
        "hours": "The core working hours are 10 AM to 4 PM PST, but we are fully remote and flexible.",
        "tech stack": "We primarily use Python, FastAPI, Docker, and Hugging Face models.",
        "default": "Our company values innovation, fast-paced learning, and building cool AI products!"
    }
    
    query_lower = query.lower()
    if "salary" in query_lower or "pay" in query_lower:
        return dummy_data["salary"]
    elif "hour" in query_lower or "time" in query_lower:
        return dummy_data["hours"]
    elif "stack" in query_lower or "tech" in query_lower:
        return dummy_data["tech stack"]
    else:
        return dummy_data["default"]

# We need a way to pass these Python functions to the Groq LLM.
# This will be handled in the agent_llm.py wrapper.
