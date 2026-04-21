# Skapa en vectorstore som databas
import os
from google import genai
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Hämta API-nyckel och lägg till din nyckel här
os.environ["GOOGLE_API_KEY"] 

def skapa_databas():
    print("Läser in bakgrundsiformation")
    loader = TextLoader("bakgrundsinformation.md", encoding="utf-8")
    documents = loader.load()

    # hämtar innehållet från dokumentet
    full_text = documents[0].page_content

    # Delar upp texten för varje ##(rumsrubrik) mappar ## till "Rum"
    headers_to_split_on = [
        ("##", "Rum")
    ]

    # Skapar splitten
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    # Delar upp rummen i chunks
    chunks = markdown_splitter.split_text(full_text)
    print(f"skapade {len(chunks)} logiska chunks")

    # Skapar embeddings
    print("Skapa embeddings och sparar i Vectorstore")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

    # Skapa och spara databasen lokalt i i mappen db_ealdror
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=r".\\db_ealdror"
    )

    print("Klart, mappen 'db_ealdror' har skapats")

if __name__ == "__main__":
    skapa_databas()