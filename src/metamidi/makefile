# CC=gcc


# extractorXML.o: extractorXML.c extractorXML.h tmidi.h
# 	$(CC)  -c extractorXML.c 

# tmidi.o: tmidi.c tmidi.h
# 	$(CC)  -c tmidi.c 

# metamidi: main.c extractorXML.o tmidi.o
# 	$(CC)  -o metamidi main.c extractorXML.o tmidi.o
# clean:
# 	rm *.o metamidi


CC=gcc


extractorXML.o: extractorXML.c extractorXML.h tmidi.h
	$(CC) -fPIC -shared -c extractorXML.c 

tmidi.o: tmidi.c tmidi.h
	$(CC) -fPIC -shared -c tmidi.c 

metamidi: main.c extractorXML.o tmidi.o
	$(CC) -fPIC -shared -o metamidi.so main.c extractorXML.o tmidi.o
clean:
	rm *.o metamidi
