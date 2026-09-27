from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import FILE_PATH , GOOGLE_AI_EMBEDDINGS_MODEL

class TestVectorDB:

    def __init__(self):
        self.persist_directory = "chroma/db"
        self.embedding = GoogleGenerativeAIEmbeddings(model=GOOGLE_AI_EMBEDDINGS_MODEL)
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding
        )


    def main(self):
        result = self.vector_store.get(include=["embeddings" , "documents" , "metadatas"])
        total_chunks = len(result['ids'])
        print(f"Total Chunk Count : {total_chunks}")
        print("First 5 Vector  --->>>  ")
        count = 0

        for idx , (documents , embeddings , metadatas) in enumerate(zip(result['documents'] , result['embeddings'] , result['metadatas'])):
            count += 1

            if count < 6:
                print("="  * 25)
                print(f" -----  Chunk {idx + 1}  ----- ")
                print(f"Character Count  --->>  {len(documents)}")
                print(f"Content  --->>  {documents}")
                print(f"Metadatas  --->>  {metadatas}")
                print(f"Vectors  --->>  {embeddings}")
                print("="  * 25)

            else:
                break


if __name__ == "__main__":
    test_vector_db = TestVectorDB()
    test_vector_db.main()