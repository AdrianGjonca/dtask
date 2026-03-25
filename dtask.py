from dataclasses import dataclass
from datetime import datetime
import textwrap as tw
import readline
import atexit
import os
import sys
import signal

tasks = {}

@dataclass
class Task:
    ref: str
    due: datetime | None
    dependancies: set[str]

    def normalize(self):
        removals = set()
        for subtask in self.dependancies:
            if not subtask in tasks.keys():
                removals.add(subtask)
        self.dependancies -= removals

    def __str__(self):
        result = ""
        result += f"[{self.ref}]"
        if self.due is not None:
            result += f' : {self.due.strftime("%Y-%m-%d %H:%M")}'
        return result

    def __repr__(self):
        result = ""
        result += str(self)
        result += "\n"

        self.normalize()

        subresult = ""
        i = 0
        for subtask in self.dependancies:
            i += 1
            to_add = tw.indent(repr(tasks[subtask]),"    ")
            to_add = to_add.replace("    ", "|___", 1)
            if i != len(self.dependancies):
                to_add = to_add.replace("\n ", "\n|")
            subresult += to_add
        
        result += subresult
        return result

    def serialize(self) -> str:
        due_sr: str
        if self.due is not None:
            due_sr = self.due.isoformat()
        else:
            due_sr = ""
        dependancies_sr = ",".join(self.dependancies)
        ref_sr = self.ref
        
        return ";".join([ref_sr, dependancies_sr, due_sr])
    
    @staticmethod
    def deserialize(serialized_task: str):
        sections = serialized_task.split(";")
        ref_sr, dependancies_sr, due_sr = sections
        
        ref = ref_sr
        dependancies = (
            set(dependancies_sr.split(","))
            if len(dependancies_sr)>0
            else set()
        )
        due = (
            datetime.fromisoformat(due_sr)
            if len(due_sr)>0
            else None
        )

        tasks[ref] = Task(
            ref=ref,
            due=due,
            dependancies=dependancies
        )

def addtask(ref: str):
    tasks[ref] = Task(
        ref=ref,
        due=None,
        dependancies=set()
    )

def rmtask(ref: str):
    del tasks[ref]

def adddep(this: str, depends_on: str):
    tasks[this].dependancies.add(depends_on)

def rmdep(this: str, depends_on: str):
    tasks[this].dependancies.remove(depends_on)

def displayall():
    for task in tasks.values():
        print(repr(task))

def displayall_parents():
    children = set()
    for task in tasks.values():
        if len(task.dependancies) > 0:
            children |= task.dependancies
    parents_r = tasks.keys() - children
    parents = [tasks[x] for x in parents_r]
    for task in parents:
        print(repr(task))


def depexists(this: str, depends_on: str) -> bool:
    stack = []
    stack.append(this)
    found = False
    while len(stack) != 0 and not found:
        item = stack.pop()
        stack.extend(tasks[item].dependancies)
        if item == depends_on:
            found = True
    return found

def init_time(this: str) -> bool:
    if tasks[this].due is not None:
        return False
    tasks[this].due = datetime.now()
    return True

def serialize() -> str:
    seriaized_tasks = [x.serialize() for x in tasks.values()]
    serialized = "\n".join(seriaized_tasks)
    return serialized

def deserialize(serialized: str):
    global tasks

    serialized_tasks = serialized.split("\n")
    tasks = {}
    for serialized_task in serialized_tasks:
        Task.deserialize(serialized_task)

def writeout(file: str, to_write: str):
    with open(file, 'w') as file_h:
        file_h.write(to_write)
        print("Wrote to '" + file + "'")

def readin(file: str):
    with open(file, "r") as file_h:
        serialized = file_h.read()
        deserialize(serialized)
        print("Read from '" + file + "'")

def help():
    print("+==================D-Task help-card======================+")
    print(".                                            Quit program")
    print("h                                    Open this helpscreen")
    print("n [A]                  Create new task with reference [A]")
    print("d [A] [B]            Create dependancy '[A] requires [B]'")
    print("rn [A]                                   Removes task [A]")
    print("rd [A] [B]          Removes dependancy '[A] requires [B]'")
    print("v                      Display all root dependancy graphs")
    print("v [A]                     Display dependancy graph of [A]")
    print("V                Display absolutely all dependancy graphs")
    print("? [A] [B]                    Checks if '[A] requires [B]'")
    print("tm [A] <mm>            Sets due month of task [A] to <mm>")
    print("td [A] <dd>              Sets due day of task [A] to <dd>")
    print("ty [A] <yyyy>         Sets due year of task [A] to <yyyy>")
    print("tt [A] <hh>:<mn>   Sets due time of task [A] to <hh>:<mn>")
    print("tz [A] <mn>-<dy>   Sets due date of task [A] to <mn>-<dy>")
    print(":w <file>                                Writes to <file>")
    print(":e <file>                                    Loads <file>")

def ensure_args(tokens: list[str], n_args: int) -> bool:
    tk_count = len(tokens)
    arg_count = tk_count - 1
    if arg_count == n_args:
        return True
    elif arg_count < n_args:
        print(f"Missing arguments ({arg_count}/{n_args})")
        return False
    else:
        print("Incorrect syntax, see HelpCard (h<ret>)")
        return False


def menu_n(command: str):
    tokens = command.split()
    if not ensure_args(tokens, 1):
        return
    ref = tokens[1]
    if ref in tasks.keys():
        print(f"Task [{ref}] allready exists")
    addtask(ref)
    print(f"[{ref}]")

def menu_d(command: str):
    tokens = command.split()
    if not ensure_args(tokens, 2):
        return
    refA = tokens[1]
    refB = tokens[2]
    failurestate = False
    if not refA in tasks.keys():
        print(f"Task [{refA}] does not exist!")
        failurestate = True
    if not refB in tasks.keys():
        print(f"Task [{refB}] does not exist!")
        failurestate = True
    if not failurestate:
        if depexists(refB, refA):
            print("Cannot create circular dependancies!")
            return
        adddep(refA, refB)
        print(f"[{refA}] -> [{refB}]")

def menu_rn(command: str):
    tokens = command.split()
    if not ensure_args(tokens, 1):
        return
    ref = tokens[1]
    if not ref in tasks.keys():
        print(f"Task [{ref}] does not exist")
    rmtask(ref)

def menu_rd(command: str):
    tokens = command.split()
    if not ensure_args(tokens, 2):
        return
    refA = tokens[1]
    refB = tokens[2]
    failurestate = False
    if not refA in tasks.keys():
        print(f"Task [{refA}] does not exist!")
        failurestate = True
    if not refB in tasks.keys():
        print(f"Task [{refB}] does not exist!")
        failurestate = True
    if not failurestate:
        if not depexists(refA, refB):
            print("Dependancy does not exist!")
            return
        rmdep(refA, refB)

def menu_v(command:str):
    tokens = command.split()
    if len(tokens) == 1:
        displayall_parents()
        return
    elif len(tokens) == 2:
        ref = tokens[1]
        if not ref in tasks.keys():
            print(f"Task [{ref}] does not exist!")
            return
        print(repr(tasks[ref]))
    else:
        print("Incorrect syntax, see HelpCard (h<ret>)")

def menu_V(command:str):
    tokens = command.split()
    if len(tokens) == 1:
        displayall()
        return
    else:
        print("Incorrect syntax, see HelpCard (h<ret>)")

def menu_questionmark(command:str):
    tokens = command.split()
    if not ensure_args(tokens, 2):
        return
    refA = tokens[1]
    refB = tokens[2]
    failurestate = False
    if not refA in tasks.keys():
        print(f"Task [{refA}] does not exist!")
        failurestate = True
    if not refB in tasks.keys():
        print(f"Task [{refB}] does not exist!")
        failurestate = True
    if not failurestate:
        if not depexists(refA, refB):
            print(f"[{refA}] -/-> [{refB}]")
            return
        else:
            print(f"[{refA}] -> [{refB}]")
            return

def menu_tT(command:str):
    tokens = command.split()
    if not ensure_args(tokens, 1):
        return
    refA = tokens[1]
    if not refA in tasks.keys():
        print(f"Task [{refA}] does not exist!")
        return
    if not init_time(refA):
        print(f"Task [{refA}] allready has date")
        return
    print(str(tasks[refA]))

def menu_tm(command:str):
    tokens = command.split()
    if not ensure_args(tokens, 2):
        return
    refA = tokens[1]
    month_txt = tokens[2]
    if not refA in tasks.keys():
        print(f"Task [{refA}] does not exist!")
        return
    month: int
    try:
        month = int(month_txt)
    except ValueError:
        print(f"Argument [{month_txt}] is not a number!")
        return
    if not month in range(1, 13):
        print(f"Month [{month}] must be between 1-12")
        return
    init_time(refA)
    tasks[refA].due = tasks[refA].due.replace(month=month)
    print(str(tasks[refA]))

def menu_td(command:str):
    tokens = command.split()
    if not ensure_args(tokens, 2):
        return
    refA = tokens[1]
    day_txt = tokens[2]
    if not refA in tasks.keys():
        print(f"Task [{refA}] does not exist!")
        return
    day: int
    try:
        day = int(day_txt)
    except ValueError:
        print(f"Argument [{day_txt}] is not a number!")
        return
    if not day in range(1, 32):
        print(f"Day [{day}] must be between 1-31")
        return
    init_time(refA)
    try:
        tasks[refA].due = tasks[refA].due.replace(day=day)
    except ValueError:
        print(f"Day [{day}] not valid for given month!")
        return
    print(str(tasks[refA]))

def menu_ty(command: str):
    tokens = command.split()
    if not ensure_args(tokens, 2):
        return
    refA = tokens[1]
    year_txt = tokens[2]
    if not refA in tasks.keys():
        print(f"Task [{refA}] does not exist!")
        return
    year: int
    try:
        year = int(year_txt)
    except ValueError:
        print(f"Argument [{year_txt}] is not a number!")
        return
    if year < 1 or year > 9999:
        print(f"Year [{year}] must be between 1-9999")
        return
    init_time(refA)
    try:
        tasks[refA].due = tasks[refA].due.replace(year=year)
    except ValueError:
        print(f"Year [{year}] not valid!")
        return
    print(str(tasks[refA]))

def menu_tt(command: str):
    tokens = command.split()
    if not ensure_args(tokens, 2):
        return
    refA = tokens[1]
    time_txt = tokens[2]
    if not refA in tasks.keys():
        print(f"Task [{refA}] does not exist!")
        return
    
    try:
        hour_str, minute_str = time_txt.split(':')
        hour = int(hour_str)
        minute = int(minute_str)
    except ValueError:
        print(f"Time [{time_txt}] must be in format HH:MM (e.g., 14:30)")
        return
    
    if hour not in range(0, 24):
        print(f"Hour [{hour}] must be between 0-23")
        return
    if minute not in range(0, 60):
        print(f"Minute [{minute}] must be between 0-59")
        return
    
    init_time(refA)
    tasks[refA].due = tasks[refA].due.replace(hour=hour, minute=minute)
    print(str(tasks[refA]))

def menu_tz(command: str):
    tokens = command.split()
    if not ensure_args(tokens, 2):
        return
    refA = tokens[1]
    date_txt = tokens[2]
    if not refA in tasks.keys():
        print(f"Task [{refA}] does not exist!")
        return
    
    try:
        month_str, day_str = date_txt.split('-')
        month = int(month_str)
        day = int(day_str)
    except ValueError:
        print(f"Date [{date_txt}] must be in format MM-DD (e.g., 12-25 for December 25th)")
        return
    
    if month not in range(1, 13):
        print(f"Month [{month}] must be between 1-12")
        return
    if day not in range(1, 32):
        print(f"Day [{day}] must be between 1-31")
        return
    
    init_time(refA)
    try:
        tasks[refA].due = tasks[refA].due.replace(month=month, day=day)
    except ValueError as e:
        print(f"Date {month:02d}-{day:02d} is not valid! ({e})")
        return
    print(str(tasks[refA]))

def menu__debug(command: str):
    seriaized_tasks = [x.serialize() for x in tasks.values()]
    serialized = "\n".join(seriaized_tasks)
    print(serialized)

def menu_colon_w(command: str):
    tokens = command.split()
    if not ensure_args(tokens, 1):
        return
    file = " ".join(tokens[1:])

    writeout(file, serialize())

def menu_colon_e(command: str):
    tokens = command.split()
    if not ensure_args(tokens, 1):
        return
    file = " ".join(tokens[1:])
    
    try:
        readin(file)
    except FileNotFoundError:
        print("File does not exist!", file=sys.stderr)
    except IsADirectoryError:
        print("File path stated is actually a directory!", file=sys.stderr)

#Main
print("D-Task: Task dependancy organiser and todolist")

if len(sys.argv[1:]) > 1:
    print("D-Task can only take 0 or 1 arguments!")
    #TODO something nicer and maybe a man page
    sys.exit(7)

if len(sys.argv[1:]) == 1:
    try:
        readin(sys.argv[1])
    except FileNotFoundError:
        print("File does not exist!", file=sys.stderr)
        sys.exit(2)
    except IsADirectoryError:
        print("File path stated is actually a directory!", file=sys.stderr)
        sys.exit(21)

history_file = os.path.join(os.path.expanduser("~"), ".dtask_history")
try:
    readline.read_history_file(history_file)
    readline.set_history_length(1000)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, history_file)


def _sigint_h(sig, frame):
    print("\nQuiting")
    sys.exit(0)
signal.signal(signal.SIGINT, _sigint_h)


print("type h<ret> for help")
command = ""
while not command.startswith("."):
    command = input("> ")
    if command.startswith("."):
        print("Quiting")
    elif command.startswith("h"):
        help()
    elif command.startswith("n"):
        menu_n(command)
    elif command.startswith("d"):
        menu_d(command)
    elif command.startswith("rn"):
        menu_rn(command)
    elif command.startswith("rd"):
        menu_rd(command)
    elif command.startswith("v"):
        menu_v(command)
    elif command.startswith("V"):
        menu_V(command)
    elif command.startswith("?"):
        menu_questionmark(command)
    elif command.startswith("tT"):
        menu_tT(command)
    elif command.startswith("tm"):
        menu_tm(command)
    elif command.startswith("td"):
        menu_td(command)
    elif command.startswith("ty"):
        menu_ty(command)
    elif command.startswith("tt"):
        menu_tt(command)
    elif command.startswith("tz"):
        menu_tz(command)
    elif command.startswith(":w"):
        menu_colon_w(command)
    elif command.startswith(":e"):
        menu_colon_e(command)
    elif command.startswith("_debug"):
        menu__debug(command)
    else:
        print("Command not found")
