# =========================================
# Importer
# =========================================
import os
import time
import sys
import random
from berattare import Narrator

dm= Narrator()

# =========================================
# Startskärm
# =========================================

#Spelets titelskärm
start_screen = r"""
   ^                 ^
  / \               / \
 /   \             /   \
(_____)           (_____)
 |   |  _   _   _  |   |
 | O |_| |_| |_| |_| O |
 |-  |          _  | - |
 |   |   - _^_     |   |
 |  _|    //|\\  - |   |
 |   |   ///|\\\   |  -|
 |-  |_  |||||||   |   |
 |   |   |||||||   |-  |
 |___|___|||||||___|___|
         (      (
          \      \
           )      )
           |      |
           (      (
            \      \
S L O T T E T   E A L D R O R
============================
"""

# =========================================
# 1. Spelardata / fiendedata
# =========================================
"""
fiendemall
    "namn": {
        "hp": ,
        "armor": ,
        "strength": ,
        "agility": ,
        "intelligence": ,
        "charisma": ,
        "weapon_damage":
    },
"""

enemy_types = {
    "Troll": {
        "hp": 7,
        "armor": 12,
        "strength": 8,
        "agility": 14,
        "intelligence": 8,
        "charisma": 6,
        "weapon_damage": (1, 4)
    },
    "Gravgast": {
        "hp": 11,
        "armor": 14,
        "strength": 12,
        "agility": 12,
        "intelligence": 10,
        "charisma": 8,
        "weapon_damage": (1, 6)
    },
    "Nothic": {
        "hp": 45,
        "armor": 15,
        "strength": 14,
        "agility": 16,
        "intelligence": 13,
        "charisma": 8,
        "weapon_damage": (3, 6)
    },
    "Ealdror": {
        "hp":22,
        "armor":12,
        "strength":9,
        "agility":14,
        "intelligence":17,
        "charisma":11,
        "weapon_damage":(4, 6)
    },
}


# =========================================
# 2. Klasser för spelare och fiender
# =========================================

class Character:
    def __init__(self, name, hp, armor, strength, agility, intelligence, charisma, weapon_damage):
        self.name = name
        self.hp = hp
        self.armor = armor
        self.strength = strength
        self.agility = agility
        self.intelligence = intelligence
        self.charisma = charisma
        self.weapon_damage = weapon_damage

    def take_damage(self, amount):
        self.hp -= amount
        #print(f"{self.name} tar {amount} skada. HP kvar: {self.hp}")
        
    def is_alive(self):
        return self.hp > 0
    
    def get_modifier(self, stat):
        return(stat - 10) // 2



class Player(Character):
    def __init__(self, name, hp, armor, strength, agility, intelligence, charisma, weapon_damage):
        super().__init__(name, hp, armor, strength, agility, intelligence, charisma, weapon_damage)
        self.inventory = []
        self.current_room = None
        self.equipped_weapon = None


class Krigare(Player):
    def __init__(self, name):
        super().__init__(
            name=name,
            hp=14,
            armor=15,
            strength=16,
            agility=10,
            intelligence=8,
            charisma=10,
            weapon_damage=(1, 8)
        )


class Halvling(Player):
    def __init__(self, name):
        super().__init__(
            name=name,
            hp=10,
            armor=14,
            strength=8,
            agility=16,
            intelligence=13,
            charisma=16,
            weapon_damage=(1, 6)
        )

class Dvärg(Player):
    def __init__(self, name):
        super().__init__(
            name=name,
            hp=11,
            armor=18,
            strength=14,
            agility=8,
            intelligence=10,
            charisma=12,
            weapon_damage=(1, 8)
        )

class Alv(Player):
    def __init__(self, name):
        super().__init__(
            name=name,
            hp=8,
            armor=12,
            strength=10,
            agility=15,
            intelligence=16,
            charisma=8,
            weapon_damage=(1, 8)
        )


# Fiende
class Enemy(Character):
    def __init__(self, name):
        stats = enemy_types[name]
        super().__init__(
            name=name,
            hp=stats["hp"],
            armor=stats["armor"],
            strength=stats["strength"],
            agility=stats["agility"],
            intelligence=stats["intelligence"],
            charisma=stats["charisma"],
            weapon_damage=stats["weapon_damage"]
        )

# ================= Fiender ================
# Jag valde att separera speldata (t.ex. fiendetyper och rumstyper)
# från själva klasserna genom att använda dictionaries.
# Detta gör systemet mer flexibelt och lättare att utöka utan att
# ändra den underliggande logiken





# =========================================
# 3. Item-klasser
# =========================================
class Item:
    def __init__(self, name, description="", hidden=False, dc=10):
        self.name = name
        self.description = description
        self.hidden = hidden
        self.dc = dc
    
    def use(self, player):
        print(f"Du kan inte använda{self.name} här.")

class Key(Item):
    def use(self, player):
        room = player.current_room

        for direction, exit_data in room.exits.items():
            if exit_data["locked"] and exit_data["key"] == self.name:
                exit_data["locked"] = False
                print(f"...")
                return
        print(f"{self.name} passar inte här.")

class Potion(Item):
    def __init__(self, name, heal_amount, description=""):
        super().__init__(name, description)
        self.heal_amount = heal_amount

    def use(self, player):
        player.hp += self.heal_amount
        print(f"Du använder {self.name} och återfår {self.heal_amount} HP.")
        print(f"HP: {player.hp}")
        player.inventory.remove(self)

class Book(Item):
    def __init__(self, name, text):
        super().__init__(name)
        self.text = text

    def use(self, player):
        print(f"Du läser {self.name}")
        print(self.text)

class Weapon(Item):
    def __init__(self, name, description="", damage_bonus=0, attack_bonus=0, hidden=False):
        super().__init__(name, description)
        self.damage_bonus = damage_bonus
        self.attack_bonus = attack_bonus

    def use(self, player):
        player.equipped_weapon = self
        print(f"Du utrustar {self.name}")

# =========================================
# 4. Spelvärldsdata
# =========================================
"""
Här lägger man in de olika rummen man vill använda för sitt spel, nedan finns en mall för hur rummen ska se ut.


"rumsmall"
        "namn": {
        "description":,
        "items":,
        "enemy":,
    },
"""
room_types = {
    "Källare": {
        "description": "En kall och fuktig källare",
        "items": [Key("rostig nyckel", "En gammal nyckel täckt av rost.", hidden=True, dc=2)],
        "enemy" : None
    }, 

    "Baracker": {
        "description":"Barracker med sängar, mat och logi för troll",
        "items": [Weapon("Svärd", "Ett gammalt rostigt svärd", damage_bonus=1, attack_bonus=2, hidden=False)],
        "enemy": "Troll"
    },

    "Korridor":{
        "description": "En mörk korridor med fladdrande facklor",
        "items": [],
        "enemy": None
    }, 

    "Ambros Kypta": {
    "description":"En dammig krypta med tre stående kistor.",
    "items": [],# eventuellt nyckel till slavkammare
    "enemy": "Gravgast",
    }, 

    "Slavkammare": {
    "description": "Ett lånsmalt rum fyllt med celler längs ena väggen, en mager människa finns i en av cellerna",
    "items":[], 
    "enemy":None,
    }, 

    "Vapenkammare": {
    "description": "Vapenkammare fylld med rader av svärd av olika slag",
    "items": [Weapon("Svärd", "Ett gammalt rostigt svärd", damage_bonus=1, attack_bonus=2, hidden=False)],
    "enemy": None,
    }, 

    "Bergsspricka": {
    "description":"En spricka som uppstått i bergrgunden där slottet står. en stank av ruttet kött fyller luften",
    "items": [],
    "enemy": "Nothic",
    }, 

    "Vaktbaracker": {
    "description":"En barack med fyra träsängar och smutsig disk utrsött överallt",
    "items": [],
    "enemy": "Troll"
    }, 

    "Magikerns lya": {
    "description": "Det här rumemt ser ut att vara en lya för en magisker, det är fyllt av gamla böcker och magiska drycker",
    "items": [Potion("Hälsodryck", 5, "En liten flaska med röd vätska."),
                Book("bok", "Trollens svagheter")], # svåre check på bok som hjälper en att klara bossen
    "enemy": None,
    },  #

    "Ealdrors rum": { #
    "description": "Väggarna i detta rum är draperade i röd siden, längst in i rummet står en säng och i mitten finns ett litet upplyst skrivbord. Hukad över skrivbordet sittter en mörk figur",
    "items":[], # eventuellt en trasure som du vinenr spelet med
    "enemy":"Ealdror",
    }, 

}

# =========================================
# 5. Rumsklass
# =========================================

class Room:
    def __init__(self, room_type):
        self.room_type = room_type
        data = room_types[room_type]
        
        self.description = data["description"]
        self.items = data["items"].copy()
        self.enemy = Enemy(data["enemy"]) if data["enemy"] else None
        self.exits = {}
        self.searched = False

    def connect(self, direction, room, locked=False, key=None, hidden=False, dc=10):
        self.exits[direction] = {
            "room": room,
            "locked": locked,
            "key": key,
            "hidden": hidden,
            "dc": dc
        }    

# =========================================
# 6. Hjälpfunktioner / spellogik
# =========================================

def roll_d20():
    """
    Återger en slumpmässig siffra mellan 1 - 20
    Detta återspeglar ett tärningskast och beroende på siffan kan vi utföra ett sepcifikt kommando.
    """
    return random.randint(1, 20)

def roll_damage(attacker):
    """
    Definierar skadan som sker i en attack. ÅTerger en slumpmässig siffran i attackeraens range och lägger till dess bonus från karaktärens 
    strength
    """
    low, high = attacker.weapon_damage
    damage = random.randint(low, high) + attacker.get_modifier(attacker.strength)
    if isinstance(attacker, Player) and attacker.equipped_weapon:
        damage += attacker.equipped_weapon.damage_bonus
    return max(1, damage)


def attack(attacker, defender):
    """
    Attackfuntkion, hämtar från roll d20 kollar om siffran är hög nog att träffa (ögre än armor) om träff 
    hämtar skada från roll_damage om lägre än armor ignen träff. 
    om rolld_d20 1 kritisk miss om 20 kritisk träff
    """
    base = roll_d20()
    mod = attacker.get_modifier(attacker.strength)
    weapon_bonus = 0
    if isinstance(attacker, Player) and attacker.equipped_weapon:
        weapon_bonus = attacker.equipped_weapon.attack_bonus
    
    total = base + mod + weapon_bonus
    damage = 0
    resultat_text = ""

    # --- Logik för träff/miss ---
    if base == 1:
        resultat_text = "fumlar totalt och missar pinsamt"
    elif base == 20:
        damage = roll_damage(attacker) * 2
        resultat_text = f"gör en legendarisk kritisk träff och utdelar {damage} skada"
        defender.take_damage(damage)
    elif total >= defender.armor:
        damage = roll_damage(attacker)
        resultat_text = f"träffar sitt mål och gör {damage} skada"
        defender.take_damage(damage)
    else:
        resultat_text = "försöker attackera men missar"

    # Information om HP(karaktärens hälsa)

    if not defender.is_alive():
        hälso_info = "DÖDLIG: Fienden faller till marken, besegrad och livlös."
    elif defender.hp < 5:
        hälso_info = "KRITISK: Fienden blöder kraftigt, vacklar och ser ut att vara nära döden."
    elif damage > 0:
        hälso_info = f"SÅRAD: Fienden tar skadan men står fortfarande upp. HP kvar: {defender.hp}."
    else:
        hälso_info = f"OSKADD: Fienden är fortfarande vid god vigör. HP: {defender.hp}."

    # --- AI beskrivning
    info = {
        "typ": "stridshändelse",
        "rum": "en pågående strid",
        "fiende": defender.name if isinstance(defender, Enemy) else attacker.name,
        "status": f"{attacker.name} {resultat_text} mot {defender.name}.{hälso_info} "
                  f"Försvararens HP är nu {max(0, defender.hp)}."
    }

    # Hämta den målande beskrivningen
    ai_text= dm.get_description(info)
    print("----------------------------------------------------")
    # Skriv ut resultatet
    print(f"{ai_text}")
    if defender.is_alive():
        print(f"\n[Tärning: {total} mot AC {defender.armor}][{defender.name} har {defender.hp} HP kvar]") 




# Check för handlingar i världen, tex smyga förbi fiende
def skill_check(character, stat_value, dc, action_name="handling"):
    """
    Check för handlingar i världen, tex smyga förbi fiende, leta och upptäcka dolda föremål.
    """
    base = roll_d20()
    mod = character.get_modifier(stat_value)
    total = base + mod

    print(f"{character.name} försöker {action_name}")
    print(f"slår {base} modifier {mod} = {total}")
    print(f"Svårighetsgrad: {dc}")

    if base == 1:
        print("Kritiskt misslyckande!")
        return False
    elif base == 20:
        print("Kritisk framgång!")
        return True
    elif total >= dc:
        print("Lyckades!")
        return True
    else:
        print("Misslyckades!")
        return False
    

def silent_check(character, stat_value, dc):
    base = roll_d20()
    mod = character.get_modifier(stat_value)
    total = base + mod

    if base == 1:
        return False
    if base == 20:
        return True
    return total >= dc

    #smyga
def sneak(attacker, defender):
    stealth_dc = 10 + defender.get_modifier(defender.agility)
    return skill_check(attacker, attacker.agility, stealth_dc, "smyga förbi")


def show_room(player):
    """
    Visar information om rummet spelaren befinner sig i.
    """
    room = player.current_room
    # Förbereder data för AIn
    info = {
        "typ": "besök i rum",
        "rum": room.room_type,
        "fiende": room.enemy.name if room.enemy and room.enemy.is_alive() else "Ingen",
        "status": f"HP: {player.hp}, Utrustning: {player.equipped_weapon.name if player.equipped_weapon else 'Ingen'}"
    }

    # Hämta beskrivning från Gemini
    ai_description = dm.get_description(info)

    print("\n----------------------------------------------------")
    print(ai_description)
    print("----------------------------------------------------")

    # Visa detaljer som föremål och utgångar
    visible_items = [item.name for item in room.items if not item.hidden]
    if visible_items:
        print(f"Synliga föremål: {', '.join(visible_items)}")

    visible_exits = [d for d, e in room.exits.items() if not e["hidden"]]
    print(f"Utgångar: {', '.join(visible_exits)}")

def player_command(player, command):
    room = player.current_room
    command = command.lower().strip()

    # Avlsuta spel
    if command == "avsluta":
        return False
    
    # Hjälp
    elif command == "hjälp":
        print("Kommandon: norr, söder, öster, väster, kolla, sök, inventarie, ta[föremål], attackera, avsluta, smyg, status")

    elif command == "status":
        print(f"Namn: {player.name}")
        print(f"HP: {player.hp}")
        print(f"Rustning: {player.armor}")
        print(f"Styrka: {player.strength}")
        print(f"Smidighet: {player.agility}")
        print(f"Intelligens: {player.intelligence}")
        print(f"Karisma: {player.charisma}")

    #Titta på rummet igen
    elif command == "kolla":
        show_room(player)

    # visa inventarie
    elif command == "inventarie":
        if player.inventory:
            print("Du har:", ", ".join(item.name for item in player.inventory))
            if player.equipped_weapon:
                print(f"Utrustad: {player.equipped_weapon.name}")
        else:
            print("Din inventarie är tomt.")
    
    # ta item
    elif command.startswith("ta "):
        print("...")
        item_name = command[3:]
        found_item = None
    
        for item in room.items:
            if item.name.lower() == item_name:
                found_item = item
                break
        
        if found_item:
            player.inventory.append(found_item)
            room.items.remove(found_item)
            #print(f"Du tog {found_item.name}")

            # AI beskrivning
            info = {
                "typ": "plockar upp föremål",
                "rum": room.room_type,
                "item": found_item.name,
                "status": f"Spelaren plockar upp {found_item.name}. {found_item.description}"
            }
            ai_text = dm.get_description(info)
            print(f"\n{ai_text}")
            print(f"Du tog: {found_item.name}")
            print("----------------------------------------------------")
        else:
            print("Det föremålet finns inte här")
            print("----------------------------------------------------")

    # använda item    
    elif command.startswith("använd "):
        item_name = command[7:]
        found_item = None

        for item in player.inventory:
            if item.name.lower() == item_name:
                found_item = item
                break
        if found_item:
            found_item.use(player)
            # AI beskrivning
            info = {
                "typ": "använder föremål",
                "rum": room.room_type,
                "item": found_item.name,
                "status": f"Spelaren använder {found_item.name}. Beskriv resultatet dramatiskt."
            }
            ai_text = dm.get_description(info)
            print(f"\n{ai_text}")
            print("----------------------------------------------------")
        else:
            print("Du har inte det föremålet")

    # Attackera fiende
    elif command == "attackera":
        if room.enemy and room.enemy.is_alive():
            attack(player, room.enemy)

            if not room.enemy.is_alive():
                print(f"{player.name} besegrade {room.enemy.name}!")
            else:
                attack(room.enemy, player)
            if not player.is_alive():
                print("Du har dött...")
                return False
        else:
            print("Det finns inga levande fiender här.")

    #rörelse
    elif command in room.exits and not room.exits[command]["hidden"]:
        exit_data = room.exits[command]

        if exit_data["locked"]:
            needed_key = exit_data["key"]
            has_key = any(item.name == needed_key for item in player.inventory)

            if has_key:
                print(f"Du låser upp dörren med {needed_key}.")
                exit_data["locked"] = False
                player.current_room = exit_data["room"]
                show_room(player)
            else:
                print("Dörren är låst")
        else:
            player.current_room = exit_data["room"]
            show_room(player)

    # smyga
    elif command == "smyg":
        if room.enemy and room.enemy.is_alive():
            if sneak(player, room.enemy):
                print("Du undviker strid")
            else:
                print(f"{room.enemy.name} upptäcker dig!")
                attack(room.enemy, player)
                if not player.is_alive():
                    print("du har dött...")
                    return False
        else:
            print("Det finns ingen fiende att smyga förbi")

    # Söka i rummet
    elif command == "sök":
        print("Du granskar omgivningen noggrant...")
        found_items = []
        found_exits = []

        # leta efter dolda föremål
        for item in room.items:
            if item.hidden:
                if silent_check(player, player.intelligence, item.dc):
                    item.hidden = False
                    found_items.append(item.name)

        # leta efter dolda dörrar
        for direction, exit_data in room.exits.items():
            if exit_data["hidden"]:
                if silent_check(player, player.intelligence, exit_data["dc"]):
                    exit_data["hidden"] = False
                    found_exits.append(direction)

        # AI beskrvining förberedelser
        result = "Spelaren letar noga"
        if found_items or found_exits:
            result += f" Framgång! Spelaren hittade följande: {', '.join(found_items + found_exits)}."
            result += " Beskriv hur de hittar dessa specifika detaljer baserat på bakgrundsinformationen."
        else:
            result += " Misslyckande. Spelaren hittar absolut ingenting nytt, trots ansträngningen."

        info = {
            "typ": "söker genom rummet",
            "rum": room.room_type,
            "status": result
        }

        # AI beskrivning
        ai_berättelse = dm.get_description(info)

        print(f"{ai_berättelse}")
        print("----------------------------------------------------")

        # visa även redan synliga föremål
        visible_items = [item.name for item in room.items if not item.hidden]

        if found_items:
            print("Du hittar:", ", ".join(found_items))

        if found_exits:
            print("Du upptäcker en dold passage:", ", ".join(found_exits))

        if not found_items and not found_exits:
            if visible_items:
                print("Du hittar inget nytt.")
            else:
                print("Du hittar inget.")
  
    else:
        print("Ogiltigt kommando")
    return True

def evaluate_bot(narrator):
    """
    System för att utvärdera AI.modellens svar och kontext
    """
    test_cases = [
    {
        "query": "Vad finns i tunnorna i källaren",
        "expected_keyword": "saltat fläsk",
        "context": "Källare"
    },
    {
        "query": "Hur ser trollen ut i vaktbarackerna?",
        "expected_keyword": "olivgrön",
        "context": "Vaktbaracker"
    }
    ]

    print("\n"+ "="*50)
    print("--- Systemevaluering: RAG-kontroll ---")
    for test in test_cases:
        # Simulerar ett anrop till AI-berättaren
        info = {"rum": test["context"], "typ": test["query"], "status": "Testkörning"}
        response = narrator.get_description(info)
        
        # Kontrollerar om nyckelordet finns i filen bakgrundsinformation
        success = test["expected_keyword"].lower() in response.lower()
        status = "Godkänd" if success else "Misslyckad"

        print(f"\nTestfråga: {test["query"]}")
        print(f"Status: {status}")
        print(f"AI-berättarens svar: {response[:120]}...")
    print("="*50 + "\n")

def player_loop(player):
    """Spelets huvudloop"""
    # Rensa skärmen
    os.system("cls" if os.name == "nt" else "clear")

    # Evaluering av AI innan spelet startar
    evaluate_bot(dm)
    input("Tryck ENTER för att fortsätta efter evaluering...")
    os.system("cls" if os.name == "nt" else "clear")

    # Visa startskärm
    print(start_screen)

    print("\n --- Tryck på ENTER för att påbörja din resa ---")
    input("")

    # Simulera laddnign av spel
    print("\n[system: initierar AI-berättare och laddare bakgrundshistoria...]")
    print("Vänta", end="", flush=True)

    for _ in range(3):
        time.sleep(1) # väntar en selkund
        print(".", end="", flush=True)

    print("Klart!")

    # rensa skärmen och starta spelet
    os.system("cls" if os.name == "nt" else "clear")

    print(f"Välkommen {player.name}!")
    print("Skriv 'hjälp' för att se kommandon")
    show_room(player)

    running = True
    while running and player.is_alive():
        command = input("\n> ")
        running = player_command(player, command)
    
            
# =========================================
# 7. Bygg spelvärlden
# =========================================
 
kallare = Room("Källare")
korridor = Room("Korridor")
baracker = Room("Baracker")
krypta = Room("Ambros Kypta")
slavkammare = Room("Slavkammare")
vapenkammare = Room("Vapenkammare")
bergsspricka = Room("Bergsspricka")
vaktbaracker = Room("Vaktbaracker")
magiker = Room("Magikerns lya")
ealdrorsrum = Room("Ealdrors rum")

# Utgångar källare
kallare.connect("norr", korridor, locked=False, hidden=False, dc=0, key=None) 
kallare.connect("väster", baracker, locked=True, hidden=True, dc=4, key="rostig nyckel")
kallare.connect("söder", bergsspricka, locked=False, hidden=True, dc=18, key=None)

# utgångar Barack 
baracker.connect("öster", kallare, locked=False, hidden= False, dc=0, key=None) 

# Utgångar korridor 
korridor.connect("söder", kallare, locked=False, hidden=False, dc=0, key=None)
korridor.connect("väster", krypta , locked=False, hidden=False, dc=0, key=None)

# Utgångar Ambros krypta 
krypta.connect("söder", korridor, locked=False, hidden=False, dc=0, key=None)
krypta.connect("öster", slavkammare, locked=False, hidden=False, dc=0, key=None)
krypta.connect("söder", vapenkammare, locked=False, hidden=True, dc=16, key=None)

# Utgångar slavkammare 
slavkammare.connect("väster", krypta, locked=False, hidden=False, dc=0, key=None)

# Utgångar vapenkammare 
vapenkammare.connect("söder", krypta, locked=False, hidden=False, dc=0, key=None)
vapenkammare.connect("väster", bergsspricka, locked=False, hidden=True, dc=12, key=None)

# Utgångar bergspricka 
bergsspricka.connect("öster", krypta, locked=False, hidden=False, dc=0, key=None)
bergsspricka.connect("söder", kallare, locked=False, hidden=False, dc=0, key=None)
bergsspricka.connect("väster", vaktbaracker, locked=False, hidden=False, dc=0, key=None)

# Utgångar vaktbaracker 
vaktbaracker.connect("öster", bergsspricka,locked=False, hidden=False, dc=0, key=None)
vaktbaracker.connect("norr", magiker, locked=False, hidden=False, dc=0, key=None)

# Utgångar magikerns lya
magiker.connect("söder", vaktbaracker, locked=False, hidden=False, dc=0, key=None)
magiker.connect("norr", ealdrorsrum, locked=False, hidden=False, dc=0, key=None)

# Utgångar Ealdrors lya
ealdrorsrum.connect("söder", magiker, locked=False, hidden=False, dc=0, key=None)


# =========================================
# 8. Skapa spelaren
# =========================================
player = Krigare("Bree")
player.current_room = kallare

# =========================================
# 9. Starta spelet
# =========================================
player_loop(player)

"""
Jag har skapat ett logik och textbaserat simpelt RPG-spel med inspiration från Dungeons and dragons.
Jag började med att skapa min huvudfil (spellogik.py) i vilken jag skapade min så kallade spelmotor, det är här jag bestämmer
och reglerar hur spelet ska bete sig. Alltå all udnerliggande logik blir då hårdkodad, exempelvis hur mycket liv en karaktär har,
hur mycket skada en karaktär tar osv. På den här logiken har jag sedan lagt på en chatbot med RAG som blir berättaren i spelet.
Det boten gör är att beskriva händelser och platser i spelet. Exempelvis istället för att skriva "Du står i en kall och mörk källare" 
Skriver boten något mer målande som tex "Du står i en källare, mörkret omsluter dig samtidigt som en stank av mögel fyller dina sinnen".
För att boten itne ska hitta på allt själv har jag gett den en fil där den hittar all information den ska berätta. 
I filen spellogik.py finns den initiala koden där man kan spela spelet som det är men utan någon berättare, i filen spellogisk_0.2.py
finns spellogiken blandad med AI-berättaren. 

För att få AI-berättaren att hämta rätt information skapade jag en markdownfil som innehåller all bakgrundhistora för mitt spel. 
här samlar jag information om hur dem olika rummen ser ut, hur karaktärer beter sig, hur föremål ser ut och känns. 
I från denna fil skapade jag mina embeddings vilket innebär att jag omvandlöar texten till vektorer som får rtepresentera ordens betydlese
i siffror. På det här sättet mljliggöra jag för semantisk sökning i min text.
Det som gör semantisk sökning så bra är att den möjliggör för att söka ord efter förståelse och inte bara letar efter exakta ordmatcningar.
Tex kan jag söka efter "mörker" och då kan systemet hitta beskrivnignar som nämner "skuggor" eller "lågt ljus" eftersom dessa
ord ligger nära avrandra i betydlese i min vectorstore. Det här gör att även om spelets logik eller handlignar som spelaren gör inte
exakt macthar något i bakgrundsfilen så kan den ändå hitta relevant information att hämta. 

Jag testade flera olika sätt att dela upp mina chunks. 

I filen berattare.py har jag själva AI-boten, jag har använt mig av Gemini och jag valde att köra via molnet. Det finns en risk att
det blir för många anrop och boten lägger ner då jag kör på en gratisversion samt att det slutar fungera om internet ligger nere. 
Jag har itne hårdvaran för att kunna köra den lokalt för tillfället. 

Jag skapade funktionen evaluate_bot för att utvärdera min modell. Den här testar AI-berättarens förmåga att hämta 
korrekt information från min vectorstore. Jag använde mig av nyckelordsutvärdering. Det innebär att jag ställer en fråga
till AI-berättaren och den ger mig ett svar som ska innehålla det här nyckelordet. På det här sättet kan jag 
säkertsälla att min AI hämtar korrekt information i den givna kontexten samt minimerar risken för så kallad hallucination. 

Under utvecklingsfasen upptäckte jag initialt att mitt utvärderingssystem ofta gav utslaget underkänt vid testfrågorna trots att AIn
gav korrekta meningar. DEt här berodde på att test-skriptets förväntade nyckelord inte matchade med min bakgrundsfil. 
Det här belyser ett problem med RAG-modeller, att alltid se till att ha uppdaterade och korrekta källfiler samt testskript för att
kunna lita på utvärderingen. 

Det hände även att utvärderignen gav godkänt trots att nyckelordet saknades i förhandsvisnningen av svaret.
Det beror på att förhandsvisningen var för kort för att visa nyckelordet. Min modell prioriterade helt enkelt att skriva större 
och mer målande beskrivningar än att bara fokusera på själva nyckelordet. Med detta som bakgrund hade det kanske varit bättre
att använda en annan typ av utvärderingsmetod än just nyckelordsutvärdering. Man kan tex anvädna sig av modellbaserad utvärderingar
något som troligen hade varit ett bättre val för en faktiskt produktionmiljö.






"""