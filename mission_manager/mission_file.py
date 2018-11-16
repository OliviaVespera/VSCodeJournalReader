#mission parameters
title3 = "Buy beer for the void!"
desc3 = "People at Buckland Works are getting mighty thirsty.\nHelp em out by getting em some beer!"
reward3 = {"Tridot": 10}

#mission step descriptions.
step_desc3 = [
    "Buy 2 units of beer and leave the station",
    "Jump to Evenks",
    "Dock with Buckland Works",
    "Sell 2 units of beer"]

"""mission step conditions. Until these are achieved, you can't move from this mission step. mission step = node.
each mission step can have multiple conditions"""
step_conds3 = [
    [{"event": "MarketBuy", "MarketID": 3227985664, "Type": "beer", "Count": 2},
    {"event": "Undocked", "StationName": "Zahn Station"}],

    [{"event": "StartJump", "JumpType": "Hyperspace", "StarSystem": "Evenks"}],

    [{"event": "Docked", "StationName": "Buckland Works"}],

    [{"event": "MarketSell", "MarketID": 3227968000, "Type": "beer", "Count":2}]]

#edges
edges3 = {0: 1, 1: 2, 2: 3, 3: 4}
requisites3 = {
    (1, 1): {(1, 0)},
    (2, 0): {(1, 0), (1, 1)},
    (4, 0): {(1, 0)}
    }

class MissionFile:
    def __init__(self, title, desc, reward, step_desc, conditions, edges, requisites):
        self.title = title
        self.desc = desc
        self.reward = reward
        self.step_desc = step_desc
        self.conditions = conditions
        self.edges = edges
        self.requisites = requisites

mission1 = MissionFile(title3, desc3, reward3, step_desc3, step_conds3, edges3, requisites3)
