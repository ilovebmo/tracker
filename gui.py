import logging, socketserver, threading
import tkinter as tk
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
# Tkinter GUI
#


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("gon's UDPT server implementation")
        self.root.resizable(width=False, height=False)
        self.root.iconbitmap(lib.resource_path("util/icon.ico"))

        # Mainframe setup
        self.mainframe = tk.Frame(self.root)
        self.mainframe.grid(column=0, row=0, sticky="nwes")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # User input for HOST
        self.HOST = tk.StringVar()
        self.HOST.set(lib.gethost())
        self.get_HOST = tk.Entry(self.mainframe, textvariable=self.HOST, width=30)
        self.get_HOST.grid(column=1, row=0, sticky="nswe")
        tk.Label(self.mainframe, text="HOST").grid(column=0, row=0, sticky="nswe")

        # User input for PORT
        self.PORT = tk.StringVar()
        self.PORT.set(str(0))
        self.get_PORT = tk.Entry(self.mainframe, textvariable=self.PORT)
        self.get_PORT.grid(column=1, row=1, sticky="nswe")
        tk.Label(self.mainframe, text="PORT").grid(column=0, row=1, sticky="nswe")
        
        # Input for Auth
        self.AUTH = tk.IntVar()
        tk.Checkbutton(self.mainframe, text="AUTH", variable=self.AUTH).grid(column=0, row=2)

        # Button to start server
        self.start_button = tk.Button(
            self.mainframe, text="Start", command=self.get_HOST_PORT
        )
        self.start_button.grid(column=1, row=2, sticky="nsew")

        # Info Label for server
        self.info = tk.Label(
            self.mainframe,
            text="Server is not running.\nPORT will be assigned.",
            justify="left",
            anchor="w",
        )
        self.info.grid(columnspan=2, row=3, sticky="nsew")

        # Bind so that you don't actually need to click the button to start the server
        self.root.bind("<Return>", self.get_HOST_PORT)
        self.root.mainloop()

    def stop_server(self, *event: tk.Event):
        self.server.shutdown()
        self.info.configure(text="Server is not not running.\nLogging: logging.log")
        self.start_button.configure(text="Start", command=self.get_HOST_PORT)
        self.get_HOST.configure(state=tk.NORMAL)
        self.get_PORT.configure(state=tk.NORMAL)

    def get_HOST_PORT(self, *event: tk.Event):
        # Get the PORT
        PORT_NU = self.PORT.get()
        try:
            if int(PORT_NU) > 65535:
                PORT_NU = 1212
                self.PORT.set(1212)
        except ValueError:
            PORT_NU = 1212
            self.PORT.set(1212)
        PORT_NU = int(PORT_NU)

        # Get the HOST
        HOST_IP = self.HOST.get()
        # Checks if it's in the form of IPV4
        if len(HOST_IP.split(".")) != 4:
            HOST_IP = lib.gethost()
            self.HOST.set(HOST_IP)
        # Checks if it's a valid IPV4
        try:
            for n in HOST_IP.split("."):
                int(n)
        except ValueError:
            HOST_IP = lib.gethost()
            self.HOST.set(HOST_IP)

        if self.AUTH.get():
            HandlerClass = authUDPT
        else:
            HandlerClass = UDPT
        
        # Starts the server
        try:
            self.server = socketserver.UDPServer((HOST_IP, PORT_NU), HandlerClass)
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
        except Exception:
            self.info.configure(text="Server couldn't start.\nPORTs can't be reused.")
            return

        # Unbinds the starting server input
        self.start_button.configure(command=self.stop_server, text="Stop")

        self.get_HOST.configure(state=tk.DISABLED)
        self.get_PORT.configure(state=tk.DISABLED)

        # Updates the information about the server
        self.info.configure(
            text=f"{HOST_IP}:{self.server.server_address[1]}\nLogging: logging.log"
        )
        self.PORT.set(self.server.server_address[1])


GUI()
