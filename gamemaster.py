# ================= Spelarklasser ================
class Player:
    def __init__(self, name):
        self.name = name
        self.inventory = []
        self.hp = 0
        self.attack = 0

    def take_damage(self, amount):
        self.hp -= amount
        print(f"{self.name} tar{amount} skada. HP kvar: {self.hp}")
    
    def is_alive(self):
        return self.hp > 0

class Krigare(Player):
    def __init__(self, name):
        super().__init__(name)
        self.hp = 12
        self.attack = 16

class Halvling(Player):
    def __init__(self, name):
        super().__init__(name)
        self.hp = 9
        self.attack = 8

# ================= Fiender ================
# Jag valde att separera speldata (t.ex. fiendetyper och rumstyper)
# från själva klasserna genom att använda dictionaries.
# Detta gör systemet mer flexibelt och lättare att utöka utan att
# ändra den underliggande logiken


enemy_types = {
    "Goblin": {"hp": 7, "attack":3},
    "Hobgoblin": {"hp": 11, "attack":5},
    "Bugbear": {"hp": 27, "attack": 15}
}

class enemy:
    def __init__(self, name):
        self.name = name
        stats = enemy_types[name]
        self.hp = stats["hp"]
        self.attack = stats["attack"]

    def take_damage(self, amount):
        self.hp -= amount
        print(f"{self.name} tar{amount} skada. HP kvar: {self.hp}")
    
    def is_alive(self):
        return self.hp > 0



#================= Spelvärld ========================
room_types = {
    "Fängelsecell": {
        "description": "En kall och fuktig cell med en låst dörr",
        "items": ["rostig nyckel"],
        "enemy" : None
    },
    "Korridor":{
        "description": "En märk korridor med fladdrande facklor",
        "items": [],
        "enemy": "Goblin"
    },
    "Bibliotek": {
        "description": "Ett dammigt bibliotek fullt av gamla böcker och kartor",
        "items": ["karta", "gammal bok"],
        "enemy": "Hobgoblin"
    }
}

class Room:
    def __init__(self, room_type):
        self.room_type = room_type
        data = room_types[room_type]
        
        self.description = data["description"]
        self.items = data["items"].copy()
        self.enemy = enemy(data["enemy"]) if data["enemy"] else None
        self.exits = {}
        self.searched = False

    def connect(self, direction, room, locked=False, key=None):
        self.exits[direction] = {
            "room": room,
            "locked": locked,
            "key": key
        }    


#===================== Help functions ===================
def show_room(player):
    """
    Ger en beskrivning av rummet spelaren befinner sig i
    """
    room = player.current_room
    print("\n------------------------")
    print(f"Du är i: {room.room_type}")
    print(room.description)

    if room.searched and room.items:
        print("Du ser följande föremål:", ", ".join(room.items))

    if room.enemy and room.enemy.is_alive():
        print(f"En fiende finns här: {room.enemy.name} (HP: {room.enemy.hp})")

    if room.exits:
        print("Utgångar:", ", ".join(room.exits.keys()))

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
    elif command == "inmventarie":
        if player.inventory:
            print("Du gar:", ",".join(player.inventory))
        else:
            print("Din inventarie är tomt.")
    
    # ta item
    elif command.startswith("ta "):
        item_name = command[3:]
        found_item = None
    
        for item in room.items:
            if item.lower() == item_name:
                found_item = item
                break
        
        if found_item:
            player.inventory.append(found_item)
            room.items.remove(found_item)
            print(f"Du tog {found_item}")
        else:
            print("Det itemet finns inte här")

    # Attackera fiende
    elif command == "attackera":
        if room.enemy and room.enemy.is_alive():
            room.enemy.take_damage(player.attack)

            if not room.enemy.is_alive():
                print(f"Du besegrade {room.enemy.name}!")
            else:
                player.take_damage(room.enemy.attack)
                if not player.is_alive():
                    print("Du har dött...")
                    return False
        else:
            print("Det finns inga levande fiender här.")

    #rörelse
    elif command in room.exits:
        player.current_room = room.exits[command]
        show_room(player)

    # undersök
    elif command == "sök":
        if room.searched:
            if room.items:
                print("Du har redan letat här. Du ser:".join(room.items))
            else:
                print("Du har redan letat här, det finns inget kvar")
        
        else:
            room.searched = True
            if room.items:
                print("Du letar genom rummet och hittar:", ",".join(room.items))
            else:
                print("Du letar igenom rummet men hittar inget")
    
    else:
        print("Ogiltigt kommando")
    return True

def player_loop(player):
    print(f"Välkommen {player.name}!")
    print("Skriv 'hjälp' för att se kommandon")
    show_room(player)

    running = True
    while running and player.is_alive():
        command = input("\n> ")
        running = player_command(player, command)
    
            
#===================== Rumskopplingar ===================
 
cell = Room("Fängelsecell")
korridor = Room("Korridor")
bibliotek = Room("Bibliotek")

cell.connect("norr", korridor, locked=True, key="rostig nyckel")
korridor.connect("söder", cell)
korridor.connect("öster", bibliotek)
bibliotek.connect("väster", korridor)

#============ Spelare =======================
player = Krigare("Bree")
player.current_room = cell

#============ starta spel =======================
player_loop(player)