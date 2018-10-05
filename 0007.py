import logging

import combinators.core         as core
import combinators.panic        as panic
import combinators.tokenization as tokenization

logging.basicConfig (level = logging.INFO)
logger = logging.getLogger (__name__)


specifications = [ ( "INT",     ( "[0-9]+", ) ),
                   ( "SPACE",   ( "[ \t]+", ) ),
                   ( "LETTERS", ( "[a-zA-Z]+", ) ), ]

tokenizer = tokenization.create (specifications)

try:
    sequence = panic.until (core.token_type ("LETTERS"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("1234AB CD"))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = panic.until (core.token_type ("LETTERS"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("1 2 3 4 AB CD"))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = panic.until (core.token_type ("LETTERS"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("1234"))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = panic.during (core.token_type ("LETTERS"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("AB CD"))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = panic.during (core.token_type ("LETTERS") | core.token_type ("INT"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("ABCD1234 EFGH"))))

except core.Error as error:
    logger.info (repr (error))


try:
    sequence = panic.during (core.token_type ("LETTERS"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("1234"))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = panic.during (core.token_type ("LETTERS"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("ABCD"))))

except core.Error as error:
    logger.info (repr (error))

    
