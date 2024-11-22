FROM python AS build-stage

WORKDIR /usr/src/app

RUN pip install llama-cpp-python
RUN pip install ctransformers
RUN pip install Flask

# RUN wget -O llama-2-7b-chat.ggmlv3.q4_K_S.bin https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_K_S.bin?download=true

COPY ./h2o-danube3-500m-chat-Q4_K_M.gguf .

COPY ./main.py .

CMD ["python", "main.py"]
