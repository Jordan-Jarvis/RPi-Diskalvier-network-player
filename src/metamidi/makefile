CC=gcc


extractorXML.o: extractorXML.c extractorXML.h tmidi.h
	$(CC)  -c extractorXML.c 

tmidi.o: tmidi.c tmidi.h
	$(CC)  -c tmidi.c 

metamidi: main.c extractorXML.o tmidi.o
	$(CC)  -o metamidi main.c extractorXML.o tmidi.o
clean:
	rm *.o metamidi
