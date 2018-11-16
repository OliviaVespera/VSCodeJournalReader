from mission_manager.mission_enums import NodeType, MissionStatus

#element will be an individual condition
class Step:
    def __init__(
        self, description=None, conditions=None,
        is_completed=False, node_type=NodeType.Middle):
        self.description = {}
        """{"Title":"None", "Body":"None",
        "Image":None, "Video":None, "Type": None}"""
        self.conditions = []
        self.is_completed = is_completed
        self.edges = []
        self.node_type = node_type

        if conditions is not None:
            for condition in conditions:
                self.conditions.append(condition)
        if description is not None:
            #probably a good idea to refactor this bit
            self.description["Title"] = description.get("Title")
            self.description["Body"] = description.get("Body")
            self.description["Image"] = description.get("Image")
            self.description["Video"] = description.get("Video")
            self.description["Checklist"] = description.get("Checklist")
        
    def dump(self):
        cond = []
        for condition in self.conditions:
            cond.append({
                "name": type(condition).__name__,
                "data": condition.data,
                "is_toggle": condition.is_toggle,
                "is_fail": condition.is_fail,
                "is_complete": condition.is_complete})
        return {
            "description":self.description,
            "conditions": cond,
            "is_completed": self.is_completed,
            "node_type":self.node_type.name}
    
    def __repr__(self):
        edges_description = [step.description for step in self.edges]
        return "Description: {}\nConditions: {}\nNext step is {}\n".format(
            self.description, self.conditions, edges_description)

    #deprecate
    def add_condition(self, condition):
        self.conditions.append(condition)
    
    #replace add_condition with link
    def link(self, condition):
        self.conditions.append(condition)

    def add_requisite(self, idx1, requisite):
        self.conditions[idx1].requisites.append(requisite)
    #Future code when description is a dictionary containing more information.
    #Currently unused
    def get_title(self):
        return self.description.get("title", 0)
    def get_description(self):
        return self.description.get("body", 0)
    def get_image(self):
        return self.description.get("image", 0)
    def get_video(self):
        return self.description.get("video", 0)
    def get_mission_type(self):
        return self.description.get("type", 0)

class StartNode(Step):
    def __init__(self, description={}):
        super().__init__(description ,node_type=NodeType.Beginning)
        #print("Start Node created")