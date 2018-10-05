import regex

import combinators.tokenization as tokenization

specifications = [ ( "COMMENT", ( "\(\*(.|[\r\n])*?\*\)", regex.MULTILINE ) ),
                   ( "COMMENT", ( "\{(.|[\r\n])*?\}", regex.MULTILINE ) ),
                   ( "COMMENT", ( "//.*", ) ),
                   ( "NL",      ( "[\r\n]+", ) ),
                   ( "SPACE",   ( "[ \t]+", ) ),
                   ( "NAME",    ( "[A-Za-z_][A-Za-z_0-9]*", ) ),
                   ( "INT",     ( "0x[0-9A-Fa-f]+", ) ),
                   ( "INT",     ( "[0-9]+", ) ),
                   ( "REAL",    ( "[0-9]+\.[0-9]*([Ee][+\-]?[0-9]+)*", ) ),
                   ( "OP",      ( "(\.\.)|(<>)|(<=)|(>=)|(:=)|[;,=\(\):\[\]\.+\-<>\*/@\^]", ) ),
                   ( "STRING",  ("'([^']|(''))*'", ) ),
                   ( "STRING",  ("\"([^\"]|(\"\"))*\"", ) ),
                   ( "CHAR",    ( "#[0-9]+", ) ),
                   ( "CHAR",    ( "#\$[0-9A-Fa-f]+", ) ), ]


tokenizer = tokenization.create (specifications)

try:
    s = """
(* Hey there!
   This is a long comment. *)
{ Hey there!
   This is a long comment. }
process
   output "Hello, World!%n"

3.141592
10
0x10
"""

    for token in tokenizer (s):
        print (token)

except tokenization.Error as e:
    print (e)

    
tokenizer = tokenization.filtered (tokenization.create (specifications), tokenization.strip ([ "SPACE" ]))

try:
    s = """
(* Hey there!
   This is a long comment. *)
{ Hey there!
   This is a long comment. }
process
   output "Hello, World!%n"

3.141592
10
0x10
"""

    for token in tokenizer (s):
        print (token)

except tokenization.Error as e:
    print (e)
