import time
from api_client import APIclient

class Main:
    def __init__(self) -> None:
        self.api = APIclient()


    def create_session(self) -> str:
        try:
            user_id = input("Please Enter The User name : ")
            chat_title = input("Please Enter The Chat title : ")
            result = self.api.create_session(user_id=user_id , chat_title=chat_title)
            return result

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

    def list_sessions(self) -> list:
        try:
            user_id = input("Please Enter The User name : ")
            result = self.api.list_sessions(user_id=user_id)
            return result

        except Exception as e:
            return [f"An Error Occurred  --->>  {e}"]

    def update_chat_title(self) -> str:
        try:
            session_id = input("Please Enter The session_id : ")
            new_chat_title = input("Please Enter The new chat title : ")
            result = self.api.update_chat_title(session_id=session_id , new_chat_title=new_chat_title)
            return result

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

    def delete_chat(self) -> str:
        try:
            session_id = input("Please Enter The session_id : ")
            result = self.api.delete_chat(session_id=session_id)
            return result

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

    def get_messages(self) -> list:
        try:
            session_id = input("Please Enter The session_id : ")
            result = self.api.get_messages(session_id=session_id)
            return result

        except Exception as e:
            return [f"An Error Occurred  --->>  {e}"]

    def chat(self) -> str:
        try:
            session_id = input("Please Enter The session_id : ")
            query = input("Please Enter The Message  : ")
            result = self.api.chat(session_id=session_id , query=query)
            return result

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

    def main(self):
        while True:

            print("=" * 25)
            print("        AI CHATBOT")
            print("=" * 25)
            print("1 - Create new chat")
            print("2 - list chats")
            print("3 - update chat title")
            print("4 - delete chat")
            print("5 - get chat messages")
            print("6 - chat with AI")
            print("7 - Exit")

            choice = input("Please Enter a transaction (1-7) : ").strip()

            if choice == "1":
                print(self.create_session())

            elif choice == "2":
                print(self.list_sessions())

            elif choice == "3":
                print(self.update_chat_title())

            elif choice == "4":
                print(self.delete_chat())

            elif choice == "5":
                print(self.get_messages())

            elif choice == "6":
                print(self.chat())

            elif choice == "7":
                print("The program is closing; please wait a little bit.")
                time.sleep(3)
                break

            else:
                print("Invalid choice ! please enter a number between 1-7")


app = Main()
app.main()