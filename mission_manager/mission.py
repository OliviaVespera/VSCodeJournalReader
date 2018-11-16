from datetime import datetime, timedelta
from mission_manager.step import Step, StartNode
from mission_manager.mission_enums import MissionStatus, NodeType
from mission_manager.mission_utils import convert_time_stamp
import mission_manager.condition as c
from uuid import UUID, uuid4
import json


# Conditional class previous and next point to other conditions.
# data contains the condition itself. Permanent is a bool whether
# it must always be active or not
# condition type is whether it's a fail condition or a victory condition

#an abstract base class for all flags and descriptions

# The mission class stores the mission conditions,
# timings, title and descriptions
class Mission:
    def __init__(self, uid, title, desc, steps, edges, requisites, **optional):
        self.uid: UUID = uid
        self.title: str = title
        self.desc = desc
        self.reward: dict = optional.get("reward")
        self.image: str = optional.get("image")
        self.video: str = optional.get("video")
        self.duration: timedelta = optional.get("duration")
        self.checklist: list = optional.get("checklist")

        self.steps = [StartNode({"Title":"Mission Start"})]
        self.current_step = self.steps[optional.get("current_step", 0)]
        self.start_time = optional.get("start_time")
        self.end_time = optional.get("end_time")
        self.status = optional.get("status", MissionStatus.Not_Started)
        self.dump_file = {
            "uid": self.uid.int,
            "title": self.title,
            "desc": self.desc,
            "steps": [step.dump() for step in steps],
            "edges": edges,
            "current_step": self.steps.index(self.current_step),
            "requisites": self.format_requisite(requisites),
            "optional": optional
            }

        self.__build_mission_structure(steps, edges, requisites)

    def __add_edge(self, idx1, idx2):
        if isinstance(idx2, int):
            self.steps[idx1].edges.append(self.steps[idx2])
        else:
            for i in range(len(idx2)):
                self.steps[idx1].edges.append(self.steps[i])
    
    def add_edges(self, edges):
        for key, value in edges.items():
                self.__add_edge(key, value)

    def __add_requisite(
        self, this_step, condition_idx,
        target_step_idx, target_condition_idx):
        that_step = self.steps[target_step_idx]
        that_condition = that_step.conditions[target_condition_idx]
        this_step.add_requisite(condition_idx, that_condition)
        return that_condition.data

    def add_requisites(self, requisites):
        for step_idx, condition_idx in requisites.keys():
            this_step = self.steps[step_idx]
            this_condition = this_step.conditions[condition_idx]
            target_to_link = requisites[step_idx, condition_idx]
            
            for t_step_idx, t_condition_idx in target_to_link:
                that_condition_data = self.__add_requisite(
                    this_step, condition_idx, t_step_idx, t_condition_idx)
                print(
                    str(this_condition.data)
                    + " relies on "
                    + str(that_condition_data)
                )

    def __end(self, status):
        self.status = status
        self.end_time = datetime.utcnow()

    def __win(self, inventory):
        self.__end(MissionStatus.Completed)
        print("You've completed the mission and gained...")
        for key in self.reward.keys():
            print("{} {}".format(str(self.reward[key]), key))
            inventory[key]["Balance"] = self.reward[key]
        
    # lose and cancelled not yet set
    def __fail(self):
        self.__end(MissionStatus.Failed)
        print("You've failed the mission!")

    def cancel(self):
        self.__end(MissionStatus.Cancelled)
        print("You've cancelled the mission!")

    def __build_mission_structure(self, steps, edges, requisites):
        if isinstance(steps, list) \
        and isinstance(requisites, dict) \
        and isinstance(edges, dict):
            self.steps.extend(steps)
            self.__add_edge(0, 1)
            self.add_edges(edges)
            self.add_requisites(requisites)

    def update(self, buffer, player_state):
        #check global time fail
        if self.duration is not None:
            if datetime.utcnow() - self.start_time > self.duration:
                self.__fail()
                return
        
        # iterate through conditions
        
        #for each node in edges
        for node in self.current_step.edges:
            
            #for each condition in each node
            all__conditions_completed = True
            for condition in node.conditions:

                #if condition is toggleable
                if not (condition.is_complete and  condition.is_toggle):            
                    #Checks to see if the log is after the mission start time
                    if convert_time_stamp(buffer["timestamp"]) > self.start_time:
                        
                        # if a condition has requisites, check those requisites first.
                        if condition.has_requisite() and not condition.check_requisites():
                            print("You didn't fulfill the prerequisite for this condition")
                            all__conditions_completed = condition.is_completed
                            continue  
                        
                        #if a condition is achieved, announce it and modify it so it is known
                        if condition.check(buffer, player_state):
                            print("Condition: {} achieved!".format(condition))
                            if condition.is_fail:
                                self.__fail()
                                return
                            condition.is_completed = True
                all__conditions_completed = condition.is_complete
        
            #if none of the conditions came up false, check if we're at the end.
            if all__conditions_completed:
                self._change_current_step(node)
                edge_descs = ""
                if node.node_type == NodeType.End:
                    self.__win(player_state.inventory)
                    print("You win... apparently")
                else:
                    for node in node.edges:
                        for condition in node.conditions:
                            edge_descs += condition.description + "\n"
                    print("Next step is to {}".format(edge_descs))
    def _change_current_step(self, next_step):
        self.current_step = next_step
        self.dump_file["current_step"] = self.steps.index(self.current_step)



    def start(self):
        self.start_time = datetime.utcnow()
        self.status = MissionStatus.Started
        print("Mission: '{}' has started at {}".format(self.title,
        self.start_time))
        print("First task is to ", end = "")
        for node in self.current_step.edges:
            #do you want to add a title in each step?
            print(node.description["Title"])
            for condition in node.conditions:
                print(condition.description)

    def get_steps_desc(self):
        buffer = ""
        step_num = 1
        for step in self.steps:
            if not isinstance(step, StartNode):
                buffer += "{num}. {desc}\n".format(
                    num = str(step_num), desc=step.description)
                step_num += 1
        return buffer

    def build_steps(self, conditions, step_descriptions):
        count = 0
        steps = []

        #sets last step as an end node
        for condition, description in zip(conditions, step_descriptions):
            if count == len(conditions)-1:
                steps.append(
                    Step(
                        {
                            "Title": description},
                            [condition],
                            node_type=NodeType.End))
            else:
                steps.append(
                    Step({"Title": description}, [condition]))
            count+=1
        return steps

    def format_requisite(self, tuple_dict):
        if tuple_dict:
            for k,v in tuple_dict.items():
                converted_list = []
                value_list = []
                for e in v:
                    value_list.append(e)
                converted_list.append({"key":k, "value": value_list})
                return converted_list
    
        return {}
    
    def dump(self):
        return self.dump_file

    def save(self, file_location):
        self.dump_file["steps"] = [step.dump() for step in self.steps[1:]]
        self.dump_file["current_step"] = self.steps.index(self.current_step)
        with open(file_location, mode="a", encoding="UTF-8") as cfile:
            json.dump(self.dump_file, cfile)
            cfile.write("\n")
    def save_file(self):
        self.dump_file["steps"] = [step.dump() for step in self.steps[1:]]
        self.dump_file["current_step"] = self.steps.index(self.current_step)
        return json.dump(self.dump_file) + "\n"
    @classmethod
    def _load_steps(cls, mission_json):
        loaded_steps = []
        c_classes = c.__all__
        for step in mission_json["steps"]:
            loaded_conditions = []
            for condition in step["conditions"]:
                if condition["name"] in c_classes:
                    condition_cls = getattr(c, condition["name"])
                    condition_obj = condition_cls(condition["data"], condition["is_fail"])
                    condition_obj.is_toggle = condition["is_toggle"]
                    condition_obj.is_completed = condition["is_complete"]
                    loaded_conditions.append(condition_obj)
            loaded_step = Step(step["description"], loaded_conditions, step["is_completed"], NodeType[step["node_type"]])      
            loaded_steps.append(loaded_step)
        return loaded_steps
    @classmethod
    def _load_edges(cls, mission_json):
        loaded_edges = {}
        for key, value in mission_json["edges"].items():
            loaded_edges[int(key)] = value
        return loaded_edges
    @classmethod
    def _load_requisites(cls, mission_json):
        loaded_requisites = {}
        for requisite in mission_json["requisites"]:
            loaded_requisites[tuple(requisite["key"])] = tuple(requisite["value"])
        return loaded_requisites
    @classmethod
    def load(cls, mission_json):
        uid = UUID(int=mission_json["uid"])
        title = mission_json["title"]
        desc = mission_json["desc"]
        steps = cls._load_steps(mission_json)
        edges = cls._load_edges(mission_json)
        requisites = cls._load_requisites(mission_json)
       
        return cls(uid, title, desc, steps, edges, requisites)

    @classmethod
    def load_from_json(cls, mission_file):
        with open(mission_file, mode="r", encoding="UTF-8") as cfile:
            mission_json = json.load(cfile)
        return cls.load(mission_json)

#Mission Templates
class BuyAndSell(Mission):
    def __init__(
        self, uid, title, desc, step_descriptions,
        quantity, commodity, from_station, from_system,
        to_station, to_system, **optional):
        conditions = []
        conditions.append(
            c.MarketBuy(
                {
                    "Type": commodity,
                    "Count": quantity,
                    "StationName": from_station,
                    "StarSystem": from_system
                }))
        conditions.append(
            c.Undock({
                    "StationName": from_station,
                    "StarSystem": from_system
                }))
        conditions.append(
            c.Dock({
                    "StationName": to_station,
                    "StarSystem": to_system
                }))
        conditions.append(
            c.MarketSell({
                    "Type": commodity,
                    "Count": quantity,
                    "StationName" : to_station,
                    "StarSystem" : to_system
                }))
        #sets last step as an end node
        steps = self.build_steps(conditions, step_descriptions)
        edges = {1: 2, 2: 3, 3: 4}
        requisites = {(2, 0): {(1, 0)}}
        super().__init__(uid, title, desc, steps, edges, requisites, **optional)


class FactionMission(Mission):
    def __init__(
        self, uid, title, desc, step_descriptions, 
        faction, system, **optional):
        conditions = []
        conditions.append(c.AcceptFactionMission(
            {
                "Faction": faction,
                "StarSystem": system,
            }))
        conditions.append(c.CompleteFactionMission(
            {
                "Faction": faction,
                "StarSystem": system,
            }))
        #sets last step as an end node
        steps = self.build_steps(conditions, step_descriptions)
        edges = {1:2}
        requisites = {}
        super().__init__(uid, title, desc, steps, edges, requisites, **optional)

class RedeemVoucher(Mission):
    def __init__(
        self, uid, title, desc, step_descriptions,
        faction, voucher_type, count, **optional):
        conditions = []
        conditions.append(c.RedeemVoucher(
            {
                "Faction": faction,
                "Type": voucher_type,
                "Count": count
            }))
        #sets last step as an end node
        steps = self.build_steps(conditions, step_descriptions)
        edges = {}
        requisites = {}
        super().__init__(uid, title, desc, steps, edges, requisites, **optional)


class UnDockAndDock(Mission):
    def __init__(
        self, uid, title, desc, station, system, step_descriptions, **optional):
        conditions = []
        conditions.append(c.Undock(
            {
                "StationName": station,
                "StarSystem": system}))

        conditions.append(c.Dock(
            {
                "StationName": station,
                "StarSystem": system}))
        
        #sets last step as an end node
        steps = self.build_steps(conditions, step_descriptions)
        edges = {1: 2}
        requisites = {}
        super().__init__(uid, title, desc, steps, edges, requisites, **optional)


class Dock(Mission):
    def __init__(
        self, uid, title, desc, station, system, step_descriptions, **optional):
        conditions = []
        conditions.append(c.Dock(
            {
                "StationName": station,
                "StarSystem": system
            }))
        #sets last step as an end node
        steps = self.build_steps(conditions, step_descriptions)
        edges = {}
        requisites = {}
        super().__init__(uid, title, desc, steps, edges, requisites, **optional)


class SellAtStation(Mission):
    def __init__(
        self, uid, title, desc, step_descriptions,
        commodity, quantity, to_station, to_system, **optional):
        conditions = []
        conditions.append(
            c.MarketSell(
                {
                    "Type": commodity,
                    "Count": quantity,
                    "StationName": to_station,
                    "StarSystem": to_system
                })
        )
        #sets last step as an end node
        steps = self.build_steps(conditions, step_descriptions)
        edges = {}
        requisites = {}
        super().__init__(uid, title, desc, steps, edges, requisites, **optional)


class Tour(Mission):
    def __init__(
        self, uid, title, desc, systems, **optional):
        conditions = []
        for system in systems:
            conditions.append(
                c.FSDJump({
                        "StarSystem": system
                    }
                )
            )
        #sets last step as an end node
        edges = {}
        step_descriptions = []
        for i in range(1, len(conditions)):
            edges[i] = i+1
        for condition in conditions:
            step_descriptions.append(condition.description)
        steps = self.build_steps(conditions, step_descriptions)
        print(edges)
        requisites = {}
        super().__init__(uid, title, desc, steps, edges, requisites, **optional)


class Visit(Mission):
    def __init__(
        self, uid, title, desc, systems, **optional):
        conditions = []
        for system in systems:
            conditions.append(
                c.FSDJump({
                        "StarSystem": system
                    }))
        
        #sets last step as an end node
        
        edges = {}
        
        step_descriptions = ""
        for i in range(1, len(conditions)-1):
            edges[i] = i+1
        for condition in conditions:
            step_descriptions.join("\n"+condition.description)
        steps = [Step(description={"Body":step_descriptions}, conditions=conditions)]
        print(edges)
        requisites = {}
        super().__init__(uid, title, desc, steps, edges, requisites, **optional)


#Manager class could be put in another file
class MissionManager:
    def __init__(self, player, missions=None):
        self.player = player
        self.missions = [] if missions is None else missions
        print("New mission manager created")

    def create(self, uid, title, desc, **optional):
        new_mission = Mission(uid, title, desc, **optional)
        self.missions.add(new_mission)
        print("Mission: '{}' added".format(new_mission.title))

    def add(self, mission):
        self.missions.append(mission)

    def remove_mission(self, index=None, uid=None):
        if uid is not None:
            for mission in self.missions:
                if mission.uid == uid:
                    del mission 
            return True
        if index is not None:
            del self.missions[index]
            return True
        print("No missions were removed")
        return False
    
    def start_all(self):
        for i in range(len(self.missions)):
            self.start(i)

    def start(self, index):
        self.missions[index].start()

    def update(self, buffer):
        for mission in self.missions:
            if mission.status == MissionStatus.Started:
                mission.update(buffer, self.player)
            else:
                continue
    def get_by_uid(self, uid):
        for mission in self.missions:
            if mission.uid.int == uid:
                return mission
    def save(self, file_location):
        buffer = ""
        for mission in self.missions:
            buffer += mission.save_file()
        with open(file_location, mode="r", encoding="UTF-8") as c_file:
            json.dump(buffer, c_file)

    def load(self, file_location):
        with open(file_location, mode="r", encoding="UTF-8") as m_file:
            buffer = [json.loads(line) for line in m_file]

        for line in buffer:
            mission = Mission.load(line)
            self.missions.append(mission)
        

if __name__ == "__main__":
    import json
    from pprint import pprint

    my_condition = c.Dock({"StationName": "Haplock Bay", "StarSystem":"9 Aurigae"})
    my_step = Step({"Title": my_condition.description}, {my_condition})
    
    my_mission = Mission(
        uuid4(), "Test Mission",
        "This is a test mission and this is the description text",
        {my_step}, {},{})

    test_mission = BuyAndSell(
        uuid4(), "Deliver Gold", "This is just a test mission",
        [
            "Buy stuff from market",
            "Undock from station",
            "Dock with the station", 
            "Sell stuff"
        ],
        5, "gold",
        "Milnor Enterprise", "Zach",
        "Cixin Ring", "Pularungu",
        reward={"Tridots":30},
    )

    test_mission_2 = FactionMission(uuid4(),
    "General work for the BD+49 1280 Public Service",
    "This is a test Mission",
    ["one", "two"],
    faction="BD+49 1280 Public Services",
    system="BD+49 1280",
    reward={"Tridots":30})
    
    test_mission.save("my_first.json")
    test_mission_2.save("my_first.json")

    with open("my_first.json", mode="r", encoding="UTF-8") as c_file:
        buffer = [json.loads(line) for line in c_file]
    #pprint(buffer)
    missions = [Mission.load(line) for line in buffer]
    for mission in missions:
        print(mission.title)
    test_mission_loaded = Mission.load(buffer)
    import pickle
    with open("my_first.bin", mode="wb") as bfile:
        print(pickle.dump(my_mission, bfile))

    with open("my_first.bin", mode="rb") as bfile:
        new_file = pickle.load(bfile)
    
    print(new_file.title)