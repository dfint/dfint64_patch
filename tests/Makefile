.PHONY: build clean

test64.exe: test64.asm macros.inc
	fasm test64.asm

build: test64.exe

clean:
	rm *.exe
