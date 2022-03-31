CXX = arm-linux-gnueabi-g++
CFLAGS = -march=armv7-r -O1 -mthumb -fno-inline -fno-elide-constructors -no-pie
STRIP = arm-linux-gnueabi-strip

build : object-oriented-methods.cpp
	$(CXX) $(CFLAGS) -o object-oriented-methods object-oriented-methods.cpp
	cp object-oriented-methods object-oriented-methods-stripped
	$(STRIP) object-oriented-methods-stripped

clean :
	$(RM) object-oriented-methods object-oriented-methods-stripped *.o

