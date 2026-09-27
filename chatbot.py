import pymysql
from uuid import uuid4
from config import USER , GEMINI_API_KEY , GOOGLE_AI_EMBEDDINGS_MODEL , GEMINI_MODEL , PASSWORD , PORT , DATABASE , HOST , FILE_PATH
from langchain_google_genai import ChatGoogleGenerativeAI , GoogleGenerativeAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig , RunnablePassthrough , RunnableBranch
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_chroma import Chroma
from operator import itemgetter
from pydantic import BaseModel , Field
from typing import Literal


class RouteQuery(BaseModel):
    data_source : Literal["RAG" , "CHAT"] = Field(
        ...,
        description="Route to 'RAG' for document questions or 'CHAT' for general conversation"
    )



class Structure:

    def __init__(self) -> None:
        self.LLM = ChatGoogleGenerativeAI(model=GEMINI_MODEL , temperature=0.5)
        self.embedding = GoogleGenerativeAIEmbeddings(model=GOOGLE_AI_EMBEDDINGS_MODEL)
        self.persist_directory = "chroma/db"
        self.vector_store = Chroma(embedding_function=self.embedding , persist_directory=self.persist_directory)
        self.retriever = self.vector_store.as_retriever(search_kwargs = {"k" : 3})
        self.db_path = self._get_mysql_path()
        self.chain = self._create_chain()
        self._init_session_db()
        

    def _get_mysql_path(self) -> str:
        return f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"


    def _get_summary(self):
        conn = self._connect_db()
        cursor = conn.cursor()

        try:
            query = """
                SELECT summary
                FROM summaries
                WHERE document_name = %s
            """

            cursor.execute(query , (FILE_PATH,))
            text = str(cursor.fetchone())

            return text

        except pymysql.Error as e:
            return f"An Error Occurred From MySQL Server  --->>  {e}"

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

        finally:
            conn.close()


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


    def _format_docs(self , document):
        return "\n\n".join(i.page_content for i in document)


    def _router_chain(self):
        router_template = """
            You're a professional classification assistant
            You're job is analyze the question and write 'RAG' or 'CHAT'

            Rules:
                1 - CHAT: greetings, general knowledge, daily conversation / question, 
                    math, coding, opinions, advice, translations , countries , cultures etc.
                2 - RAG: ONLY when the question is specifically about 
                    the uploaded document content described below

            RAG summary : {summary}

            Give only one word ('RAG' or 'CHAT') , don't write anything else
        """

        router_prompt = ChatPromptTemplate.from_messages([
            ("system" , router_template),
            ("human" , "{question}")
        ])

        structured_llm = self.LLM.with_structured_output(RouteQuery)

        router_chain = (
            RunnablePassthrough.assign(
                summary = lambda _: self._get_summary()
            )
            | router_prompt
            | structured_llm
        )

        return router_chain


    def _chat_chain(self):
        template = """
            You are a highly skilled and friendly AI assistant.

            Rules:
                1 - Respond in the same language the user writes in
                2 - Be clear, concise and professional
                3 - You can answer any general question using your own knowledge
                4 - If user greets you, greet them back warmly
                5 - Use markdown formatting when helpful

        """

        prompt = ChatPromptTemplate.from_messages([
            ("system" , template),
            MessagesPlaceholder(variable_name="history"),
            ("human" , "{question}")
        ])

        chain = prompt | self.LLM | StrOutputParser()

        return chain


    def _rag_chain(self):
        rephrase_template = """
            Take into account the chat history and the user’s most recent issue 
            If the user asks a question using expressions such as ‘that’, ‘this’ or
            ‘that one’ in relation to the previous context:
            rewrite the question as a search query that is understandable on its own 
            If the question is already clear, do not make any adjustments and NEVER 
            answer the question; simply return the corrected question as the output
        """

        rephrase_prompt = ChatPromptTemplate.from_messages([
            ("system" , rephrase_template),
            ("human" , "{question}")
        ])

        rephrase_chain = rephrase_prompt | self.LLM | StrOutputParser()

        template = """
            You are a professional document assistant.

            Rules:
                1 - Answer questions ONLY based on the provided context
                2 - Respond in the same language the user writes in
                3 - If the context contains relevant information, provide a detailed answer
                4 - If the context does NOT contain relevant information, say:
                    "This question is not covered in the uploaded documents. 
                    Please try asking a general question instead."
                5 - Never make up information that is not in the context
                6 - Use markdown formatting when helpful

            Context: {context}

        """

        prompt = ChatPromptTemplate.from_messages([
            ("system" , template),
            MessagesPlaceholder(variable_name="history"),
            ("human" , "{question}")
        ])

        chain = (
            RunnablePassthrough.assign(
                search_query = rephrase_chain
            )
            |
            RunnablePassthrough.assign(
                context = itemgetter("search_query") | self.retriever | self._format_docs
            )
            | prompt
            | self.LLM
            | StrOutputParser()
        )

        return chain


    def _create_chain(self):
        router_chain = self._router_chain()
        rag_chain = self._rag_chain()
        chat_chain = self._chat_chain()

        branch = RunnableBranch((lambda x : x['topic'].data_source == "RAG" , rag_chain) , chat_chain)

        chain = RunnablePassthrough.assign(topic=router_chain) | branch

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

    sessions = chatbot.list_sessions(user_id=user)

    if not sessions:
        session_id = chatbot.create_session(user_id=user , chat_title="example chat")
        print(f"Created new session : {session_id}")

    else:
        session_id = sessions[0]['session_id']
        print(session_id)
    

    response = chatbot.chat(session_id=session_id , query="example question")
    print(response)

    print(" === MESSAGE HISTORY === ")
    for msg in chatbot.get_messages(session_id=session_id):
        print(f" {msg.type} - {msg.content}")