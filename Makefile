CFLAGS+= -Wall
SRCS=$(shell echo src/*.c | sed 's/\.c*//g')

.PHONY: all

all: setup $(SRCS)

clean:
	rm -rf _build

install:
	cp _build/* bin/

setup:
	mkdir -p _build

%:%.c
	$(CC) $(CFLAGS) -o _build/`basename $@` $< 

