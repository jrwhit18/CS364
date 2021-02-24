# import re
#
# str = "-4"
#
# print(int(str))
#
# token = "laks5678emi"
#
# # if re.findall('^[0-9]', token):
# #     print ("wrong id")
# # else:
# #     print ("might be okay")
#
# # check if valid ID
# if re.findall('^[_a-zA-Z][_a-zA-Z0-9]*', token):
#     if len(re.findall('[_a-zA-Z][_a-zA-Z0-9]*', token)) > 1:
#         print(token, "INVLAID SYNTAX")
#     #print(re.findall('[_a-zA-Z][_a-zA-Z0-9]*', token))
#     print(token, "ID")
# else:
#
#     print(token, "INVLAID SYNTAX")
# from lexer import Lexer
#
# escape_chars = set(["+","(",")","[","?","*","||",".","^","!"])
#
# splits = ['('+token+') |' for token in Lexer.tokensDict.keys() if token not in escape_chars]
# s = ['(\\'+token+') |' for token in escape_chars]
#
# allToken = s + splits
#
# total = r'\s | (//\.*) | ("[^\"]*") |'
# for token in allToken:
#     total += token
#
# total = total[:-1]
# print(total)




