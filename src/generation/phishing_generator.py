import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from src.generation.prompt_templates import get_template

# Load configurations
# load_dotenv moved inside class for robustness

class PhishingGenerator:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        env_path = os.path.join(os.getcwd(), '.env')
        load_dotenv(env_path)
        
        print(f"DEBUG: Looking for .env at: {env_path}")
        print(f"DEBUG: .env exists: {os.path.exists(env_path)}")
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                print(f"DEBUG: .env content first 10 chars: {f.read()[:10]}")
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found in environment.")
            print(f"DEBUG: Env keys: {[k for k in os.environ.keys() if 'GROQ' in k]}")
        
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.7
        )
        self.storage_file = "data/generated_phishing_v1.jsonl"

    def generate(self, attack_type, params):
        """
        Generates a phishing email and saves it with metadata.
        """
        template = get_template(attack_type)
        chain = LLMChain(llm=self.llm, prompt=template)
        
        print(f"Generating {attack_type} phishing email...")
        try:
            # Generate the email
            response = chain.run(params)
            
            # Metadata for Step 4
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "attack_type": attack_type,
                "model": self.llm.model,
                "parameters": params,
                "generated_content": response
            }
            
            self._save_to_log(metadata)
            return response
            
        except Exception as e:
            print(f"Error during generation: {e}")
            return None

    def _save_to_log(self, metadata):
        """
        Appends metadata and the generated sample to a JSONL file.
        """
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        with open(self.storage_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(metadata) + "\n")
        print(f"Metadata and email logged to {self.storage_file}")

if __name__ == "__main__":
    # Quick Test Instance
    # Note: Requires a valid XAI_API_KEY in .env to run successfully
    generator = PhishingGenerator()
    
    # Example: Spear Phishing
    sample_params = {
        "target_name": "Phillipp Allen",
        "organization": "Enron Energy Services",
        "role": "Trader",
        "context": "Recent forecast reports for the Western Market",
        "urgency": "High - Immediate review needed",
        "phishing_link": "http://enron-portal.verify-access.net/reports"
    }
    
    # To run this, uncomment below after adding API key:
    # generator.generate("spear_phishing", sample_params)
