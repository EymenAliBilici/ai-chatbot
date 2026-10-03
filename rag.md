# 📄 RAG (Retrieval-Augmented Generation)

## 🤔 What is RAG?

RAG is an AI technique that allows the model to answer questions based on 
your own documents instead of only using its built-in knowledge.
Without RAG → AI answers from its own training data With RAG → AI answers from YOUR documents

---

## ⚙️ How Does It Work?
1. Your PDF is split into small chunks ↓
2. Each chunk is converted into vectors (embeddings) ↓
3. Vectors are stored in ChromaDB ↓
4. User asks a question ↓
5. Router detects → "This is a document question" ↓
6. Most relevant chunks are retrieved from ChromaDB ↓
7. AI answers based on those chunks

---

## 🚀 How to Run RAG in This Project?

### Step 1: Add Your PDF and Select an Embedding Model

1. Replace `your_pdf.pdf` with your own PDF file in the project root.

2. Visit [Google Embedding Models](https://ai.google.dev/gemini-api/docs/embeddings) to select an embedding model.

3. Then update your `.env` file:

```bash
FILE_PATH=your_pdf.pdf
GOOGLE_AI_EMBEDDINGS_MODEL=your_google_gemini_embeddings_model
```

### Step 2: Test The Vector DB

```bash
python test_vector_db.py
```

You can test the Vector DB and if there any wrongs you will learn it from here


### Step 3: Create The Vector Database

```bash
    python vector_db.py
```

This will split your document into chunks and store them in chroma/db/


### Step 4: Summarise The Document

```bash
python document_summariser.py
```

This will create a summary of your document for the Router chain. The summary is stored in MySQL.


### Step 5: Run The App

```bash
python main.py
```

Now you can ask questions about your document!


## ✅ Quick Checklist

1. PDF file added to project root
2. FILE_PATH updated in .env
3. Run `python vector_db.py`
4. Run `python test_vector_db.py`
5. Run `python document_summariser.py`
6. Run `python main.py`
7. Ask questions about your document! 🎉

### 💬 Example

You  → "What does the document say about X?"

Bot  → Router detects RAG
     → Retrieves relevant chunks
     → "Based on the document, X means..."