# =========================================
# Importer
# =========================================
import random

# =========================================
# 1. Spelardata / fiendedata
# =========================================

enemy_types = {
    "Goblin": {
        "hp": 7,
        "armor": 12,
        "strength": 8,
        "agility": 14,
        "intelligence": 8,
        "charisma": 6,
        "weapon_damage": (1, 4)
    },
    "Hobgoblin": {
        "hp": 11,
        "armor": 14,
        "strength": 12,
        "agility": 12,
        "intelligence": 10,
        "charisma": 8,
        "weapon_damage": (1, 6)
    },
    "Bugbear": {
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

def roll_damage(attacker):
    low, high = attacker.weapon_damage
    damage = random.randint(low, high) + attacker.get_modifier(attacker.strength)
    return max(1, damage)


def attack(attacker, defender):
    roll = roll_d20() + attacker.get_modifier(attacker.strength)
    print(f"{attacker.name} slår: {roll}")

    if roll >= defender.armor:
        damage = roll_damage(attacker)
        print(f"Träff! {attacker.name} gör {damage} skada.")
        defender.take_damage(damage)
    else:
        print(f"{attacker.name} missar.")

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
            print("Du gar:", ", ".join(item.name for item in player.inventory))
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
                print("Du har redan letat här. Du ser:", ", ".join(item.name for item in room.items))
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

cell.connect("norr", korridor, locked=True, key="rostig nyckel")
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