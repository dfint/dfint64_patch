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

    mov rax, buffer
    movups xmm0, xword [aUnitReportShee] ; "Unit report sheet popup"
    movups [rax], xmm0
    mov ecx, dword [aUnitReportShee+10h] ; "t popup"
    mov [rax+10h], ecx
    movzx ecx, word [aUnitReportShee+14h] ; "pup"
    mov [rax+14h], cx
    movzx ecx, byte [aUnitReportShee+16h] ; "p"
    mov [rax+16h], cl
    writeln hOut, rax, aUnitReportShee.length

    invoke ExitProcess, 0

.data
    buffer rb 1024

    endl string 13, 10
    sHello string 'Hello, World!'
    aUnitReportShee string 'Unit report sheet popup'
    hOut dq ?

.end start
