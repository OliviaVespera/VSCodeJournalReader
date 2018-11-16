from mission_manager.app import Application
from mission import BuyAndSell, UnDockAndDock, Dock, Tour, FactionMission, Visit
from pprint import pprint
title_1 = "Deliver Special beer!"
description_1 = "Our first Mission. Deliver 5 tons of alcohol to Evenks from Zahn Station."
reward_1 = {"Tridots": 20}

#buy num commodity from station, system and sell at station, system

buy_mission = BuyAndSell(
    "Deliver beer", "This is just a test mission", {"Tridots":30},
    [
        "Buy stuff from market",
        "Undock from station",
        "dock with the station", 
        "sell stuff"],
    20, "Beer",
    "Wrangell Dock", "NLTT 16389",
    "Woolley Orbital", "LFT 446",
    )
step_names = ["buy the stuff", "get out of dodge", "get "]
buy_mission2 = BuyAndSell(
    "Deliver Insulating Membrane", "This is just a test mission", {"Tridots":30},
    ["Buy stuff from market",
    "Undock from station",
    "dock with the station", 
    "sell stuff"],
    1, "insulatingmembrane",
    "Milnor Enterprise", "Zach",
    "Cixin Ring", "Pularungu"
    )

buy_mission3 = BuyAndSell(
    "Deliver Gold", "This is just a test mission", {"Tridots":30},
    [
        "Buy stuff from market",
        "Undock from station",
        "dock with the station", 
        "sell stuff"],
    1, "gold",
    "Milnor Enterprise", "Zach",
    "Cixin Ring", "Pularungu"
    )

short_mission = UnDockAndDock(
    "Station undocking test",
    "This is just a test mission",
    {"Tridots":30},
    [
        "one",
        "two"],
    "Cixin Ring", "Pularungu",
)
dock = Dock(
    "Deliver Insulating Membrane",
    "This is just a test mission",
    {"Tridots":30},
    "Just dock with the station",
    "Cixin Ring",
    "Pularungu",
)

faction_mission = FactionMission(4,
    "General work for the BD+49 1280 Public Service",
    "This is a test Mission",
    ["one", "two"],
    faction="BD+49 1280 Public Services",
    system="BD+49 1280",
    reward={"Tridots":30}
)
print("START FACTION MISSION DICT")
#pprint(faction_mission.__dict__)


"""systems=[
    "Zach",
    "NLTT 16389",
    "NN 3365",
    "BD+47 1236",
    "HAT 94-00572",
    "9 Aurigae",
    "LHS 1758",
    "Du Shenge",
    "LP 84-34",
    "Evenks",
    "Lalande 9828"
]
reward={"Tridots": 30}
tour = Tour(
    1, "Home system Jaunt", "Visit all systems", systems, reward=reward)

visit = Visit(
    2, "Home system Jaunt", "Visit all systems", ["Zach"], reward=reward)

App = Application()

#App.mission.add(buy_mission)
#App.mission.add(buy_mission2)
#App.mission.add(buy_mission3)
#App.mission.add(short_mission)
#App.mission.add(dock)
App.mission.add(faction_mission)
#App.mission.add(tour)

#start loop
#App.mission.start_all()
#App.mainLoop()
"""