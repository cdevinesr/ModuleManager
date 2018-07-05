import curses, os, sys, subprocess

####################
# Global Variables #
####################

# Name of this utility
name = "Module Manager"

# Version number
version = "0.1"

# Instructions for use
instructions = ["Up/Dn = Move, Right = Select for reordering", "Left/Enter = Commit new position, Space = Toggle enabled/disabled"]

# Instructions below the module display box
instructions2 = "Press 'Q' to quit"

# Quit Message
quitmsg = "Save changes? (Y)es/(N)o/(C)ancel"

# Module directory
moddir = "modules.d"

# Begin-comment character(s)
startcomment = "#"

# Number of rows in module display box.
rowct = 15

# Max length of module lines in module display box
maxmodlen = 60

# Left padding on module entries
modleftpad = 5

# Width of module display box (mostly to account for border)
menuwidth = maxmodlen + 2

################################
# Class / Function Definitions #
################################

class Module:
    def __init__(self, name, active, filename):
        self.name = str(name)
        self.active = bool(active)

        try:
            self.rank, self.filename = filename.split("_")
            self.rank = self.rank.zfill(2)
        except ValueError:
            self.rank = ""
            self.filename = filename

    def __str__(self):
        upperbound = (maxmodlen - modleftpad) - 1
        isactive = "* " if self.active else "  "
        output = isactive + str(self.name)

        if len(output) > upperbound:
            output = output[:upperbound - 3] + "..."

        return output

    def toggle_active(self):
        self.active = not self.active

    def set_rank(self, rank):
        self.rank = str(rank).zfill(2)

class ModuleList(list):
    def move_up(self, index):
        if index == 0:
            return False

        tmp = self[index - 1]
        self[index - 1] = self[index]
        self[index] = tmp
        return True

    def move_down(self, index):
        if index == len(self) - 1:
            return False

        tmp = self[index + 1]
        self[index + 1] = self[index]
        self[index] = tmp
        return True

def fail_cleanly(message):
        curses.endwin()
        os.system('clear')
        print("FATAL: " + str(message))
        sys.exit(1)

def draw_header(screen):
    header = " {!s} v{!s} ".format(name, version)
    hdrlen = len(header)

    if hdrlen > curses.COLS:
        fail_cleanly("Current terminal window too narrow to display header.  Please make the terminal window larger.")

    start = (curses.COLS - hdrlen) // 2
    screen.addstr(0, start, header, headerText)

def draw_screen(screen, modules):
    global oldposition, oldstartpos, instr2_y
    screen.clear()
    curses.curs_set(0)
    screen.border()
    draw_header(screen)
    menuwin.mvwin((curses.LINES - (rowct + 2)) // 2, (curses.COLS - menuwidth) // 2)
    instr_y = menuwin.getbegyx()[0] - len(instructions) - 1

    if instr_y <= 1:
        fail_cleanly("Current terminal window too short to draw instructions.  Please make the terminal window larger.")

    for line in instructions:
        if len(line) > curses.COLS:
            fail_cleanly("Current terminal window is too narrow to display instructions.  Please make the terminal window larger.")

        screen.addstr(instr_y, (curses.COLS - len(line)) // 2, line)
        instr_y += 1

    instr2_y = menuwin.getbegyx()[0] + menuwin.getmaxyx()[0] + 1
    screen.addstr(instr2_y, (curses.COLS - len(instructions2)) // 2, instructions2)

    menuwin.border()
    mwbegy, mwbegx = menuwin.getbegyx()
    mwendy, mwendx = menuwin.getmaxyx()
    mwendy += mwbegy
    mwendx += mwbegx
    fill_module_pad(modules)
    screen.noutrefresh()
    menuwin.noutrefresh()

    if oldstartpos == -2:
        startpos = 0
    elif oldstartpos == -1:
        startpos = len(modules) - rowct
    else:
        startpos = oldstartpos

        if position > oldposition:
            if position - startpos > rowct - 1:
                startpos = oldstartpos + 1
        elif position == 0:
            startpos = 0
        else:
            if position < oldstartpos:
                startpos = oldstartpos - 1
            else:
                startpos = oldstartpos

    modulepad.noutrefresh(startpos, 0, mwbegy + 1, mwbegx + 1, mwendy - 2, mwendx - 2)
    curses.doupdate()
    oldstartpos = startpos
    oldposition = position

def fill_module_pad(modules):
    pady = 0

    for module in modules:
        if pady == position:
            if active_selection:
                modulepad.addstr(pady, modleftpad, str(module), selected)
            else:
                modulepad.addstr(pady, modleftpad, str(module), highlighted)
        else:
            modulepad.addstr(pady, modleftpad, str(module), default)

        pady += 1

def process_quit(screen):
    retval = None

    while True:
        keypress = screen.getch()

        if keypress == ord('y') or keypress == ord('Y'):
            return True
        elif keypress == ord('n') or keypress == ord('N'):
            return False
        elif keypress == ord('c') or keypress == ord('C'):
            return None
        elif keypress == curses.KEY_RESIZE:
            if sys.version_info[1] < 5:
                fail_cleanly("Dynamic resizing requires Python 3.5 or later.")
            else:
                curses.update_lines_cols()
def move_modules(modules):
    newrank = 1

    for module in modules:
        oldrank = module.rank + "_" if module.rank else ""

        if not module.active:
            module.set_rank(99)
        else:
            module.set_rank(newrank)
            newrank += 1

        try:
            os.rename("{!s}/{!s}{!s}".format(moddir, oldrank, module.filename), "{!s}/{!s}_{!s}".format(moddir, module.rank, module.filename))

            if not module.active:
                os.chmod("{!s}/{!s}_{!s}".format(moddir, module.rank, module.filename), 0o644)
            else:
                os.chmod("{!s}/{!s}_{!s}".format(moddir, module.rank, module.filename), 0o744)
        except:
           # TODO: Implement handler when logging is implemented
           pass

def main(screen):
    if curses.COLS < menuwidth:
        fail_cleanly("Current terminal window too narrow to display menu.  Please make the terminal window larger.")

    global default, headerText, highlighted, selected, menuwin, modulepad, position, active_selection, oldstartpos, oldposition, instr2_y
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
    default = curses.A_NORMAL
    headerText = curses.color_pair(1)
    highlighted = curses.color_pair(2)
    selected = curses.color_pair(3)
    menuwin = curses.newwin(rowct + 2, menuwidth, (curses.LINES - (rowct + 2)) // 2, (curses.COLS - menuwidth) // 2)
    modules = ModuleList()

    for modfile in os.listdir(moddir):
        if not os.path.isfile("{!s}/{!s}".format(moddir, modfile)):
            continue

        active = bool(os.access("{!s}/{!s}".format(moddir, modfile), os.X_OK))

        try:
            name = subprocess.check_output("grep -Po '(?<={!s} TITLE: ).+' {!s}/{!s}".format(startcomment, moddir, modfile), shell=True)
            name = name.decode()
        except subprocess.CalledProcessError:
            try:
                modname = modfile.split("_")[1]
            except IndexError:
                modname = modfile

            name = "! Undefined ! ({!s})".format(modname)

        modules.append(Module(name, active, modfile))

    modules = ModuleList(sorted(modules, key=lambda x: x.rank))
    position = 0
    oldposition = 0
    oldstartpos = 0
    active_selection = False
    modulepad = curses.newpad(len(modules) + 1, menuwidth - 2)

    while True:
        modct = len(modules)
        draw_screen(screen, modules)
        keypress = screen.getch()

        if keypress == ord('q') or keypress == ord('Q'):
            if active_selection:
                continue

            screen.addstr(instr2_y + 2, (curses.COLS - len(quitmsg)) // 2, quitmsg)

            doquit = process_quit(screen)
            if doquit is None:
                continue
            else:
                if doquit:
                    move_modules(modules)
                    pass
                break
        elif keypress == ord(" "):
            if active_selection:
                continue

            modules[position].toggle_active()
        elif keypress == curses.KEY_RIGHT:
            active_selection = True
        elif keypress == curses.KEY_LEFT or keypress == curses.KEY_ENTER or keypress == 10 or keypress == 13:
            active_selection = False
        elif keypress == curses.KEY_DOWN:
            if position < modct - 1:
                if active_selection:
                    if modules.move_down(position):
                        position += 1
                else:
                    position += 1
        elif keypress == curses.KEY_UP:
            if position > 0:
                if active_selection:
                    if modules.move_up(position):
                        position -= 1
                else:
                    position -= 1
        elif keypress == curses.KEY_PPAGE:
            if position <= rowct:
                position = 0
                oldstartpos = -2
            else:
                if position > oldstartpos:
                    position = oldstartpos
                else:
                    oldstartpos -= rowct
                    position = oldstartpos
        elif keypress == curses.KEY_NPAGE:
            if position + rowct > modct - 1:
                position = modct - 1
            else:
                if oldstartpos + rowct > modct - rowct:
                    oldstartpos = modct - rowct
                    position = modct - 1
                else:
                    oldstartpos += rowct
                    position += rowct
        elif keypress == curses.KEY_HOME:
            if active_selection:
                while modules.move_up(position):
                    position -= 1
            position = 0
            oldstartpos = -2
        elif keypress == curses.KEY_END:
            if active_selection:
                while modules.move_down(position):
                    position += 1
            oldstartpos = -1
            position = modct - 1
        elif keypress == curses.KEY_RESIZE:
            if sys.version_info[1] < 5:
                fail_cleanly("Dynamic resizing requires Python 3.5 or later.")
            else:
                curses.update_lines_cols()

########
# MAIN #
########

if sys.version_info[0] < 3:
    print("FATAL: This utility requires Python 3.")
    sys.exit(1)

if not os.path.isdir(moddir):
    print("FATAL: Invalid directory specified for modules.")
    sys.exit(1)

curses.wrapper(main)
os.system('clear')
sys.exit(0)
