import httpx
import json


class APIclient:

    def __init__(self) -> None:
        self.base_url = "http://localhost:8000"

    def create_session(self , user_id : str , chat_title : str = "new chat") -> str:
        payload = {"user_id" : user_id , "chat_title" : chat_title}
        response = httpx.post(url=f"{self.base_url}/create/session" , json=payload)
        return response.json()

    def list_sessions(self , user_id : str) -> list:
        payload = {"user_id" : user_id}
        response = httpx.get(url=f"{self.base_url}/list/sessions" , params=payload)
        return response.json()

    def update_chat_title(self , session_id : str , new_chat_title : str) -> str:
        payload = {"session_id" : session_id , "new_chat_title" : new_chat_title}
        response = httpx.patch(url=f"{self.base_url}/update/chat_title" , json=payload)
        return response.json()

    def delete_chat(self , session_id : str) -> str:
        payload = {"session_id" : session_id}
        response = httpx.delete(url=f"{self.base_url}/delete/chat" , params=payload)
        return response.json()

    def get_messages(self , session_id : str) -> list:
        payload = {"session_id" : session_id}
        response = httpx.get(url=f"{self.base_url}/messages" , params=payload)
        return response.json()

    def chat(self , session_id : str , query : str) -> str:
        payload = {"session_id" : session_id , "query" : query}
        response = httpx.post(url=f"{self.base_url}/chat" , json=payload , timeout=None)
        return response.json()




if __name__ == "__main__":
    api = APIclient()
    # for test the functions , for example : 
    result = api.create_session(user_id="X USer" , chat_title="X Chat")
    result = api.list_sessions(user_id="X user")
    result = api.update_chat_title(session_id="606b42d0-1f0f-46e2-8fcd-cc80f32a66ea" , new_chat_title="Y Chat")
    result = api.delete_chat(session_id="606b42d0-1f0f-46e2-8fcd-cc80f32a66ea")
    result = api.get_messages(session_id="606b42d0-1f0f-46e2-8fcd-cc80f32a66ea")
    # example question to LLM
    result = api.chat(session_id="606b42d0-1f0f-46e2-8fcd-cc80f32a66ea" , query="example question")
    print(result)