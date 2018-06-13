# ModuleManager
ModuleManager is a Python 3 curses program for managing modules for modular scripts/processes.  Currently only tested on Linux.

Provided with this utility is a directory with example modules (with no content).  This allows you to see how things are handled at a high level.  The examples use Bash, but you can use this utility with anything interpreted by changing the 'startcomment' variable to reflect how comments are started in your language of choice.

This utility expects a directory full of modules, named '##_name', where '##' implies the 'rank' of the module, or what order it should appear in the list.  If this is not included, it will be added the first time the utility saves the new order.

Modules that are found to be executable are assumed to be active modules.  Non-executable modules are inactive.  This is denoted by a '*' before the module entry in the list.

No unit testing currently exists because, frankly, I am still trying to determine how best to do so with curses.  If you have suggestions, feel free to let me know.

Dynamic terminal window resizing requires Python 3.5 or above.  This is because that is the earliest version implementing the 'update_lines\_cols()' function.  Previous versions will still function, but if the window is resized, the program will exit with a note about Python version requirements.

## Version history

*0.1* (June 13, 2018)

* Initial public release.

---

© 2018 Claude Devine.  ModuleManager is released under the MIT license.  See `LICENSE` for details.
