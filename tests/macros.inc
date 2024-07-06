; Custom align macro which aligns with zero bytes instead of nops
macro align value {
    db (value-1)-($+value-1) mod value dup 0
}

struc string [text] {
common
    . db text
    .length = $ - .
    db 0
    align 4
}

macro writeln hOut, text, text_length {
    invoke WriteConsole, [hOut], text, text_length, 0, 0
    invoke WriteConsole, [hOut], endl, endl.length, 0, 0
}
