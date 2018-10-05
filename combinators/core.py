import types

# ----------------------------------------
# PRIVATE FUNCTIONS
# ----------------------------------------

def collapse (outer):
    result = [ ]

    for inner in outer:
        if isinstance (inner, list):
            for item in inner:
                result.append (item)

        elif isinstance (inner, str):
            result.append (inner)

        else:
            result.append (inner)

    return result

# ----------------------------------------
# EXPORTED FUNCTIONS AND TYPES
# ----------------------------------------

class Error (Exception):
    def __init__ (self, message, state):
        self.message = message
        self.state   = state


    def __repr__ (self):
        return "PARSE ERROR (%r, %r)" % ( self.message, self.state )


class State:
    def __init__ (self, current_offset = 0, maximum_offset = 0):
        self.current_offset = current_offset
        self.maximum_offset = maximum_offset


    def __repr__ (self):
        return "STATE (%r, %r)" % ( self.current_offset, self.maximum_offset )


    def eof (self):
        return self.current_offset >= self.maximum_offset


def declare_parser (name):
    def decorator (parser):
        return ParserType (parser, name)


    return decorator


class ParserType:
    def __init__ (self, parser, name):
        self.parser = parser
        self.name   = name
        self.run    = getattr (parser, "run", parser)


    def __repr__ (self):
        return self.name


    def parse (self, tokens):
        try:
            if hasattr (self.parser, "run"):
                return self.parser.run (tokens, State (maximum_offset = len (tokens)))[0]

            else:
                return self.parser (tokens, State (maximum_offset = len (tokens)))[0]

        except Error as error:
            token = tokens[error.state.maximum_offset] if len (tokens) > error.state.maximum_offset else "<EOF>"

            raise Error ("%s %s" % ( error.message, token ), error.state)


    def run (self, tokens, state):
        raise NotImplementedError ("INTERNAL ERROR")


    def __add__ (self, other):
        # This could be written in terms of BIND and PURE:
        #
        # _ = self.bind (lambda left : other.bind (lambda right : pure (collapse ([ left, right ]))))
        #
        @declare_parser ("SEQUENCE (%s, %s)" % ( self, other ))
        def _ (tokens, state):
            ( left_value, left_state )   = self.run (tokens, state)
            ( right_value, right_state ) = other.run (tokens, left_state)

            return ( collapse ([ left_value, right_value ]), right_state )
            

        return _


    def __or__ (self, other):
        @declare_parser ("ALTERNATIVE (%s, %s)" % ( self, other ))
        def _ (tokens, state):
            try:
                return self.run (tokens, state)

            except Error as error:
                return other.run (tokens, state)


        return _


    def __rshift__ (self, f):
        # This could be written in terms of BIND and PURE:
        #
        # _ = self.bind (lambda value : pure (f (value)))
        #
        @declare_parser ("(%s) >> %s" % ( self, f.__name__ ))
        def _ (tokens, state):
            ( value, new_state ) = self.run (tokens, state)

            return ( f (value), new_state )


        return _


    def bind (self, f):
        @declare_parser ("(%s) >>= %s" % ( self, f.__name__ ))
        def _ (tokens, state):
            ( value, new_state ) = self.run (tokens, state)

            return f (value).run (tokens, new_state)


        return _


def pure (value):
    @declare_parser ("PURE (%s)" % value)
    def _ (tokens, state):
        return ( value, state )


    return _


def many (parser):
    @declare_parser ("MANY (%s)" % parser)
    def _ (tokens, state):
        result = [ ]

        try:
            while True:
                ( value, state ) = parser.run (tokens, state)

                result.append (value)

        except Error as error:
            return ( result, State (state.current_offset, error.state.maximum_offset) )


    return _


def some (parser):
    @declare_parser ("SOME (%s)" % parser)
    def _ (tokens, state):
        ( value, first_state ) = parser.run (tokens, state)
        ( values, new_state ) = many (parser).run (tokens, first_state)

        return ( [ value ] + values, new_state )


    return _


def optional (parser):
    _ = parser | pure (None)

    return _


def one (predicate):
    @declare_parser ("ONE (%s)" % predicate.name)
    def _ (tokens, state):
        if state.eof ():
            raise Error ("Encountered <EOF>.", state)

        else:
            token = tokens[state.current_offset]

            if predicate (token):
                offset    = state.current_offset + 1
                new_state = State (offset, max (offset, state.maximum_offset))

                return ( token, new_state )

            else:
                raise Error ("Expected %s, encountered %s." % ( predicate, token.value ), state)


    return _


def never (message):
    # NEVER is a parser that never succeeds. It's useful as the identity for ORing parsers together.
    #
    @declare_parser ("NEVER")
    def _ (tokens, state):
        raise Error ("Never always fails. %s" % message, state)
    

    return _


def predeclared (name):
    def declare (self, parser):
        self.run  = parser.run
        self.name = parser.name

    @declare_parser ("PREDECLARED (%s)" % name)
    def _ (tokens, state):
        raise NotImplementedError ("Predeclared parser %s was never declared." % name)


    _.declare = types.MethodType (declare, _)

    return _


def declare_parser_suspended (name):
    def decorator (parser):
        @declare_parser ("SUSPENDED (%s)" % name)
        def _ (tokens, state):
            return parser ().run (tokens, state)

        return _


    return decorator


def position ():
    @declare_parser ("POSITION")
    def _ (tokens, state):
        if state.eof ():
            return ( "<EOF>", state )

        else:
            return ( tokens[0].start, state )


    return _


def token_type (type):
    predicate      = lambda token : token.type == type
    predicate.name = "TOKEN TYPE (%s)" % type

    return one (predicate)


def token_value (value):
    predicate      = lambda token : token.value == value
    predicate.name = "TOKEN VALUE (%s)" % value

    return one (predicate)
