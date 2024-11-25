FROM python:bookworm AS download-stage

WORKDIR /usr/src/app

RUN wget -q -O model https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q2_K.bin?download=true

FROM python:bookworm AS final-stage

WORKDIR /usr/src/app

RUN pip -q install flask flask_cors waitress ctransformers --no-binary ctransformers

COPY  --from=download-stage /usr/src/app/model ./model

COPY ./main.py ./

COPY ./client.html ./static/

CMD ["python", "main.py"]
