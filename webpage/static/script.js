document.addEventListener("DOMContentLoaded", function () {
    const messagesDiv = document.getElementById("messages");
    const startButton = document.getElementById("start-button");
    const languageSelect = document.getElementById("language-select");
    console.log("Script loaded successfully!"); // Debugging: Check if script runs

    // Attach event listener to form
    document.getElementById("contactForm").addEventListener("submit", handleSubmit);

    let isBotActive = false;

    startButton.addEventListener("click", async () => {
        if (!isBotActive) {
            await startBot();
        } else {
            await stopBot();
        }
    });

    async function startBot() {
        isBotActive = true;
        startButton.textContent = "Listening...";
        startButton.disabled = true;

        const selectedLanguage = languageSelect.value; // Get selected language

        try {
            // Step 1: Record Audio
            const recordResponse = await fetch("/record", { method: "POST" });
            const recordData = await recordResponse.json();

            if (recordData.error) {
                throw new Error(recordData.error);
            }

            appendMessage("user", recordData.text);

            // Step 2: Get AI Response
            const aiResponse = await fetch("/respond", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: recordData.text, language: selectedLanguage })
            });

            const aiData = await aiResponse.json();
            appendMessage("assistant", aiData.response);

            // Step 3: Convert AI Response to Speech
            const speechResponse = await fetch("/speak", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: aiData.response })
            });

            const speechData = await speechResponse.json();
            playAudio(speechData.audio_url);

        } catch (error) {
            console.error("Error:", error);
            appendMessage("assistant", "Error processing request. Please try again.");
        } finally {
            startButton.textContent = "Start";
            startButton.disabled = false;
            isBotActive = false;
        }
    }

    function appendMessage(sender, text) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);
        
        // Styling for user vs. assistant messages
        if (sender === "user") {
            messageDiv.innerHTML = `<strong>You:</strong> ${text}`;
        } else {
            messageDiv.innerHTML = `<strong>AI:</strong> ${text}`;
        }

        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight; // Auto-scroll to latest message
    }

    function playAudio(audioUrl) {
        const audioElement = new Audio(audioUrl);
        audioElement.play().catch(error => console.error("Audio playback error:", error));
    }

});

function handleSubmit(event) {
    event.preventDefault(); // Prevent default form submission

    // Get form values
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const message = document.getElementById("message").value.trim();

    // Debugging: Log the values to ensure they are captured
    console.log("Name:", name, "Email:", email, "Message:", message);
    alert("Opening email client...");

    // Validate fields
    if (!name || !email || !message) {
        alert("Please fill in all fields.");
        return;
    }

    // Email recipient (update this with your actual email)
    const recipientEmail = "keerthipriyanka1911@gmail.com"; 

    // Email subject
    const subject = encodeURIComponent("Inquiry about AI Voice Assist");

    // Email body with proper formatting
    const body = encodeURIComponent(`Hello,\n\nMy Name: ${name}\nMy Email: ${email}\n\nMessage:\n${message}\n\nBest Regards,\n${name}`);

    // Construct the mailto link
    const mailtoLink = `mailto:${recipientEmail}?subject=${subject}&body=${body}`;

    // Open the user's default email client
    window.location.href = mailtoLink;
}
