CXX = arm-linux-gnueabi-g++
CFLAGS = -march=armv7-r -O1 -mthumb -fno-inline -fno-elide-constructors -no-pie
STRIP = arm-linux-gnueabi-strip

build : object-oriented-virtual-methods.cpp
	$(CXX) $(CFLAGS) -o object-oriented-virtual-methods object-oriented-virtual-methods.cpp
	cp object-oriented-virtual-methods object-oriented-virtual-methods-stripped
	$(STRIP) object-oriented-virtual-methods-stripped

clean :
	$(RM) object-oriented-virtual-methods object-oriented-virtual-methods-stripped *.o

