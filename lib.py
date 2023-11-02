"""
Includes several useful functions and data/values for use in the UDPT.
"""

import ctypes, random, sys, os
from socket import gethostbyname, gethostname


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

# Reverses bits
def rev_b(num) -> bytes:
    return bytes(reversed(bytes(num)))

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

# Useful types
protocol_id = rev_b(ctypes.c_int64(0x41727101980))
connect = rev_b(ctypes.c_int32(0))
zero = rev_b(ctypes.c_int64(0))
zero_32 = rev_b(ctypes.c_int32(0))
announce = rev_b(ctypes.c_int32(1))
started = rev_b(ctypes.c_int32(2))
stopped = rev_b(ctypes.c_int32(3))
error = stopped
interval = rev_b(ctypes.c_int32(60))
    
# Events of client announce requests
event = {
    connect: "connected",
    announce: "completed",
    started: "started",
    stopped: "stopped",
}

# Generates connection_ids
def connection_id():
    return rev_b(random.randbytes(8))

# The Peer class definition
class Peer:
    """
    The Peer class.
    
    Includes all the data in the BEP15 standard. Also has auth.
    """
    def __init__(
        self,
        info_hash: bytes,
        peer_id: bytes,
        downloaded: bytes,
        left: bytes,
        uploaded: bytes,
        event: bytes,
        IP: bytes,
        key: bytes,
        num_want: bytes,
        port: bytes,
        auth: bytes = "",
    ):
        self.info_hash: bytes = info_hash
        self.peer_id: bytes = peer_id
        self.downloaded: bytes = downloaded
        self.left: bytes = left
        self.uploaded: bytes = uploaded
        self.event: bytes = event
        self.IP: bytes = IP
        self.key: bytes = key
        self.num_want: bytes = num_want
        self.port: bytes = port
        self.auth: bytes = auth
