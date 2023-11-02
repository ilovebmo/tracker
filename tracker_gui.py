import logging, socketserver, threading, lib
import tkinter as tk


#
#
#
# Basic setup
#

# Logging to logging.log
logging.basicConfig(filename='logging.log', encoding='utf-8', level=logging.INFO)

# Torrents dictionary, stores info_hashes as keys, which map to a dictionary of structure peer_id: Peer
torrents = {}

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

        # Check if it's a connection request
        if data[:12] == lib.protocol_id + lib.connect:
            # Connects
            self._connect(data, socket)
            return

        # Gets the connections from the file
        connections = []
        with open("connections", "rb") as c:
            for n in c.read().split(lib.newline)[:-1]:
                connections.append(n)
                
        # Checks if it's a valid connection_id
        if data[:8] in connections:
            # Checks if it's an announce request
            if data[8:12] == lib.announce:
                # Announces
                self.announce(data, socket)
                return
            
            else:
                # Currently there's no scrape support, so it sends an error packet
                socket.sendto(
                    lib.stopped + data[12:16] + b"No scraping!", self.client_address
                )
                logging.warn(" {self.client_address[0]}:{self.client_address[1]} tried to scrape.\n")

    # Method for handling the initial connection
    def _connect(self, data: bytes, socket: socketserver.socket):
        # Creates a random connection_id and stores it in the connections file
        cid = lib.connection_id()
        with open("connections", "ab") as c:
            c.write(cid+lib.newline)
        
        # Responds according to BEP15 with the connection_id
        socket.sendto(data[8:] + cid, self.client_address)

    # Method for handling announce requests
    def announce(self, data: bytes, socket: socketserver.socket):
        # Creates a Peer object using the info provided by the client
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

        # Console and logging
        print(
            f"{self.client_address[0]}:{self.client_address[1]} has {lib.event[peer.event]}.\n"
        )
        logging.info(f" {self.client_address[0]}:{self.client_address[1]} has {lib.event[peer.event]}.\n")

        # If no IP was provided by the client, use the socket address
        if peer.IP == lib.zero_32:
            peer.IP = lib.ip_32(self.client_address[0])

        # Checks if the info_hash was in the torrents dictionary
        if peer.info_hash in torrents.keys():
            # Checks if the peer_id is already in the database
            if peer.peer_id in torrents[data[16:36]].keys():
                # Updates state of peer
                torrents[data[16:36]][peer.peer_id] = peer
                
        else:
            # If peer isn't in the database, add it
            torrents.update({data[16:36]: {peer.peer_id: peer}})

        # Constructs UDP response according to BEP15
        response = data[8:16] + lib.interval + self._leechers(data) + self._seeders(data)
        # Adds IPs and ports of connected peers to the response
        for p in torrents[data[16:36]].values():
            response += p.IP + p.port

        # Sends response
        socket.sendto(response, self.client_address)

    # Method for counting leechers
    def _leechers(self, data: bytes):
        _leech = 0
        
        # If there's still data left, the file isn't completed, therefore it's a leech
        for p in torrents[data[16:36]].values():
            if p.left != lib.zero:
                _leech += 1

        return lib.rev_b(lib.make32(_leech))

    # Method for counting seeders
    def _seeders(self, data: bytes):
        _seed = 0
        
        # If there's no data left, the file isn't completed, therefore it's a seed
        for p in torrents[data[16:36]].values():
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
