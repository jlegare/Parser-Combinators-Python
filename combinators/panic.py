from . import core

# ----------------------------------------
# EXPORTED FUNCTIONS AND TYPES
# ----------------------------------------

def during (parser):
    @core.declare_parser ("PANIC DURING (%s)" % parser)
    def _ (tokens, state):
        discarded = [ ]
        old_state = state

        try:
            while not old_state.eof ():
                ( _, new_state ) = parser.run (tokens, old_state)
                discarded += tokens[old_state.current_offset:new_state.current_offset]
                old_state = new_state

        except core.Error as error:
            return ( discarded, old_state )

        raise core.Error ("Encountered <EOF> while panicking.", state)
                

    return _


def until (parser):
    @core.declare_parser ("PANIC UNTIL (%s)" % parser)
    def _ (tokens, state):
        discarded = [ ]
        old_state = state

        while not old_state.eof ():
            try:
                ( _, _ ) = parser.run (tokens, old_state)

                return ( discarded, old_state )

            except core.Error as error:
                discarded += [ tokens[old_state.current_offset] ]
                offset = old_state.current_offset + 1
                old_state = core.State (offset, max (offset, old_state.maximum_offset))

        raise core.Error ("Encountered <EOF> while panicking.", state)
                

    return _
