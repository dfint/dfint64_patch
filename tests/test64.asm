format pe64 console
include 'includes/win64ax.inc'
include 'macros.inc'

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
    endl string 13, 10
    sHello string 'Hello, World!'
    hOut dq ?

.end start
