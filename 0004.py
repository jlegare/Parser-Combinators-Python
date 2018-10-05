import logging

import combinators.core         as core
import combinators.tokenization as tokenization

logging.basicConfig (level = logging.INFO)
logger = logging.getLogger (__name__)


specifications = [ ( "SPACE",   ( "[ \t]+", ) ),
                   ( "LETTERS", ( "[a-zA-Z]+", ) ), ]

tokenizer = tokenization.create (specifications)

letters = core.predeclared ("LETTERS")
space   = core.token_type ("SPACE")

try:
    sequence = core.many (letters + space)

    logger.info (sequence.name)
    letters.declare (core.token_type ("LETTERS"))
    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("ABC DEF GHI JKL"))))

except core.Error as error:
    logger.info (repr (error))
