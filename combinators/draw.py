import functools
import itertools

import graphviz

# ----------------------------------------
# PRIVATE FUNCTIONS AND GLOBALS
# ----------------------------------------

counter = itertools.count ()


def decorator (element_name, default_properties = { }):
    def _ (f):
        def __ (content, properties = { }):
            return element (tags (element_name, { **default_properties, **properties }), f (content))


        return __


    return _


def element (tags, content):
    return tags[0] + content + tags[1]


def tags (name, properties):
    def serialize (properties = { }):
        return " ".join ([ name + "=\"" + properties[name] + "\"" for name in properties ])


    return ( "<" + name + (" " if len (properties) > 0 else "") + serialize (properties) + ">", "</" + name + ">" )

# ----------------------------------------
# EXPORTED FUNCTIONS
# ----------------------------------------

def html_like (content):
    return "<" + content + ">"


@decorator ("table", { "border": "0" })
def table (rows):
    return functools.reduce (lambda result, row : result + row, rows, "")


@decorator ("tr")
def row (cells):
    return functools.reduce (lambda result, cell : result + cell, cells, "")


@decorator ("td", { "align": "left" })
def cell (content):
    return content


@decorator ("font", { "face": "Helvetica", "point-size": "8" })
def label (s):
    return s


def label_token (value, type):
    return html_like (table ([ row ([ cell (label ("VALUE:"), { "align": "right" }), cell (value) ]),
                               row ([ cell (label ("TYPE:"), { "align": "right" }), cell (type) ]) ]))


def draw (tree, as_text = False):
    symbols = { "middle":       "\u251c\u2500 ",
                "end":          "\u2514\u2500 ",
                "continuation": "\u2502  ",
                "last":         "   ",
                "root":         "" }

    def get_id ():
        return str (next (counter))


    def children_of (node):
        if isinstance (node, tuple):
            return node[1:]

        elif hasattr (node, "children_of"):
            return node.children_of ()

        else:
            return [ ]


    def graphical (node, parent_id, graph):
        def show (node):
            styles = { "node": { "fontname": "Courier",
                                 "fontsize": "10",
                                 "shape":    "box",
                                 "style":    "filled", },
                       "edge": {  } }


            if isinstance (node, tuple):
                return { **{ "label": label_token (node[0].value, node[0].type) }, **styles["node"] }

            elif hasattr (node, "show"):
                return node.show (True)

            else:
                return { **{ "label": label_token (node.value, node.type) }, **styles["node"] }


        id = get_id ()

        graph.node (id, **show (node))

        if parent_id:
            graph.edge (parent_id, id)

        for child in children_of (node):
            graphical (child, id, graph)

        return id


    def textual (node, indent, symbol):
        def show (node):
            if isinstance (node, tuple):
                return "%s: %s" % ( node[0].value, node[0].type )

            elif hasattr (node, "show"):
                return node.show (False)

            else:
                return "%s: %s" % ( node.value, node.type )


        line     = indent + symbol + show (node)
        children = children_of (node)

        if len (children) == 0:
            return line

        else:
            if symbol == symbols["middle"]:
                indent = indent + symbols["continuation"]

            elif symbol == symbols["root"]:
                indent = indent + symbols["root"]
                
            else:
                indent = indent + symbols["last"]

            leaders = [ symbols["middle"] ] * (len (children) - 1) + [ symbols["end"] ]
            lines   = [ textual (node, indent, symbol) for ( node, symbol ) in zip (children, leaders) ]

            return "\n".join ([ line ] + lines)


    if as_text:
        graph = textual (tree, "", symbols["root"])

    else:
        graph = graphviz.Digraph (format = "svg")

        graphical (tree, None, graph)

    return graph


