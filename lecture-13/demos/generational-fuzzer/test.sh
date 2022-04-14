#!/bin/bash

# These inputs won't crash
echo -ne "MAGC\x08abcdefgh" | program/program
echo -ne "MAGC\xffabcdefgh" | program/program
echo -ne "MAGC\x08AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" | program/program

# This input should cause an error
echo -ne "\x08abcdefgh" | program/program

# Cause a segfault
python3 -c "import sys; sys.stdout.buffer.write(b'MAGC\xff' + b'A'*0xff)" | program/program

