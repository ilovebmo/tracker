import threading, socketserver, lib, logging, meipass_get
import tkinter as tk
from socket import gethostbyname, gethostname
from ctypes import c_int32


logging.basicConfig(filename='logging.log', encoding='utf-8', level=logging.INFO)
connections = []
torrents = {}


class UDPT(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]

        if data[:12] == lib.protocol_id + lib.connect:
            self.connect(data, socket)
            return

        if data[:8] in connections:
            if data[8:12] == lib.announce:
                self.announce(data, socket)
                return
            else:
                socket.sendto(
                    lib.stopped + data[12:16] + b"No scraping!", self.client_address
                )
                logging.warn(" {self.client_address[0]}:{self.client_address[1]} tried to scrape.\n")

    def connect(self, data: bytes, socket: socketserver.socket):
        cid = lib.connection_id()
        connections.append(cid)
        socket.sendto(data[8:] + cid, self.client_address)

    def announce(self, data: bytes, socket: socketserver.socket):
        peer = lib.Peer(
            data[16:36],
            data[36:56],
            data[56:64],
            data[64:72],
            data[72:80],
            data[80:84],
            data[84:88],
            data[88:92],
            data[92:96],
            data[96:98],
            data[98:],
        )

        print(
            f"{self.client_address[0]}:{self.client_address[1]} has {lib.event[peer.event]}.\n"
        )
        logging.info(f" {self.client_address[0]}:{self.client_address[1]} has {lib.event[peer.event]}.\n")

        if peer.IP == lib.zero_32:
            peer.IP = lib.ip_32(self.client_address[0])

        if data[16:36] in torrents.keys():
            if peer.peer_id in torrents[data[16:36]].keys():
                torrents[data[16:36]][peer.peer_id] = peer
        else:
            torrents.update({data[16:36]: {peer.peer_id: peer}})

        msg = data[8:16] + lib.interval + self.leechers(data) + self.seeders(data)
        for p in torrents[data[16:36]].values():
            msg += p.IP + p.port

        socket.sendto(msg, self.client_address)

    def leechers(self, data: bytes):
        _leech = 0
        for p in torrents[data[16:36]].values():
            if p.left != lib.zero:
                _leech += 1

        return lib.rev_b(c_int32(_leech))

    def seeders(self, data: bytes):
        _seed = 0
        for p in torrents[data[16:36]].values():
            if p.left == lib.zero:
                _seed += 1

        return lib.rev_b(c_int32(_seed))


def gethost() -> str:
    return gethostbyname(gethostname())


def UDPTstart(HOST: str = gethost(), PORT: int = 1212):
    with socketserver.UDPServer((HOST, PORT), UDPT) as server:
        server.serve_forever()


def get_HOST_PORT(*event: tk.Event):
    HOST_IP = HOST.get()
    try:
        PORT_NU = int(PORT.get())
    except ValueError:
        PORT_NU = 1212

    if len(HOST_IP.split(".")) != 4:
        HOST_IP = gethost()

    try:
        for n in HOST_IP.split("."):
            int(n)
    except ValueError:
        HOST_IP = gethost()

    root.unbind("<Return>")
    start_button.destroy()
    stop_notice.grid(columnspan=2, row=2, sticky="nsew")
    info.configure(text=f"HOST: {HOST_IP}\nPORT: {PORT_NU}\nLogging: logging.log")

    server_thread = threading.Thread(
        target=UDPTstart, args=(HOST_IP, PORT_NU), daemon=True
    )
    server_thread.start()


root = tk.Tk()
root.title("gon's UDPT server implementation")
root.resizable(width=False, height=False)
root.iconbitmap(lib.resource_path("util/icon.ico"))

mainframe = tk.Frame(root)
mainframe.grid(column=0, row=0, sticky="nwes")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

HOST = tk.StringVar()
get_HOST = tk.Entry(mainframe, textvariable=HOST, width=30).grid(
    column=1, row=0, sticky="nswe"
)
tk.Label(mainframe, text="HOST").grid(column=0, row=0, sticky="nswe")

PORT = tk.StringVar()
get_PORT = tk.Entry(mainframe, textvariable=PORT).grid(column=1, row=1, sticky="nswe")
tk.Label(mainframe, text="PORT").grid(column=0, row=1, sticky="nswe")

start_button = tk.Button(mainframe, text="Start", command=get_HOST_PORT)
start_button.grid(columnspan=2, row=2, sticky="nsew")

stop_notice = tk.Label(mainframe, text="Close the window to Stop")

info = tk.Label(
    mainframe,
    text="Default HOST: localhost\nDefault PORT: 1212",
    justify="left",
    anchor="w",
)
info.grid(columnspan=2, row=3, sticky="nsew")

root.bind("<Return>", get_HOST_PORT)
root.mainloop()
