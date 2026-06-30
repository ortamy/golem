.PHONY: all clean run

all: boot.bin

boot.bin: boot/boot.asm
	nasm -f bin $< -o $@

clean:
	del /Q boot.bin 2>nul || rm -f boot.bin

run: boot.bin
	qemu-system-i386 -drive format=raw,file=boot.bin