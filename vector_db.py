from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import GOOGLE_AI_EMBEDDINGS_MODEL , FILE_PATH
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


class VectorDB:

    def __init__(self):
        self.file_path = FILE_PATH
        self.persist_directory = "chroma/db"
        self.embedding = GoogleGenerativeAIEmbeddings(model=GOOGLE_AI_EMBEDDINGS_MODEL)


    def main(self):
        try:
            loader = PyPDFLoader(file_path=self.file_path)
            docs = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1800,
                chunk_overlap = 220
            )

            vector_store = Chroma.from_documents(
                documents=docs,
                embedding=self.embedding,
                persist_directory=self.persist_directory
            )

            print(vector_store)

        except Exception as e:
            return f"An Error Occurred  --->>  {e}"


if __name__ == "__main__":
    vector_db = VectorDB()
    result = vector_db.main()
    print(result)