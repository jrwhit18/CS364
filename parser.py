import sys

from lexer import Lexer
from ast import *
from ast import SLUCInvalidTypeError as InvalidTypeError

"""
  The SLU-C Grammar:
  Program         →  { FunctionDef }
  FunctionDef     →  Type id ( Params ) { Declarations Statements }
  Params          →  Type id { , Type id } | ε
  Declarations    →  { Declaration }
  Declaration     →  Type  id  ;
  Type            →  int | bool | float
  Statements      →  { Statement }
  Statement       →  ; | Block | Assignment | IfStatement |     
                     WhileStatement |  PrintStmt | ReturnStmt
  ReturnStmt      →  return Expression ;
  Block           →  '{' Statements '}'
  Assignment      →  id = Expression ;
  IfStatement     →  if ( Expression ) Statement [ else Statement ]
  WhileStatement  →  while ( Expression ) Statement  
  PrintStmt       →  print(PrintArg { , PrintArg })
  PrintArg        →  Expression | stringlit 
  Expression      →  Conjunction { || Conjunction }
  Conjunction     →  Equality { && Equality }
  Equality        →  Relation [ EquOp Relation ]
  Relation        →  Addition [ RelOp Addition ]
  Addition        →  Term { AddOp Term }
  Term            →  Factor { MulOp Factor }
  Factor          →  [ UnaryOp ] Primary
  UnaryOp         →  - | !
  Primary         →  id | intlit | floatlit | ( Expression )
  RelOp           →  < | <= | > | >=   
  AddOp           →  + | -
  MulOp           →  * | / | %
  EquOp           →  == | != 
"""


class Parser:

    def __init__(self, fn: str):

        self.lex = Lexer(fn)
        self.tg = self.lex.token_generator()
        self.currtok = next(self.tg)

    """
        Expr  →  Term { (+ | -) Term }
        Term  → Fact { (* | / | %) Fact }
        Fact  → [ - ] Primary
        Primary  → ID | INTLIT | ( Expr )
        Recursive descent parser. Each non-terminal corresponds 
        to a function.
        -7  -(7 * 5)  -b   unary minus
    """

    # top-level function that will be called

    def program(self):
        """
            Program         →  { FunctionDef }
        """
        functionDefDecls = {}
        functions = []
        while self.currtok[0] != "EOF":
            if self.currtok[0] == "RBRACE":
                self.currtok = next(self.tg)
            f = self.functionDef(functionDefDecls)
            functions.append(f)
        for i in range(len(functions)):
            if functions[i].id == "main":
                functions.insert(0, functions.pop(i))
        functions = functions[:-1]
        return Program(functions)

    def functionDef(self, functionDefDecls):
        """
        FunctionDef     →  Type id ( Params ) { Declarations Statements }
        """
        decls = {}
        try:
            t = self.type(decls, functionDefDecls)
        except SLUCInvalidTypeError:
            return FunctionDef(None,None,None,None,None)
        if self.currtok[1] == "ID":
            id = self.currtok[0]
            decls[id] = t
            self.currtok = next(self.tg)
        if self.currtok[1] == "(":
            self.currtok = next(self.tg)
            parm = self.params(decls, functionDefDecls)
        else:
            raise SLUCSyntaxError("ERROR: Missing left parenthesis on line {0}".format(self.currtok[2]))

        if self.currtok[1] == ")":
            self.currtok = next(self.tg)
        else:
            raise SLUCSyntaxError("ERROR: Missing right parenthesis on line {0}".format(self.currtok[2]))

        if self.currtok[1] == "{":
            self.currtok = next(self.tg)
            decl = self.declarations(decls, functionDefDecls)
            stmts = self.stmts(decls, functionDefDecls)
        else:
            raise SLUCSyntaxError("ERROR: Missing left brace on line {0}".format(self.currtok[2]))
        functionDefDecls[id] = t
        return FunctionDef(t, id, parm, decl, stmts)

    def params(self, decls, functionDefDecls):
        """
        Params          →  Type id { , Type id } | ε
        """
        params = [] # used to be a list []
        try:
            t = self.type(decls, functionDefDecls)
        except SLUCInvalidTypeError:
            return Param(params)
        if self.currtok[1] == "ID":
            id = self.currtok[0]
            if id in decls.keys():
                raise SLUCDuplicateReferenceError(
                    "ERROR: {0} on line {1} is duplicately delcared.".format(id, self.currtok[2]))
            decls[id] = t
            self.currtok = next(self.tg)
            params.append((t, id)) # used to be params.append((t, id))
            while self.currtok[1] == ",":
                self.currtok = next(self.tg)

                t = self.type(decls, functionDefDecls)
                if self.currtok[1] == "ID":
                    id = self.currtok[0]
                    if id in decls.keys():
                        raise SLUCDuplicateReferenceError(
                            "ERROR: {0} on line {1} is duplicately delcared.".format(id, self.currtok[2]))
                    decls[id] = t
                    self.currtok = next(self.tg)
                    params.append((t, id))
        return Param(params)

    def declarations(self, decls, functionDefDecls):
        """
        Declarations    →  { Declaration }
        """
        decl_list = []
        while self.currtok[1] in {'int', 'bool', 'float'}:
            d = self.declaration(decls, functionDefDecls)
            decl_list.append(d)

        return Declarations(decl_list)

    def declaration(self, decls, functionDefDecls):
        """
        Declaration     →  Type  id  ;
        """
        t = self.type(decls, functionDefDecls)
        if self.currtok[1] == "ID":
            tmp = self.currtok
            if tmp[0] in decls.keys():
                raise SLUCDuplicateReferenceError(
                    "ERROR: {0} on line {1} is duplicately delcared.".format(tmp[0], tmp[2]))
            decls[tmp[0]] = t
            self.currtok = next(self.tg)
            if self.currtok[1] == ";":
                self.currtok = next(self.tg)
            else:
                raise SLUCSyntaxError("ERROR: Missing semicolon on line {0}".format(self.currtok[2]))

            return Declaration(str(t), tmp[0])

    def type(self, decls, functionDefDecls):
        """
        Type  →  int | bool | float
        """
        if self.currtok[1] in {'int', 'bool', 'float'}:
            tmp = self.currtok[1]
            self.currtok = next(self.tg)
            return tmp
        else:
            raise SLUCInvalidTypeError("ERROR: Invalid type on line number {0}.".format(self.currtok[2]))

    def ifstmt(self, decls, functionDefDecls):
        """
        IfStatement →  if ( Expression ) Statement [ else Statement ]
        """
        if self.currtok[1] == "if":
            self.currtok = next(self.tg)
            if self.currtok[1] == "(":
                self.currtok = next(self.tg)
                exp = self.expression(decls, functionDefDecls)
            else:
                raise SLUCSyntaxError("ERROR: Missing left parenthesis on line {0}".format(self.currtok[2]))
            if self.currtok[1] == ")":
                self.currtok = next(self.tg)
            else:
                raise SLUCSyntaxError("ERROR: Missing right parenthesis on line {0}".format(self.currtok[2]))

            s = self.stmt(decls, functionDefDecls)

            if self.currtok[1] == "else":
                self.currtok = next(self.tg)
                if self.currtok[1] == "{":
                    elseStmt = self.stmt(decls, functionDefDecls)

                    return IfStmt(exp, s, elseStmt)
            return IfStmt(exp, s)

    def returnstmt(self, decls, functionDefDecls):
        """
        ReturnStmt      →  return Expression ;
        """
        if self.currtok[1] == "return":
            self.currtok = next(self.tg)
            ret = self.expression(decls, functionDefDecls)
        if self.currtok[1] == ";":
            self.currtok = next(self.tg)
            return ReturnStmt(ret)
        elif self.currtok[1] == "(":  # instead else raise exception
            self.currtok = next(self.tg)
            params = []
            while self.currtok[1] != ")":
                p = self.expression(decls, functionDefDecls)
                params.append(p)
                if self.currtok[1] == ",":
                    self.currtok = next(self.tg)
            self.currtok = next(self.tg)
            funCall = FunctionCallExpr(str(ret), params)
            if (self.currtok[1] == ";"):
                self.currtok = next(self.tg)
            return ReturnStmt(funCall)
        else:
            raise SLUCSyntaxError("ERROR: Missing semicolon on line {0}".format(self.currtok[2]))

    def whilestmt(self, decls, functionDefDecls):
        """
        WhileStatement  →  while ( Expression ) Statement
        """
        if self.currtok[1] == "while":
            self.currtok = next(self.tg)
            if self.currtok[1] == "(":
                self.currtok = next(self.tg)
                exp = self.expression(decls, functionDefDecls)
            else:
                raise SLUCSyntaxError("ERROR: Missing left parenthesis on line {0}".format(self.currtok[2]))
            if self.currtok[1] == ")":
                self.currtok = next(self.tg)
            else:
                raise SLUCSyntaxError("ERROR: Missing right parenthesis on line {0}".format(self.currtok[2]))

            s = self.stmt(decls, functionDefDecls)

            return WhileStmt(exp, s)

    def assignment(self, decls, functionDefDecls):
        """
        Assignment →  id = Expression ;
        """
        if self.currtok[1] == "ID":
            id = self.currtok[0]
            if id not in decls.keys():
                if id not in functionDefDecls.keys():
                    raise SLUCReferenceBeforeAssignment(
                        "ERROR: {0} is reference before assignment on line {1}".format(id, self.currtok[2]))
            self.currtok = next(self.tg)
            if self.currtok[0] == "ASSIGNMENT":
                self.currtok = next(self.tg)
                expr = self.expression(decls, functionDefDecls)
            else:
                raise SLUCSyntaxError("ERROR: Invalid assignment statement on line {0}".format(self.currtok[2]))
            if self.currtok[0] == "SEMICOLON":
                self.currtok = next(self.tg)
                return AssignStmt(str(id), expr)
            elif self.currtok[1] == "(": # instead else raise exception
                self.currtok = next(self.tg)
                params = []
                while self.currtok[1] != ")":
                    p = self.expression(decls, functionDefDecls)
                    params.append(p)
                    if self.currtok[1] == ",":
                        self.currtok = next(self.tg)
                self.currtok = next(self.tg)
                funCall = FunctionCallExpr(str(expr), params)
                if(self.currtok[1] == ";"):
                    self.currtok = next(self.tg)
                return AssignStmt(str(id), funCall)

        return self.printstmt(decls, functionDefDecls)

    def stmts(self, decls, functionDefDecls):
        """
        Statements  →  { Statement }
        """
        stmt_list = []

        while self.currtok[1] in {"ID", "{", "print", "return", ";", "if", "while"}:
            s = self.stmt(decls, functionDefDecls)
            stmt_list.append(s)
        return Stmts(stmt_list)

    def block(self, decls, functionDefDecls):
        """
        Block →  '{' Statements '}'
        """
        stmts_list = []
        while self.currtok[0] != "RBRACE":
            s = self.stmts(decls, functionDefDecls)
            stmts_list.append(s)
        self.currtok = next(self.tg)
        return Stmts(stmts_list)

    def stmt(self, decls, functionDefDecls):
        """
        Statement → ; | Block | Assignment | IfStatement |
                     WhileStatement |  PrintStmt | ReturnStmt
        """
        if self.currtok[0] == "SEMICOLON":
            self.currtok = next(self.tg)

        if self.currtok[0] == "LBRACE":
            self.currtok = next(self.tg)
            return self.block(decls, functionDefDecls)
        if self.currtok[1] == "ID":
            return self.assignment(decls, functionDefDecls)
        if self.currtok[1] == "print":
            return self.printstmt(decls, functionDefDecls)
        if self.currtok[1] == "while":
            return self.whilestmt(decls, functionDefDecls)
        if self.currtok[1] == "return":
            return self.returnstmt(decls, functionDefDecls)
        if self.currtok[1] == "if":
            return self.ifstmt(decls, functionDefDecls)

        return self.printarg(decls, functionDefDecls)  # we thnk this is one of the lowest level function

    def printstmt(self, decls, functionDefDecls):
        """
        PrintStmt →  print(PrintArg { , PrintArg })
        """
        exprs = []
        if self.currtok[1] == "print":
            self.currtok = next(self.tg)
            if self.currtok[1] == "(":
                self.currtok = next(self.tg)
                parg = self.printarg(decls, functionDefDecls)
                exprs.append(parg)
                while self.currtok[1] == ",":
                    self.currtok = next(self.tg)
                    parg = self.printarg(decls, functionDefDecls)
                    exprs.append(parg)
            else:
                raise SLUCSyntaxError("ERROR: Missing left parenthesis on line {0}".format(self.currtok[2]))
            if self.currtok[1] == ")":
                self.currtok = next(self.tg)
            else:
                raise SLUCSyntaxError("ERROR: Missing right parenthesis on line {0}".format(self.currtok[2]))
            if self.currtok[0] == "SEMICOLON":
                self.currtok = next(self.tg)
                return PrintStmt(exprs)
            else:
                raise SLUCSyntaxError("ERROR: Missing semicolon on line {0}".format(self.currtok[2] - 1))

        return self.printarg(decls, functionDefDecls)

    def printarg(self, decls, functionDefDecls):
        """
        PrintArg → Expression | stringlit
        """

        if self.currtok[1] == "STRING":
            tmp = self.currtok[0]
            self.currtok = next(self.tg)
            left = StringExpr(str(tmp))
        elif self.currtok[0] in functionDefDecls:
            id = self.currtok[0]
            self.currtok = next(self.tg)
            if self.currtok[1] == "(": # instead else raise exception
                self.currtok = next(self.tg)
                params = []
                while self.currtok[1] != ")":
                    p = self.primary(decls, functionDefDecls)
                    params.append(p)
                    if self.currtok[1] == ",":
                        self.currtok = next(self.tg)
                funCall = FunctionCallExpr(id, params)
                self.currtok = next(self.tg)
                return funCall
        else:
            left = self.expression(decls, functionDefDecls)

        return left

    def expression(self, decls, functionDefDecls):
        """
        Expression →  Conjunction { || Conjunction }
        """
        left = self.conjunction(decls, functionDefDecls)
        while self.currtok[0] in {Lexer.tokensDict.get("||")}:
            tmp = self.currtok
            self.currtok = next(self.tg)  # advance to the next token
            # because we matched a +
            right = self.conjunction(decls, functionDefDecls)

            left = BinaryExpr(str(tmp[1]), left, right)

        return left

    def conjunction(self, decls, functionDefDecls):
        """
        Conjunction →  Equality { && Equality }
        """

        left = self.equality(decls, functionDefDecls)
        while self.currtok[0] in {Lexer.tokensDict.get("&&")}:
            tmp = self.currtok
            self.currtok = next(self.tg)  # advance to the next token
            # because we matched a +
            right = self.equality(decls, functionDefDecls)
            left = BinaryExpr(str(tmp[1]), left, right)

        return left

    def equality(self, decls, functionDefDecls):
        """
        Equality →  Relation [ EquOp Relation ]
        """
        left = self.relation(decls, functionDefDecls)
        if self.currtok[0] in {Lexer.tokensDict.get("=="), Lexer.tokensDict.get("!=")}:
            tmp = self.currtok
            self.currtok = next(self.tg)  # advance to the next token
            # because we matched a +
            right = self.relation(decls, functionDefDecls)
            left = BinaryExpr(str(tmp[1]), left, right)

        return left

    def relation(self, decls, functionDefDecls):  # a < b
        """
        Relation  →  Addition [ RelOp Addition ]
        """
        left = self.addition(decls, functionDefDecls)

        if self.currtok[0] in {Lexer.tokensDict.get(">"), Lexer.tokensDict.get("<"), Lexer.tokensDict.get(">="),
                               Lexer.tokensDict.get("<=")}:
            tmp = self.currtok
            self.currtok = next(self.tg)  # advance to the next token
            # because we matched a +
            right = self.addition(decls, functionDefDecls)
            left = BinaryExpr(str(tmp[1]), left, right)

        return left

    def addition(self, decls, functionDefDecls) -> Expr:
        """
        Addition →  Term { AddOp Term }
        """

        left = self.term(decls, functionDefDecls)
        while str(self.currtok[0]) in {Lexer.tokensDict.get("+"), Lexer.tokensDict.get("-")}:
            tmp = self.currtok
            self.currtok = next(self.tg)  # advance to the next token
            # because we matched a +
            right = self.term(decls, functionDefDecls)
            left = BinaryExpr(str(tmp[1]), left, right)

        return left

    def term(self, decls, functionDefDecls) -> Expr:
        """
        Term  → Fact { * Fact }
        """
        left = self.fact(decls, functionDefDecls)

        while self.currtok[0] in {Lexer.tokensDict.get("*"), Lexer.tokensDict.get("/"), Lexer.tokensDict.get("%")}:
            tmp = self.currtok
            self.currtok = next(self.tg)
            right = self.fact(decls, functionDefDecls)
            left = BinaryExpr(str(tmp[1]), left, right)

        return left

    def fact(self, decls, functionDefDecls) -> Expr:
        """
        Fact  → [ UnaryOp ] Primary
        """

        if self.currtok[0] in {Lexer.tokensDict.get("-"), Lexer.tokensDict.get("!")}:
            tmp = self.currtok[1]
            self.currtok = next(self.tg)
            tree = self.primary(decls, functionDefDecls)
            return UnaryOp(tree, tmp)

        return self.primary(decls, functionDefDecls)

    def primary(self, decls, functionDefDecls) -> Expr:
        """
        Primary  → id | intlit | floatlit | true | false | ( Expression )
        """
        if self.currtok[1] == "(":
            self.currtok = next(self.tg)
            tree = self.expression(decls, functionDefDecls)
            if self.currtok[1] == ")":
                self.currtok = next(self.tg)
                return tree
            else:
                # use the line number from your token object
                raise SLUCSyntaxError("ERROR: Missing right paren on line {0}".format(self.currtok[2]))

        if Lexer.is_numeric(self.currtok[0])[1] == "FLOAT":  # using ID in expression
            tmp = self.currtok
            self.currtok = next(self.tg)
            return FloatExpr(str(tmp[0]))
        # parse an ID

        if self.currtok[1] in {"true", "false"}:
            tmp = self.currtok
            self.currtok = next(self.tg)
            return BoolExpr(str(tmp[1]))

        if Lexer.valid_ID(self.currtok[0])[1] == "ID":  # using ID in expression
            if self.currtok[0] not in decls.keys():
                if self.currtok[0] not in functionDefDecls.keys():
                    raise SLUCReferenceBeforeAssignment(
                        "{0} reference before assignment on line {1}".format(self.currtok[0], self.currtok[2]))
            tmp = self.currtok
            self.currtok = next(self.tg)
            return IDExpr(str(tmp[0]))
        # parse an integer literal

        if Lexer.is_numeric(self.currtok[0])[1] == "INTLIT":  # using ID in expression
            tmp = self.currtok
            self.currtok = next(self.tg)
            return IntLitExpr(str(tmp[0]))

        raise SLUCSyntaxError("ERROR: Unexpected token {0} on line {1}".format(self.currtok[1], self.currtok[2]))


# create our own exception by inheriting
# from Python's exception
class SLUCSyntaxError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message


class SLUCInvalidTypeError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message


class SLUCReferenceBeforeAssignment(Exception):
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message


class SLUCDuplicateReferenceError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message


if __name__ == '__main__':
    file = sys.argv[1:]  # takes input from comandline
    if len(file) != 1:
        print("File name does not exist, exiting")
        exit()
    par = Parser(file[0])
    #par = Parser("test.sluc")
    try:
        a = par.program()
        a.eval()
    except (SLUCDuplicateReferenceError, SLUCReferenceBeforeAssignment, SLUCInvalidTypeError, SLUCSyntaxError,
            InvalidTypeError) as err:
        print(err)
