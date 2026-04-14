# Skapa en vectorstore som databas
import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Hämta API-nyckel
api_key = os.getenv("chat_key")

# Kontrollera att den hittar api key
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
else:
    print("Kunde inte hitta miljövariabeln")

def skapa_databas():
    print("Läser in bakgrundsiformation")
    loader = TextLoader("bakgrundsinformation.md", encoding="utf-8")
    documents = loader.load()

    # Jag delar upp texten i 600 tecken med lite överlapp
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n##", "\n###", "\n\n", "\n", " "]
    )
    chunks = text_splitter.split_documents(documents)

    # Skapar embeddings
    print("Skapa embeddings och sparar i Vectorstore")
    embeddings = GoogleGenerativeAIEmbeddings(model="text-embeddings-004")

    # Skapa och spara databasen lokalt i i mappen db_ealdror
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=r".\\db_ealdror"
    )

    print("Klart, mappen 'db_ealdror' har skapats")

if __name__ == "__main__":
    skapa_databas()