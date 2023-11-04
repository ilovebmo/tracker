import logging, socketserver, threading, keyboard, os
from sys import exit
from util.tracker import UDPT
import util.lib as lib

#
#
#
# Logging setup
#

# Logging to logging.log
logging.basicConfig(filename="logging.log", encoding="utf-8", level=logging.INFO)


#
#
#
# Basic CLI
#

class CLI:
    def __init__(self):
        os.system("title " + "gon's UDPT server implementation")
        os.system("\x1b[?25l")
        
        self.HOST = lib.gethost()
        self.PORT = str(0)
        
        self.s_sel = "\x1b[1;31m"
        self.e_sel = "\x1b[1;0m"
        self.d_host = self.HOST
        self.d_port = self.PORT
        
        self.CONT = f"""Start server on {self.s_sel+self.HOST}:{self.PORT+self.e_sel}?
↑ edit HOST : ↓ edit PORT
(enter to Start : esc to Exit)"""
        self.d_cont = self.CONT
        
        self.running = False
        self.handler()
    
    def handler(self):
        self.d_cont = self.CONT
        self.d_host = self.HOST
        self.d_port = self.PORT
        self.display()
        while True:
            event = keyboard.read_event(suppress=True)
            if event.event_type != keyboard.KEY_DOWN:
                continue
            if event.name not in ["up", "down", "enter", "esc"]:
                continue
            
            if event.name == "up":
                self.select_host()
            elif event.name == "down":
                self.select_port()
            elif event.name == "esc":
                if not self.running:
                    exit()
                else:
                    self.stop()
            else:
                self.start()

    def display(self):
        os.system("cls")
        print(f"""✨ gon's UDPT server implementation ✨
        
        HOST: {self.d_host}
        PORT: {self.d_port}
        
{self.d_cont}""")
        
    def select_host(self):
        self.d_port = self.PORT
        self.d_cont = self.CONT
        self.update_d_host()
        self.display()
        while True:
            event = keyboard.read_event(suppress=True)
            if event.event_type != keyboard.KEY_DOWN:
                continue
            if event.name not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "backspace", "enter", "esc"]:
                continue
            
            if event.name == "backspace":
                self.HOST = self.HOST[:-1]
            elif event.name == "enter" or event.name == "esc":
                self.CONT = f"""Start server on {self.s_sel+self.HOST}:{self.PORT+self.e_sel}?
↑ edit HOST : ↓ edit PORT
(enter to Start : esc to Exit)"""
                self.d_cont = self.CONT
                self.display()
                break
            else:
                self.HOST += event.name
            
            self.update_d_host()
            self.display()

        self.handler()
    
    def select_port(self):
        self.d_host = self.HOST
        self.d_cont = self.CONT
        self.update_d_port()
        self.display()
        while True:
            event = keyboard.read_event(suppress=True)
            if event.event_type != keyboard.KEY_DOWN:
                continue
            if event.name not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "backspace", "enter", "esc"]:
                continue
            
            if event.name == "backspace":
                self.PORT = self.PORT[:-1]
            elif event.name == "enter" or event.name == "esc":
                self.CONT = f"""Start server on {self.s_sel+self.HOST}:{self.PORT+self.e_sel}?
↑ edit HOST : ↓ edit PORT
(enter to Start : esc to Exit)"""
                self.d_cont = self.CONT
                self.display()
                break
            else:
                self.PORT += event.name
            
            self.update_d_port()
            self.display()

        self.handler()
        
    def update_d_host(self):
        self.d_host = self.s_sel+self.HOST+self.e_sel
        self.CONT = f"Start server on {self.s_sel+self.HOST+self.e_sel}:{self.PORT}?\n(enter to Confirm : esc to Return)"
        self.d_cont = self.CONT
        
    def update_d_port(self):
        self.d_port = self.s_sel+self.PORT+self.e_sel
        self.CONT = f"Start server on {self.HOST}:{self.s_sel+self.PORT+self.e_sel}?\n(enter to Confirm : esc to Return)"
        self.d_cont = self.CONT
    
    def start(self):
        try:
            if int(self.PORT) > 65535:
                self.PORT = "1212"
        except ValueError:
            self.PORT = "1212"
            
        if len(self.HOST.split(".")) != 4:
            self.HOST = lib.gethost()
        try:
            for n in self.HOST.split("."):
                int(n)
        except ValueError:
            self.HOST = lib.gethost()
        
        try:
            self.server = socketserver.UDPServer((self.HOST, int(self.PORT)), UDPT)
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
            self.PORT = str(self.server.server_address[1])
            self.d_port = self.PORT
            self.d_host = self.HOST
            self.CONT = f"Server running on {self.s_sel+self.HOST}:{self.PORT+self.e_sel}.\n(esc to Stop)"
            self.d_cont = self.CONT
            self.running = True
            self.display()
        except Exception:
            self.CONT = f"{self.s_sel+self.HOST}:{self.PORT+self.e_sel} is an invalid address.\n(esc to exit)"
            self.d_cont = self.CONT
            self.display()
            
    def stop(self):
        self.server.shutdown()
        self.running = False
        self.CONT = f"Start server on {self.s_sel+self.HOST}:{self.PORT+self.e_sel}?\n(esc to exit)"
        self.d_cont = self.CONT
        self.display()
        
        
CLI()
        