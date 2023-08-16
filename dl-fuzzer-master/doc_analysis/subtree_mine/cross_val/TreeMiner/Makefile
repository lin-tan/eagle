CC = g++
CFLAGS = -O3
HDRS = treeminer.h timetrack.h calcdb.h eqclass.h stats.h idlist.h hashtable.h
OBJS = calcdb.o eqclass.o stats.o idlist.o treeminer.o hashtable.o
LIBS = 
TARGET = treeminer

default: $(TARGET)

clean:
	rm -rf *~ *.o $(TARGET)

treeminer: $(OBJS) $(HFILES)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS) $(LIBS)

.SUFFIXES: .o .cpp

.cpp.o:
	$(CC) $(CFLAGS) -c $<


# dependencies
# $(OBJS): $(HFILES)
treeminer.o: $(HDRS)
calcdb.o: calcdb.h treeminer.h idlist.h
eqclass.o: eqclass.h treeminer.h idlist.h calcdb.h idlist.h
stats.o: stats.h
idlist.o: idlist.h
hashtable.o: hashtable.h treeminer.h eqclass.h
