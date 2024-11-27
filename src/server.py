from ctransformers import AutoModelForCausalLM
import time
from flask import Flask, request, Response, current_app
from flask_cors import CORS
from waitress import serve
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Loading model...")

start = time.time()

# Load the pretrained model
llm = AutoModelForCausalLM.from_pretrained('./model', model_type='llama')

load_time = time.time()

logger.info(f"Time taken to load model: {load_time-start} seconds")

app = Flask(__name__)

CORS(app) # Enables Cross-Origin Resource Sharing

# Create a lock object so only one request can use the model at a time
llm_lock = threading.Lock()

@app.route("/", methods=["GET"])
def serve_app():
    return current_app.send_static_file("index.html")

@app.route("/prompt", methods=["POST"])
def prompt():
    prompt = request.get_data(as_text=True)

    complete_prompt = f"[INST]<<SYS>>You are Socrates. Keep your answers short.<</SYS>>{prompt}[/INST]"

    def generate():
        with llm_lock:  # Acquire the lock before calling the llm function
            for word in llm(complete_prompt, stream=True, max_new_tokens=500): # Generate up to 500 tokens which should be more than enough
                yield word

    return Response(generate(), content_type="text/plain")

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
