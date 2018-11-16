import condition as con
from player_state import Player
import unittest
from condition import _margin_test as margin_test

p = Player()
p.missions[1] = {"Faction":"Green Party of Zosia", "StarSystem":"Zosia"}
print(p.missions)
c = con.CompleteFactionMission({"Faction":"Green Party of Zosia", "StarSystem":"Zosia"})
buffer = {"event":"MissionCompleted", "MissionID":1}
print(c.check(buffer, p))

class TestConditions(unittest.TestCase):

    def test_location(self):
        location = p.Location("9 Aurigae", "9 Aurgae C 1", 201, 200)
        self.assertEqual(location.body, "9 Aurgae C 1")

    def test_two(self):
        c = con.EjectCargo()
        unittest.TestCase()
    def test_two(self):
        c = con.EjectCargo()
        unittest.TestCase()
    def test_two(self):
        c = con.EjectCargo()
        unittest.TestCase()
    def test_two(self):
        c = con.EjectCargo()
        unittest.TestCase()


if __name__ == '__main__':
    unittest.main()