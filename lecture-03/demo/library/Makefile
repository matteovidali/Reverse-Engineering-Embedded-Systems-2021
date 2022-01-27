CC = arm-linux-gnueabi-gcc
STRIP = arm-linux-gnueabi-strip
CFLAGS = -O2 -fno-inline

all: use-library libdemo.so

libdemo.so: demo.o
	$(CC) -shared -o libdemo.so demo.o
	$(STRIP) libdemo.so

use-library: use-library.o libdemo.so
	$(CC) -o use-library use-library.o -L. -ldemo -Wl,-rpath,'$$ORIGIN'
	$(STRIP) use-library

demo.o: demo.c demo.h
	$(CC) -c -o demo.o demo.c $(CFLAGS) -fPIC

use-library.o: use-library.c demo.h
	$(CC) -c -o use-library.o use-library.c $(CFLAGS)

clean:
	rm use-library use-library.o demo.o libdemo.so
