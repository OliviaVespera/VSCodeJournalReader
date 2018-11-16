"""
The reader class is a general reader class that finds and allows
the reading and outputting of read filelines. last line, lines etc.

the journalReader and Status reader are elite dangerous specific readers for the 
status and json files.
"""

import os
from pathlib import Path

ED_DIRECTORY = "~/Saved Games/Frontier Developments/Elite Dangerous/"


class Reader:
    def __init__(self, file_search, directory):
        self.directory = Path(
            directory).expanduser()
        self.file_search = file_search
        self.current_file = self.fine_latest_file_path()

    def __repr__(self):
        return str(self.current_file)

    def fine_latest_file_path(self):
        files = self.directory.glob(self.file_search)
        latest_file = max(files, key=os.path.getmtime)
        # print(latest_file)

        return latest_file

    def get_lines(self):
        with open(self.current_file, "r", encoding='UTF-8') as c_file:
            buffer = [line for line in c_file]
            return buffer

    def get_last_lines(self, prev_line=None, rw="r"):
        with open(self.current_file, rw, encoding='UTF-8') as c_file:
            if prev_line is None:
                #print("prev_line is None!!!!!!!!")

                #getthelastline
                for line in c_file:
                    buffer = line
                # print(buffer)
                return [buffer]
            return self.prev_lines_in_file(prev_line, c_file)

    def prev_lines_in_file(self, prev_line, file):
        pass


class StatusReader(Reader):
    # sets directory and current_journal on initialization
    def __init__(self):
        super().__init__("Status.json", ED_DIRECTORY)

    def _prev_line_in_file(self, prev_line, file):
        #file_lines = file.readlines() 
        #if prev_line not in file_lines[-1:]:
        #    index = file_lines.index(prev_line)
        #    buffer = file_lines[index+1:]
        #return buffer
        if prev_line not in file:
            file.seek(0)
            buffer = file.read()
            print("prev_line:", prev_line, "\nbuffer:", buffer)
            if prev_line != buffer:
                return [buffer]
        return 0


class JournalReader(Reader):
    def __init__(self):
        super().__init__("Journal.*.log", ED_DIRECTORY)
    
    def prev_lines_in_file(self, prev_line, file):
        file_lines = file.readlines() 

        if prev_line not in file_lines[-1:]:
            index = file_lines.index(prev_line)
            buffer = file_lines[index+1:]
            # print(buffer)
            return buffer
        return []



#i'm thinking, JournalReader>EDReader>Reader
class EDReader(Reader):
    def __init__(self, file_search):
        super().__init__(file_search, ED_DIRECTORY)