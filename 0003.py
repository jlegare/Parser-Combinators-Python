import logging

import combinators.core         as core
import combinators.tokenization as tokenization

logging.basicConfig (level = logging.INFO)
logger = logging.getLogger (__name__)


def f (list):
    logger.info ("PARSED: %r" % list)

    return list


specifications = [ ( "INT",     ( "[0-9]+", ) ),
                   ( "SPACE",   ( "[ \t]+", ) ),
                   ( "LETTERS", ( "[a-zA-Z]+", ) ), ]

tokenizer = tokenization.create (specifications)

letters = core.token_type ("LETTERS")
space   = core.token_type ("SPACE")

try:
    sequence = letters + space >> f

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("ABC DEF GHI JKL"))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = core.many (letters + space) >> f

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("ABC DEF GHI JKL"))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = core.many (letters + space >> f)

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("ABC DEF GHI JKL"))))

except core.Error as error:
    logger.info (repr (error))

    
