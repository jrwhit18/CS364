import sys
from typing import Generator, Tuple
import re


class Lexer:
    # class variables

    #TODO
    # sci not _ before the dot, spliter takes off - signs in the middle
    # fixed escaped "
    line_num = 0
    tokensDict = {"+": "PLUS", "(": "LPAREN", ")": "RPAREN", "{": "LBRACE", "}": "RBRACE", "[":"LBRACKET",
                  "]":"RBRACKET", "-": "MINUS", "*": "MULT", "/": "DIVIDE", "%": "MOD", "||": "OR",
                  "&&": "AND", "==": "EQUALITY",  "<<": "LBITWISE", ">>": "RBITWISE",
                   "<=": "LESS_THAN_EQUAL", ">=": "GREATER_THAN_EQUAL", "!=": "NOT_EQUAL", "=": "ASSIGNMENT", "<": "LESS_THAN",
                  ">": "GREATER_THAN", ";": "SEMICOLON",",": "COMMA",
                  "if": "KEYWORD", "print": "KEYWORD", "bool": "KEYWORD", "else": "KEYWORD", "false": "KEYWORD",
                  "true": "KEYWORD", "float": "KEYWORD", "int": "KEYWORD", "while": "KEYWORD",
                  "char": "KEYWORD", "return": "KEYWORD", "!": "NOT"}

    # fn - file name we are lexing
    def __init__(self, fn: str):

        try:
            self.f = open(fn)
        except IOError:
            print("File {} not found".format(fn))
            print("Exiting")
            sys.exit(1)  # can't go on


    @staticmethod
    def is_string(token):
        if re.findall('"[^"]*"', token):
            return token, "STRING", Lexer.line_num
        else:
            return token, "INVALID SYNTAX", Lexer.line_num

    @staticmethod
    def is_comment(token):
        # checking if it starts with // followed by as many characters(0 and more)
        if re.findall('^//.*', token):
            #if yes then it is comment, so we return empty strings(check my_print for the reason).
            pass
        else:
            # if not we check if the token is a string or not.
            return Lexer.is_string(token)

    #@staticmethod
    #def is_function_call(token):


    @staticmethod
    def valid_ID(token):
        # invalid ID
        # - start with number
        # - only _

        # check if valid ID
        # check if it starts with either a letter or _
        if re.findall('^[_a-zA-Z][_a-zA-Z0-9]*', token):     # check to make sure there are only legal signs for an ID
            # if the array created has more than one element in it
            #then it means there was an illegal sign which broke
            #the entery in to more than one piece. Therefore the token is not a valid ID.(example : hell!o)
            if len(re.findall('[_a-zA-Z][_a-zA-Z0-9]*', token)) > 1:
                # if not a valid ID we check to see if it's a comment or not
                if Lexer.is_comment(token) is None:
                    pass
                else:
                    return Lexer.is_comment(token)
            #otherwise we return the token as valid ID
            return token, "ID", Lexer.line_num
        else:
            # if not a valid ID we check to see if it's a comment or not
            if Lexer.is_comment(token) is None:
                pass
            else:
                return Lexer.is_comment(token)

    @staticmethod
    def is_numeric(token):
        if re.findall('^[0-9][.]?[e][-0-9]?[0-9]$|' # checks if it is any combination of leagal scientific notation
                 '^[0-9]+[0-9_]*[.]?(?!_)[0-9_]*[0-9][e][-]?[0-9]$|'
                 '^[0-9]+[0-9_]*[.]?(?!_)[0-9_]*[0-9][e][-]?[0-9][0-9_]*[0-9]$|'
                 '^[0-9][.]?[e][-]?[0-9][0-9_]*[0-9]$'
                 ,token): #scientific notation
            return token, "FLOAT", Lexer.line_num
        elif re.findall('^[0-9][0-9_]*[0-9][.][0-9][0-9_]*[0-9]$|' # all legal combinations of characters that can be floats
                       '^[0-9][.][0-9][0-9_]*[0-9]$|'
                       '^[0-9][.][0-9]$|'
                       '^[0-9][0-9_]*[0-9][.][0-9]$'
                        , token):  # float
            return token, "FLOAT", Lexer.line_num
        elif re.findall('^[0-9][0-9_]*[0-9]$|^[0-9]$', token): # checks if it is either a 2+ digit int or a 1 digit int
            if len(re.findall('^[0-9][0-9_]*[0-9]$|^[0-9]$', token)[0]) != len(token): # makes sure there are not any things in caught up in the token like 10g9
                if Lexer.valid_ID(token) is None:
                    pass
                else:
                    return Lexer.valid_ID(token)
            else:
                return token, "INTLIT", Lexer.line_num
        else:
            if Lexer.valid_ID(token) is None:
                pass
            else:
                return Lexer.valid_ID(token)

    @staticmethod
    def create_split_patt():
        escape_chars = {"+", "(", ")", "[", "*", "||", "%"}
        keywords = {"if", "print", "bool", "else", "false", "true", "float", "int", "while", "main", "char"}

        splits = ['(' + token + ') | ' for token in Lexer.tokensDict.keys() if
                  token not in escape_chars and token not in keywords]
        s = ['(\\' + token + ') | ' for token in escape_chars]

        allToken = splits

        total = r'\s | (//.*) | ("[^\"]*") | (\+) | (\() | (\)) | (\[) | (\?) | (\*) | (\%) |'
        for token in allToken:
            total += token
        total = total[:-2]
        return total

    def token_generator(self) -> Generator[Tuple[int, str], None, None]:
        """
        Returns the tokens of the language
        """

        pattern = Lexer.create_split_patt()
        split_patt = re.compile(pattern, re.VERBOSE)

        for line in self.f:
            Lexer.line_num += 1
            tokens = (t for t in split_patt.split(line) if t)
            for t in tokens:
                # if it is not a known token, start cascade of method
                if not Lexer.tokensDict.get(t):
                    if Lexer.is_numeric(t) is None:
                        pass
                    else:
                        yield Lexer.is_numeric(t)
                # otherwise yield token with the line number
                else:
                    yield (Lexer.tokensDict.get(t), t, Lexer.line_num)
        yield ("EOF", "EOF", Lexer.line_num)


    @staticmethod
    def my_print(tokens): #function to print the output nice and clean.
        token, name, linenum = tokens
        # check if they are empty string then we know they are comments, so we avoid displaying them.
        if token and name and linenum:
            # making equal spaces for displaying output to make the output look clean.
            length1 = len(token)
            length2 = len(name)
            dist1 = 20 - length1
            dist2 = 20 - length2
            spaces1 = " "*dist1
            spaces2 = " "*dist2

            print(token, spaces1, name, spaces2, linenum)


if __name__ == "__main__":
    lex = Lexer("test.sluc")
    g = lex.token_generator()
    while True:
        try:
            #print(next(g))
            Lexer.my_print(next(g))
        except StopIteration:
            print("Done")
            break

#     file = sys.argv[1:] # takes input from comandline
#
#
#     if len(file) != 1:
#         print("File name does not exist, exiting")
#         exit()
#     lex = Lexer(file[0])
#
#     lex = Lexer("test.sluc")
#
#     g = lex.token_generator()
#     print("""Token                 Name                  Line Number
# ---------------------------------------------------------""")
#     while True:
#         try:
#             #print(next(g))
#             Lexer.my_print(next(g))
#         except StopIteration:
#             print("Done")
#             break