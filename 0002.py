import logging

import combinators.core         as core
import combinators.tokenization as tokenization

logging.basicConfig (level = logging.INFO)
logger = logging.getLogger (__name__)


specifications = [ ( "INT",     ( "[0-9]+", ) ),
                   ( "SPACE",   ( "[ \t]+", ) ),
                   ( "LETTERS", ( "[a-zA-Z]+", ) ), ]

tokenizer = tokenization.create (specifications)

try:
    sequence = core.many (core.token_type ("INT") + core.token_type ("SPACE"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("1 2 3 4 "))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = core.many (core.token_value ("1") + core.token_type ("SPACE") + core.token_value ("2"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("1 2"))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = core.some (core.token_type ("INT") + core.token_type ("SPACE"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("1 2 3 4 "))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = (core.position ()
                + core.token_type ("INT") + core.token_type ("SPACE")
                + core.optional (core.token_type ("INT"))
                + core.position ())

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("1 2"))))
    logger.info (sequence.parse (list (tokenizer ("1 "))))

except core.Error as error:
    logger.info (repr (error))

    
try:
    sequence = (core.many ((core.token_type ("LETTERS") | core.token_type ("INT"))
                                  + core.token_type ("SPACE")))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("1 "))))
    logger.info (sequence.parse (list (tokenizer ("A "))))
    logger.info (sequence.parse (list (tokenizer ("1 A B 2 "))))
    logger.info (sequence.parse (list (tokenizer ("1 A B 2 "))))
    logger.info (sequence.parse (list (tokenizer ("1 A B 2 !"))))

except tokenization.Error as error:
    logger.info (repr (error))

except core.Error as error:
    logger.info (repr (error))


try:
    sequence = core.never ("Expected failure.") | core.many (core.token_type ("LETTERS"))

    logger.info (sequence.name)

    logger.info (sequence.parse (list (tokenizer ("ABC"))))

except tokenization.Error as error:
    logger.info (repr (error))

except core.Error as error:
    logger.info (repr (error))

