# **AI Voice Assist for Customer Support🎙️🤖**  

## **Overview**  
AI Voice Assist is a Python-based voice assistant that can recognize speech, process commands, and respond intelligently. It utilizes **Flask**, **OpenAI’s GPT**, **ElevenLabs for text-to-speech**, and other AI-driven tools to enhance user interaction.  

🚀 **Current Status:**  
- ✅ Backend is fully functional  
- ❌ **Frontend is not yet connected** (Planned for future updates)  

---

## **Features**  
✔️ **Speech Recognition** – Converts spoken words into text using `SpeechRecognition`  
✔️ **AI-powered Responses** – Uses `openai` & `google-generativeai` for intelligent conversations  
✔️ **Text-to-Speech** – Converts responses into speech with `elevenlabs`  
✔️ **Multilingual Translation** – Supports multiple languages via `deep-translate`  
✔️ **Environment Variable Support** – Uses `python-dotenv` for secure API key management  
✔️ **Flask-based Backend** – Lightweight API for handling voice requests  

---

## **Installation & Setup**  

### **1. Clone the Repository**  
```bash
git clone https://github.com/SivaShankar-Juthuka/AI_Voice_Assist.git
cd AI_Voice_Assist
```

### **2. Create and Activate a Virtual Environment (Recommended)**  
```bash
python -m venv venv
```
#### **Activate the Virtual Environment:**  
- **Windows:**  
  ```bash
  venv\Scripts\activate
  ```
- **Mac/Linux:**  
  ```bash
  source venv/bin/activate
  ```

### **3. Install Dependencies**  
```bash
pip install -r requirements.txt
```

### **4. Set Up Environment Variables**  
Create a `.env` file in the project root and add your API keys:  
```
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY =your-gemini-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
ELEVENLABS_VOICE_ID = voice-id
ELEVENLABS_MODEL = model-name
```

---

## **Usage**  

### **Run the Flask Backend**  
```bash
python main.py
```
The backend will start, ready to process voice commands.  

---

## **Planned Updates 🚀**  
🔗 **Connect Frontend to Backend**  
🎨 **Develop a User Interface**  
📡 **Enhance AI Capabilities**  

---

## **Contributing**  
Want to improve AI Voice Assist? Fork the repo, make changes, and submit a pull request!  

---

## **License**  
This project is open-source.  

---
