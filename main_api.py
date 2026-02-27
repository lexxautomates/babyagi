import babyagi
import os
from flask_cors import CORS

app = babyagi.create_app('/dashboard')
CORS(app) # Enable CORS for all routes

# Define any additional routes or overrides if necessary
@app.route('/health')
def health():
    return {"status": "ok", "message": "BabyAGI backend is running"}

if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is handled or set a dummy one if using Ollama
    if 'OPENAI_API_KEY' not in os.environ:
        os.environ['OPENAI_API_KEY'] = 'dummy_key_for_ollama'
        
    babyagi.add_key_wrapper('openai_api_key', os.environ['OPENAI_API_KEY'])
    
    # Load the new Solo Entrepreneur Productivity Pack
    babyagi.load_functions("babyagi/functionz/packs/productivity_pack.py")
    
    # Run the Flask app on port 8080 (backend standard for this project)
    app.run(host='0.0.0.0', port=8080)
