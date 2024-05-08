# import all the required modules
import threading
import select
from tkinter import *
from tkinter import Tk, Toplevel, Label, Entry, Text, Button, font
from chat_utils import *
import json

# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self, send, recv, sm, s):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""
        self.setup_fonts()
        self.setup_colors()
        self.users = {}
        
    def setup_fonts(self):
        self.base_font = font.Font(family="Helvetica", size=16)
        self.header_font = font.Font(family="Helvetica", size=20, weight="bold")

    def setup_colors(self):
        self.bg_color = "#FFFFFF" # White for background
        self.fg_color = "#333333" # Dark grey for text
        self.button_color = "#4CAF50" # Green for buttons
        self.entry_bg_color = "#F0F0F0" # Light grey for entry fields

    def verify_login(self, username, password):
        # Simple verification against the local dictionary
        return self.users.get(username) == hash_password(password)

    def register_user(self, username, password):
        # Add user to the dictionary
        if username in self.users:
            return False
        self.users[username] = hash_password(password)
        return True

    def login(self):
        # Login Window
        self.login = Toplevel()

        # Title
        self.login.title("Login")
        self.login.resizable(width = False, height = False)
        self.login.geometry("400x400")
        self.login.configure(bg = self.bg_color)
        
        # Instruction Label
        Label(self.login, text = "Please Login to Continue", font = self.header_font, fg = self.fg_color, bg = self.bg_color).pack(pady=(20, 10))
        
        # Username Label
        Label(self.login, text = "Enter Username", font = self.base_font, fg = self.fg_color, bg = self.bg_color).pack()
          
        # Username Entry
        self.entryName = Entry(self.login, font = self.base_font, fg = self.fg_color, bg = self.entry_bg_color)
        self.entryName.pack(ipadx=20, ipady=5, pady=(0, 20))

        # Password Label
        Label(self.login, text = "Enter Password", font = self.base_font, fg = self.fg_color, bg = self.bg_color).pack()

        # Password Entry
        self.entryPassword = Entry(self.login, font = self.base_font, fg = self.fg_color, bg = self.entry_bg_color)
        self.entryPassword.pack(ipadx=20, ipady=5, pady=(0, 20))
         
        # Login Button
        Button(self.login, text = "LOGIN", font = self.base_font, fg = self.fg_color, bg = self.button_color, 
               command = lambda: self.goAhead(self.entryName.get(), self.entryPassword.get())).pack(pady=(0, 20))
         
        # Register Button
        Button(self.login, text="REGISTER", font=self.base_font, fg=self.fg_color, bg=self.button_color, 
               command=lambda: self.handle_registration(self.entryName.get(), self.entryPassword.get())).pack(pady=(0, 20))
        
        self.Window.mainloop()
    
    def handle_registration(self, username, password):
        if len(username) > 0 and len(password) > 0:
            if self.register_user(username, password):
                self.popup("Registration successful!")
            else:
                self.popup("Username already exists...")

    def popup(self, msg):
        popup = Toplevel()
        popup.title("ATTENTION")
        popup.geometry("200x100")
        popup.configure(bg = self.bg_color)
        Label(popup, text = msg, font = self.base_font, fg = self.fg_color, bg = self.bg_color).pack(pady=(20, 10))
        Button(popup, text = "OK", font = self.base_font, fg = self.fg_color, bg = self.button_color, command = popup.destroy).pack(pady=(0, 20))

    def goAhead(self, name, password):
        if len(name) > 0:
            if self.verify_login(name, password):
                try:
                    msg = json.dumps({"action":"login", "name": name})
                    self.send(msg)
                    response = json.loads(self.recv())
                    if response["status"] == 'ok':
                        self.login.destroy()
                        self.sm.set_state(S_LOGGEDIN)
                        self.sm.set_myname(name)
                        self.layout(name)
                        self.textCons.config(state = NORMAL)
                        self.textCons.insert(END, f"{menu}\n\n")
                        self.textCons.config(state = DISABLED)
                        self.textCons.see(END)

                except Exception as e:
                    print(f"Erorr: {e}")

                threading.Thread(target=self.proc, daemon=True).start()
            
            else:
                self.popup("Invalid credentials!")

    def layout(self,name):
        self.name = name
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False, height=False)
        self.Window.geometry('600x600')
        self.Window.configure(bg=self.bg_color)

        self.labelHead = Label(self.Window, bg=self.bg_color, fg=self.fg_color, text=self.name, font=self.header_font, pady=5)
        self.labelHead.pack(fill='x')

        self.textCons = Text(self.Window, width=20, height=2, bg=self.entry_bg_color, fg=self.fg_color, font=self.base_font, padx=5, pady=5)
        self.textCons.pack(expand=True, fill=BOTH, padx=10, pady=10)
        
        self.labelBottom = Label(self.Window, bg = self.bg_color, height = 100)
        self.labelBottom.pack(fill='x')
        
        self.entryMsg = Entry(self.labelBottom, bg=self.entry_bg_color, fg = self.fg_color, font = self.base_font)
        self.entryMsg.pack(side=LEFT, fill='x', expand=True, padx=10, pady=10)
        self.entryMsg.focus()

        self.entryMsg.bind("<Return>", lambda x: self.sendButton(self.entryMsg.get()))

        self.buttonMsg = Button(self.labelBottom, text = "Send", font = self.base_font, bg=self.button_color, fg=self.fg_color,
                                command = lambda : self.sendButton(self.entryMsg.get()))
        self.buttonMsg.pack(side=RIGHT, padx=10, pady=10)

        scrollbar = Scrollbar(self.textCons)
        scrollbar.pack(side=RIGHT, fill='y')
        self.textCons.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.textCons.yview)
        self.textCons.config(state = DISABLED)
  
    def sendButton(self, msg):
        self.textCons.config(state = DISABLED)
        self.my_msg = msg
        self.entryMsg.delete(0, END)

    def proc(self):
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            if self.socket in read:
                peer_msg = self.recv()

            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                self.system_msg += self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""
                self.textCons.config(state = NORMAL)
                self.textCons.insert(END, self.system_msg +"\n\n")      
                self.textCons.config(state = DISABLED)
                self.textCons.see(END)

    def run(self):
        self.login()