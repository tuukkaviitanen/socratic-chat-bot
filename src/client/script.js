const synth = window.speechSynthesis;
const inputField = document.getElementById("input-field");
const submitButton = document.getElementById("submit-button");
const chatBox = document.getElementById("chat-box");

const messagePrefix = "Bot: ";

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

document
  .getElementById("input-form")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    inputField.disabled = true;
    submitButton.disabled = true;

    const userInput = inputField.value;

    // Display user input in chat box
    const userMessage = document.createElement("div");
    userMessage.className = "message";
    userMessage.textContent = "You: " + userInput;
    chatBox.appendChild(userMessage);

    chatBox.scrollTop = chatBox.scrollHeight;

    // Send POST request
    fetch("/prompt", {
      method: "POST",
      body: userInput,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Display response in chat box
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        const botMessage = document.createElement("div");
        botMessage.className = "message";
        botMessage.textContent = messagePrefix;

        chatBox.appendChild(botMessage);
        chatBox.scrollTop = chatBox.scrollHeight;

        const processChunk = async () => {
          const { done, value } = await reader.read();
          if (done) {
            speakCurrentSentence();

            inputField.disabled = false;
            submitButton.disabled = false;

            inputField.focus();

            return;
          }

          const chunk = decoder.decode(value, { stream: true });
          botMessage.textContent += chunk;

          currentSentence += chunk;

          const endOfSentence = /[.!?]/.test(chunk);
          const endOfEmote = /\*.+\*/.test(currentSentence);

          if (endOfSentence || endOfEmote) {
            speakCurrentSentence();
          }

          processChunk();
        };

        processChunk();
      })
      .catch((error) => {
        console.error("Error:", error);

        const botMessage = document.createElement("div");
        botMessage.className = "message";
        botMessage.textContent =
          messagePrefix +
          "Sorry, I couldn't process your request. Please try again.";

        chatBox.appendChild(botMessage);
        chatBox.scrollTop = chatBox.scrollHeight;

        inputField.disabled = false;
        submitButton.disabled = false;
      });

    // Clear input field
    inputField.value = "";
  });
