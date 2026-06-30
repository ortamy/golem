[bits 16]
[org 0x7C00]

start:
    ; Initialize segments and stack
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    
    ; Disable interrupts
    cli
    
    ; Enable A20 line for access to memory above 1MB
    call enable_a20
    
    ; Load Global Descriptor Table
    lgdt [gdt_descriptor]
    
    ; Switch to protected mode
    mov eax, cr0
    or eax, 1
    mov cr0, eax
    
    ; Far jump to flush pipeline and load 32-bit code segment
    jmp 0x08:pm_start

enable_a20:
    push ax
    in al, 0x92
    test al, 2
    jnz .done
    or al, 2
    out 0x92, al
.done:
    pop ax
    ret

[bits 32]
pm_start:
    ; Initialize 32-bit data segments
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov esp, 0x7C00
    
    ; Clear screen (VGA text mode: 80x25, white on black)
    mov edi, 0xB8000
    mov ecx, 2000
    mov eax, 0x0F200F20
    rep stosd
    
    ; Print first message: "Shema, Yisrael! Yahweh Echad!"
    mov esi, msg1
    mov edi, 0xB8000 + 2
    call print_string
    
    ; Print second message: "Golem OS v0.1"
    mov esi, msg2
    mov edi, 0xB8000 + 162
    call print_string
    
hang:
    jmp hang

print_string:
    push eax
.next_char:
    lodsb
    test al, al
    jz .done
    mov ah, 0x0F
    stosw
    jmp .next_char
.done:
    pop eax
    ret

msg1 db "Shema, Yisrael! Yahweh Echad!", 0
msg2 db "Golem OS v0.1", 0

; Global Descriptor Table
gdt_start:
    dd 0, 0
    
    ; Code segment descriptor (base=0, limit=4GB, 32-bit)
    dw 0xFFFF
    dw 0x0000
    db 0x00
    db 10011010b
    db 11001111b
    db 0x00
    
    ; Data segment descriptor (base=0, limit=4GB, 32-bit)
    dw 0xFFFF
    dw 0x0000
    db 0x00
    db 10010010b
    db 11001111b
    db 0x00
gdt_end:

gdt_descriptor:
    dw gdt_end - gdt_start - 1
    dd gdt_start

times 510-($-$$) db 0
dw 0xAA55