document.addEventListener("DOMContentLoaded", () => {
  const chatContent = document.getElementById("chat-content");
  const inputField = document.getElementById("userInput");
  const sendButton = document.getElementById("send-btn");
  const saveButton = document.getElementById("save-btn");
  const sidebarList = document.getElementById("saved-conversations-list");
  const newChatButton = document.getElementById("new-chat");

  let conversations = JSON.parse(localStorage.getItem("conversations")) || {};
  let currentConversation = null;

  const appendMessage = (content, sender) => {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
    messageDiv.innerHTML = marked.parse(content);
    chatContent.appendChild(messageDiv);
    chatContent.scrollTop = chatContent.scrollHeight;
  };

  const showTypingIndicator = () => {
    const typingIndicator = document.createElement("div");
    typingIndicator.classList.add("message", "bot-message");
    typingIndicator.id = "typing-indicator";
    typingIndicator.textContent = "Typing...";
    chatContent.appendChild(typingIndicator);
    chatContent.scrollTop = chatContent.scrollHeight;
  };

  const removeTypingIndicator = () => {
    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) typingIndicator.remove();
  };

  const fetchBotResponse = async (userMessage) => {
    showTypingIndicator();
    try {
      const response = await fetch("http://localhost:5000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: `${userMessage}:` })
      });

      removeTypingIndicator();
      if (!response.ok) {
        const errorMessage = await response.text();
        throw new Error(`Failed to fetch response: ${errorMessage}`);
      }

      const data = await response.json();
      appendMessage(data.response.trim(), "bot");
    } catch (error) {
      removeTypingIndicator();
      appendMessage(`⚠️ Error: ${error.message}`, "bot");
    }
  };

  const createNewConversation = (firstMessage) => {
    const conversationName = firstMessage.slice(0, 20).trim() || "Untitled Chat";
    let uniqueName = conversationName;
    let count = 1;
    while (conversations[uniqueName]) {
      uniqueName = `${conversationName} (${count})`;
      count++;
    }
    currentConversation = uniqueName;
    conversations[currentConversation] = [{ sender: "bot", content: "Welcome! How can AI support you today?" }];
    localStorage.setItem("conversations", JSON.stringify(conversations));
    addConversationToSidebar(currentConversation);
    loadConversation(currentConversation);
  };

  sendButton.addEventListener("click", () => {
    const userMessage = inputField.value.trim();
    if (!userMessage) return;

    if (!currentConversation) {
      createNewConversation(userMessage);
    }

    appendMessage(userMessage, "user");
    inputField.value = "";
    inputField.focus();

    fetchBotResponse(userMessage);
  });

  inputField.addEventListener("keypress", (event) => {
    if (event.key === "Enter") sendButton.click();
  });

  const addConversationToSidebar = (name) => {
    if ([...sidebarList.children].some((li) => li.textContent === name)) return;
    const li = document.createElement("li");
    li.textContent = name;
    li.addEventListener("click", () => loadConversation(name));
    sidebarList.appendChild(li);
  };

  const loadConversation = (name) => {
    currentConversation = name;
    chatContent.innerHTML = "";
    (conversations[name] || []).forEach((msg) => appendMessage(msg.content, msg.sender));
  };

  const loadSavedConversations = () => {
    Object.keys(conversations).forEach(addConversationToSidebar);
  };

  newChatButton.addEventListener("click", () => {
    currentConversation = null;
    chatContent.innerHTML = "";
    appendMessage("Welcome! How can AI support you today?", "bot");
  });

  saveButton.addEventListener("click", () => {
    const messages = [];
    chatContent.querySelectorAll('.message').forEach(msg => {
      messages.push({
        sender: msg.classList.contains('user-message') ? 'user' : 'bot',
        content: msg.textContent
      });
    });

    const topic = inputField.value.trim() || "Untitled";
    if (messages.length > 0 && topic) {
      const key = `savedChat_${topic}`;
      conversations[topic] = messages;
      localStorage.setItem("conversations", JSON.stringify(conversations));
      alert(`Conversation saved as "${topic}"`);
      loadSavedConversations();
    } else {
      alert("Please send a message before saving.");
    }
  });

  loadSavedConversations();
});