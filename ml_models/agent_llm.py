import os
import json
from groq import Groq
from core.logger import logger

# Import our Python tools
from agent_tools.interview_tools import grade_technical_answer, query_job_description
class AgentLLM:
    def __init__(self, rag_system):
        """
        Initializes the Groq client and our conversation history.
        We pass the RAG System in so the LLM can use it as a tool!
        """
        logger.info("Initializing AgentLLM (Groq)...")
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            logger.warning("GROQ_API_KEY is missing or invalid! The Voicebot will not work until you put it in .env")
            
        self.client = Groq(api_key=api_key)
        self.rag_system = rag_system
        self.model_name = "llama-3.1-8b-instant" # Fast and smart model
        
        # System Prompt dictates the 'Persona'
        self.system_prompt = {
            "role": "system",
            "content": (
                "You are an AI Technical Screener for TechCorp Inc. "
                "You are conducting a verbal interview with a backend engineering intern candidate. "
                "Be conversational, professional, and concise since this is a voice-to-voice interaction. "
                "Do not use markdown like asterisks or bolding, just plain text that sounds good when spoken aloud. "
                "If the user answers a technical question, use your tool to grade it. "
                "If the user asks about the company, use your RAG tool to search the job description."
            )
        }
        
        # We start the history with just the system prompt.
        self.message_history = [self.system_prompt]
        
        # --- TOOL SCHEMAS ---
        # This tells the LLM EXACTLY what tools exist and what arguments they require using JSON Schema.
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "grade_technical_answer",
                    "description": "Call this tool IMMEDIATELY after a candidate provides an answer to a technical question. Do not answer them conversationally first, grade it first.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "concept_asked": {
                                "type": "string",
                                "description": "The specific technical concept you asked them about (e.g., 'API Routing', 'OOP')"
                            },
                            "user_answer_transcript": {
                                "type": "string",
                                "description": "The raw transcript of the user's answer."
                            }
                        },
                        "required": ["concept_asked", "user_answer_transcript"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_job_description",
                    "description": "Call this tool if the candidate asks a question about the company, the role, the tech stack, or expectations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up in the company vector database."
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def chat(self, user_text: str) -> str:
        """
        The main interaction loop (ReAct loop).
        1. Append user text to history.
        2. Send to LLM.
        3. If LLM wants to call a tool, we execute the Python function and send the result BACK to the LLM.
        4. Return the final text.
        """
        # Append what the user just said (via Speech-to-Text)
        self.message_history.append({"role": "user", "content": user_text})
        
        try:
            # First LLM Call
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.message_history,
                tools=self.tools_schema,
                tool_choice="auto",
                max_tokens=200
            )
            
            response_message = response.choices[0].message
            
            # Check if LLM decided to use a Tool!
            if response_message.tool_calls:
                # Add the LLM's thought process to history
                self.message_history.append(response_message)
                
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"LLM decided to trigger tool: {function_name} with args: {function_args}")
                    
                    # Execute the actual Python code!
                    if function_name == "grade_technical_answer":
                        function_response = grade_technical_answer(
                            concept_asked=function_args.get("concept_asked"),
                            user_answer_transcript=function_args.get("user_answer_transcript")
                        )
                    elif function_name == "query_job_description":
                        # We route this tool call directly into our RAG System!
                        function_response = self.rag_system.query(
                            question=function_args.get("query")
                        )
                    else:
                        function_response = "Error: Tool not found."
                        
                    # Send the result of the Python function BACK to the LLM
                    # so it can formulate a final spoken answer.
                    self.message_history.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )
                
                # Second LLM Call (now that it has the tool results!)
                second_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=self.message_history
                )
                final_answer = second_response.choices[0].message.content
                self.message_history.append({"role": "assistant", "content": final_answer})
                return final_answer
                
            else:
                # Basic conversational response (no tools needed)
                final_answer = response_message.content
                self.message_history.append({"role": "assistant", "content": final_answer})
                return final_answer
                
        except Exception as e:
            logger.error(f"LLM Chat Error: {e}")
            return "I'm having trouble connecting to my brain. Please check the Groq API key."
