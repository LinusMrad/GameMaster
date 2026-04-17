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
        
        # Test med en annan Query. 
        #search_query = f"Beskrivning av rummet {event_info.get('rum')}. Detaljer om varelser, fiender och monster som heter {event_info.get('fiende', 'inga')}, deras utseende och beteende."

        # Hämta de två mest relevanta textbitarna från vectorstore 
        relevant_chunks = self.vector_db.similarity_search(search_query, k=4)
        context = "\n".join([doc.page_content for doc in relevant_chunks])

        # Systemprompt, ger Gemini en personlighet
        system_instruction = f"""
        Du är en professionell och atmosfärisk Dungeon Master för rollspelet 'Slottet Ealdror'. 
        Din ton är mörk, ödesmättad och fokuserad på sinnena (kyla, lukt, tvekan, skuggor).

        ### DIN ROLL & BEGRÄNSNINGAR:
        1. STRICT TRUTH: Du får ENDAST beskriva föremål, dörrar och varelser som finns i den bifogade BAKGRUNDSINFORMATIONEN.
        2. INGA HALLUCINATIONER: Om en dörr eller ett föremål inte nämns i Lore, finns det inte. Hitta aldrig på magiska effekter eller rumshändelser på egen hand.
        3. INGEN FRAMTIDSBLICK: Beskriv enbart den nuvarande handlingen. Om spelaren tar ett föremål, beskriv bara det ögonblicket fantisera inte om vad som händer i nästa rum.
        4. "När spelaren söker ('sök'), beskriv endast vad de upptäcker eller ser i omgivningen. Spelaren rör eller plockar aldrig upp föremål i sök-beskrivningen. Spara den interaktionen tills spelaren faktiskt använder 'ta'-kommandot.
        {context}

        Händelse: {event_info.get('typ')}
        Spelarens status: {event_info.get('status')}

        ### INSTRUKTIONER FÖR SVAR:
        - Var kortfattad (max 4-5 meningar) men mycket målande.
        - Använd detaljer från Bestiariet om en fiende interagerar.
        - Om spelaren tar ett föremål: Beskriv dess fysiska känsla (tyngd, textur, doft) baserat på informationen i Lore.
        - Om spelaren strider: Beskriv våldet och dramatiken, men håll dig till de skadevärden som anges i statusen.
        """
        response = self.llm.invoke(system_instruction)
        return response.content