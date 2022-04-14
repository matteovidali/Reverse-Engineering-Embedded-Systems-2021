#!/bin/bash

# These inputs won't crash
echo -ne "\x08abcdefgh" | program/program
echo -ne "\xffabcdefgh" | program/program
echo -ne "\x08AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" | program/program

# Cause a segfault
python3 -c "import sys; sys.stdout.buffer.write(b'\xff' + b'A'*0xff)" | program/program

