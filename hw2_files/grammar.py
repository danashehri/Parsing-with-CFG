"""
COMS W4705 - Natural Language Processing
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""
import math
import sys
from collections import defaultdict
from math import fsum

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        # TODO, Part 1

        lhs_sum = []
        lhs = self.lhs_to_rules #lists of rules(tuples) where tuple[0] is the lhs
        #key : non terminal, v : list of its tuples

        for non_terminal, list in lhs.items():
            for tuple in list:
                #check if non-terminal is uppercase
                if tuple[0].isupper():
                    prob = tuple[2]
                    lhs_sum.append(prob)
            #check if sum == 1
            print(round(math.fsum(lhs_sum), 2))
            if round(math.fsum(lhs_sum), 2) == 1.0:
                lhs_sum = []
            else:
                return False

        return True


if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        if grammar.verify_grammar():
            print("Valid PCFG in CNF")
        else:
            ValueError("Not Valid PCFG in CNF")

        
