.c.o:
	$(CC) -c $(CFLAGS) $*.c

CC = arm-linux-gnueabi-gcc
CFLAGS = -Wall -fomit-frame-pointer -O1

SRCS = $(wildcard *.c)

all : $(SRCS:.c=)

