import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

load_dotenv(os.path.join(os.getcwd(), '.env'))

class LLMClassifier:
    """
    Uses LLM reasoning to detect social engineering and phishing intent.
    """
    
    DETECTION_PROMPT = """
    You are a Senior Cybersecurity Threat Analyst specializing in Social Engineering detection.
    Analyze the following email and determine if it is a phishing attempt.
    
    --- EMAIL START ---
    Subject: {subject}
    Content: {body}
    --- EMAIL END ---
    
    Evaluate based on:
    1. Psychological Triggers: (Fear, Urgency, Curiosity, Authority, Greed).
    2. Contextual Anomalies: Does the request make sense in a corporate environment?
    3. Call to Action: Is there a suspicious link or request for sensitive info?
    
    Return your analysis strictly in the following JSON format:
    {{
        "risk_score": (int from 0 to 100),
        "risk_level": "(Low/Medium/High)",
        "analysis": "(Brief explanation of why it is or isn't phishing)",
        "detected_tactics": ["tactic1", "tactic2"]
    }}
    """

    def __init__(self, model_name=None):
        if model_name is None:
            model_name = os.getenv("MODEL_NAME", "mixtral-8x7b-32768")
        api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.1 # Low temperature for consistent analysis
        )
        self.prompt = PromptTemplate(
            input_variables=["subject", "body"],
            template=self.DETECTION_PROMPT
        )
        # Modern LangChain Expression Language (LCEL)
        self.chain = self.prompt | self.llm

    def analyze(self, subject, body):
        """
        Runs the LLM analysis and returns the parsed JSON result.
        """
        try:
            # Use invoke for modern compatibility
            response = self.chain.invoke({"subject": subject, "body": body})
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Find JSON block in case LLM adds chat filler around it
            if "{" in response_text and "}" in response_text:
                json_str = response_text[response_text.find("{"):response_text.rfind("}")+1]
                return json.loads(json_str)
            return {
                "risk_score": 0,
                "risk_level": "Error",
                "analysis": "Failed to parse LLM response.",
                "detected_tactics": []
            }
        except Exception as e:
            print(f"LLM Classification Error: {e}")
            return {
                "risk_score": 0,
                "risk_level": "Error",
                "analysis": str(e),
                "detected_tactics": []
            }

if __name__ == "__main__":
    # Test
    classifier = LLMClassifier()
    test_subject = "Urgent: HR Policy Update Required"
    test_body = "Hi, please review the new HR policy at http://enron-compliance.net/update immediately or your salary may be delayed."
    result = classifier.analyze(test_subject, test_body)
    print(json.dumps(result, indent=2))
