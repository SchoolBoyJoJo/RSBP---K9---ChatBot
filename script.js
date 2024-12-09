const chatDiv = document.getElementById("chat");
const inputField = document.getElementById("input");
const sendButton = document.getElementById("button");
const id = makeid(36);
let selectedMode = null; // Variabel untuk menyimpan pilihan pengguna

function makeid(length) {
  let result = "";
  const characters =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  const charactersLength = characters.length;
  let counter = 0;
  while (counter < length) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
    counter += 1;
  }
  return result;
}

// Fungsi untuk menampilkan pop-up pilihan mode
function showModeSelection() {
  const modePopup = document.createElement("div");
  modePopup.classList.add("mode-popup");

  const message = document.createElement("p");
  message.textContent = "Pilih mode chatbot:";

  const genAIButton = document.createElement("button");
  genAIButton.textContent = "Generative AI";
  genAIButton.onclick = () => {
    selectedMode = "genai";
    document.body.removeChild(modePopup);
  };

  const pythonModelButton = document.createElement("button");
  pythonModelButton.textContent = "Model Python";
  pythonModelButton.onclick = () => {
    selectedMode = "python";
    document.body.removeChild(modePopup);
  };

  modePopup.appendChild(message);
  modePopup.appendChild(genAIButton);
  modePopup.appendChild(pythonModelButton);

  document.body.appendChild(modePopup);
}

// Tampilkan pop-up saat halaman dimuat
window.onload = () => {
  showModeSelection();
};

// Fungsi untuk menambahkan pesan ke chat
function appendMessage(text, isUser) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", isUser ? "user" : "bot");

  // Tambahkan avatar
  const avatarDiv = document.createElement("div");
  avatarDiv.classList.add("avatar");

  // Tambahkan teks
  const textDiv = document.createElement("div");
  textDiv.classList.add("text");
  textDiv.innerHTML = text;

  messageDiv.appendChild(isUser ? textDiv : avatarDiv);
  messageDiv.appendChild(isUser ? avatarDiv : textDiv);

  chatDiv.appendChild(messageDiv);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

// Kirim pesan ke server
sendButton.addEventListener("click", () => {
  if (!selectedMode) {
    alert("Silakan pilih mode terlebih dahulu.");
    return;
  }

  const userMessage = inputField.value.trim();
  if (!userMessage) return;

  appendMessage(userMessage, true);
  inputField.value = "";

  // Kirim pesan ke server Flask
  fetch(`http://127.0.0.1:5000/${id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage, mode: selectedMode }), // Kirim mode bersama pesan
  })
    .then((response) => response.json())
    .then((data) => {
      appendMessage(data.response, false);
    })
    .catch((error) => {
      appendMessage("Error: Unable to connect to chatbot.", false);
    });
});

// Kirim pesan dengan tombol Enter
inputField.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendButton.click();
  }
});
