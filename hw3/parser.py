import ply.lex as lex
from ply import yacc
import json


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
    print ("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


def p_program(p):
    'program : s_exp_list'
    p[0] = p[1]


def p_s_exp_list(p):
    '''s_exp_list : s_exp s_exp_list
                | s_exp'''
    print(len(p), list(p))
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

data = '''
(groups
    ("ИКБО-1-20"
    "ИКБО-2-20"
    "ИКБО-3-20"
    "ИКБО-4-20"
    "ИКБО-5-20"
    "ИКБО-6-20"
    "ИКБО-7-20"
    "ИКБО-8-20"
    "ИКБО-9-20"
    "ИКБО-10-20"
    "ИКБО-11-20"
    "ИКБО-12-20"
    "ИКБО-13-20"
    "ИКБО-14-20"
    "ИКБО-15-20"
    "ИКБО-16-20"
    "ИКБО-24-20")
students (
(age 19 group "ИКБО-4-20" name "Иванов И.И.")
(age 18 group "ИКБО-5-20" name "Петров П.П.")
(age 18 group "ИКБО-5-20" name "Сидоров С.С."))
subject "Конфигурационное управление")
'''

result = parser.parse(data)

print(result)
json_result = json.dumps(result, indent=2)
print(json_result)