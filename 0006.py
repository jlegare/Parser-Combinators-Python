import logging

import combinators.core         as core
import combinators.draw         as draw
import combinators.operators    as operators
import combinators.tokenization as tokenization


logging.basicConfig (level = logging.INFO)
logger = logging.getLogger (__name__)

specifications = [ ( "INTEGER", ( "[0-9]+", ) ),
                   ( "SPACE",   ( "[ \t]+", ) ),
                   ( "PLUS",    ( "\+", ) ),
                   ( "MINUS",   ( "-", ) ),
                   ( "TIMES",   ( "\*", ) ),
                   ( "DIVIDE",  ( "/", ) ),
                   ( "POWER",   ( "\^", ) ), ]

tokenizer = tokenization.filtered (tokenization.create (specifications), tokenization.strip ([ "SPACE" ]))

integer = core.token_type ("INTEGER")
primary = integer

operator_table = [ [ operators.OperatorInfix ("^", operators.Associativity.RIGHT), 
                     operators.OperatorInfix ("$", operators.Associativity.RIGHT), ],
                   [ operators.OperatorInfix ("*", operators.Associativity.LEFT),
                     operators.OperatorInfix ("/", operators.Associativity.LEFT), ],
                   [ operators.OperatorInfix ("+", operators.Associativity.LEFT),
                     operators.OperatorInfix ("-", operators.Associativity.LEFT), ], ]

expression = operators.build (operator_table, primary)


try:
    logger.info ("PARSING: 1 + 2 + 3")
    logger.info ("\n" + draw.draw (expression.parse (list (tokenizer ("1 + 2 + 3"))), True))

    logger.info ("PARSING: 1 ^ 2 ^ 3")
    logger.info ("\n" + draw.draw (expression.parse (list (tokenizer ("1 ^ 2 ^ 3"))), True))

    logger.info ("PARSING: 1 + 2 * 3 + 4")
    logger.info ("\n" + draw.draw (expression.parse (list (tokenizer ("1 + 2 * 3 + 4"))), True))

    logger.info ("PARSING: 2^3+4^5")
    logger.info ("\n" + draw.draw (expression.parse (list (tokenizer ("2^3+4^5"))), True))

    logger.info ("PARSING 1 + 2 - 3 + 4 - 5 + 6")
    logger.info ("\n" + draw.draw (expression.parse (list (tokenizer ("1 + 2 - 3 + 4 - 5 + 6"))), True))

except core.Error as error:
    logger.info (repr (error))


try:
    logger.info ("PARSING: 1 + 2 + 3")
    tree = expression.parse (list (tokenizer ("1 + 2 + 3")))
    graph = draw.draw (tree)
    graph.render ("0007")
    
except combinators.Error as error:
    logger.info (repr (error))


