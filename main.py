from ctransformers import AutoModelForCausalLM
import time
from flask import Flask, request, Response
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
CORS(app, resources={r"/*": {"origins": "*"}})

# Create a lock object so only one request can use the model at a time
llm_lock = threading.Lock()

@app.route("/", methods=["POST"])
def root():
    prompt = request.data
    decoded_prompt = prompt.decode('utf-8')

    complete_prompt = f"[INST]<<SYS>>You are Socrates.<</SYS>>{decoded_prompt}[/INST]"

    def generate():
        with llm_lock:  # Acquire the lock before calling the llm function
            for word in llm(complete_prompt, stream=True):
                yield word

    return Response(generate(), content_type="text/plain")

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=80)
