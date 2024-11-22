FROM python:bookworm AS build-stage

WORKDIR /usr/src/app

RUN pip -q install llama-cpp-python ctransformers flask flask_cors waitress

RUN wget -q -O model https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q2_K.bin?download=true

COPY ./main.py ./

COPY ./client.html ./static/

CMD ["python", "main.py"]
