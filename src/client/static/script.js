const synth = window.speechSynthesis;

const inputFormElement = document.getElementById("input-form");
const inputFieldElement = document.getElementById("input-field");
const submitButtonElement = document.getElementById("submit-button");
const chatBoxElement = document.getElementById("chat-box");

const botMessagePrefix = "Bot: ";
let currentSentence = "";
const utteranceQueue = [];

const getGreekVoice = () =>
  synth.getVoices().find((voice) => /Nestoras/i.test(voice.name)) ??
  synth.getVoices().find((voice) => /el-GR/i.test(voice.lang === "el-GR")) ??
  synth.getVoices().find((voice) => voice.default);

let utteranceVoice = getGreekVoice();

synth.onvoiceschanged = () => {
  utteranceVoice = getGreekVoice();
};

const speakCurrentSentence = () => {
  const utterance = new SpeechSynthesisUtterance(currentSentence);
  currentSentence = "";
  utterance.voice = utteranceVoice;
  synth.speak(utterance);
};

const setInputDisabled = (disabled) => {
  inputFieldElement.disabled = disabled;
  submitButtonElement.disabled = disabled;
};

const spawnMessage = (initialMessage) => {
  const messageElement = document.createElement("div");
  messageElement.className = "message";
  messageElement.textContent = initialMessage;

  chatBoxElement.appendChild(messageElement);

  chatBoxElement.scrollTop = chatBoxElement.scrollHeight;

  return messageElement;
};

inputFormElement.addEventListener("submit", async (event) => {
  event.preventDefault();

  /*
  iOS requires direct user interaction to activate speech synthesis.
  This empty speech call therefore allows future non-user-triggered speech,
  as the rest of the speech is actually triggered by the fetch response processing.
  */
  speakCurrentSentence();

  setInputDisabled(true);

  const userInput = inputFieldElement.value;

  spawnMessage("You: " + userInput);

  // Clear input field
  inputFieldElement.value = "";

  try {
    const response = await fetch("/prompt", {
      method: "POST",
      body: userInput,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    const botMessageElement = spawnMessage(botMessagePrefix);

    const processChunk = async () => {
      const { done, value } = await reader.read();
      if (done) {
        speakCurrentSentence();

        setInputDisabled(false);

        inputFieldElement.focus();

        return;
      }

      const chunk = decoder.decode(value, { stream: true });
      botMessageElement.textContent += chunk;

      currentSentence += chunk;

      const endOfSentence = /[.!?]/.test(chunk);
      const endOfEmote = /\*.+\*/.test(currentSentence);

      if (endOfSentence || endOfEmote) {
        speakCurrentSentence();
      }

      await processChunk();
    };

    await processChunk();
  } catch (error) {
    console.error("Error:", error);

    spawnMessage(
      botMessagePrefix +
        "Sorry, I couldn't process your request. Please try again."
    );

    setInputDisabled(false);
  }
});
