# AI Chatbot

> This AI-powered chatbot app provides automated text-based responses to help users with frequently asked questions and routine tasks. The app, which uses basic natural language processing technology, is currently in the development phase.

## ✨ Features

- 🚀 Gemini models support 
- 🐍 FastAPI support
- 🔗 LangChain Integration
- 🗄️ MySQL Database
- ⚡ Performance 
- 🔐 API key Security 

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Language** | Python 3.10+ |
| **AI Model** | Gemini Models |
| **Framework** | LangChain |
| **API** | FastAPI |
| **Database** | MySQL |
| **Validation** | Pydantic |
| **Config** | python-dotenv |

> 📋 Full dependencies list in [requirements.txt](requirements.txt)

## 🔐 Getting Your Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/api-keys)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated key
5. Paste it into your `.env` file 

## 📦 Installation

### 1. Clone The Repo

```bash
git clone https://github.com/eymenalibilici/ai-chatbot.git
cd ai-chatbot
```

### 2. Create a Venv

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Libraries

```bash
pip install -r requirements.txt
```

### 4. Create a Environment (.env) file

#### Copy The .env.example file

```bash
cp .env.example .env
```

#### Open The .env file and enter your keys

### 5. Run The Code

```bash
you can run the code on main.py file (terminal)
```

## 🎯 Using

 > we have 7 basic transactions

```
1 - Create new chat
2 - list chats
3 - update chat title
4 - delete chat
5 - get chat messages
6 - chat with AI
7 - Exit
```


## 📁 Project Structure

```
project/
├── main.py                 # for run the app on terminal
├── api.py                  # FastAPI service
├── config.py               # It's doing return .env datas to python datas (with load=dotenv) 
├── test_ai.py              # For test Genai models , you can run this file before run the project
├── api_client.py           # It's taking the responses from API
├── chatbot.py              # the main file , It have the chatbot structure
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
└── README.md
└── LICENSE
```

## 🗺️ Roadmap

 - [✅] basic chain
 - [✅] MySQL database
 - [✅] FastAPI service
 - [❌] GUI
 - [❌] LangGraph
 - [❌] RAG
 
## 📄 LICENSE

This Project have MIT license  ,  You can refer to [LICENSE](LICENSE) for details.

## 👤 Developer

**Eymen Ali Bilici**

- 💼 LinkedIn: [linkedin.com/in/eymen-ali-bilici-34298b397/](https://www.linkedin.com/in/eymen-ali-bilici-34298b397/)
- 📧 Email: eymenalibilici@icloud.com

## 🌟 Support

If you like this project please don't forget give the ⭐ , thanks.

## 🙏 Thanks

 - [Google-ai-studio](https://aistudio.google.com/)
 - [Python](https://python.org/)
 - [LangChain](https://www.langchain.com/)
 - [MySQL](https://www.mysql.com/)
 - [FastAPI](https://fastapi.tiangolo.com/)