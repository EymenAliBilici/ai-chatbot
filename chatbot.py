import pymysql
from uuid import uuid4
from config import USER , GEMINI_API_KEY , GEMINI_MODEL , PASSWORD , PORT , DATABASE , HOST
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder
from langchain_community.chat_message_histories import SQLChatMessageHistory


class Structure:

    def __init__(self) -> None:
        self.LLM = ChatGoogleGenerativeAI(model=GEMINI_MODEL , temperature=0.5)
        self.db_path = self._get_mysql_path()
        self.chain = self._create_chain()
        self._init_session_db()
        

    def _get_mysql_path(self) -> str:
        return f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"


    def _connect_db(self):
        return pymysql.connect(
            user=USER,
            port=int(PORT),
            host=HOST,
            database=DATABASE,
            password=PASSWORD,
            cursorclass=pymysql.cursors.DictCursor
        )


    def _get_session_history(self , session_id : str) -> BaseChatMessageHistory:
        return SQLChatMessageHistory(
            session_id=session_id,
            connection=self.db_path,
            table_name="messages"
        )


    def _init_session_db(self):
        conn = self._connect_db()
        cursor = conn.cursor()

        try:
            query = """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id  VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    chat_title VARCHAR(255) DEFAULT 'new chat',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

            cursor.execute(query)
            conn.commit()

        except pymysql.Error as e:
            return f"An Error Occurred From MySQL Server  --->>  {e}"

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

        finally:
            conn.close()


    def _create_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system" , "you're prefessional assistant , Your job is to assist the user in a detailed and professional manner"),
            MessagesPlaceholder(variable_name="history"),
            ("human" , "{question}")
        ])

        chain = prompt | self.LLM | StrOutputParser()

        chain_memory = RunnableWithMessageHistory(
            chain,
            self._get_session_history,
            input_messages_key="question",
            history_messages_key="history"
        )

        return chain_memory




    def create_session(self , user_id : str , chat_title : str = "new chat") -> str:
        session_id = str(uuid4())
        conn = self._connect_db()
        cursor = conn.cursor()

        try:
            query = """
                INSERT INTO chat_sessions (session_id , user_id , chat_title) VALUES (%s , %s , %s)
            """

            cursor.execute(query , (session_id , user_id , chat_title))
            conn.commit()

        except pymysql.Error as e:
            return f"An Error Occurred From MySQL Server  --->>  {e}"

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

        finally:
            conn.close()

        return session_id


    def list_sessions(self , user_id : str) -> list[dict]:
        conn = self._connect_db()
        cursor = conn.cursor()
        sessions = []

        try:
            query = """
                SELECT chat_title , session_id
                FROM chat_sessions
                WHERE user_id = %s
                ORDER BY created_at DESC
            """

            cursor.execute(query , (user_id,))

            rows = cursor.fetchall()

            for i in rows:
                sessions.append(i)

        except pymysql.Error as e:
            return [{"error" : f"An Error Occurred From MySQL Server  --->>  {e}"}]

        except Exception as e:
            return [{"error" : f"An Error Occurred  --->>  {e}"}]

        finally:
            conn.close()

        return sessions


    def update_chat_title(self , session_id : str , new_chat_title : str) -> str:
        conn = self._connect_db()
        cursor = conn.cursor()

        try:
            query = """
                UPDATE chat_sessions 
                SET chat_title = %s
                WHERE session_id = %s
            """

            cursor.execute(query , (new_chat_title , session_id))
            conn.commit()
            return "Title Successfully Updated !"

        except pymysql.Error as e:
            return f"An Error Occurred From MySQL Server  --->>  {e}"

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

        finally:
            conn.close()


    def delete_chat(self , session_id : str) -> str:
        conn = self._connect_db()
        cursor = conn.cursor()

        try:
            query = """
                DELETE FROM chat_sessions
                WHERE session_id = %s
            """

            cursor.execute(query , (session_id,)) 
            conn.commit()
            return "Chat Successfully deleted !"

        except pymysql.Error as e:
            return f"An Error Occurred From MySQL Server  --->>  {e}"

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

        finally:
            conn.close()     


    def get_messages(self , session_id : str):
        history = self._get_session_history(session_id=session_id)
        return history.messages


    def chat(self , session_id : str , query : str) -> str:
        config = RunnableConfig({"configurable" : {"session_id" : session_id}})

        try:
            response = self.chain.invoke({"question" : query} , config=config)
            return response

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"
        



if __name__ == "__main__":
    # For Test Functions
    chatbot = Structure()

    user = "Anthony"

    session_id = chatbot.create_session(user_id=user , chat_title="AI Engineering")
    print(f"Created new session : {session_id}")

    update = chatbot.update_chat_title("25bbb9cb-6190-4838-9cb3-c057fa23e882" , "Iot's Future")

    delete = chatbot.delete_chat("25bbb9cb-6190-4838-9cb3-c057fa23e882")

    sessions = chatbot.list_sessions(user_id=user)
    print(sessions)

    if not sessions:
        session_id = chatbot.create_session(user_id=user , chat_title="IoT Engineering")
        print(f"Created new session : {session_id}")

    else:
        session_id = sessions[0]['session_id']
        print(session_id)
    

    response = chatbot.chat(session_id=session_id , query="Hello")
    print(response)

    print(" === MESSAGE HISTORY === ")
    for msg in chatbot.get_messages(session_id=session_id):
        print(f" {msg.type} - {msg.content}")
    # print(chatbot.get_messages(session_id=session_id))