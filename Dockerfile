FROM python:3.14-rc-bookworm AS download-stage

WORKDIR /usr/src/app

RUN wget -q -O model https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q2_K.bin?download=true

FROM python:3.14-rc-bookworm AS final-stage

WORKDIR /usr/src/app

RUN pip -q install \
    flask==3.1 \
    flask_cors==5.0.0 \
    waitress==3.0.2 \
    ctransformers==0.2.27 \
    --no-binary ctransformers

COPY  --from=download-stage /usr/src/app/model ./model

COPY ./src/server.py ./

COPY ./src/client ./static

CMD ["python", "server.py"]
