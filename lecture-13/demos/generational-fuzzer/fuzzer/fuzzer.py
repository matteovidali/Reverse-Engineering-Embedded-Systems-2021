#!/usr/bin/env python3

import sys
import subprocess
import random
import struct

if len(sys.argv) > 1:
    prog_name = sys.argv[1]
else:
    prog_name = "../program/program"


iters = 0
while True:
    iters += 1

    # First field is magic number
    randominput = b"MAGC"

    # Second field is length
    numbytes = random.randint(1, 255)
    randominput += struct.pack("B", numbytes)

    # Now add the random bytes
    randominput += random.randbytes(numbytes)

    # Provide the input to the program
    complete = subprocess.run(prog_name, input=randominput, shell=False,
            capture_output=True)

    # Check to see if the program crashed
    if complete.returncode < 0:
        print(f"Crashed after iteration {iters} from signal {-complete.returncode} with input {randominput.hex()}")
        break
    else:
        print(f"No crash after iteration {iters} with input {randominput.hex()}")


