import regex
import unicodedata

# ----------------------------------------
# EXPORTED FUNCTIONS AND TYPES
# ----------------------------------------

def filtered (tokenizer, predicate):
    # Return a tokenizer that contains only tokens satisfying PREDICATE.
    #
    def _ (input):
        return filter (predicate, tokenizer (input))

    return _


def strip (types):
    # Define a predicate that can be combined with FILTERED () to remove tokens whose type is in TYPES.
    #
    def _ (token):
        return token.type not in types


    return _


class Error (Exception):
    def __init__ (self, position, message):
        self.message  = message
        self.position = position


class TokenPosition:
    def __init__ (self, line, offset):
        self.line   = line
        self.offset = offset


    def __repr__ (self):
        return "TOKEN POSITION (%r, %r)" % ( self.line, self.offset )


class Token:
    def __init__ (self, type, value, start = None, end = None, case_sensitive = True):
        self.type           = type
        self.value          = value
        self.start          = start
        self.end            = end
        self.case_sensitive = case_sensitive


    def __eq__ (self, other):
        def normalize (s, case_sensitive = True):
            return unicodedata.normalize ("NFKD", s if case_sensitive else s.casefold ())


        return (self.type == other.type 
                and normalize (self.value, self.case_sensitive) == normalize (other.value, other.case_sensitive))


    def __repr__ (self):
        return "TOKEN (%r, %r, %r, %r)" % ( self.type, self.value, self.start, self.end )


def create (specifications):
    def compile (specification):
        ( token_name, arguments ) = specification

        return ( token_name, regex.compile (*arguments) )


    def index (specifications):
        indexed = { }

        for ( index, specification ) in enumerate (specifications):
            ( type, _ ) = specification

            if type not in indexed:
                indexed[type] = index

        return indexed


    compiled = list (map (compile, specifications))
    indexed  = index (specifications)

    def match (specifications, input, current_offset, position):
        def attempt (specification):
            ( type, pattern ) = specification

            matched = pattern.match (input, current_offset)

            if matched is None:
                return None

            else:
                return ( type, matched.group (0) )


        attempts = reversed (sorted (filter (lambda x : x is not None, map (attempt, specifications)),
                                     key = lambda t : ( t[1], -indexed[t[0]] )))

        try:
            ( type, value ) = next (attempts)

            newline_count = value.count ("\n")
            end_line = position.line + newline_count

            if newline_count == 0:
                end_offset = position.offset + len (value)

            else:
                end_offset = len (value) - value.rfind ("\n") - 1

            return Token (type, value, position, TokenPosition (end_line, end_offset))
        
        except StopIteration:
            s = input.splitlines ()[position.line - 1]

        raise Error (s, position)


    def tokenizer (input):
        length = len (input)
        position = TokenPosition (1, 0)
        i = 0
        while i < length:
            token = match (compiled, input, i, position)
            yield token
            position = token.end
            i += len (token.value)

    return tokenizer
