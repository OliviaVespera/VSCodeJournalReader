from abc import abstractmethod

class Flag:
    def __init__(self, name: str, desc: str):
        self.name = name
        self.desc = desc
    @abstractmethod
    def check(self, flag, buffer):
        pass
    def __repr__(self):
        return self.desc

def landed(flag, buffer):  
    if flag["event"] == "Touchdown":
        print("Touchdown at latitude: {}, longitude: {} on planet {}.".format(
            buffer["Latitude"],
            buffer["Longitude"], "unknown"))
        return True
    return False

def docked(flag, buffer):
    if flag.get("StationName", 0) == buffer.get("StationName", 1):
        return flag["event"] in ("Docked", "Undocked")
    return False

def market_trade(flag, buffer):
    test1 = flag.get("Type", 0) == buffer.get("Type", 1)
    test2 = flag.get("Count", 0) <= buffer.get("Count", 1)
    if test1 and test2:
        return flag["event"] in ("MarketSell", "MarketBuy")
    return False


def jump(flag, buffer):
    if flag.get("StarSystem", 0) == buffer.get("StarSystem", 1):
        return flag["event"] in ("FSDJump", "StartJump")
    return False


def supercruise_exit(flag, buffer):
    if flag["event"] == "SupercruiseExit":
        test2 = flag["StarSystem"] == buffer["StarSystem"]
        test3 = flag["StationName"] == buffer["StationName"]
        return test2 and test3
    return False

def supercruise(flag, buffer):
    return "JumpType" in buffer and buffer["JumpType"] == "Supercruise"

#requires dependency system
def mission_accepted_faction(flag, buffer):
    if flag["MissionAccepted"] == buffer["MissionAccepted"]:
        return flag["Faction"] == buffer["Faction"]
    return False

#requires dependency system
def mission_abandoned_faction(flag, buffer):
    if flag["MissionAbandoned"] == buffer["MissionAbandoned"]:
        return flag["Faction"] == buffer["Faction"]
    return False

def scanned(flag, buffer):
    pass
    #Event:Scanned
    #ScanType:Cargo

def Ship_targeted(self, buffer):
    pass
    #Event:ShipTargeted
    #TargetLocked:true/false
    #"PilotName":"$ShipName_Police_Independent;"
    #"PilotRank": "Dangerous"
    #"Ship": "eagle"
    #"Faction": "LFT 446 Power Company"
    #"LegalStatus":"Clean"

#"event":"RefuelAll", "Cost":148, "Amount":2.950530
def game_mode(flag, buffer):
    if flag["event"] == "LoadGame":
        return flag["GameMode"] == buffer["GameMode"]

def approach_body(flag, buffer):
    if flag["event"] == "ApproachBody":
        if flag["StarSystem"] == buffer["StarSystem"]:
            return flag["body"] == buffer["body"]
    return False

def leave_body(flag, buffer):
    if flag["event"] == "LeaveBody":
        if flag["StarSystem"] == buffer["StarSystem"]:
            return flag["body"] == buffer["body"]
    return False

#i don't want to program:
# docking cancelled, denied, granted, requested or timeout
#i see no value for mission manager

def is_wanted_in_system(flag, buffer):
    if flag["event"] == "FSDjump":
        if flag["StarSystem"] == buffer["StarSystem"]:
            return flag["body"] == buffer["body"]
    return False

def liftoff(flag, buffer):
    if flag["event"] == "Liftoff":
        if flag["PlayerControlled"] == buffer["PlayerControlled"]:
            coords = (flag["Latitude"], flag["Longitude"])
            buffer_coords = (buffer["Latitude"], buffer["longitude"])
            test1 = coords[0]-1 <= buffer_coords[0] <= coords[0]+1
            test2 = coords[1]-1 <= buffer_coords[1] <= coords[1]+1
            return test1 and test2
    return False
def touchdown(flag, buffer):
    if flag["event"] == "touchdown":
        if flag["PlayerControlled"] == buffer["PlayerControlled"]:
            coords = (flag["Latitude"], flag["Longitude"])
            buffer_coords = (buffer["Latitude"], buffer["longitude"])
            test1 = coords[0]-1 <= buffer_coords[0] <= coords[0]+1
            test2 = coords[1]-1 <= buffer_coords[1] <= coords[1]+1
            return test1 and test2

def shield_state(flag, buffer):
    if flag["event"] == "ShieldState":
        return buffer["ShieldsUp"] == flag["ShieldsUp"]

#needs dependency, system  
def sell_exploration_data(flag, buffer):
    return flag["event"] == "SellExplorationData"

#needs dependency, mission cargo
def EjectCargo(flag, buffer):
    if flag["event"] == "EjectCargo":
        return True
    return False

