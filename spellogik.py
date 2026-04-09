# =========================================
# Importer
# =========================================
import random

# =========================================
# 1. Spelardata / fiendedata
# =========================================

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
    "Gast": {
        "hp": 11,
        "armor": 14,
        "strength": 12,
        "agility": 12,
        "intelligence": 10,
        "charisma": 8,
        "weapon_damage": (1, 6)
    },
    "Björntroll": {
        "hp": 27,
        "armor": 16,
        "strength": 16,
        "agility": 10,
        "intelligence": 8,
        "charisma": 7,
        "weapon_damage": (2, 6)
    }
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
        print(f"{self.name} tar {amount} skada. HP kvar: {self.hp}")
        
    def is_alive(self):
        return self.hp > 0
    
    def get_modifier(self, stat):
        return(stat - 10) // 2



class Player(Character):
    def __init__(self, name, hp, armor, strength, agility, intelligence, charisma, weapon_damage):
        super().__init__(name, hp, armor, strength, agility, intelligence, charisma, weapon_damage)
        self.inventory = []
        self.current_room = None
        self.equiped_weapon = None


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
                print(f"Du låser upp dörren mot {direction} med {self.name}.")
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
"rumsmall"
        "namn": {
        "description":,
        "items":,
        "Enemy":,
    },
"""
room_types = {
    "Källare": {
        "description": "En kall och fuktig källare",
        "items": [Key("rostig nyckel", "En gammal nyckel täckt av rost.", hidden=True, dc=2)],
        "enemy" : None
    }, #Connect: Norr Korridor(öppen), Väster barack(låst nyckel i rum, lätt check) söder bergsspricka(hemlig dörr hög sök)

    "Barracker": {
        "description":"Barracker med sängar, mat och logi för troll",
        "items": [Weapon("Svärd", "Ett gammalt rostigt svärd", damage_bonus=1, attack_bonus=2, hidden=False)],
        "Enemy": "Troll"
    },# Connect:  öster källare

    "Korridor":{
        "description": "En mörk korridor med fladdrande facklor",
        "items": [],
        "enemy": None
    }, #Connect söder källare(öppen), väster kryptan(öppen)


    "Ambros Kypta": {
    "description":"En dammig krypta med tre stående kistor.",
    "items": None,# eventuellt nyckel till slavkammare
    "Enemy": "Gast",
    }, # connect söder korridor (olåst) öster slavkammare (olåst) Norr vapenkammare (gömd dörr, svår) 

    "slavkammare": {
    "description": "Ett lånsmalt rum fyllt med celler längs ena väggen, en mager människa finns i en av cellerna",
    "items":None, # eventuellt health potion eller annat hjälpverktyg
    "Enemy":None,
    #"NPC": "slav(Namn:Dudu svår check att få ur information om vart man kan gå för att besegra bossen.)",
    }, #connect väster ambros krypta

    "Vapenkammare": {
    "description": "Vapenkammare fylld med rader av svärd av olika slag",
    "items": [Weapon("Svärd", "Ett gammalt rostigt svärd", damage_bonus=1, attack_bonus=2, hidden=False)],
    "Enemy": None,
    }, # connect söder, ambros kypta connect väster Bergsspricka (gömd medelcheck)

    "Bergsspricka": {
    "description":"En spricka som uppstått i bergrgunden där slottet står. en stank av ruttet kött fyller luften",
    "items": None,
    "Enemy": "Nothic",
    }, #connect öster ambros krypta söder, källare, väster vaktbaracker

    "Vaktbarracker": {
    "description":"En barack med fyra träsängar och smutsig disk utrsött överallt",
    "items": None,
    "Enemy": "Troll, Goblin",
    }, # connect öster, bergspricka, norr magikerns lya

    "Magikerns lya": {
    "description": "Det här rumemt ser ut att vara en lya för en magisker, det är fyllt av gamla böcker och magiska drycker",
    "items": [Potion("healing potion", 5, "En liten flaska med röd vätska."),
                Book("bok", "I den här boken får du reda på hur du kan besegra goblins")], # svåre check på bok som hjälper en att klara bossen
    "Enemy": None,
    },  # connect, söder Vaktbaracker öster, norr ealdrors rum

    "Ealdrors rum": { #
    "description": "Väggarna i detta rum är draperade i röd siden, längst in i rummet står en säng"
    " och i mitten finns ett litet upplyst skrivbord. Hukad över skrivbordet sittter en mörk figur",
    "items":None, # eventuellt en trasure som du vinenr spelet med
    "Enemy":"Ealdror",
    }, # connect söder magikerns lya

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

def narrate(event_type, data):
    """
    Funktion för användandet av AI-chatbot för berättelsen.
    """
    print(f"[AI BESKRIVNING HÄR] {event_type} - {data}")


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
    if isinstance(attacker, player) and attacker.equipped_weapon:
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
    weapon_bonus= 0
    if isinstance(attacker, player) and attacker.equipped_weapon:
        weapon_bonus = attacker.equipped_weapon.attack_bonus
    total = base + mod + weapon_bonus

    print(f"{attacker.name} slår: {base} modifier {mod} vapenbonus {weapon_bonus} = {total}")
    print(f"{defender.name} har sköld {defender.armor}")
    if base == 1:
        print(f"{attacker.name} fumlar och missar!")
    elif base == 20:
        damage = roll_damage(attacker) * 2
        print(f"Kritisk träff! {attacker.name} gör {damage} skada!")
        defender.take_damage(damage)
    elif total >= defender.armor:
        damage = roll_damage(attacker)
        print(f"Träff! {attacker.name} gör {damage} skada.")
        defender.take_damage(damage)
    else:
        print(f"{attacker.name} missar {defender.name}.")

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
    print("\n------------------------")
    print(f"Du är i: {room.room_type}")
    print(room.description)

    visible_items = [item.name for item in room.items if not item.hidden]
    if visible_items:
        print("Du ser:", ",".join(visible_items))

    if room.enemy and room.enemy.is_alive():
        print(f"En fiende finns här: {room.enemy.name}")

    visible_exits = []
    for direction, exit_data in room.exits.items():
        if not exit_data["hidden"]:
            if exit_data["locked"]:
                visible_exits.append(f"{direction} (låst)")
            else:
                visible_exits.append(direction)
    if visible_exits:
        print("Utgångar:", ", ".join(visible_exits))

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
        item_name = command[3:]
        found_item = None
    
        for item in room.items:
            if item.name.lower() == item_name:
                found_item = item
                break
        
        if found_item:
            player.inventory.append(found_item)
            room.items.remove(found_item)
            print(f"Du tog {found_item.name}")
        else:
            print("Det itemet finns inte här")
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

    elif command == "sök":
        print(f"{player.name} söker genom rummet...")

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

def player_loop(player):
    """Spelets huvudloop"""
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
bibliotek = Room("Bibliotek")
baracker = Room("Baracker")
krypta = Room("Ambros Kypta")
slavkammare = Room("slavkammare")
vapenkammare = Room("vapenkammare")
bergsspricka = Room("Bergsspricka")
vaktbaracker = Room("vaktbaracker")
magiker = Room("magikerns lya")
ealdrorslya = Room("ealdrors lya")

# Utgångar källare
kallare.connect("norr", korridor, locked=False, hidden=False, dc=0, key=None) 
kallare.connect("väster", baracker, locked=True, hidden=True, dc=4, key="rostig nyckel")
kallare.connect("söder", bergsspricka, locked=False, hidden=True, dc=14, key=None)

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
bergsspricka.connect("öster", krypta, locked=False, hidden=False, dc=0 key=None)
bergsspricka.connect("söder", kallare, locked=False, hidden=False, dc=0 key=None)
bergsspricka.connect("väster", vaktbaracker, locked=False, hidden=False, dc=0 key=None)

# Utgångar vaktbaracker 
vaktbaracker.connect("öster", bergsspricka,locked=False, hidden=False, dc=0, key=None)
vaktbaracker.connect("norr", magiker, locked=False, hidden=False, dc=0, key=None)

# Utgångar magikerns lya
magiker.connect("söder", vaktbaracker, locked=False, hidden=False, dc=0, key=None)
magiker.connect("norr", ealdrorslya, locked=False, hidden=False, dc=0, key=None)

# Utgångar Ealdrors lya
ealdrorslya.connect("söder", magiker, locked=False, hidden=False, dc=0, key=None)


korridor.connect("söder", kallare)
korridor.connect("öster", bibliotek)
bibliotek.connect("väster", korridor)
"""
narrate("enter_room", {
    "room": room.room_type,
    "description": room.description,
    "enemy": room.enemy.name if room.enemy and room.enemy.is_alive() else None,
    "items": [item.name for item in room.items if not item.hidden]
})
"""

# =========================================
# 8. Skapa spelaren
# =========================================
player = Krigare("Bree")
player.current_room = cell

# =========================================
# 9. Starta spelet
# =========================================
player_loop(player)