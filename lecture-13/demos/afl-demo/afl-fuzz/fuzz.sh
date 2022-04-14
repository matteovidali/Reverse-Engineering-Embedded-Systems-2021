#!/bin/sh

afl-gcc -o program_instrumented ../program/program.c
mkdir inputs
echo "abcdefg" > inputs/input1
mkdir outputs

sudo sh -c "echo core >/proc/sys/kernel/core_pattern"
afl-fuzz -i inputs -o outputs -- ./program_instrumented

