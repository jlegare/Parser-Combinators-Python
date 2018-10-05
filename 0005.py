import logging

import combinators.core         as core
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
    logger.info (expression.name)
    logger.info (expression.parse (list (tokenizer ("1 + 2 + 3"))))

    logger.info (expression.name)
    logger.info (expression.parse (list (tokenizer ("1 ^ 2 ^ 3"))))

    logger.info (expression.name)
    logger.info (expression.parse (list (tokenizer ("1 + 2 * 3 + 4"))))

    logger.info (expression.name)
    logger.info (expression.parse (list (tokenizer ("2^3+4^5"))))

    logger.info (expression.name)
    logger.info (expression.parse (list (tokenizer ("1 + 2 - 3 + 4 - 5 + 6"))))

except core.Error as error:
    logger.info (repr (error))
