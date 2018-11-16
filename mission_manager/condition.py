from abc import abstractmethod, ABC

def _pluralizer(single, plural):
    return lambda x: plural if x > 1 else single

def _unit_pluralizer(num):
    return "units" if num > 1 else "unit"

def _ship_pluralizer(num):
    return "ships" if num > 1 else "ship"

def _margin_test(num1, num2, margin):
    return num1-margin <= num2 <= num1+margin

def _body_type_pluralizer(planet_body):
    body = planet_body.replace("body", "bodie")
    body = list(body.partition("giant"))
    body.insert(2,"s")
    body = "".join(body)
    return body
        
#These conditions assumes that player is updated after the check.
#All conditions inherit from Condition

#A list of all classes grouped (23)
#Touchdown, Liftoff, Dock, Undock
#FSDJump, SupercruiseExit, SupercruiseEntry
#MarketBuy and MarketSell
#AcceptFactionMission, CompleteFactionMission, FailFactionMission
#CollectCargo, EjectCargo
#SellExplorationData, Scan, JetConeBoost
#PowerplayDeliver, #PowerplayVoucher(!implemented), #PowerplayVote(!implemented)
#MurderFactionShips #RedeemVoucher
#GameMode, Continued(!implemented)

class Condition(ABC):
    def __init__(self, name, description, data=None, is_toggle=False, is_fail=False):
        self.name = name
        self.description = description
        self.data = [] if data is None else data
        self.is_toggle = is_toggle
        self.is_fail = is_fail
        self.requisites = []
        self.is_complete =  False

    def __repr__(self):
        return str(self.description)

    def has_requisite(self):
        return self.requisites

    def check_requisites(self):
        """for requisite in self.requisites:
            if not requisite.is_completed:
                return False
        return True"""
        return all(self.requisites)
    
    @abstractmethod
    def check(self, buffer, player):
        pass
    
    def format_description(self, data, count):
        pass


class Touchdown(Condition):
    """Takes in a dictionary with keys, Margin, Latitude, Longitude, Body, StarSystem"""
    def __init__(self, data, is_fail=False):
        description = "Land within {} of {}, {}, on {}, {}.".format(
            data["Margin"],
            data["Latitude"],
            data["Longitude"],
            data["Body"],
            data["StarSystem"]
        )
        super().__init__("Touchdown", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            test1 = self.data["Body"] == player.location.body
            test2 = self.data["StarSystem"] == player.location.system
            if test1 and test2:
                if self.data["PlayerControlled"] == buffer["PlayerControlled"]:
                    margin = self.data["Margin"]
                    test1 = _margin_test(
                        self.data["Latitude"],
                        buffer["Latitude"], margin)
                    test2 = _margin_test(
                        self.data["Longitude"],
                        buffer["Longitude"], margin)
                    return test1 and test2
        return False


class LiftOff(Condition):
    """Takes in a dictionary with keys, Body, Latitude, Longitude"""
    def __init__(self, data, is_fail=False):
        description = "Liftoff from {} at {}, {}.".format(
            data["Body"],
            data["Latitude"],
            data["Longitude"],
        )
        super().__init__("Liftoff", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            if self.data["Body"] == player.location.body:
                if self.data["PlayerControlled"] == buffer["PlayerControlled"]:
                    margin = self.data["Margin"]
                    test1 = _margin_test(
                        self.data["Latitude"], buffer["Latitude"], margin)
                    test2 = _margin_test(
                        self.data["Longitude"], buffer["longitude"], margin)
                    return test1 and test2
        return False


class Dock(Condition):
    """Takes in a dictionary with keys, StationName and StarSystem"""
    def __init__(self, data, is_fail=False):
        
        description = "Dock at {}, {}.".format(
            data["StationName"],
            data["StarSystem"])
        super().__init__("Docked", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            if self.data["StarSystem"] == buffer["StarSystem"]:
                print(self.data["StationName"], buffer["StationName"])
                return self.data["StationName"] == buffer["StationName"]
        return False


class Undock(Condition):
    """Takes in a dictionary with keys, StationName and Starsystem"""
    def __init__(self, data, is_fail=False):
        description = "Undock from {}, {}.".format(
            data["StationName"],
            data["StarSystem"])
        super().__init__("Undocked", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            if self.data["StarSystem"] == player.location.system:
                return self.data["StationName"] == buffer["StationName"]
        return False


class FSDJump(Condition):
    """Takes in a dictionary with keys, StarSystem"""
    def __init__(self, data, is_fail=False):
        description = "Jump to {}.".format(data["StarSystem"])
        super().__init__("FSDJump", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            return self.data["StarSystem"] == buffer["StarSystem"]
        return False


class SupercruiseExit(Condition):
    """Takes in a dictionary with keys, Body, StarSystem"""
    def __init__(self, data, is_fail=False):
        description = "Exit supercruise at {} in {}".format(
            data["Body"], data["StarSystem"]
        )
        super().__init__("SupercruiseExit", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            if self.data["StarSystem"] == buffer["StarSystem"]:
                return self.data["Body"] == buffer["Body"]
        return False


class SupercruiseEntry(Condition):
    """Takes in a dictionary with keys, Body, Latitude, Longitude"""
    def __init__(self, data, is_fail=False):
        description = "Enter supercruise"
        super().__init__("SupercruiseEntry", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        return buffer["event"] == self.name

class MarketBuy(Condition):
    def __init__(self, data, is_fail=False):
        plural = _unit_pluralizer(data["Count"])
        self.star_system = data.get("StarSystem", False)
        self.station = data.get("StationName", False)
        location = ""
        if self.star_system and self.station:
            location = " from {} in {}".format(self.station, self.star_system)
        elif self.station:
            location = " from {}".format(self.station)
        elif self.star_system:
            location = " in {}".format(self.station)
        description = "Buy {} {} of {}{}.".format(
            data["Count"],
            plural,
            data["Type"],
            location)
        super().__init__("MarketBuy", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            if self.star_system:
                if self.star_system != player.location.system:
                    return False
            if self.station:
                if self.station != player.location.station:
                    return False
            if self.data.get("Type", 0) == buffer.get("Type", 1):
                return self.data.get("Count", 0) <= buffer.get("Count", 1)


        return False


class MarketSell(Condition):
    def __init__(self, data, is_fail=False):
        plural = _unit_pluralizer(data["Count"])
        self.star_system = data.get("StarSystem", False)
        self.station = data.get("StationName", False)
        location = ""
        if self.star_system and self.station:
            location = " to {} in {}".format(self.station, self.star_system)
        elif self.station:
            location = " to {}".format(self.station)
        elif self.star_system:
            location = " in {}".format(self.station)

        description = "Sell {} {} of {}{}.".format(
            data["Count"],
            plural,
            data["Type"],
            location)
        super().__init__("MarketSell", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            if self.star_system:
                if self.star_system != player.location.system:
                    return False
            if self.station:
                if self.station != player.location.station:
                    return False
            if self.data.get("Type", 0) == buffer.get("Type", 1):
                return self.data.get("Count", 0) <= buffer.get("Count", 1)
        return False


class AcceptFactionMission(Condition):
    def __init__(self, data, is_fail=False):
        description = "Accept mission from {} in {}".format(
            data["Faction"],
            data["StarSystem"])
        super().__init__("MissionAccepted", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            test1 = self.data["StarSystem"] == player.location.system
            test2 = self.data["Faction"] == buffer["Faction"]
            if test1 and test2:
                mission_id = buffer["MissionID"]
                player.missions[mission_id] = {
                    #delete faction is not needed
                    "Faction":buffer["Faction"],
                    "StarSystem":player.location.system
                }
                print ("Mission \"{}\" accepted".format(buffer["Name"]))
                return True
        return False


class CompleteFactionMission(Condition):
    def __init__(self, data, is_fail=False):
        description = "Complete mission from {} in {}".format(
            data["Faction"],
            data["StarSystem"])
        super().__init__("MissionCompleted", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            mission_id = buffer["MissionID"]
            if mission_id in player.missions:
                details = player.missions[mission_id]
            test1 = self.data["StarSystem"] == details["StarSystem"]
            test2 = self.data["Faction"] == details["Faction"]
            return test1 and test2
        return False


#This will not work
class FailFactionMission(Condition):
    def __init__(self, data, is_fail=False):
        description = "Mission from {} for {} not completed".format(
            data["StarSystem"],
            data["Faction"])
        super().__init__("MissionFailed", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            condition_mission = player.mission[buffer["MissionID"]]
            mission_origin_System = condition_mission["StarSystem"]
            test1 = mission_origin_System == self.data["StarSystem"]
            test2 = self.data["Faction"] == buffer["Faction"]
            return test1 and test2
        return False


class CollectCargo(Condition):
    def __init__(self, data, is_fail=False):
        self.count = 0
        description = self.format_description(data, self.count)
        super().__init__("CollectCargo", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            if self.data["Type"] == buffer["Type"]:
                self.count += 1
                self.description = self.format_description(
                    self.data, self.count)
                return self.data["Count"] <= self.count
        return False
    
    def format_description(self, data, count):
        description = "Collect {} {} of cargo. {} remaining.".format(
            data["Count"],
            _unit_pluralizer(data["Count"]),
            str(data["Count"] - count)
        )
        return description


class EjectCargo(Condition):
    """Takes in a dictionary with keys, Count and Type"""
    def __init__(self, data, is_fail=False):
        self.count = 0
        description = self.format_description(data, self.count)
        super().__init__("EjectCargo", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            if self.data["Type"] == buffer["Type"]:
                self.count += buffer["Count"]
                self.description = self.format_description(
                    self.data, self.count)
                return self.data["Count"] <= self.count
        return False
    
    def format_description(self, data, count):
        description = "Eject {} {} of cargo. {} remaining.".format(
            data["Count"],
            _unit_pluralizer(data["Count"]),
            str(data["Count"] - count)
        )
        return description


class SellExplorationData(Condition):
    def __init__(self, data, is_fail=False):
        end_bit = ""
        if "System" in data and data["System"] in data["System"]:
            end_bit = " from {}".format(data["System"])
        description = "Sell {}Cr worth of Exploration Data{}.".format(
            data["TotalEarnings"],
            end_bit
        )
        super().__init__("System", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            is_found = False
            for system in buffer["Systems"]:
                if system == self.data["System"]:
                    is_found = True; break
        return is_found


class Scan(Condition):
    def __init__(self, data, is_fail=False):
        self.count = 0
        description = self.format_description(data, self.count)
        super().__init__("Scan", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            if self.data["Body"] == buffer["Body"]:
                self.count += 1
                self.description = self.format_description(self.data, self.count)
                return self.count
    
    def format_description(self, data, count):
        body_p = _pluralizer(data["Body"], _body_type_pluralizer(data["Body"]))
        body = body_p(data["Count"])
        if "Sector" in data:
            sector_string = "in ".join(data["Sector"])
        description = "Scan {} {} {}. {} remaining.".format(
            data["Count"], body, sector_string, str(data["Count"] - count)
        )
        return description


class JetConeBoost(Condition):
    def __init__(self, data, is_fail=False):
        if "StarSystem" in data:
            system = " at {}".join(data["StarSystem"])
        description = "Supercharge your FSD{}.".format(system)
        super().__init__("class_name", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            if "StarSystem" in self.data:
                return self.data["StarSystem"] == player.location.system
            return True
        return False


class PowerplayDeliver(Condition):
    def __init__(self, data, is_fail=False):
        self.count = 0
        description = self.format_description(data, self.count)
        super().__init__("PowerplayDeliver", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        test1 = player.location.system
        test2 = buffer["event"] == self.name
        if test1 and test2:
            #might be able to remove power check and look at type only
            if self.data["Power"] == buffer["Power"]:
                if self.data["Type"] == buffer["Type"]:
                    self.count += buffer["Count"]
                    self.description = self.format_description(
                        self.data, self.count)
                    return self.data["Count"] <= self.count
        
    def format_description(self, data, count):
        description = "Deliver {} {} of {} to {}. {} Remaining".format(
            data["Count"], _unit_pluralizer(data["Count"]),
            data["Type"], data["StarSystem"],
            str(data["Count"] - count)
        )
        return description

#planned to add
class PowerplayVoucher(Condition):
    pass
class PowerplayVote(Condition):
    pass
"""class BountyCount(Condition):
    def __init__(self, data, is_fail=False):
        bounty_pluralizer = _pluralizer("bounty", "bounties")
        description = "Gain {} {} by killing {}'s ships.".format(
            data["Count"],
            bounty_pluralizer(data["Count"]),
            Data["VictimFaction"]
        )
        super().__init__("Bounty", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:"""

class RedeemVoucher(Condition):
    "redeem voucher request needs Faction, Amount, and Type"
    def __init__(self, data, is_fail=False):
        self.count = 0
        description = self.format_description(data, self.count)
        super().__init__("RedeemVoucher", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name and buffer["Type"] == self.data["Type"]:
            if buffer["Type"] == "Bounty":
                for faction in buffer["Factions"]:
                    if self.data["Faction"] == faction["Faction"]:
                        if self.data["Amount"] < buffer["Amount"]:
                            self.count += 1
                            self.description = self.format_description(
                                self.data, self.count)
            else:
                if buffer["Faction"] == self.data["Faction"]:
                    if self.data["Amount"] < buffer["Amount"]:
                        self.count += 1
                        self.description = self.format_description(
                            self.data, self.count)
            if self.count >= self.data["Count"]:
                return True
        return False
    
    def format_description(self, data, count):
        voucher_pluralizer = _pluralizer("voucher", "vouchers")
        description = "Redeem {}CR worth of {} {} for {}. {} remaining.".format(
            data["Count"], data["Type"],
            voucher_pluralizer(data["Count"]),
            data["Factions"],
            str(data["Count"] - count)
        )
        return description


class MurderFactionShips(Condition):
    def __init__(self, data, is_fail=False):
        self.count = 0
        description = self.format_description(data, self.count)
        super().__init__("CommitCrime", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name and buffer["CrimeType"] == "Murder":
            if self.data["Faction"] == buffer["Faction"]:
                self.count += 1
                self.description = self.format_description(
                    self.data, self.count)
                return self.data["Count"] <= self.count
    
    def format_description(self, data, count):
        ship_pluralizer = _pluralizer("ship", "ships")
        description = "Kill {} {} {} in {}. {} remaining".format(
            data["Count"], data["Faction"],
            ship_pluralizer(data["Count"]),
            data["StarSysten"],
            str(data["Count"] - count)
        )
        return description


class GameMode(Condition):
    def __init__(self, data, is_fail=False):
        description = "Start game in {} mode.".format(data["GameMode"])
        super().__init__("LoadGame", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        if buffer["event"] == self.name:
            return self.data["GameMode"] == buffer["GameMode"]


#remove. this is not required.
class Continued(Condition):
    def __init__(self, data, is_fail=False):
        description = "Journal file has grown to 500k lines. new file created"
        super().__init__("Continued", description, data, is_fail=is_fail)

    def check(self, buffer, player):
        return buffer["event"] == self.name


__all__ = [cls.__name__ for cls in Dock.__bases__[0].__subclasses__()]

"""[
    "Touchdown",
    "LiftOff",
    "Dock",
    "Undock",
    "FSDJump",
    "SupercruiseExit",
    "SupercruiseEntry",
    "MarketBuy",
    "MarketSell",
    "AcceptFactionMission",
    "CompleteFactionMission",
    "FailFactionMission",
    "CollectCargo",
    "EjectCargo",
    "SellExplorationData",
    "Scan",
    "JetConeBoost",
    "PowerplayDeliver",
    "PowerplayVoucher",
    "PowerplayVote",
    "RedeemVoucher",
    "MurderFactionShips",
    "GameMode",
    "Continued"]"""
## not converted
"""def approach_body(self.data, buffer):
    if buffer["event"] == "ApproachBody":
        if self.data["StarSystem"] == buffer["StarSystem"]:
            return self.data["body"] == buffer["body"]
    return False

def leave_body(self.data, buffer):
    if buffer["event"] == "LeaveBody":
        if self.data["StarSystem"] == buffer["StarSystem"]:
            return self.data["body"] == buffer["body"]
    return False

def shield_state(self.data, buffer):
    if buffer["event"] == "ShieldState":
        return buffer["ShieldsUp"] == self.data["ShieldsUp"]

def is_wanted_in_system(self.data, buffer):
    if buffer["event"] == "FSDjump":
        if self.data["StarSystem"] == buffer["StarSystem"]:
            return self.data["body"] == buffer["body"]
    return False"""

if __name__ == "__main__":
    dock = Dock({"StationName": "Station", "StarSystem": "star system"})
    print([cls.__name__ for cls in Dock.__bases__[0].__subclasses__()])