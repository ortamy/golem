# Golem OS Bootloader

Minimal 32-bit bootloader for Golem OS.

## Requirements

- NASM (Netwide Assembler)
- QEMU (i386 emulator)

## Build

```bash
make
```

This runs:
```bash
nasm -f bin boot/boot.asm -o boot.bin
```

## Run

```bash
make run
```

Or directly:
```bash
qemu-system-i386 -drive format=raw,file=boot.bin
```

## Clean

```bash
make clean
```

## What it does

1. Loads via BIOS at 0x7C00
2. Switches to 32-bit protected mode
3. Clears screen to white-on-black
4. Prints:
   - `Shema, Yisrael! Yahweh Echad!`
   - `Golem OS v0.1`
5. Hangs in infinite loop

## Structure

```
boot/
  boot.asm    — 512-byte bootloader (ends with 0xAA55)
Makefile      — build targets
run.sh        — QEMU launcher
README.md     — this file