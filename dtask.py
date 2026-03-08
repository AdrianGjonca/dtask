from dataclasses import dataclass
from datetime import datetime
import textwrap as tw

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


def help():
    print("+==================D-Task help-card======================+")
    print(".                                            Quit program")
    print("h                                    Open this helpscreen")
    print("n [A]                  Create new task with reference [A]")
    print("d [A] [B]            Create dependancy '[A] requires [B]'")
    print("rn [A]                                   Removes task [A]")
    print("rd [A] [B]          Removes dependancy '[A] requires [B]'")
    print("v                           Display all dependancy graphs")
    print("v [A]                     Display dependancy graph of [A]")
    print("? [A] [B]                    Checks if '[A] requires [B]'")
    print("tm [A] <mm>            Sets due month of task [A] to <mm>")
    print("td [A] <dd>              Sets due day of task [A] to <dd>")
    print("ty [A] <yyyy>         Sets due year of task [A] to <yyyy>")
    print("tt [A] <hh>:<mn>   Sets due time of task [A] to <hh>:<mn>")

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
        displayall()
        return
    elif len(tokens) == 2:
        ref = tokens[1]
        if not ref in tasks.keys():
            print(f"Task [{ref}] does not exist!")
            return
        print(repr(tasks[ref]))
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


#Main
print("D-Task: Task dependancy organiser and todolist")
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
    elif command.startswith("?"):
        menu_questionmark(command)
    elif command.startswith("tT"):
        menu_tT(command)
    elif command.startswith("tm"):
        menu_tm(command)
    elif command.startswith("td"):
        menu_td(command)
    else:
        print("Command not found")
