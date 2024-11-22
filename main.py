from ctransformers import AutoModelForCausalLM
import time
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import urllib.parse
import threading
import uvicorn

start = time.time()

# Load the pretrained model
llm = AutoModelForCausalLM.from_pretrained('./model', model_type='llama')

load_time = time.time()

print(f"\n\nTime taken to load model: {load_time-start} seconds\n\n")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Create a lock object so only one request can use the model at a time
# llm_lock = threading.Lock()

@app.post("/")
async def root(request: Request):
    prompt = await request.body()
    decoded_prompt = prompt.decode('utf-8')

    complete_prompt = f"[INST] <<SYS>> You are Socrates. Keep your answers short.<</SYS>>{decoded_prompt}[/INST]"

    def generate():
        # with llm_lock:  # Acquire the lock before calling the llm function
        for word in llm(complete_prompt, stream=True):
            # encoded_word = urllib.parse.quote(word)
            yield word

    return StreamingResponse(generate(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
