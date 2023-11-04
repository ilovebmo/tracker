import socketserver, util.lib, logging


# The UDP Tracker handler class, no auth
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
            case util.lib.Requests.announced:
                logging.info(f" {host_port} has announced.")
                return
            case util.lib.Requests.completed:
                logging.info(f" {host_port} has completed.")
                return
            case util.lib.Requests.started:
                logging.info(f" {host_port} has started.")
                return
            case util.lib.Requests.stopped:
                logging.info(f" {host_port} has stopped.")
                return
            case util.lib.Requests.scraped:
                logging.info(f" {host_port} has scraped.")
                return
            case util.lib.Requests.error:
                logging.warn(f" {host_port} has caused an error.")
                return
            case util.lib.Requests.invalid:
                logging.warn(f" {host_port} used an invalid connection_id.")
                return
            case _:
                logging.warn(f" {host_port} caused something odd to happen...")

    # Method for handling the initial connection
    def _connect(self, data: bytes, socket: socketserver.socket) -> bool:
        # Check if it's a connection request
        if data[:12] != util.lib.protocol_id + util.lib.connect:
            return False

        # Creates a random connection_id and stores it in the connections file
        cid = util.lib.connection_id()
        with open("connections", "ab") as c:
            c.write(cid + util.lib.newline)

        # Responds according to BEP15 with the connection_id
        socket.sendto(data[8:] + cid, self.client_address)
        return True

    # Assemble connection_ids
    def _service(self, data: bytes, socket: socketserver.socket) -> str:
        # Gets the connections from the file
        connections = []
        with open("connections", "rb") as c:
            for n in c.read().split(util.lib.newline)[:-1]:
                connections.append(n)

        # Checks if it's a valid connection_id
        if data[:8] not in connections:
            return "invalid"

        # Directs the data
        match data[8:12]:
            case util.lib.IDs.announce:
                return self._announce(data, socket)
            case util.lib.IDs.scrape:
                return self._scrape(data, socket)
            case _:
                self._error(data[12:16], socket)
                return "error"

    # Method for handling announce requests
    def _announce(self, data: bytes, socket: socketserver.socket) -> str:
        # Creates a Peer object using the info provided by the client
        peer = util.lib.Peer(data)

        # Gets the torrents from the file
        torrents = util.lib.get_torrents()

        # If no IP was provided by the client, use the socket address
        if peer.IP == util.lib.zero_32:
            peer.IP = util.lib.ip_32(self.client_address[0])

        # Updates torrents based on Peer
        torrents = util.lib.peer_torrent(peer, torrents)

        # Constructs UDP response according to BEP15
        response = (
            data[8:16]
            + util.lib.interval
            + self._leechers(peer.info_hash, torrents)
            + self._seeders(peer.info_hash, torrents)
        )
        # Adds IPs and ports of connected peers to the response
        for p in torrents[peer.info_hash].values():
            response += p.IP + p.port

        # Stores torrents state
        util.lib.up_torrents(torrents)

        # Sends response
        socket.sendto(response, self.client_address)

        return util.lib.event[peer.event]

    # Method for handling scrape requests
    def _scrape(self, data: bytes, socket: socketserver.socket) -> str:
        # Get all the info_hashes
        to_scrape = len(data[16:]) / 20

        # Max number of scrapes is 74
        if to_scrape > 74:
            raise ValueError

        infos = []
        for t in range(n):
            infos.append(data[16 + 20 * t : 16 + 20 * (t + 1)])

        # Gets the torrents from the file
        torrents = util.lib.get_torrents()

        # Construct a response
        response = data[8:16]
        for t in infos:
            # In case there's an info_hash requested that isn't in the database
            try:
                # Haven't implemented times-downloaded so just send 0
                response += (
                    self._leechers(i, torrents)
                    + util.lib.zero_32
                    + self._seeders(i, torrents)
                )
            except:
                pass

        # Sends response
        socket.sendto(response, self.client_address)

        return "scraped"

    # Method for handling errors
    def _error(
        self, t_id: bytes, socket: socketserver.socket, msg=b"Something went wrong"
    ):
        socket.sendto(util.lib.error + t_id + msg, self.client_address)

    # Method for counting leechers
    def _leechers(self, info_hash: bytes, torrents: dict) -> bytes:
        """
        Counts leechers.
        """
        _leech = 0

        # If there's still data left, the file isn't completed, therefore it's a leech
        for p in torrents[info_hash].values():
            if p.left != util.lib.zero:
                _leech += 1

        return util.lib.rev_b(util.lib.make32(_leech))

    # Method for counting seeders
    def _seeders(self, info_hash: bytes, torrents: dict) -> bytes:
        """
        Counts seeders.
        """
        _seed = 0

        # If there's no data left, the file isn't completed, therefore it's a seed
        for p in torrents[info_hash].values():
            if p.left == util.lib.zero:
                _seed += 1

        return util.lib.rev_b(util.lib.make32(_seed))


# The UDP Tracker handler class, authentication mode
class authUDPT(socketserver.BaseRequestHandler):
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
            case util.lib.Requests.announced:
                logging.info(f" {host_port} has announced.")
                return
            case util.lib.Requests.completed:
                logging.info(f" {host_port} has completed.")
                return
            case util.lib.Requests.started:
                logging.info(f" {host_port} has started.")
                return
            case util.lib.Requests.stopped:
                logging.info(f" {host_port} has stopped.")
                return
            case util.lib.Requests.scraped:
                logging.info(f" {host_port} has scraped.")
                return
            case util.lib.Requests.error:
                logging.warn(f" {host_port} has caused an error.")
                return
            case util.lib.Requests.invalid:
                logging.warn(f" {host_port} used an invalid connection_id.")
                return
            case _:
                logging.warn(f" {host_port} caused something odd to happen...")

    # Method for handling the initial connection
    def _connect(self, data: bytes, socket: socketserver.socket) -> bool:
        # Check if it's a connection request
        if data[:12] != util.lib.protocol_id + util.lib.connect:
            return False

        # Creates a random connection_id and stores it in the connections file
        cid = util.lib.connection_id()
        with open("connections", "ab") as c:
            c.write(cid + util.lib.newline)

        # Responds according to BEP15 with the connection_id
        socket.sendto(data[8:] + cid, self.client_address)
        return True

    # Assemble connection_ids
    def _service(self, data: bytes, socket: socketserver.socket) -> str:
        # Gets the connections from the file
        connections = []
        with open("connections", "rb") as c:
            for n in c.read().split(util.lib.newline)[:-1]:
                connections.append(n)

        # Checks if it's a valid connection_id
        if data[:8] not in connections:
            return "invalid"

        # Directs the data
        match data[8:12]:
            case util.lib.IDs.announce:
                return self._announce(data, socket)
            case util.lib.IDs.scrape:
                return self._scrape(data, socket)
            case _:
                self._error(data[12:16], socket)
                return "error"

    # Method for handling announce requests
    def _announce(self, data: bytes, socket: socketserver.socket) -> str:
        # Creates a Peer object using the info provided by the client
        peer = util.lib.Peer(data)

        # Authenticate
        if not util.lib.authenticate(self.client_address[0], peer.auth[3:]):
            logging.critical(f" {self.client_address} is not authorized.")
            return

        # Gets the torrents from the file
        torrents = util.lib.get_torrents()

        # If no IP was provided by the client, use the socket address
        if peer.IP == util.lib.zero_32:
            peer.IP = util.lib.ip_32(self.client_address[0])

        # Updates torrents based on Peer
        torrents = util.lib.peer_torrent(peer, torrents)

        # Constructs UDP response according to BEP15
        response = (
            data[8:16]
            + util.lib.interval
            + self._leechers(peer.info_hash, torrents)
            + self._seeders(peer.info_hash, torrents)
        )
        # Adds IPs and ports of connected peers to the response
        for p in torrents[peer.info_hash].values():
            response += p.IP + p.port

        # Stores torrents state
        util.lib.up_torrents(torrents)

        # Sends response
        socket.sendto(response, self.client_address)

        return util.lib.event[peer.event]

    # Method for handling scrape requests
    def _scrape(self, data: bytes, socket: socketserver.socket) -> str:
        # Get all the info_hashes
        to_scrape = len(data[16:]) / 20

        # Max number of scrapes is 74
        if to_scrape > 74:
            raise ValueError

        infos = []
        for t in range(n):
            infos.append(data[16 + 20 * t : 16 + 20 * (t + 1)])

        # Gets the torrents from the file
        torrents = util.lib.get_torrents()

        # Construct a response
        response = data[8:16]
        for t in infos:
            # In case there's an info_hash requested that isn't in the database
            try:
                # Haven't implemented times-downloaded so just send 0
                response += (
                    self._leechers(i, torrents)
                    + util.lib.zero_32
                    + self._seeders(i, torrents)
                )
            except:
                pass

        # Sends response
        socket.sendto(response, self.client_address)

        return "scraped"

    # Method for handling errors
    def _error(
        self, t_id: bytes, socket: socketserver.socket, msg=b"Something went wrong"
    ):
        socket.sendto(util.lib.error + t_id + msg, self.client_address)

    # Method for counting leechers
    def _leechers(self, info_hash: bytes, torrents: dict) -> bytes:
        """
        Counts leechers.
        """
        _leech = 0

        # If there's still data left, the file isn't completed, therefore it's a leech
        for p in torrents[info_hash].values():
            if p.left != util.lib.zero:
                _leech += 1

        return util.lib.rev_b(util.lib.make32(_leech))

    # Method for counting seeders
    def _seeders(self, info_hash: bytes, torrents: dict) -> bytes:
        """
        Counts seeders.
        """
        _seed = 0

        # If there's no data left, the file isn't completed, therefore it's a seed
        for p in torrents[info_hash].values():
            if p.left == util.lib.zero:
                _seed += 1

        return util.lib.rev_b(util.lib.make32(_seed))
