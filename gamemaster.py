# =========================================
# Importer
# =========================================
import random

# =========================================
# 1. Spelardata / fiendedata
# =========================================

enemy_types = {
    "Goblin": {"hp": 7, "attack":3, "armor": 8},
    "Hobgoblin": {"hp": 11, "attack":5, "armor": 12},
    "Bugbear": {"hp": 27, "attack": 7, "armor": 16}
}

# =========================================
# 2. Klasser för spelare och fiender
# =========================================

class Player:
    def __init__(self, name):
        self.name = name
        self.inventory = []
        self.hp = 0
        self.armor = 0

        self.strength = 10 # påverkar attacker
        self.agility = 10 # påverkar förmåga att smyga eller fly
        self.intelligence = 10 # påverkar förmågan att upptäcka föremål och ledtrådar
        self.charisma = 10 # påverkar förmågan att övertala eller få ut infroamtion i konversationer

    def take_damage(self, amount):
        self.hp -= amount
        print(f"{self.name} tar {amount} skada. HP kvar: {self.hp}")
    
    def is_alive(self):
        return self.hp > 0
    
    def get_modifier(self, stat):
        return(stat - 10) // 2

class Krigare(Player):
    def __init__(self, name):
        super().__init__(name)
        self.hp = 12
        self.armor = 15
        self.strength = 16
        self.agility = 9
        self.intelligence = 11
        self.charisma = 14

class Halvling(Player):
    def __init__(self, name):
        super().__init__(name)
        self.hp = 10
        self.armor = 14
        self.strength = 8
        self.agility = 16
        self.intelligence = 13
        self.charisma = 16

class Dvärg(Player):
    def __init__(self, name):
        super().__init__(name)
        self.hp = 11
        self.armor = 18
        self.strength = 14
        self.agility = 8
        self.intelligence = 10
        self.charisma = 12

class Alv(Player):
    def __init__(self, name):
        super().__init__(name)
        self.hp = 8
        self.armor = 12
        self.strength = 10
        self.agility = 15
        self.intelligence = 16
        self.charisma = 8



# Fiende
class Enemy:
    def __init__(self, name):
        self.name = name
        stats = enemy_types[name]
        self.hp = stats["hp"]
        self.attack = stats["attack"]
        self.armor = stats["armor"]

    def take_damage(self, amount):
        self.hp -= amount
        print(f"{self.name} tar {amount} skada. HP kvar: {self.hp}")
    
    def is_alive(self):
        return self.hp > 0

# ================= Fiender ================
# Jag valde att separera speldata (t.ex. fiendetyper och rumstyper)
# från själva klasserna genom att använda dictionaries.
# Detta gör systemet mer flexibelt och lättare att utöka utan att
# ändra den underliggande logiken





# =========================================
# 3. Item-klasser
# =========================================
class Item:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
    
    def use(self, player):
        print(f"Du kan itne använda{self.name} här.")

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

# =========================================
# 4. Spelvärldsdata
# =========================================
room_types = {
    "Fängelsecell": {
        "description": "En kall och fuktig cell med en dörr",
        "items": [Key("rostig nyckel", "En gammal nyckel täckt av rost.")],
        "enemy" : None
    },
    "Korridor":{
        "description": "En mörk korridor med fladdrande facklor",
        "items": [],
        "enemy": "Goblin"
    },
    "Bibliotek": {
        "description": "Ett dammigt bibliotek fullt av gamla böcker och kartor",
        "items": [Potion("healing potion", 5, "En liten flaska med röd vätska."), 
                  Book("bok", "I den här boken får du reda på hur du kan besegra goblins")], # lägg till karta och bok
        "enemy": "Hobgoblin"
    }
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

    def connect(self, direction, room, locked=False, key=None):
        self.exits[direction] = {
            "room": room,
            "locked": locked,
            "key": key
        }    

# =========================================
# 6. Hjälpfunktioner / spellogik
# =========================================

def roll_d20():
    return random.randint(1, 20)


def attack(attacker, defender):
    roll = roll_d20()
    print(f"{attacker.name} slår en d20: {roll}")

    if roll >= defender.armor:
        print(f"Träff! {roll} >= {defender.armor}")
        defender.take_damage(attacker.attack)
    else:
        print(f"Miss! {roll} < {defender.armor}")

def show_room(player):
    """
    Visar information om rummet spelaren befinner sig i.
    """
    room = player.current_room
    print("\n------------------------")
    print(f"Du är i: {room.room_type}")
    print(room.description)

    if room.searched and room.items:
        print("Du ser:", ", ".join(item.name for item in room.items))

    if room.enemy and room.enemy.is_alive():
        print(f"En fiende finns här: {room.enemy.name} (HP: {room.enemy.hp})")

    if room.exits:
        print("Utgångar:")
        for direction, exit_data in room.exits.items():
            if exit_data["locked"]:
                print(f"{direction} (låst)")
            else:
                print(f"{direction}")

def player_command(player, command):
    room = player.current_room
    command = command.lower().strip()

    # Avlsuta spel
    if command == "avsluta":
        return False
    
    # Hjälp
    elif command == "hjälp":
        print("Kommandon: norr, söder, öster, väster, kolla, sök, inventarie, ta[item], attackera, avsluta")

    #Titta på rummet igen
    elif command == "kolla":
        show_room(player)

    # visa inventarie
    elif command == "inventarie":
        if player.inventory:
            print("Du gar:", ",".join(item.name for item in player.inventory))
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
            print("Du har itne det föremålet")

    # Attackera fiende
    elif command == "attackera":
        if room.enemy and room.enemy.is_alive():
            attack(player, room.enemy)

            if not room.enemy.is_alive():
                print(f"Du besegrade {room.enemy.name}!")
            else:
                attack(room.enemy, player)
            if not player.is_alive():
                print("Du har dött...")
                return False
        else:
            print("Det finns inga levande fiender här.")

    #rörelse
    elif command in room.exits:
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

    # undersök
    elif command == "sök":
        if room.searched:
            if room.items:
                print("Du har redan letat här. Du ser:".join(item.name for item in room.items))
            else:
                print("Du har redan letat här, det finns inget kvar")
        
        else:
            room.searched = True
            if room.items:
                print("Du letar genom rummet och hittar:", ",".join(item.name for item in room.items))
            else:
                print("Du letar igenom rummet men hittar inget")
    
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
 
cell = Room("Fängelsecell")
korridor = Room("Korridor")
bibliotek = Room("Bibliotek")

cell.connect("norr", korridor, locked=True, key=("rostig nyckel"))
korridor.connect("söder", cell)
korridor.connect("öster", bibliotek)
bibliotek.connect("väster", korridor)

# =========================================
# 8. Skapa spelaren
# =========================================
player = Krigare("Bree")
player.current_room = cell

# =========================================
# 9. Starta spelet
# =========================================
player_loop(player)