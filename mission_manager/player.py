"""Start writing stuff here
and keep doing so


"""

from pprint import pprint

class Player:
    def __init__(self):
        
        self.ship = Ship()
        self.cmdr = Cmdr()
        self.location = Location()
        self.status = Status()
        self.credits = 0
        self.credit_loan = 0
        self.tridots = 0
        self.missions = {
            0:{"System": None, "Faction": None}}
        self.inventory = {
            "Cargo": [],
            "Materials": [],
            "Credits": {"Balance":0, "Loan": 0},
            "Tridots": {"Balance": 0, "Loan": 0}}
        
        self.status = Status(0)
    def load(self):
        #load gamestate
        pass
    def save(self):
        pass
    
    def update(self, buffer):
            self.flags(buffer)
            self.approach_body(buffer)
            if buffer["event"] == "Location" or buffer["event"] == "Docked" \
            or buffer["event"] == "Undocked" or buffer["event"] == "SupercruiseExit":
                self.location.update(buffer)
                print(self.location)
            if buffer["event"] == "SupercruiseEntry":
                self.location.station = None
            if buffer["event"] == "FSDJump":
                self.location.station = None
                self.location.body = None

    def approach_body(self, buffer):
        if buffer["event"] == "ApproachBody":
            self.location.body = buffer["Body"]
        if buffer["event"] == "LeaveBody":
            self.location.body = None

            self.location.system = buffer["StarSystem"]
            print(self.location.body, self.location.system)

    def flags(self, buffer):
        if buffer["event"] == "Status":
            self.status.flags = buffer.get("Flags", 0)
            if self.status.has_lat_lon():
                self.location.latitude = buffer["Latitude"]
                self.location.longitude = buffer["Longitude"]
                self.location.heading = buffer["Heading"]
                self.location.altitude = buffer["Altitude"]
                self.location.has_coordiantes = True
            elif self.location.has_coordinates:
                self.location.reset_coordinates()

    def set_location(self, buffer):
        if buffer["event"] == "Location":
                self.location = {"StarSystem":buffer["StarSystem"],
                "Body":buffer.get("Body"), "StationName":buffer.get("StationName"),
                "starPos":buffer["StarPos"]}
                print("You are on or near {} in the {} system.".format(
                    self.location["Body"], self.location["StarSystem"]))
    def load_game(self, buffer):
        if buffer["event"] == "LoadGame":
            self.ship.load_game(buffer)
            self.cmdr.load_game(buffer)
            self.credits = buffer["Credits"]
            self.credit_loan = buffer["Loan"]
        elif buffer["event"] == "Rank":
            self.cmdr.set_ranks(buffer)
        elif buffer["event"] == "Progress":
            pass
        elif buffer["event"] == "Reputation":
            pass
        elif buffer["event"] == "Loadout":
            self.ship.set_loadout(buffer)
        elif buffer["event"] == "Location" or buffer["event"] == "FSDJump"\
        or buffer["event"] == "Docked" or buffer["event"] == "Undocked":
            self.location.load_location(buffer)
            #print(self.location)
        elif buffer["event"] == "Materials":
            self.inventory["Materials"] = buffer["Raw"]
        elif buffer["event"] == "Cargo":
            self.inventory["Cargo"] = buffer["Inventory"]
        elif buffer["event"] == "MarketBuy":
            is_added = False
            for commodity in self.inventory["Cargo"]:
                if "Name" in commodity:
                    commodity_name = commodity["Name"]
                elif "Type" in commodity:
                    commodity_name = commodity["Type"]
                if buffer["Type"] == commodity_name:
                    commodity["Count"] += buffer["Count"]
                    is_added = True
            if not is_added:
                self.inventory["Cargo"].append({
                    "Type":buffer["Type"],
                    "Count":buffer["Count"]})
        elif buffer["event"] == "MarketSell":
            for commodity in self.inventory["Cargo"]:
                commodity_name = None
                if "Name" in commodity:
                    commodity_name = commodity["Name"]
                elif "Type" in commodity:
                    commodity_name = commodity["Type"]
                if buffer["Type"] == commodity_name:
                    commodity["Count"] -= buffer["Count"]
                    if commodity["Count"] == 0:
                        self.inventory["Cargo"].remove(commodity)
        

            
    #set cargo to an array of cargo objects that contain, 
    #name, count and stolen
    def write_cargo(self):
        for cargo in self.inventory["Cargo"]:
            stolen = ""
            if cargo["Stolen"] > 0:
                stolen = " {} units are stolen.".format(cargo["stolen"])
            return "You are carrying: {} units of {}.{}".format(
                cargo["Count"], cargo["Name"], stolen)

class Ship:
    def __init__(
        self):
        self.name = None
        self.type = None
        self.id = None
        self.shields = 0
        self.cargo = []
        self.hull = 0
        self.fuel = (0, 0)
        self.modules = {}
        self.outfitting = {}

    def load_game(self, buffer):
        self.name = buffer["ShipName"]
        self.id = buffer["ShipIdent"]
        self.type = buffer["Ship"]
        self.fuel = (buffer["FuelLevel"], buffer["FuelCapacity"])

    def set_loadout(self, buffer):
        self.modules = buffer["Modules"]
class Location:
    def __init__(self): 
        self.system = None
        self.star_pos = None
        self.body = None
        self.previous_system = None
        self.reset_coordinates()
        self.is_docked = False
        self.station = None

    def __repr__(self):
        body_text = ""
        preposition = "near"
        station_preposition= "near"
        coordinates_text = ""
        station_text = ""
        if self.latitude:
            preposition = "on"
            coordinates_text = " at coordinates: {}, {}".format(
                str(self.latitude),
                str(self.longitude))

        if self.body:
            body_text = " {} {}".format(preposition, self.body)

        if self.station:
            if self.is_docked:
                station_preposition = "docked at"
            station_text = " {} {}".format(station_preposition, self.station)
        if self.body == self.station:
            body_text = ""

        return "You are{}{} in the {} system{}.".format(
                    station_text,
                    body_text,
                    self.system,
                    coordinates_text)

    def load_location(self, buffer):
        self.system = buffer.get("StarSystem", self.system)
        self.star_pos = buffer.get("StarPos", self.star_pos)
        self.body = buffer.get("Body", None)
        self.station = buffer.get("StationName", None)
        self.latitude = buffer.get("Latitude", None)
        self.longitude = buffer.get("Longitude", None)
        self.check_docked(buffer)

    def update(self, buffer):
        self.system = buffer.get("StarSystem", self.system)
        self.star_pos = buffer.get("StarPos", self.star_pos)
        self.body = buffer.get("Body", self.body)
        self.station = buffer.get("StationName", self.station)
        self.latitude = buffer.get("Latitude", self.latitude)
        self.longitude = buffer.get("Longitude", self.longitude)
        self.check_docked(buffer)
        if buffer["event"] == "supercruiseEntry" or buffer["event"] == "startJump":
            self.body = None

    def check_docked(self, buffer):
        if buffer["event"] == "Docked":
            self.is_docked = True
        elif buffer["event"] == "Undocked":
            self.is_docked = False
        

    def reset_coordinates(self):
        self.latitude = None
        self.longitude = None
        self.altidue = None
        self.heading = None
        self.has_coordinates=False


class Cmdr:
    def __init__(self):
        self.name = None
        self.combat = None
        self.explore = None
        self.cqc = None
        self.trade = None
        self.federation = None
        self.empire = None
        #self.alliance = alliance

    def __repr__(self):
        vocation = ""
        if self.name is not None:
            if self.explore > self.combat and self.explore > self.trade:
                vocation = "an Explorer"
            elif self.combat > self.explore and self.combat > self.trade:
                vocation = "a Combateer"
            elif self.trade > self.explore and self.trade > self.combat:
                vocation = "a Trader"
            else:
                vocation = "a Spacer"

            return "You are CMDR {} and you are {}.".format(self.name, vocation)
        return "system not initialized"

    def load_game(self,buffer):
        self.name=buffer["Commander"]

    def set_ranks(self, buffer):
        self.combat = int(buffer["Combat"])
        self.explore = int(buffer["Explore"])
        self.trade = int(buffer["Trade"])
        self.cqc = int(buffer["CQC"])
        self.federation = int(buffer["Federation"])
        self.empire = int(buffer["Empire"])
        #self.alliance = buffer["Alliance"]
class Status:
    def __init__(self, flags=0):
        self.flags = flags
    
    def check(self, binarynum):
        if self.flags & binarynum > 0:
            return True
        return False

    #general ship status flags
    def is_docked(self): #docked
        return self.check(1)

    def is_landed(self):
        return self.check(2)
    
    def is_shields_up(self):
        return self.check(8)

    def is_supercruise(self):
        return self.check(16)

    def is_fa_off(self):
        return self.check(32)

    def is_hardpoints_deployed(self):
        return self.check(64)

    def is_in_wing(self):
        return self.check(128)

    def is_lights_on(self):
        return self.check(256)

    def scoop_deployed(self):
        return self.check(512)

    def is_silent_running(self):
        return self.check(1024)

    def is_scooping_fuel(self):
        return self.check(2048)

    #SRV state flags
    def is_srv_handbrake(self):
        return self.check(4096)

    def is_srv_turret(self):
        return self.check(8192)
    
    def is_srv_undership(self):
        return self.check(16384)
    
    def is_srv_drive_assist(self):
        return self.check(32768)
    

    #FSD related flags
    def is_mass_locked(self):
        return self.check(65536)
    
    def is_fsd_charging(self): #StartJump
        return self.check(131072)
        
    def is_fsd_cooldown(self):
        return self.check(262144)

    #warning flags
    def is_low_fuel(self):
        return self.check(524288)

    def is_overheating(self):
        return self.check(1048576)
    
    #miscellaneous general flgs
    def has_lat_lon(self): #approach_body
        return self.check(2097152)
    
    def is_in_danger(self):
        return self.check(4194304)

    def is_Interdicted(self):
        return self.check(8388608)

    #says which carft you're flying
    def in_main_ship(self):
        return self.check(16777216)

    def in_fighter(self):
        return self.check(33554432)

    def in_SRV(self):
        return self.check(67108864)