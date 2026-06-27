# This file is part of: glwssa-compiler 
# Copyright (C) 2025  @theolaos
# glwssa-compiler is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from glwssa_compiler import *
from glwssa_compiler.ast_nodes import *

files_dir = "tests/levels_test/parser_test/scripts/"
logs_dir = "tests/levels_test/parser_test/logs/"


def test_constants():
    func_name = "test_constants"
    update_path(logs_dir, func_name + ".log")
    log(f"Start of '{func_name}'", tags=["pytest"])

    ast = run_parser_on_file(files_dir + "constants.glwssa")

    expected_ast = Program([
        ProgramName(name="gr_DOK_STATHERES"),
        ConstantDeclaration(name="gr_a", expr=String(value='"γ"')),
        ConstantDeclaration(name="gr_b", expr=String(value="'Γ'")),
        ConstantDeclaration(name="gr_g", expr=Number(value="3")),
        ConstantDeclaration(name="gr_p", expr=Float(value="3.14")),
        ConstantDeclaration(name="gr_d", expr=Boolean(value="true")) 
    ])

    assert ast == expected_ast
    log(f"End", tags=["pytest"])


def test_variables():
    func_name = "test_variables"
    update_path(logs_dir, func_name + ".log")
    log(f"Start of '{func_name}'", tags=["pytest"])

    ast = run_parser_on_file(files_dir + "variables.glwssa")

    expected_ast = Program([
        ProgramName(name='gr_DOK_METABLHTES'),
        VariableDeclaration(variable=Variable(name='gr_AG', var_type=IntType)),
        VariableDeclaration(variable=Variable(name='en_i', var_type=IntType)),
        VariableDeclaration(variable=Variable(name='en_j', var_type=IntType)),
        VariableDeclaration(variable=Variable(name='gr_SP', var_type=RealType)),
        VariableDeclaration(variable=Variable(name='gr_LOG', var_type=BoolType)),
        VariableDeclaration(variable=Variable(name='gr_ON', var_type=ArrayType(val_dim=[Number(value='1'), Number(value='2'), Number(value='3'), Number(value='4'), Number(value='5'), Number(value='6')], val_type=CharType))),
        VariableDeclaration(variable=Variable(name='gr_ONOMA', var_type=CharType)),
        VariableDeclaration(variable=Variable(name='gr_EPITHETO', var_type=CharType)),
    ])

    assert ast == expected_ast
    log(f"End", tags=["pytest"])


def test_write_read():
    func_name = "test_write_read"
    update_path(logs_dir, func_name + ".log")
    log(f"Start of '{func_name}'", tags=["pytest"])

    ast = run_parser_on_file(files_dir + "write_read.glwssa")

    expected_ast = Program([
        ProgramName(name='gr_DOK_EKTYPWSE_DIABASE'),
        Write(
            expression=[
                BinaryOperation(
                    left=Number(value='10'), 
                    operator='PLUS', 
                    right=BinaryOperation(
                        left=BinaryOperation(
                            left=Number(value='5'), 
                            operator='FDIV', 
                            right=Number(value='6')), 
                        operator='MUL', 
                        right=BinaryOperation(
                            left=Number(value='4'), 
                            operator='PLUS', 
                            right=Number(value='8')
                        )
                    )
                )
            ]
        ),
        Write(
            expression=[
                ArrayIndex(
                    name='gr_ON', 
                    index_dim=[Number(value='5')], 
                    var_type=None
                )
            ]
        ),
        Write(
            expression=[
                String(value="'Για σου κόσμε'"), 
                BinaryOperation(
                    left=Number(value='10'), 
                    operator='PLUS', 
                    right=Number(value='5')
                ), 
                ArrayIndex(name='gr_ON', index_dim=[
                    BinaryOperation(
                        left=Number(value='5'), 
                        operator='MINUS', 
                        right=BinaryOperation(
                            left=Number(value='1'), 
                            operator='FDIV', 
                            right=Variable(name='en_A', var_type=None)
                        )
                    )], var_type=None
                )
            ]
        ),
        Read(
            variable_list=[
                Variable(name='gr_AG', var_type=None), 
                Variable(name='gr_SP', var_type=None), 
                Variable(name='gr_ON', var_type=ArrayType(val_dim=[Number(value='6')], val_type=None))]),
    ])

    assert ast == expected_ast
    log(f"End", tags=["pytest"])


def test_assign():
    func_name = "test_assign"
    update_path(logs_dir, func_name + ".log")
    log(f"Start of '{func_name}'", tags=["pytest"])

    ast = run_parser_on_file(files_dir + "assign.glwssa")

    expected_ast = Program([
        ProgramName(name='gr_DOK_EKCHWRHSH'),
        VariableAssignement(target='gr_SP', expr=Number(value='0')),
        VariableAssignement(target='gr_LOG', 
            expr=BinaryOperation(
                left=BinaryOperation(
                    left=Variable(name='gr_AG', var_type=None), 
                    operator='GT', 
                    right=Number(value='0')), 
                operator='AND', 
                right=BinaryOperation(
                    left=Variable(name='gr_AG', var_type=None), 
                    operator='LTE', 
                    right=Number(value='5')
                )
            )
        ),
    ])

    assert ast == expected_ast
    log(f"End", tags=["pytest"])


def test_if_elif_else_nested():
    func_name = "test_if_elif_else_nested"
    update_path(logs_dir, func_name + ".log")
    log(f"Start of '{func_name}'", tags=["pytest"])

    ast = run_parser_on_file(files_dir + "if_elif_else_nested.glwssa")

    expected_ast = Program([
        ProgramName(name='gr_DOK_AN_EMFWLEYMENH'),
        If(
            branches=[
                Branch(
                    condition=BinaryOperation(
                        left=Variable(name='gr_AG', var_type=None), 
                        operator='GT', 
                        right=Number(value='0')
                    ), 
                    body=Block(
                        body=[
                            VariableAssignement(target='gr_SP', expr=Variable(name='gr_AG', var_type=None)), 
                            Write(expression=[Number(value='0')])
                        ]
                    )
                ), 
                Branch(
                    condition=BinaryOperation(
                        left=Variable(name='gr_AG', var_type=None), 
                        operator='GT', 
                        right=Number(value='100')
                    ), 
                    body=Block(
                        body=[
                            VariableAssignement(target='gr_SP', expr=Number(value='1')), 
                            If(branches=[
                                Branch(
                                    condition=BinaryOperation(
                                        left=Variable(name='gr_AG', var_type=None), 
                                        operator='LTE', 
                                        right=Number(value='100')
                                    ), 
                                    body=Block(
                                        body=[
                                            Write(expression=[String(value='"ΓΙΑ ΣΟΥ ΚΟΣΜΕ"')])
                                        ]
                                    )
                                )
                            ], else_branch=Block(body=[])
                            )
                        ]
                    )
                ), 
                Branch(
                    condition=BinaryOperation(
                        left=Variable(name='gr_AG', var_type=None), 
                        operator='GT', 
                        right=Number(value='1000')
                    ), 
                    body=Block(
                        body=[
                            VariableAssignement(target='gr_SP', expr=Number(value='1'))
                        ]
                    )
                )
            ], else_branch=Block(body=[])),

    ])

    assert ast == expected_ast
    log(f"End", tags=["pytest"])


def test_loops():
    func_name = "test_loops"
    update_path(logs_dir, func_name + ".log")
    log(f"Start of '{func_name}'", tags=["pytest"])

    ast = run_parser_on_file(files_dir + "loops.glwssa")

    expected_ast = Program([
        ProgramName(name='gr_DOK_EPANALHPSEIS'),
        While(
            condition=BinaryOperation(left=Number(value='10'), operator='EQ', right=Number(value='10')), 
            body=Block(
                body=[
                    Write(expression=[String(value='"ΓΙΑ ΣΟΥ ΚΟΣΜΕ"')])
                ]
            )
        ),
        For(
            counter=Variable(name='en_i', var_type=None), 
            from_expr=Number(value='1'), 
            to_expr=Number(value='10'), 
            step=BinaryOperation(
                left=Number(value='5'), 
                operator='PLUS', 
                right=Number(value='6')
            ), 
            body=Block(
                body=[
                    Write(expression=[Variable(name='en_i', var_type=None)])
                ]
            )
        ),
        For(
            counter=Variable(name='en_i', var_type=None), 
            from_expr=Number(value='1'), 
            to_expr=Number(value='10'), 
            step=Number(value='1'), 
            body=Block(
                body=[
                    Write(expression=[Variable(name='en_i', var_type=None)])
                ]
            )
        ),
        For(
            counter=Variable(name='en_i', var_type=None), 
            from_expr=Number(value='1'), 
            to_expr=Number(value='10'), 
            step=Number(value='1'), 
            body=Block(
                body=[
                    Write(expression=[String(value='"Εμφωλευμένη 1"')]), 
                    For(
                        counter=Variable(name='en_j', var_type=None), 
                        from_expr=Number(value='10'), 
                        to_expr=Number(value='1'), 
                        step=UnaryOperator(operator='MINUS', operand=Number(value='1')), 
                        body=Block(body=[
                            Write(expression=[String(value='"Εμφωλευμένη 2"')])
                        ])
                    )
                ]
            )
        ),
        Do(
            condition=BinaryOperation(left=Number(value='10'), operator='EQ', right=Number(value='10')), 
            body=Block(body=[
                Write(expression=[String(value='"ΚΑΛΗΝΥΧΤΑ ΚΟΣΜΕ"')])
            ])
        ),
    ])

    assert ast == expected_ast
    log(f"End", tags=["pytest"])