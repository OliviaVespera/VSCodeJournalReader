import json
from time import clock
from mission_manager.journalreader import JournalReader, StatusReader
from mission_manager.mission import MissionManager
from mission_manager.player import Player

# Journal parser parses for information.
class Application:
    def __init__(self):
        self.journal_reader = JournalReader()
        self.status_reader = StatusReader()
        self.player = Player()
        self.mission = MissionManager(self.player)
        self.faction = None # for future use exp: 15/oct/2018
        #maybe we can automatically add mission, ship and faction
        # to update list if they're initialized
        self.updatelist = []
        self.previous_journal_line = ""
        self.status_t = int(clock())
        self.journal_t = self.status_t
    def missions(self):
        return self.mission.missions
    def update(self, buffer, list_of_functions_to_call):
        for line in buffer:
            try:
                loaded_line = json.loads(line)
            except json.decoder.JSONDecodeError:
                print("first line in update printed an error")
                loaded_line = None
            for each_function in list_of_functions_to_call:
                each_function(loaded_line)
            previous_line = line
        return previous_line
    
    def start(self):
        #saves a list of all logs
        self.previous_journal_line = self.journal_reader.get_lines()
        self.previous_journal_line = self.update(
            self.previous_journal_line,
            [self.player.load_game, self.mission.update])

        status_buffer = self.status_reader.get_lines()
        self.update(status_buffer, [self.player.update])

        print(self.player.cmdr)
        print(self.player.location)
        print(self.player.write_cargo())

        self.status_t = int(clock())
        self.journal_t = self.status_t
    def _is_it_time(self, current_time, previous_time, interval):
        return current_time - previous_time > interval
    
    def gui_loop(self, journal_time_delay=1, status_time_delay=3):
        check_time = clock()
        #status is read here
        if self._is_it_time(check_time, self.status_t, status_time_delay):
            buffer = self.status_reader.get_lines()
            if buffer:
                if len(buffer) ==0:
                    print("buffer is 0 but this still happened??")
                self.update(buffer, [self.player.update]) 
                self.status_t = int(check_time)
  
        #journal is read here
        if self._is_it_time(check_time, self.journal_t, journal_time_delay):
            buffer = self.journal_reader.get_last_lines(
                self.previous_journal_line)
            if len(buffer) != 0:
                #if buffer isn't empty cause buffer is a []
                self.previous_journal_line = self.update(
                    buffer, [self.mission.update, self.player.update])
            self.journal_t = int(check_time)

    def mainLoop(self, journal_time_delay=1, status_time_delay=3): 
        self.start()
        while True:
            self.gui_loop(journal_time_delay, status_time_delay)