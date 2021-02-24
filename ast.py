"""
SLU-C Abstract Syntax Trees
An abstract syntax tree (AST) is a data structure that represents
the concrete (text) syntax of a program
"""
from typing import Sequence, Union, Optional
# Use a class hierarchy to represent types.


"""
Program → { FunctionDef }
 FunctionDef → Type id ( Params ) { Declarations Statements }
 Params → Type id { , Type id } | ε
 Declarations → { Declaration }
 Declaration → Type Identifier ;
 Type → int | bool | float
 Statements → { Statement }
 Statement → ; | Block | Assignment | IfStatement | WhileStatement
 | PrintStmt | ReturnStmt
 ReturnStmt → return Expression ;
 Block → { Statements }
 Assignment → id = Expression ;
 IfStatement → if ( Expression ) Statement [ else Statement ]
 WhileStatement → while ( Expression ) Statement
 PrintStmt → print( PrintArg { , PrintArg })
 PrintArg → Expression | stringlit
 Expression → Conjunction { || Conjunction }
 Conjunction → Equality { && Equality }
 Equality → Relation [ EquOp Relation ]
 Relation → Addition [ RelOp Addition ]
 Addition → Term { AddOp Term }
 Term → Factor { MulOp Factor }
 Factor → [ UnaryOp ] Primary
 UnaryOp → - | !
 Primary → id | intlit | floatlit | true | false | ( Expression )
 RelOp → < | <= | > | >=
 AddOp → + | -
 MulOp → * | / | %
 EquOp → == | !=
// Test #1 Euler project proble
"""


class Expr:
    """
    Base class for expressions
    """
    pass


class FunctionDef:
    def __init__(self, t, id: Expr, params, decls, stmts):
        # provide type hints for all of the parameters
        # Decls should be a dictionary
        # Key: id
        # Value: Type
        self.t = t
        self.id = id
        self.params = params
        self.decls = decls
        self.stmts = stmts

    def typecheck(self, env_value, envtype, funcs):
        # tyecheck each statement

        self.stmts.typecheck(env_value,envtype, funcs)

    def __str__(self):
        return "{0} {1} ({2}) {5}\n{3}{4} ".format(str(self.t), str(self.id), str(self.params), str(self.decls),
                                                   str(self.stmts), "{")

    def eval(self,values ,funcs) -> Union[int, float, bool]:
        # an environment maps identifiers to values
        # parameters or local variables
        # to evaluate a function you evaluate all of the statements
        # within the environment
        declsDict = self.decls.buildDict()
        paramsDict = self.params.buildDict()
        typeEnv = {**paramsDict,**declsDict} # building a different enviornment 
        env = {} # create the environment for a new function
        retVal = None # return value starts as None
        env = {self.params.buildList()[i]: values[i] for i in range(len(self.params.buildList()))}
        # puts all the params in an new function. for main it just starts as empty
        if self.decls:
            self.decls.eval(env) # eval ends up putting all the declarations in the enviornment
        if self.params:
            self.params.eval(env) # same with params
        if self.stmts:
            retVal = self.stmts.eval(env, funcs) # if there is a return value we save it. We eval the other statment regardless
            self.typecheck(env, typeEnv, funcs) # type check everything
            return retVal # return the return value.






class Program:

    def __init__(self, funcs: Sequence[FunctionDef]):
        self.funcs = funcs

    def __str__(self):
        acc = ""
        for func in self.funcs:
            acc = acc + str(func)
        return acc

    def eval(self):
        self.funcs[0].eval({}, self.funcs)
        # we know from how we built our parser that the first function is always main so we just eval that to start
        # regardless of where it appears in our file

class Primary(Expr):
    pass


class Param:
    def __init__(self, params: Sequence[str]):
        self.params = params

    def __str__(self):
        output = ""
        for typ, id in self.params:
            output = output + typ + " " + id + ", "
        return output[:-2]

       
       
    # build dict and build list are utility functions because we originally designed our
    # params in parser as a list of tuples but that really was difficult to work with
    # as an environment so we can build a dict or a list when we need to.    
    def buildDict(self):
        env = {}
        for type,id in self.params:
            env[id] = type

        return env

    def buildList(self):
        idlst = []
        for type, id in self.params:
            idlst.append(id)
        return idlst

    def eval(self, env):
        for param in self.params:
            if param[1] not in env.keys():
                env[param[1]] = None # params are always none the param[1] is because the param[0] is the id and [1] is the value
                                     # if there are any past parameters that gets hanled in function def


class Declaration:
    def __init__(self, typ: str, id: Expr):
        self.typ = typ
        self.id = id

    def __str__(self):
        return "{0} {1};".format(self.typ, self.id)

    def buildDict(self):
        return self.typ, self.id
    def eval(self, env):
        env[self.id] = None


class Declarations(Declaration):
    def __init__(self, decls: [Declaration]):
        self.decls = decls

    def __str__(self):
        acc = "\t"
        for decs in self.decls:
            acc = acc + str(decs) + "\n\t"
        return acc[:-1]



    def buildDict(self):
        env = {}
        for decl in self.decls:
            type, id = decl.buildDict()
            env[id] = type
        return en

    def eval(self, env):
        for dec in self.decls:
            dec.eval(env) # puts the decls in the environment but they haven't been assigned yet so they are none


class Stmt:
    # def __init__(self, stmt):
    pass


class Stmts(Stmt):
    """
    Statements → { Statement }
    """
    def __init__(self, stmts: [Stmt]):
        self.stmts = stmts

    def __str__(self):
        acc = "\t"
        for stmt in self.stmts:
            acc = acc + str(stmt) + '\n\t'
        return acc[:-1]
    
    #type checking all the statement in our statements using a loop(iterate through all the statement)
    def typecheck(self, env_value,envtype ,funcs):
        for stmt in self.stmts:
            stmt.typecheck(env_value,envtype, funcs)
   
    #evaluating all the statement in our statements using a loop(iterate through all the statement)
    def eval(self, env, funcs):
        for stmt in self.stmts:
            # if it is a return statement we return the evaluation
            if type(stmt) == ReturnStmt:
                return stmt.eval(env, funcs)
            stmt.eval(env, funcs)


class Block:
    """
    Block → { Statements }
    """
    
    def __init__(self, block: Sequence[Stmts]):
        self.block = Stmts
    
    def __str__(self):
        acc = ""
        for stmts in self.block:
            acc = acc + str(stmts) + '\n'
        return acc
    # Making sure that we typecheck all the statements in our block
    def typecheck(self, env_value,envtype ,funcs):
        for stmts in self.block:
            stmts.typecheck(env_value,envtype ,funcs)


class IfStmt(Stmt):
    """
    IfStatement → if ( Expression ) Statement [ else Statement ]
    """
    
   # use Optional for cases with else statement
    def __init__(self, expr: Expr, stmt: Stmt, elseStmt: Optional[Stmt] = None):
        self.expr = expr
        self.stmt = stmt
        self.elseStmt = elseStmt

    def __str__(self):
        if self.elseStmt == None:
            return "if ({0}) {2}\n \t {1}\n{3}".format(self.expr, self.stmt, "{", "}")
        else:
            return "if ({0}) {3}\n \t {1} \n{4} else {5}\n \t {2}\n{6}".format(self.expr, self.stmt, self.elseStmt, "{",
                                                                             "}", "{", "}")
    #typechecking the expression in our if
    def typecheck(self, env_value, envtype,funcs):
        #TODO envtype might be wrong
        self.expr.typeof(envtype)
    #evaluating, true we return the statement inside our if
    def eval(self, env, funcs):
        if self.expr.eval(env, funcs):
            return self.stmt.eval(env, funcs)
        #if there is else we return the statement in our else.(if our if is true we never get here since 
        #we have aready callled the statement in if
        elif self.elseStmt is not None:
            return self.elseStmt.eval(env, funcs)


class ReturnStmt(Stmt):
    """
    ReturnStmt → return Expression ;
    """
    def __init__(self, expr: Expr):
        self.expr = expr

    def __str__(self):
        return "return {0};".format(self.expr)
    #type checking the return statement
    def typecheck(self, env_value,envtype, funcs):
        self.expr.typeof(envtype)
    # returning the value of the expression
    def eval(self, env, funcs):
        return self.expr.eval(env, funcs)


class WhileStmt(Stmt):
    """
     WhileStatement → while ( Expression ) Statement
    """   
    def __init__(self, expr: Expr, stmt: Stmts):
        self.expr = expr
        self.stmt = stmt

    def __str__(self):
        return "while ({0}) {2} \n{1}\n{3}".format(self.expr, self.stmt, "{", "}")
    #type checking the expression
    def typecheck(self, env_value ,envtype, funcs):
        self.expr.typeof(envtype)
    #while the expression is true we run the statement in the while
    def eval(self, env, funcs):
        while self.expr.eval(env, funcs):
            self.stmt.eval(env, funcs)


class AssignStmt(Stmt):
    """
    Assignment → id = Expression ;
    """
    def __init__(self, id: str, expr: Expr):
        self.id = id
        self.expr = expr

    def __str__(self):
        return "{0} = {1};".format(self.id, self.expr)

    def typecheck(self, env_value, envtype, funcs):
        # Making a dict have the type in string form( making it easy to evaluate the type of id and expression
        typedict = {int: "int", float: "float" , bool: "bool"}
        # getting the class type of right
        right_type = type(self.expr.eval(env_value, funcs))
        #using typedict to have the type in string form
        if right_type in typedict:
            right_type = typedict[right_type]
        # getting the left type using our environment type
        left_type = envtype[self.id]
        # if sides are not from same type
        if left_type != right_type:
            # and if one side is a bool, then raise an error.
            if left_type == "bool" or right_type == "bool":
                raise SLUCInvalidTypeError("Error: Invalid Type")

    # eval the expression and put in environment for that specific id
    def eval(self, env, funcs):
        env[self.id] = self.expr.eval(env, funcs)


class PrintStmt(Stmt):
    """
    PrintStmt → print( PrintArg { , PrintArg })
    """
    def __init__(self, printarg: Expr):
        self.printarg = printarg

    def __str__(self):
        stri = "print("
        for value in self.printarg:
            stri = stri + str(value) + ","
        return stri[:-1] + ");"
    # type checking all the print arguments 
    def typecheck(self, env_value,envtype, funcs):
        for arg in self.printarg:
            arg.typeof(envtype)
    # printing all the arguments
    def eval(self, env, funcs):
        for printargs in self.printarg:
            #if printing a string, we get rid of '""' to make the outpul look clean
            if (type(printargs.eval(env, funcs)) == str):
                print(printargs.eval(env, funcs)[1:-1], end="\n")
            else:
                print(printargs.eval(env, funcs), end="\n")


class BinaryExpr(Expr):

    def __init__(self, operator: str, left: Expr, right: Expr):
        self.left = left
        self.right = right
        self.operator = operator
        self.exprdict = {'+': lambda x, y: x + y,
                         '*': lambda x, y: x * y,
                         '&&': lambda x, y: x and y,
                         '||': lambda x, y: x or y,
                         '==': lambda x, y: x == y,
                         '!=': lambda x, y: x != y,
                         '/': lambda x, y: x / y,
                         '%': lambda x, y: x % y,
                         '>': lambda x, y: x > y,
                         '<': lambda x, y: x < y,
                         '>=': lambda x, y: x >= y,
                         '<=': lambda x, y: x <= y,
                         '-': lambda x, y: x - y}

    def __str__(self):
        return "({0} {1} {2})".format(str(self.left), self.operator, str(self.right))

    def eval(self, env, funcs):
        t = self.typeof(env)
        return self.exprdict[self.operator](self.left.eval(env, funcs), self.right.eval(env, funcs))

    def typeof(self, env) -> type:

        left = self.left.typeof(env)
        right = self.right.typeof(env)

        if self.operator in {"&&", "||"}:
            if left == bool and right == bool:
                return bool
            else:
                raise SLUCInvalidTypeError("ERROR: Type Error")
        if self.operator in {"<=", "<", ">", ">=", "!=", "=="}:
            if left == bool and (right == float or right == int):
                raise SLUCInvalidTypeError("ERROR: Type Error")
            elif right == bool and (left == float or left == int):
                raise SLUCInvalidTypeError("ERROR: Type Error")
            else:
                return bool

        if self.operator in {"+", "*", "-", "%", "/"}:

            if left == bool or right == bool:
                raise SLUCInvalidTypeError("ERROR: Type Error")
            if left == float or right == float:
                return float
            # if self.operator == "/" and (self.left.eval(env) % self.right.eval(env) != 0):
            #     return float
            return int


class FunctionCallExpr(Expr):
    def __init__(self, id, arguments: Sequence[Expr]):  # Sequence[Expr]
        self.id = id
        self.args = arguments

    def __str__(self):
        acc = self.id + "("
        for arg in self.args:
            acc = acc + str(arg) + ", "
        return acc[:-2] + ")"

    def eval(self, env, funcs):
        # f(2*a, z, 99, g(x))
        # lookup FunctionDef using id
        # call eval on the function def passings the values
        evaledArgs = []
        for arg in self.args:
            evaledArgs.append(arg.eval(env, funcs))
        for func in funcs:
            if func.id == self.id:
                return func.eval(evaledArgs, funcs)

    def typeof(self, env) -> type:
        pass #TODO do this

class UnaryOp(Expr):
    def __init__(self, tree: Expr, sign: str):
        self.tree = tree
        self.sign = sign

    def __str__(self):
        return "{0}({1})".format(self.sign, str(self.tree))

    def typeof(self, env):
        self.tree.typeof(env)

    def eval(self, env, funcs):
        if self.sign == "!":
            return not self.tree.eval(env, funcs)
        else:
            return - self.tree.eval(env, funcs)


class IntLitExpr(Expr):

    def __init__(self, boo: str):
        self.boo = boo

    def __str__(self):
        return str(self.boo)

    def eval(self, env, funcs):
        return int(self.boo)

    def typeof(self, env) -> type:
        return int


class FloatExpr(Expr):

    def __init__(self, boo: str):
        self.boo = boo

    def __str__(self):
        return str(self.boo)

    def eval(self, env, funcs):
        return float(self.boo)

    def typeof(self, env) -> type:
        return float


class BoolExpr(Expr):

    def __init__(self, boo: str):
        self.boo = boo

    def __str__(self):
        return str(self.boo)

    def eval(self, env, funcs):
        if self.boo == "true":
            return True
        else:
            return False

    def typeof(self, env) -> type:
        return bool


class StringExpr(Expr):

    def __init__(self, boo: str):
        self.boo = boo

    def __str__(self):
        return str(self.boo)

    def eval(self, env, funcs):
        return str(self.boo)

    def typeof(self, env) -> type:
        return str


class IDExpr(Expr):

    def __init__(self, boo: str):
        self.boo = boo

    def __str__(self):
        return str(self.boo)

    def eval(self, env, funcs):
        return env[self.boo]

    def typeof(self, env) -> type:
        typedict = {"int" : int, "float": float, "bool": bool}
        if env[self.boo] in typedict:
            return typedict[env[self.boo]]
        else:
            return type(env[self.boo])


class SLUCInvalidTypeError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message
