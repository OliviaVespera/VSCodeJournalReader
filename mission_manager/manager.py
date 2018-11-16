from mission_manager.mission import Mission
from mission_manager.player import Player
from mission_manager.mission_enums import MissionStatus

class MissionManager:
    def __init__(self, player, missions=None):
        self.player: Player = player
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