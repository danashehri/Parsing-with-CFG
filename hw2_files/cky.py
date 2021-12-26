"""
COMS W4705 - Natural Language Processing
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        n = len(tokens) #number of words
        table = defaultdict() #initialization

        for i in range(0, n):
            for j in range(i + 1, n + 1):
                table[(i, j)] = defaultdict() #initialization

                if i + 1 == j:  # diagonal tuple
                    if self.grammar.rhs_to_rules.get((tokens[i],)):
                        k = (tokens[i],)
                        rules = self.grammar.rhs_to_rules[k]
                        #print("k = ", k)
                        #print("rules = ", rules)
                        for rule in rules:
                            table[(i, j)][rule[0]] = tokens[i]

        for length in range(2, n + 1):
            for i in range(0, n - length + 1):
                j = i + length
                for k in range(i + 1, j):
                    for key in self.grammar.rhs_to_rules.keys():
                        for t1 in table[(i, k)]:
                            for t2 in table[(k, j)]:
                                if key == (t1, t2):
                                    #print("key = ", key)
                                    rules = self.grammar.rhs_to_rules.get(key)
                                    #print("rules = ", rules)
                                    for r in rules:
                                        #print((t1, i, k), (t2, k, j))
                                        table[(i, j)][r[0]] = ((t1, i, k), (t2, k, j))

        if self.grammar.startsymbol in table[(0,n)]:
            return True
        else:
            return False

       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3

        """
        TODO: Write the method parse_with_backpointers(self, tokens). You should modify your CKY implementation from part 2, but use 
        (and return) specific data structures. The method should take a list of tokens as input and 
        returns a) the parse table b) a probability table. Both objects should be constructed during 
        parsing. They replace whatever table data structure you used in part 2.
        """

        table= defaultdict()  #initialization
        probs = defaultdict() #initialization
        n = len(tokens)  # number of words

        for i in range(0, n):
            for j in range(i+1, n+1):
                table[(i, j)] = defaultdict() #initialization
                probs[(i, j)] = defaultdict() #initialization

                if i + 1 == j: #diagonal tuple
                    if self.grammar.rhs_to_rules.get((tokens[i],)):
                        k = (tokens[i],)
                        rules = self.grammar.rhs_to_rules[k]
                        for rule in rules:
                            table[(i, j)][rule[0]] = tokens[i]
                            probs[(i, j)][rule[0]] = math.log(rule[2])

        for length in range(2, n + 1):
            for i in range(0, n - length + 1):
                j = i + length
                for k in range(i + 1, j):
                    for key in self.grammar.rhs_to_rules.keys():
                        for t1 in table[(i, k)]:
                            for t2 in table[(k, j)]:
                                if key == (t1,t2):

                                    rules = self.grammar.rhs_to_rules.get(key)
                                    p = probs[(i, k)][t1] + probs[(k, j)][t2]

                                    for r in rules:
                                        log_prob = math.log(r[2]) + p
                                        if r[0] in table[(i, j)]:
                                            #check for the highest probability value
                                            if log_prob > probs[(i, j)][r[0]]:
                                                probs[(i, j)][r[0]] = log_prob
                                                table[(i, j)][r[0]] = ((t1, i, k), (t2, k, j))
                                        else:
                                            probs[(i, j)][r[0]] = log_prob
                                            table[(i, j)][r[0]] = ((t1, i, k), (t2, k, j))
        return table, probs


def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4

    backpointers = chart[(i,j)][nt]
    #print(backpointers)
    if type(backpointers) != str:
        result = (nt,
                  (get_tree(chart, i=backpointers[0][1], j=backpointers[0][2], nt=backpointers[0][0])),
                  (get_tree(chart, i=backpointers[1][1], j=backpointers[1][2], nt=backpointers[1][0])))
        return result
    else:
        result = (nt, backpointers)
        return result

       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks1 =['flights', 'from','miami', 'to', 'cleveland','.']
        print(parser.is_in_language(toks1))
        toks2 = ['miami', 'flights','cleveland', 'from', 'to','.']
        print(parser.is_in_language(toks2))
        #toks3 = ['flights', 'miami', 'from', 'to', 'cleveland', '.'] #true
        #toks3 = ['from', 'flights', 'miami', 'to', 'cleveland', '.'] #true
        #toks3 = ['to', 'miami', 'flgihts', 'from', 'cleveland', '.'] #false
        #toks3 = ['miami', 'to', 'from', 'flights', 'cleveland', '.'] #true
        #print(parser.is_in_language(toks3))
        table,probs = parser.parse_with_backpointers(toks1)
        assert check_table_format(table)
        assert check_probs_format(probs)
        parse_tree = get_tree(table, 0, len(toks1), grammar.startsymbol)
        print(parse_tree)
        
