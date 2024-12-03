const chatDiv = document.getElementById("chat");
const inputField = document.getElementById("input");
const sendButton = document.getElementById("button");
const id = makeid(36);

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
  const userMessage = inputField.value.trim();
  if (!userMessage) return;

  appendMessage(userMessage, true);
  inputField.value = "";

  // Kirim pesan ke server Flask
  fetch(`http://127.0.0.1:5000/${id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage }),
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
