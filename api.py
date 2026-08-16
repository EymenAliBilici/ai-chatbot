from fastapi import FastAPI , HTTPException
from pydantic import BaseModel
from chatbot import Structure
from fastapi.middleware.cors import CORSMiddleware


class CreateSessionRequest(BaseModel):
    user_id : str
    chat_title : str = "new chat"

class UpdateChatTitleRequest(BaseModel):
    session_id : str
    new_chat_title : str

class ChatRequest(BaseModel):
    session_id : str
    query : str


chatbot = Structure()
app = FastAPI(title="ChatBot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True
)


@app.post("/create/session")
def create_session(request : CreateSessionRequest):
    try:
        session_id = chatbot.create_session(user_id=request.user_id , chat_title=request.chat_title)
        return session_id

    except Exception as e:
        raise HTTPException(status_code=500 , detail=str(e))


@app.get("/list/sessions")
def list_sessions(user_id : str):
    try:
        sessions = chatbot.list_sessions(user_id=user_id)
        return sessions

    except Exception as e:
        raise HTTPException(status_code=500 , detail=str(e))


@app.patch("/update/chat_title")
def update_chat_title(request : UpdateChatTitleRequest):
    try:
        update = chatbot.update_chat_title(session_id=request.session_id , new_chat_title=request.new_chat_title)
        return update

    except Exception as e:
        raise HTTPException(status_code=500 , detail=str(e))


@app.delete("/delete/chat")
def delete_chat(session_id : str):
    try:
        delete = chatbot.delete_chat(session_id=session_id)
        return delete

    except Exception as e:
        raise HTTPException(status_code=500 , detail=str(e))


@app.get("/messages")
def get_messages(session_id : str):
    try:
        history = []
        messages = chatbot.get_messages(session_id=session_id)
        for msg in messages:
            history.append({"type" : msg.type , "content" : msg.content})
        return history

    except Exception as e:
        raise HTTPException(status_code=500 , detail=str(e))


@app.post("/chat")
def chat(request : ChatRequest):
    try:
        response = chatbot.chat(session_id=request.session_id , query=request.query)
        return response

    except Exception as e:
        raise HTTPException(status_code=500 , detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app , host="localhost" , port=8000)