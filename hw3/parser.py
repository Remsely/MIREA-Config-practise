import os
import sys
import json
from ply import lex
from ply import yacc


tokens = (
    'NUMBER',
    'STRING',
    'NAME',
    'COMMENT',
    'OPEN',
    'CLOSE'
)

t_NAME = r'[A-Za-z][A-Za-z0-9]*'
t_OPEN = r'\('
t_CLOSE = r'\)'

t_ignore = ' \t\n'


def t_STRING(t):
    r'"([^"]*)"'
    t.value = t.value[1:-1]
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_COMMENT(t):
    r';[^\n]*'
    pass


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


def p_program(p):
    'program : s_exp_list'
    p[0] = p[1]


def p_s_exp_list(p):
    '''s_exp_list : s_exp s_exp_list
                | s_exp'''

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_s_exp(p):
    '''s_exp : data
            | NAME data
            | OPEN s_exp_list CLOSE
            | NAME OPEN s_exp_list CLOSE'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = {p[1]: p[2]}
    elif len(p) == 4:
        if isinstance(p[2][0], dict):
            result_dict = {}
            for d in p[2]:
                result_dict.update(d)
            p[0] = result_dict
        else:
            p[0] = p[2]
    else:
        p[0] = {p[1]: p[3]}


def p_data(p):
    '''data : STRING
            | NUMBER'''
    p[0] = p[1]


def p_error(p):
    print(f"Syntax error at line {p.lineno}, position {p.lexpos}, token '{p.value}'")


parser = yacc.yacc()

if len(sys.argv) != 2:
    print("Usage: python your_script.py input_file")
    sys.exit(1)

input_file = sys.argv[1]
current_directory = os.getcwd()
file_path = os.path.join(current_directory, input_file)

data = ''.join(open(file_path, 'r', encoding='UTF-8').readlines())

result = parser.parse(data)
# print(result)
json_result = json.dumps(result[0], ensure_ascii=False, indent=2)
print(json_result)
