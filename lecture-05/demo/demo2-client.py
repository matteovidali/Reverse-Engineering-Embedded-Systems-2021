#!/usr/bin/env python3

import optparse
import socket
import struct
import time

def send_and_receive(ip, port, msg):
    sock = socket.socket()
    sock.connect((ip, port))

    sock.sendall(msg)

    sock.settimeout(2.0)

    resp = b""
    while (len(resp) < 8):
        resp += sock.recv(8 - len(resp))

    sock.close()
    return resp

def test_sum(ip, port, ints):
    msg = b"SUMS"
    msg += struct.pack("<I", len(ints))
    for i in ints:
        msg += struct.pack("<I", i)

    print(f"SENDING: {msg}")
    resp = send_and_receive(ip, port, msg)
    print(f"RECEIVED: {resp}")

    if resp[0:4] != b"SUMS":
        raise ValueError("Magic number in response")

    result = struct.unpack("<I", resp[4:8])[0]
    print(f"Result: {result}")


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-i", "--ip", dest="ip", help="IP address of target",
            default="169.254.15.2")
    parser.add_option("-p", "--port", dest="port",
            help="TCP port number of service", default="31331")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        print("Providing default arguments of 1 2 3 4 5")
        nums = [1, 2, 3, 4, 5]
    else:
        nums = [int(i) for i in args]
    test_sum(options.ip, int(options.port), nums)

