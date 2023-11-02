import logging, socketserver, threading, lib, pickle
import tkinter as tk


#
#
#
# Logging setup
#

# Logging to logging.log
logging.basicConfig(filename='logging.log', encoding='utf-8', level=logging.INFO)

#
#
#
# The UDP Tracker server
#

# The UDP Tracker handler class
class UDPT(socketserver.BaseRequestHandler):
    """
    Defines the handle() method for handling UDP requests.
    """
    
    # The handle method
    def handle(self):
        # Gets the data from the client request and the client socket to respond
        data = self.request[0].strip()
        socket = self.request[1]
        host_port = f"{self.client_address[0]}:{self.client_address[1]}"

        # Check if it's a connection request
        if self._connect(data, socket):
            logging.info(f" {host_port} has connected.")
            return

        # Handles other requests
        match self._service(data, socket):
            case lib.Requests.announced:
                logging.info(f" {host_port} has announced.")
                return
            case lib.Requests.completed:
                logging.info(f" {host_port} has completed.")
                return
            case lib.Requests.started:
                logging.info(f" {host_port} has started.")
                return
            case lib.Requests.stopped:
                logging.info(f" {host_port} has stopped.")
                return
            case lib.Requests.scraped:
                logging.info(f" {host_port} has scraped.")
                return
            case lib.Requests.error:
                logging.warn(f" {host_port} has caused an error.")
                return
            case lib.Requests.invalid:
                logging.warn(f" {host_port} used an invalid connection_id.")
                return
            case _:
                logging.warn(f" {host_port} caused something odd to happen...")

    # Method for handling the initial connection
    def _connect(self, data: bytes, socket: socketserver.socket) -> bool:
        # Check if it's a connection request
        if data[:12] != lib.protocol_id + lib.connect:
            return False
        
        # Creates a random connection_id and stores it in the connections file
        cid = lib.connection_id()
        with open("connections", "ab") as c:
            c.write(cid+lib.newline)
        
        # Responds according to BEP15 with the connection_id
        socket.sendto(data[8:] + cid, self.client_address)
        return True

    # Assemble connection_ids
    def _service(self, data: bytes, socket: socketserver.socket) -> str:
        # Gets the connections from the file
        connections = []
        with open("connections", "rb") as c:
            for n in c.read().split(lib.newline)[:-1]:
                connections.append(n)
        
        # Checks if it's a valid connection_id
        if data[:8] not in connections:
            return "invalid"
        
        # Directs the data
        match data[8:12]:
            case lib.IDs.announce:
                return self._announce(data, socket)
            case lib.IDs.scrape:
                return self._scrape(data, socket)
            case _:
                self._error(data[12:16], socket)
                return "error"
    
    # Method for handling announce requests
    def _announce(self, data: bytes, socket: socketserver.socket) -> str:
        # Creates a Peer object using the info provided by the client
        peer = lib.Peer(data)
        
        # Gets the torrents from the file
        torrents = lib.get_torrents()

        # If no IP was provided by the client, use the socket address
        if peer.IP == lib.zero_32:
            peer.IP = lib.ip_32(self.client_address[0])

        # Updates torrents based on Peer
        torrents = lib.peer_torrent(peer, torrents)

        # Constructs UDP response according to BEP15
        response = data[8:16] + lib.interval + self._leechers(peer.info_hash, torrents) + self._seeders(peer.info_hash, torrents)
        # Adds IPs and ports of connected peers to the response
        for p in torrents[peer.info_hash].values():
            response += p.IP + p.port

        # Stores torrents state
        lib.up_torrents(torrents)
        
        # Sends response
        socket.sendto(response, self.client_address)
        
        return lib.event[peer.event]

    # Method for handling scrape requests
    def _scrape(self, data: bytes, socket: socketserver.socket) -> str:
        # Get all the info_hashes
        to_scrape = len(data[16:])/20
        
        # Max number of scrapes is 74
        if to_scrape > 74:
            raise ValueError
        
        infos = []
        for t in range(n):
            infos.append(data[16+20*t:16+20*(t+1)])
        
        # Gets the torrents from the file
        torrents = lib.get_torrents()
        
        # Construct a response
        response = data[8:16]
        for t in infos:
            # In case there's an info_hash requested that isn't in the database
            try:
                # Haven't implemented times-downloaded so just send 0
                response += self._leechers(i, torrents) + lib.zero_32 + self._seeders(i, torrents)
            except:
                pass
        
        # Sends response
        socket.sendto(response, self.client_address)
        
        return "scraped"
    
    # Method for handling errors
    def _error(self, t_id: bytes, socket: socketserver.socket, msg=b"Something went wrong"):
        socket.sendto(lib.error+t_id+msg, self.client_address)
    
    # Method for counting leechers
    def _leechers(self, info_hash: bytes, torrents: dict) -> bytes:
        """
        Counts leechers.
        """
        _leech = 0
        
        # If there's still data left, the file isn't completed, therefore it's a leech
        for p in torrents[info_hash].values():
            if p.left != lib.zero:
                _leech += 1

        return lib.rev_b(lib.make32(_leech))

    # Method for counting seeders
    def _seeders(self, info_hash: bytes, torrents: dict) -> bytes:
        """
        Counts seeders.
        """
        _seed = 0
        
        # If there's no data left, the file isn't completed, therefore it's a seed
        for p in torrents[info_hash].values():
            if p.left == lib.zero:
                _seed += 1

        return lib.rev_b(lib.make32(_seed))

# Function for starting the server
def UDPTstart(HOST: str = lib.gethost(), PORT: int = 1212):
    with socketserver.UDPServer((HOST, PORT), UDPT) as server:
        server.serve_forever()

#
#
#
# Tkinter GUI
#

# Function to handle user input on HOST and PORT selection
def get_HOST_PORT(*event: tk.Event):
    # Get the PORT
    try:
        PORT_NU = int(PORT.get())
    except ValueError:
        PORT_NU = 1212
    
    # Get the HOST
    HOST_IP = HOST.get()  
    # Checks if it's in the form of IPV4
    if len(HOST_IP.split(".")) != 4:
        HOST_IP = lib.gethost()
    # Checks if it's a valid IPV4
    try:
        for n in HOST_IP.split("."):
            int(n)
    except ValueError:
        HOST_IP = lib.gethost()

    # Unbinds the starting server input
    root.unbind("<Return>")
    start_button.destroy()
    
    # Updates the information about the server
    stop_notice.grid(columnspan=2, row=2, sticky="nsew")
    info.configure(text=f"HOST: {HOST_IP}\nPORT: {PORT_NU}\nLogging: logging.log")

    # Starts the server
    server_thread = threading.Thread(
        target=UDPTstart, args=(HOST_IP, PORT_NU), daemon=True
    )
    server_thread.start()

# Simple Tkinter setup
root = tk.Tk()
root.title("gon's UDPT server implementation")
root.resizable(width=False, height=False)
root.iconbitmap(lib.resource_path("util/icon.ico"))

# Mainframe setup
mainframe = tk.Frame(root)
mainframe.grid(column=0, row=0, sticky="nwes")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# User input for HOST
HOST = tk.StringVar()
get_HOST = tk.Entry(mainframe, textvariable=HOST, width=30).grid(
    column=1, row=0, sticky="nswe"
)
tk.Label(mainframe, text="HOST").grid(column=0, row=0, sticky="nswe")

# User input for PORT
PORT = tk.StringVar()
get_PORT = tk.Entry(mainframe, textvariable=PORT).grid(column=1, row=1, sticky="nswe")
tk.Label(mainframe, text="PORT").grid(column=0, row=1, sticky="nswe")

# Button to start server
start_button = tk.Button(mainframe, text="Start", command=get_HOST_PORT)
start_button.grid(columnspan=2, row=2, sticky="nsew")

# Label that replaces the Button
stop_notice = tk.Label(mainframe, text="Close the window to Stop")

# Info Label for server
info = tk.Label(
    mainframe,
    text="Default HOST: localhost\nDefault PORT: 1212",
    justify="left",
    anchor="w",
)
info.grid(columnspan=2, row=3, sticky="nsew")

# Bind so that you don't actually need to click the button to start the server
root.bind("<Return>", get_HOST_PORT)
root.mainloop()
