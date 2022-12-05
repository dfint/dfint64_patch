format pe64 console
include 'includes/win64ax.inc'

.code

start:
    invoke GetStdHandle, STD_OUTPUT_HANDLE
    mov [hOut], rax

    lea rdx, [sHello]
    mov r8d, sHello.length
    call writeln

    invoke ExitProcess, 0

writeln:
    frame
        invoke WriteConsole, [hOut], rdx, r8d, 0, 0
        invoke WriteConsole, [hOut], endl, endl.length, 0, 0
    endf
    retn

.data
    ; Custom align macro which aligns with zero bytes instead of nops
    macro align value {
        db (value-1)-($+value-1) mod value dup 0
    }

    endl db 13, 10
    .length = $ - endl
    db 0
    align 8

    sHello db 'Hello, World!'
    .length = $ - sHello
    db 0
    align 8

    hOut dq ?

.end start
