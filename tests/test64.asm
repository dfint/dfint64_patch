format pe64 console
include 'includes/win64ax.inc'

.code

start:
    invoke GetStdHandle, STD_OUTPUT_HANDLE
    mov [hOut], rax
    invoke WriteConsole, [hOut], sHello, sHello.length, 0, 0
    invoke ExitProcess, 0

.data
    sHello db 'Hello!'
    .length = $ - sHello
    hOut dq ?

.end start
