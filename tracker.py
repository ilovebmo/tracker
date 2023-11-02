import socketserver, lib
from socket import gethostbyname, gethostname
from ctypes import c_int32


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
                socket.sendto(lib.stopped + data[12:16] + b"No scraping!", self.client_address)
            

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
            data[98:]
        )
        
        print(f"{self.client_address[0]}:{self.client_address[1]} has {lib.event[peer.event]}.\n")
        
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
    print("IM HERE")
    with socketserver.UDPServer((HOST, PORT), UDPT) as server:
        server.serve_forever()
    print("QUIT")
