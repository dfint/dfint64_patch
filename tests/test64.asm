format pe64 console
include 'includes/win64ax.inc'
include 'macros.inc'

.code

start:
    invoke GetStdHandle, STD_OUTPUT_HANDLE
    mov [hOut], rax

    lea rdx, [sHello]
    mov r8d, sHello.length
    writeln hOut, rdx, r8d

    invoke ExitProcess, 0

.data
    endl string 13, 10
    sHello string 'Hello, World!'
    hOut dq ?

.end start
