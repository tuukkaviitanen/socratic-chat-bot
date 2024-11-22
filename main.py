from ctransformers import AutoModelForCausalLM
import time
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import urllib.parse
import threading

start = time.time()

# Load the pretrained model
llm = AutoModelForCausalLM.from_pretrained('./llama-2-7b-chat.ggmlv3.q4_K_S.bin', model_type='llama')

load_time = time.time()

print(f"\n\nTime taken to load model: {load_time-start} seconds\n\n")

app = FastAPI()

# Create a lock object so only one request can use the model at a time
llm_lock = threading.Lock()

@app.post("/")
async def root(request: Request):
    prompt = await request.body()
    prompt = prompt.decode('utf-8')

    def generate():
        with llm_lock:  # Acquire the lock before calling the llm function
            for word in llm(prompt, stream=True):
                encoded_word = urllib.parse.quote(word)
                yield f"data: {encoded_word}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
