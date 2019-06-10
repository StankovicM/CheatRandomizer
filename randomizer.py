from threading import Thread, Event
import os, time, ctypes, random, msvcrt
from ctypes.wintypes import WORD, DWORD, LONG, WPARAM, UINT
user32 = ctypes.WinDLL('user32', use_last_error=True)

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

ULONG_PTR = WPARAM

VKEYS = {
    'a':0x41,
    'b':0x42,
    'c':0x43,
    'd':0x44,
    'e':0x45,
    'f':0x46,
    'g':0x47,
    'h':0x48,
    'i':0x49,
    'j':0x4A,
    'k':0x4B,
    'l':0x4C,
    'm':0x4D,
    'n':0x4E,
    'o':0x4F,
    'p':0x50,
    'q':0x51,
    'r':0x52,
    's':0x53,
    't':0x54,
    'u':0x55,
    'v':0x56,
    'w':0x57,
    'x':0x58,
    'y':0x59,
    'z':0x5A
}

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          LONG),
                ("dy",          LONG),
                ("mouseData",   DWORD),
                ("dwFlags",     DWORD),
                ("time",        DWORD),
                ("dwExtraInfo", ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         WORD),
                ("wScan",       WORD),
                ("dwFlags",     DWORD),
                ("time",        DWORD),
                ("dwExtraInfo", ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    DWORD),
                ("wParamL", WORD),
                ("wParamH", WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))

    _anonymous_ = ("_input",)
    _fields_ = (("type",   DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (UINT,
                             LPINPUT,
                             ctypes.c_int)

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

delay = 0.04
cheat_time = 10
stacking = True
cheats = dict()
total_cost = 0
total_cheats = 0

class Exec(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global total_cheats, total_cost
        print('Starting the script, press ESC to stop it.')
        passed_time = 0
        last_time = time.time()
        last_cheat = ''
        while True:
            now = time.time()
            passed_time += now - last_time
            last_time = now

            if passed_time >= cheat_time:
                cheat = random.choice(cheats.keys()).lower()
                total_cost += int(cheats[cheat][1])
                total_cheats += 1

                if not stacking:
                    for i in range(len(last_cheat)):
                        PressKey(VKEYS[last_cheat[i]])
                        time.sleep(delay)
                        ReleaseKey(VKEYS[last_cheat[i]])
                        time.sleep(delay)

                for i in range(len(cheat)):
                    PressKey(VKEYS[cheat[i]])
                    time.sleep(delay)
                    ReleaseKey(VKEYS[cheat[i]])
                    time.sleep(delay)

                print('{0: <30} activated! {1}.'.format(cheat.upper(), cheats[cheat][0]))
                last_cheat = cheat
                passed_time = 0
            else:
                if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode():
                    break
                    
                time.sleep(0.05)

        return

if __name__ == '__main__':
    with open('cheats.txt', 'r') as f:
        for line in f:
            args = str(line).split(';')
            cheats[args[0].lower()] = (args[1], args[2])

    cheat_time = -1
    while cheat_time < 0:
        try:
            cheat_time = int(raw_input('Time between each cheat: '))
            if cheat_time < 0:
                print('Time must be greater than 0 seconds.')
        except ValueError:
            print('Time must be a number.')
    
    print('Time set to {0} seconds.'.format(cheat_time))

    s = ''
    while s not in ('n', 'y', 'N', 'Y'):
        s = raw_input('Stacking (y/n): ')

    if s in ('n', 'N'):
        stacking = False

    if stacking:
        print('Stacking enabled.')
    else:
        print('Stacking disabled.')

    exec_thread = Exec()
    exec_thread.start()
    exec_thread.join()

    print('Script stopped.')
    print('Total number of cheats used is {0}.'.format(total_cheats))
    print('Total cost of the cheats used is {0} duckets.'.format(total_cost))
