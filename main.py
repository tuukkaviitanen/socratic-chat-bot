from ctransformers import AutoModelForCausalLM
import time
from flask import Flask, request, Response
import urllib.parse
import threading

start = time.time()

# Load the pretrained model
llm = AutoModelForCausalLM.from_pretrained('./llama-2-7b-chat.ggmlv3.q4_K_S.bin', model_type='llama')

load_time = time.time()

print(f"\n\nTime taken to load model: {load_time-start} seconds\n\n")

app = Flask('app')

# Create a lock object so only one request can use the model at a time
llm_lock = threading.Lock()

@app.route('/', methods=['POST'])
def root():
    prompt = request.data.decode('utf-8')

    def generate():
        with llm_lock:  # Acquire the lock before calling the llm function
            for word in llm(prompt, stream=True):
                encoded_word = urllib.parse.quote(word)
                yield f"data: {encoded_word}\n\n"

    return Response(generate(), mimetype="text/event-stream")

app.run(host='0.0.0.0')
