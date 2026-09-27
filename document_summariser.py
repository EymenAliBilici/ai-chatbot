import pymysql
from langchain_chroma import Chroma
from config import (
    GEMINI_API_KEY , GEMINI_MODEL , GOOGLE_AI_EMBEDDINGS_MODEL , PASSWORD , PORT , USER , DATABASE , HOST
)
from langchain_google_genai import ChatGoogleGenerativeAI , GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from uuid import uuid4
from langchain_core.runnables import RunnableLambda


class Summariser:

    def __init__(self) -> None:
        self.embedding = GoogleGenerativeAIEmbeddings(model=GOOGLE_AI_EMBEDDINGS_MODEL)
        self.persist_directory = "chroma/db"
        self.vector_store = Chroma(embedding_function=self.embedding , persist_directory=self.persist_directory)
        self.LLM = ChatGoogleGenerativeAI(model=GEMINI_MODEL , api_key=GEMINI_API_KEY , temperature=0.1)


    def _init_summariser_table(self):
        conn = self._connect_db()
        cursor = conn.cursor()

        try:
            query = """
                CREATE TABLE IF NOT EXISTS summaries (
                    id VARCHAR(255) PRIMARY KEY NOT NULL,
                    summary VARCHAR(1755),
                    document_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

            cursor.execute(query)

            conn.commit()

        except pymysql.Error as e:
            return f"An Error Occurred From The MySQL Database  --->>  {e}"

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

        finally:
            conn.close()


    def _connect_db(self):
        return pymysql.connect(
            user=USER,
            port=int(PORT),
            password=PASSWORD,
            host=HOST,
            database=DATABASE,
            cursorclass=pymysql.cursors.DictCursor
        )


    def get_document(self , transaction : str , _=None):

            result = self.vector_store.get(include=['documents' , "metadatas"])
            
            def get_text():
                docs = result.get("documents" , [])
                text = "\n\n".join(docs)

                return text

            def get_docs_name():
                metadata = result.get("metadatas" , [])[0].get("source" , "")

                return metadata

            if transaction == "text":
                return get_text()

            if transaction == "document_name":
                return get_docs_name()


    def post_ai(self):
        promtp_template = """
            you're a professional summariser
            you're job is summarise the context above according the rules

            rules:
                The Result max be same with Context's language
                The result must be 6-7 sentences
                The result must be clearly and successfully
                The result must be str type
                Don't add extra informations into summarise

            context : {context}

        """

        prompt = ChatPromptTemplate.from_messages([
            ("system" , promtp_template),
            ("human" , "summarise the context above according the rules.")
        ])

        chain = (
            { "context" : RunnableLambda(lambda x : self.get_document(transaction="text"))}
            | prompt
            | self.LLM
            | StrOutputParser()
        )

        return chain.invoke({}) 


    def post_summary_to_db(self):
        conn = self._connect_db()
        cursor = conn.cursor()
        id = str(uuid4())
        summary = self.post_ai()
        document_name = self.get_document(transaction="document_name")

        try:
            query = """
                INSERT INTO summaries (id , summary , document_name)
                VALUES (%s , %s , %s)
            """
            

            cursor.execute(query , (id , summary , document_name))
            conn.commit()

        except pymysql.Error as e:
            return f"An Error Occurred From The MySQL Database  --->>  {e}"

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"

        finally:
            conn.close()



if __name__ == "__main__":
    summariser = Summariser()
    print(summariser.post_summary_to_db())