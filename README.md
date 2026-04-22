Slottet Ealdror – Ett RAG-drivet RPG
Välkommen till Slottet Ealdror, ett textbaserat rollspel där din resa genom mörka källare och farliga baracker får liv med hjälp av artificiell intelligens. Spelet kombinerar klassisk spellogik i Python med modern RAG-teknik (Retrieval-Augmented Generation) för att skapa en unik och atmosfärisk berättarupplevelse.
Funktioner
	• AI-Dungeon Master: Använder Google Gemini 2.5 Flash för att generera målande miljö- och stridsbeskrivningar.
	• RAG-system: En vectordatabas (ChromaDB) lagrar spelets "lore". AI:n hämtar kontextspecifik information för att undvika hallucinationer och hålla sig till spelets värld.
	• Semantisk sökning: AI:n förstår sammanhanget i rummet oavsett hur du formulerar dina kommandon.
	• Automatiskt evalueringssystem: En inbyggd modul som testar att AI:n hämtar korrekt information innan spelet startar.
1. Förutsättningar
Du behöver Python installerat samt en API-nyckel från Google AI Studio.
2. Installera bibliotek
Klona detta repository och kör följande kommando i terminalen:
pip install -r requirements.txt

3. API-Nyckel
Öppna berattare.py (eller din .env-fil) och klistra in din Google Gemini API-nyckel:
Python

# I berattare.py
self.api_key = "DIN_API_NYCKEL_HÄR"

Så här spelar du
Steg 1: Initiera databasen
Innan du kör spelet för första gången måste du bygga din vectordatabas från lore-filen:

python setup_db.py

teg 2: Starta spelet
Starta äventyret genom att köra huvudfilen:
Bash

python main.py
