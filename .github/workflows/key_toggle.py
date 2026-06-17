import tkinter as tk
from pynput.keyboard import Key, Controller, KeyCode
import threading

keyboard = Controller()

HELD_KEYS = {}
HELD_LOCK = threading.Lock()

KEY_LAYOUT = [
    ['`','1','2','3','4','5','6','7','8','9','0','-','=','Bksp'],
    ['Tab','Q','W','E','R','T','Y','U','I','O','P','[',']','\\'],
    ['Caps','A','S','D','F','G','H','J','K','L',';',"'",'Enter'],
    ['Shift','Z','X','C','V','B','N','M',',','.','/','RShift'],
    ['Ctrl','Alt','Win','Space','RAlt','RCtrl'],
]

WIDE_KEYS  = {'Tab','Caps','Enter','Bksp','Shift','RShift'}
WIDER_KEYS = {'Ctrl','Alt','Win','RAlt','RCtrl'}
WIDEST_KEY = 'Space'

PYNPUT_MAP = {
    'Bksp':   Key.backspace,
    'Tab':    Key.tab,
    'Caps':   Key.caps_lock,
    'Enter':  Key.enter,
    'Shift':  Key.shift,
    'RShift': Key.shift_r,
    'Ctrl':   Key.ctrl_l,
    'RCtrl':  Key.ctrl_r,
    'Alt':    Key.alt_l,
    'RAlt':   Key.alt_r,
    'Win':    Key.cmd,
    'Space':  Key.space,
    '`':      KeyCode.from_char('`'),
    '-':      KeyCode.from_char('-'),
    '=':      KeyCode.from_char('='),
    '[':      KeyCode.from_char('['),
    ']':      KeyCode.from_char(']'),
    '\\':     KeyCode.from_char('\\'),
    ';':      KeyCode.from_char(';'),
    "'":      KeyCode.from_char("'"),
    ',':      KeyCode.from_char(','),
    '.':      KeyCode.from_char('.'),
    '/':      KeyCode.from_char('/'),
}

def get_pynput_key(label):
    if label in PYNPUT_MAP:
        return PYNPUT_MAP[label]
    return KeyCode.from_char(label.lower())

BG         = '#1e1e1e'
KEY_BG     = '#2d2d2d'
KEY_FG     = '#e0e0e0'
KEY_ON_BG  = '#2563eb'
KEY_ON_FG  = '#ffffff'
BORDER_OFF = '#444444'
BORDER_ON  = '#3b82f6'
ACTIVE_BG  = '#111111'
FONT_KEY   = ('Segoe UI', 10, 'bold')
FONT_SMALL = ('Segoe UI', 9)

class KeyToggleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Key Toggle')
        self.configure(bg=BG)
        self.resizable(False, False)
        self.buttons = {}
        self._build_ui()

    def _build_ui(self):
        # Title bar
        title = tk.Label(self, text='Key Toggle', bg=BG, fg='#888888',
                         font=('Segoe UI', 11), pady=8)
        title.pack()

        # Active keys display
        self.active_frame = tk.Frame(self, bg=ACTIVE_BG, pady=6, padx=8)
        self.active_frame.pack(fill='x', padx=12, pady=(0, 8))
        self.active_label = tk.Label(self.active_frame, text='No keys toggled',
                                     bg=ACTIVE_BG, fg='#666666', font=FONT_SMALL)
        self.active_label.pack()

        # Keyboard rows
        kb_frame = tk.Frame(self, bg=BG, padx=12, pady=4)
        kb_frame.pack()

        for row in KEY_LAYOUT:
            row_frame = tk.Frame(kb_frame, bg=BG)
            row_frame.pack(pady=3)
            for label in row:
                if label == WIDEST_KEY:
                    w = 14
                elif label in WIDER_KEYS:
                    w = 6
                elif label in WIDE_KEYS:
                    w = 7
                else:
                    w = 4

                btn = tk.Button(
                    row_frame, text=label, width=w, height=1,
                    bg=KEY_BG, fg=KEY_FG, activebackground=KEY_ON_BG,
                    activeforeground=KEY_ON_FG, font=FONT_KEY,
                    relief='flat', bd=0, cursor='hand2',
                    highlightthickness=1, highlightbackground=BORDER_OFF,
                )
                btn.pack(side='left', padx=2)
                btn.bind('<Button-1>', lambda e, l=label: self.toggle_key(l))
                self.buttons[label] = btn

        # Clear all button
        clear_btn = tk.Button(self, text='Clear All', bg='#3a1a1a', fg='#ff6b6b',
                              activebackground='#5a2a2a', activeforeground='#ff9999',
                              font=FONT_SMALL, relief='flat', bd=0,
                              cursor='hand2', pady=6, padx=16,
                              command=self.clear_all)
        clear_btn.pack(pady=(4, 12))

        # Warning label
        warn = tk.Label(self, text='⚠  Toggled keys are held down system-wide',
                        bg=BG, fg='#666666', font=('Segoe UI', 8))
        warn.pack(pady=(0, 8))

    def toggle_key(self, label):
        with HELD_LOCK:
            if label in HELD_KEYS:
                pkey = HELD_KEYS.pop(label)
                keyboard.release(pkey)
                btn = self.buttons[label]
                btn.configure(bg=KEY_BG, fg=KEY_FG,
                              highlightbackground=BORDER_OFF)
            else:
                pkey = get_pynput_key(label)
                keyboard.press(pkey)
                HELD_KEYS[label] = pkey
                btn = self.buttons[label]
                btn.configure(bg=KEY_ON_BG, fg=KEY_ON_FG,
                              highlightbackground=BORDER_ON)
        self._update_active_label()

    def clear_all(self):
        with HELD_LOCK:
            for label, pkey in list(HELD_KEYS.items()):
                keyboard.release(pkey)
                self.buttons[label].configure(bg=KEY_BG, fg=KEY_FG,
                                              highlightbackground=BORDER_OFF)
            HELD_KEYS.clear()
        self._update_active_label()

    def _update_active_label(self):
        with HELD_LOCK:
            keys = list(HELD_KEYS.keys())
        if keys:
            self.active_label.configure(
                text='Held: ' + '  +  '.join(keys), fg='#60a5fa')
        else:
            self.active_label.configure(text='No keys toggled', fg='#666666')

    def destroy(self):
        self.clear_all()
        super().destroy()

if __name__ == '__main__':
    app = KeyToggleApp()
    app.mainloop()
