import os 
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

class Narrator:
    def __init__(self):
        # Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

        # Ladda vectordatabasen
        self.vector_db = Chroma(
            persist_directory="./db_ealdror",
            embedding_function=self.embeddings
        )

        # Initiera Gemini som motor
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    
    def get_description(self, event_info):
        # Skapar en sökväg till vectorstore baserat på rumemt eller fienden
        search_query = f"{event_info.get('rum')} {event_info.get('fiende', '')}"

        # Hämta de två mest relevanta textbitarna från vectorstore 
        relevant_chunks = self.vector_db.similarity_search(search_query, k=2)
        context = "\n".join([doc.page_content for doc in relevant_chunks])

        # Systemprompt, ger Gemini en personlighet
        system_instruction = f"""
        Du är en atmosfärisk och mörk Dungeon Master för rollspelet 'Slottet Ealdror'.eval
        använd följande bakgrundsinformation för att beskriva vad som händer:
        {context}

        Händelse: {event_info.get('typ')}
        Spelarens status: {event_info.get('status')}

        Regler:
        Var kosrtfattad men målande
        Fokusera på sinnena (lukt, ljud, kyla)
        Om en fiende nämns, använd beskrivning från bestiarium
        """

        response = self.llm.invoke(system_instruction)
        return response.content