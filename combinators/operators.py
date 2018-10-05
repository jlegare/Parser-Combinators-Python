import enum
import functools

from . import core

# ----------------------------------------
# PRIVATE FUNCTIONS AND GLOBALS
# ----------------------------------------

class Associativity (enum.Enum):
    LEFT  = 1
    RIGHT = 2

    
# These default constructors always put the operator first ... makes it easier to find later when walking the parse tree.
#
def constructor_infix (lhs, operator, rhs):
    return ( operator, lhs, rhs )


def constructor_prefix (operator, operand):
    return ( operator, operand )

# ----------------------------------------
# EXPORTED FUNCTIONS AND TYPES
# ----------------------------------------

class Operator:
    def __init__ (self, operator, constructor):
        if isinstance (operator, str):
            self.parser = core.token_value (operator)

        else:
            self.parser = operator

        self.constructor = constructor


    def parse (self, tokens, state):
        return self.parser.run (tokens, state)


class OperatorInfix (Operator):
    def __init__ (self, operator, associativity, constructor = constructor_infix):
        super ().__init__ (operator, constructor)
        self.associativity = associativity


    def __repr__ (self):
        return "INFIX %s (%s) -> %s" % ( self.associativity, self.parser, self.constructor.__name__ )


class OperatorPrefix (Operator):
    def __init__ (self, operator, constructor = constructor_prefix):
        super ().__init__ (operator, constructor)
        

    def __repr__ (self):
        return "PREFIX (%s) -> %s" % ( self.parser, self.constructor.__name__ )
    

def build (levels, primary):
    # This SPLIT function is fairly generic: it takes a set of criteria (i.e., functions from a -> Bool), and splits the
    # provided list into sublists, where each sublist contains only items satisfying the corresponding criterion. Any
    # items that do not satisfy any of the supplied criteria are caught and collected into an additional, lastmost
    # sublist.
    #
    def split (criteria, items):
        def classify (augmented_criteria, item):
            def apply (augmented_criterion, item):
                if augmented_criterion[0] (item):
                    return ( augmented_criterion[0], augmented_criterion[1] + [ item ] )

                else:
                    return ( augmented_criterion[0], augmented_criterion[1] )
            

            return map (lambda augmented_criterion : apply (augmented_criterion, item), augmented_criteria)
            

        # Add an item to the criteria which is the complement of the other criteria. This catches anything that falls
        # through the cracks in the supplied criteria.
        #
        extended_criteria = criteria + [ lambda x : not any ([ criterion (x) for criterion in criteria ]) ]

        return map (lambda t : t[1], functools.reduce (classify, items, [ ( criterion, [ ] ) for criterion in extended_criteria ]))


    # For a left-associative operator, what we want is
    #
    #    Expression ->   Expression Operator Primary
    #                  | Primary
    #
    # But clearly that won't work ... it's left-recursive. So we need to instead use
    #
    #    Expression -> Primary (Operator Primary)*
    #
    # but build the result into the appropriate tree. The inner expression of the Kleene group is represented by ATTEMPT,
    # below. The Kleene star itself is the infinite loop that calls ATTEMPT.
    #
    def left_associative (primary, operators, lhs):
        @core.declare_parser ("LEFT ASSOCIATIVE (%s, %s)" % ( primary, operators ))
        def _ (tokens, state):
            class AttemptFailed (Exception):
                pass


            def attempt (tokens, state):
                for operator in operators:
                    try:
                        ( operator_result, operator_state ) = operator.parse (tokens, state)
                        ( rhs, state ) = primary.run (tokens, operator_state)

                        return ( operator.constructor (result, operator_result, rhs), state )

                    except core.Error as error:
                        pass

                raise AttemptFailed ()


            result = lhs

            try:
                while True:
                    ( result, state ) = attempt (tokens, state)

            except AttemptFailed as failed:
                return ( result, state )


        return _


    # For a right-associative operator, what we want is
    #
    #    Expression ->   Primary Operator Expression
    #                  | Primary
    #
    # This is a lot easier than the left-associative case. Notice that we build the parser up by iterating over the
    # operators in reverse: it makes handling the boundary cases simpler.
    #
    def right_associative (primary, operators):
        def apply (constructor):
            def _ (l):
                return constructor (l[0], l[1], l[2])

            return _
        

        @core.declare_parser_suspended ("RIGHT ASSOCIATIVE (%s, %s)" % ( primary, operators ))
        def _ ():
            parser = primary

            for operator in reversed (operators):
                parser = (primary + operator.parser + _ >> apply (operator.constructor)) | parser

            return parser


        return _


    def prefix (primary, operators):
        def apply (constructor):
            def _ (l):
                return constructor (l[0], l[1])

            return _


        @core.declare_parser_suspended ("PREFIX (%s, %s)" % ( primary, operators ))
        def _ ():
            parser = primary

            for operator in operators:
                parser = (operator.parser + _ >> apply (operator.constructor)) | parser

            return parser

        return _


    def build_level (level, criteria, primary):
        operators = list (split (criteria, level))
        term      = prefix (primary, operators[2])

        return right_associative (term, operators[0]).bind (lambda lhs : left_associative (term, operators[1], lhs))


    criteria = [ lambda operator : isinstance (operator, OperatorInfix) and operator.associativity == Associativity.RIGHT,
                 lambda operator : isinstance (operator, OperatorInfix) and operator.associativity == Associativity.LEFT,
                 lambda operator : isinstance (operator, OperatorPrefix) ]
                 
    return functools.reduce (lambda parser, level : build_level (level, criteria, parser), levels, primary)
