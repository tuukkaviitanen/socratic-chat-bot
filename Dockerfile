FROM python AS build-stage

WORKDIR /usr/src/app

RUN wget -O llama-2-7b-chat.ggmlv3.q4_K_S.bin https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_K_S.bin?download=true

RUN pip install llama-cpp-python ctransformers fastapi uvicorn

COPY ./main.py .

CMD ["python", "main.py"]
