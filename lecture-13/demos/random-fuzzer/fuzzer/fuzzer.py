#!/usr/bin/env python3

import sys
import subprocess
import random

if len(sys.argv) > 1:
    prog_name = sys.argv[1]
else:
    prog_name = "../program/program"


iters = 0
while True:
    iters += 1
    # Generate a random bytestring of random length
    numbytes = random.randint(1, 256)
    randominput = random.randbytes(numbytes)

    # Provide the input to the program
    complete = subprocess.run(prog_name, input=randominput, shell=False,
            capture_output=True)

    # Check to see if the program crashed
    if complete.returncode < 0:
        print(f"Crashed after iteration {iters} from signal {-complete.returncode} with input {randominput.hex()}")
        break
    else:
        print(f"No crash after iteration {iters} with input {randominput.hex()}")


