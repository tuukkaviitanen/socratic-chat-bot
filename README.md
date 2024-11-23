# Socratic Chat Bot

> Standalone chat bot that thinks it's Socrates

![Screenshot of a Socratic chat](image.png)

## Model

The chat bot is using a [small language model](https://medium.com/@nageshmashette32/small-language-models-slms-305597c9edf2) found here [Llama-2-7B-Chat-GGML](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML) and is based on [Llama-2-7b-chat-hf](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)

Specifically it's using the model file [llama-2-7b-chat.ggmlv3.q2_K.bin](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/blob/main/llama-2-7b-chat.ggmlv3.q2_K.bin) as it has the smallest system requirements. It's still not super fast on my hardware, but it's fast enough.

## Server

The model is loaded by a [Python](https://www.python.org/) application which also starts a HTTP API with [Flask](https://flask.palletsprojects.com/en/stable/) to handle communication between clients and the model.

The environment is created with a Dockerfile that first downloads the pretrained model. [ctransformers](https://github.com/marella/ctransformers) is then used to load the model.

Each prompt request to the API is wrapped in a [prompt template](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML#prompt-template-llama-2-chat) and fed to the model. This means that the model has no knowledge of prior prompts. It would be possible to also include the chat history ([see examples here](https://gpus.llm-utils.org/llama-2-prompt-template/)), but it affects the speed of the responses greatly, so the history is sacrificed in this project.

A [mutex lock](<https://en.wikipedia.org/wiki/Lock_(computer_science)>) is also used on the model to avoid multiple requests from accessing the model at the same time, which would cause the whole server to crash. Any new requests will wait for their turn. Any cancelled requests will automatically release the lock. I migrated back to [Flask](https://flask.palletsprojects.com/en/stable/) from [FastAPI](https://fastapi.tiangolo.com/) because FastAPI's asynchronous nature would cause problems with the lock. Even when using an [asyncio](https://docs.python.org/3/library/asyncio.html) lock instead of threading library's lock, the lock would work, but cancelling the request wouldn't stop the model from processing the prompt. It was easier to just switch back to Flask which works seemlessly with threading library's locks.

The response is returned from the model as a stream of words or syllables. Those are then returned to the client as a plain text stream. The connection is closed after the response is complete. No [websockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) or [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) are used here to avoid complexity.

## Client

The application also includes a vanilla HTML/CSS/JavaScript client application. It's nothing fancy and has only a chat area and an input field. When the input is submitted, it's sent to the server, and the response is then streamed on the chat area.

When a complete sentence is received, the app starts running it through text-to-speech using the browser's [SpeechSynthesis API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis). The API handles queueing automatically, so the sentences can just be added there when they are finished. It's using just the browser's default voice, as the voices differ from each browser. Also I feel that the robotic default voice is quite fitting.

## Thoughts

It was a nice small project for learning about language models. It was easier than I expected, since the pre-trained models work really well out of the box. The resource usage was quite interesting. It only takes about 300-400 MiB of memory to run, whether the model is processing or not. The CPU usage on the other hand is close to zero when idle, but it uses about 50 % of my CPU when processing.
