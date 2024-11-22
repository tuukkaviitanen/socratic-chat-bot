FROM python:bookworm AS build-stage

WORKDIR /usr/src/app

RUN pip install llama-cpp-python ctransformers flask flask_cors waitress

RUN wget -O model https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q2_K.bin?download=true

COPY ./main.py .

CMD ["python", "main.py"]
