"""
Includes several useful functions and data/values for use in the UDPT.
"""

import ctypes, random, sys, os, pickle, json, hashlib
from socket import gethostbyname, gethostname


# Reverses bits
def rev_b(num) -> bytes:
    return bytes(reversed(bytes(num)))


# The Peer class definition
class Peer:
    """
    The Peer class.

    Includes all the data in the BEP15 standard. Also has auth.
    """

    def __init__(self, data: bytes):
        self.info_hash: bytes = data[16:36]
        self.peer_id: bytes = data[36:56]
        self.downloaded: bytes = data[56:64]
        self.left: bytes = data[64:72]
        self.uploaded: bytes = data[72:80]
        self.event: bytes = data[80:84]
        self.IP: bytes = data[84:88]
        self.key: bytes = data[88:92]
        self.num_want: bytes = data[92:96]
        self.port: bytes = data[96:98]
        self.auth: bytes = data[98:]


# Auth
def authenticate(addr: str, password: bytes) -> bool:
    """
    Authentication procedure for udp://HOST:PORT/PASSWORD_HASH

    addr:     str   -> User IP address
    password: bytes -> User password"""

    with open("users.json", "r") as f:
        users = json.load(f)

    if addr not in users.keys():
        return False

    if bytes(hashlib.sha256(bytes(users[addr], "utf-8")).hexdigest(), "utf-8") != password:
        return False

    return True


# Useful types
protocol_id = rev_b(ctypes.c_int64(0x41727101980))
connect = rev_b(ctypes.c_int32(0))
zero = rev_b(ctypes.c_int64(0))
zero_32 = rev_b(ctypes.c_int32(0))
announce = rev_b(ctypes.c_int32(1))
completed = announce
started = rev_b(ctypes.c_int32(2))
scrape = started
stopped = rev_b(ctypes.c_int32(3))
error = stopped
interval = rev_b(ctypes.c_int32(60))
newline = bytes("\n", "utf-8")


# Requests
class Requests:
    announced = "announced"
    completed = "completed"
    started = "started"
    stopped = "stopped"
    scraped = "scraped"
    error = "error"
    invalid = "invalid"


# Request Ids
class IDs:
    announce = announce
    scrape = scrape


# Generates connection_ids
def connection_id():
    return rev_b(random.randbytes(8))


# Get torrents dict
def get_torrents():
    """
    Gets the torrents dict.
    """
    try:
        with open("torrents.pkl", "rb") as t:
            return pickle.load(t)
    except (FileNotFoundError, EOFError):
        return {}


# Update torrents dict
def up_torrents(torr: dict):
    with open("torrents.pkl", "wb") as t:
        pickle.dump(torr, t, pickle.HIGHEST_PROTOCOL)


# Peer in torrents
def peer_torrent(peer: Peer, torr: dict) -> dict:
    # Checks if torrent is in database
    if peer.info_hash in torr.keys():
        # Checks if the peer_id is already in the database
        if peer.peer_id in torr[peer.info_hash].keys():
            # Update peer in database
            torr[peer.info_hash][peer.peer_id] = peer

    else:
        # If peer isn't in the database, add it
        torr.update({peer.info_hash: {peer.peer_id: peer}})
    return torr


# Gets the resource path for the icon, useful for -F executable
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Gets the host IP
def gethost() -> str:
    return gethostbyname(gethostname())


# Makes int32_t
def make32(num):
    return ctypes.c_int32(num)


# Makes IPs into int32_t
def ip_32(s: str) -> bytes:
    s = s.split(".")
    return (
        rev_b(ctypes.c_int8(int(s[0])))
        + rev_b(ctypes.c_int8(int(s[1])))
        + rev_b(ctypes.c_int8(int(s[2])))
        + rev_b(ctypes.c_int8(int(s[3])))
    )


# Events of client announce requests
event = {
    connect: "announced",
    completed: "completed",
    started: "started",
    stopped: "stopped",
}
