import logging, socketserver, threading, os
from pynput.keyboard import Listener
from sys import exit
from util.tracker import UDPT, authUDPT
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
        self.AUTH = False

        self.s_sel = "\x1b[1;31m"
        self.e_sel = "\x1b[1;0m"
        self.d_host = self.HOST
        self.d_port = self.PORT
        self.d_auth = self.s_sel + "off" + self.e_sel

        self.CONT = f"""Start server on {self.s_sel+self.HOST}:{self.PORT+self.e_sel}?
↑ edit HOST : ↓ edit PORT : a toggle AUTH
(enter to Start : esc to Exit)"""
        self.d_cont = self.CONT

        self.running = False
        self.display()
        self.listener = Listener(on_press=self.handler)
        with self.listener as listener:
            listener.join()

    def handler(self, key):
        self.d_cont = self.CONT
        self.d_host = self.HOST
        self.d_port = self.PORT
        self.display()
        if self.make_string(key) not in [
            "Key.up",
            "Key.down",
            "a",
            "Key.enter",
            "Key.esc",
        ]:
            return

        if self.make_string(key) == "Key.up":
            self.select_host(key)
        elif self.make_string(key) == "Key.down":
            self.select_port(key)
        elif self.make_string(key) == "Key.esc":
            if not self.running:
                exit()
            else:
                self.stop()
        elif self.make_string(key) == "a":
            self.switch_auth()
        else:
            self.start()

    def display(self):
        os.system("cls")
        print(
            f"""✨ gon's UDPT server implementation ✨
        
        HOST: {self.d_host}
        PORT: {self.d_port}
        AUTH: {self.d_auth}
        
{self.d_cont}"""
        )

    def switch_auth(self):
        self.AUTH = not self.AUTH
        if self.AUTH:
            self.d_auth = self.s_sel + "on" + self.e_sel
        else:
            self.d_auth = self.s_sel + "off" + self.e_sel
        self.display()

    def select_host(self, key):
        self.d_port = self.PORT
        self.d_cont = self.CONT
        self.update_d_host()
        self.display()
        if self.make_string(key) not in [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "0",
            ".",
            "Key.backspace",
            "Key.enter",
            "Key.esc",
        ]:
            self.listener.on_press = self.select_host
            return

        if str(key) == "Key.backspace":
            self.HOST = self.HOST[:-1]
        elif str(key) == "Key.enter" or str(key) == "Key.esc":
            self.CONT = f"""Start server on {self.s_sel+self.HOST}:{self.PORT+self.e_sel}?
↑ edit HOST : ↓ edit PORT : a toggle AUTH
(enter to Start : esc to Exit)"""
            self.d_cont = self.CONT
            self.d_host = self.HOST
            self.display()
            self.listener.on_press = self.handler
            return
        else:
            self.HOST += self.make_string(key)

        self.update_d_host()
        self.display()

    def select_port(self, key):
        self.d_host = self.HOST
        self.d_cont = self.CONT
        self.update_d_port()
        self.display()
        if self.make_string(key) not in [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "0",
            "Key.backspace",
            "Key.enter",
            "Key.esc",
        ]:
            self.listener.on_press = self.select_port
            return

        if str(key) == "Key.backspace":
            self.PORT = self.PORT[:-1]
        elif str(key) == "Key.enter" or str(key) == "Key.esc":
            self.CONT = f"""Start server on {self.s_sel+self.HOST}:{self.PORT+self.e_sel}?
↑ edit HOST : ↓ edit PORT : a toggle AUTH
(enter to Start : esc to Exit)"""
            self.d_cont = self.CONT
            self.d_port = self.PORT
            self.display()
            self.listener.on_press = self.handler
            return
        else:
            self.PORT += self.make_string(key)

        self.update_d_port()
        self.display()

    def update_d_host(self):
        self.d_host = self.s_sel + self.HOST + self.e_sel
        self.CONT = f"Start server on {self.s_sel+self.HOST+self.e_sel}:{self.PORT}?\n(enter to Confirm : esc to Return)"
        self.d_cont = self.CONT

    def update_d_port(self):
        self.d_port = self.s_sel + self.PORT + self.e_sel
        self.CONT = f"Start server on {self.HOST}:{self.s_sel+self.PORT+self.e_sel}?\n(enter to Confirm : esc to Return)"
        self.d_cont = self.CONT

    def make_string(self, key) -> str:
        if len(str(key)) == 3:
            return str(key)[1]
        else:
            return str(key)

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

        if self.AUTH:
            HandlerClass = authUDPT
        else:
            HandlerClass = UDPT

        try:
            self.server = socketserver.UDPServer(
                (self.HOST, int(self.PORT)), HandlerClass
            )
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
            self.PORT = str(self.server.server_address[1])
            self.d_port = self.PORT
            self.d_host = self.HOST
            self.CONT = f"Server running on {self.s_sel+self.HOST}:{self.PORT+self.e_sel}.\n(esc to Stop)"
            self.d_cont = self.CONT
            self.running = True
            self.display()
        except Exception:
            self.CONT = f"{self.s_sel+self.HOST}:{self.PORT+self.e_sel} is an invalid address.\n(esc to Exit)"
            self.d_cont = self.CONT
            self.display()

    def stop(self):
        self.server.shutdown()
        self.running = False
        self.CONT = f"Start server on {self.s_sel+self.HOST}:{self.PORT+self.e_sel}?\n(esc to Exit)"
        self.d_cont = self.CONT
        self.display()


CLI()
