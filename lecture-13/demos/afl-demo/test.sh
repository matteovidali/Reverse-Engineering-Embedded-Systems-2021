#!/bin/bash

# These inputs won't crash
echo -ne "MAGC\x08\x00abcdefgh" | program/program
echo -ne "MAGC\x08\xc8abcdefgh" | program/program
echo -ne "MAGC\xff\x00abcdefgh" | program/program
echo -ne "MAGC\xff\xc8abcdefgh" | program/program
echo -ne "MAGC\x08\x00AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" | program/program
python3 -c "import sys; sys.stdout.buffer.write(b'MAGC\xff\x00' + b'A'*0xff)" | program/program

# This input should cause an error
echo -ne "\x08abcdefgh" | program/program

# Cause a segfault
python3 -c "import sys; sys.stdout.buffer.write(b'MAGC\xff\xc8' + b'A'*0xff)" | program/program

