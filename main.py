from ctransformers import AutoModelForCausalLM
import time
from flask import Flask, request, Response

start = time.time()

# Load the pretrained model
# llm = AutoModelForCausalLM.from_pretrained('TheBloke/Llama-2-7B-Chat-GGML', model_file = 'llama-2-7b-chat.ggmlv3.q2_K.bin' )
# llm = AutoModelForCausalLM.from_pretrained('h2oai/h2o-danube3-4b-chat-GGUF', model_file = 'h2o-danube3-4b-chat-Q2_K.gguf' )
llm = AutoModelForCausalLM.from_pretrained('h2oai/h2o-danube3-500m-chat-GGUF', model_file = 'h2o-danube3-500m-chat-Q4_K_M.gguf' )

load_time = time.time()

print(f"\n\nTime taken to load model: {load_time-start} seconds\n\n")

app = Flask('app')

@app.route('/', methods=['POST'])
def root():
    prompt = request.data.decode('utf-8')

    def generate():
        for word in llm(prompt, stream=True):
            yield word

    return Response(generate(), mimetype='text/plain')

app.run(host='0.0.0.0')
