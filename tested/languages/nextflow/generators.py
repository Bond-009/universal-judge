import json
import shlex

from typing import Literal, cast
from pathlib import Path

from tested.datatypes import AdvancedStringTypes, BasicStringTypes
from tested.languages.conventionalize import submission_file
from tested.languages.preparation import (
    PreparedContext,
    PreparedExecutionUnit,
    PreparedTestcase,
    PreparedTestcaseStatement,
)
from tested.languages.utils import convert_unknown_type
from tested.serialisation import (
    Expression,
    FunctionCall,
    FunctionType,
    Identifier,
    Statement,
    StringType,
    Value,
    VariableAssignment,
)
from tested.testsuite import MainInput

def convert_value(value: Value) -> str:
    assert isinstance(value, StringType), f"Invalid literal: {value!r}"
    if value.type in (AdvancedStringTypes.CHAR, BasicStringTypes.TEXT):
        return json.dumps(value.data)
    elif value.type == BasicStringTypes.UNKNOWN:
        return convert_unknown_type(value)
    raise AssertionError(f"Invalid literal: {value!r}")

def convert_arguments(arguments: list[Expression]) -> str:
    return ", ".join(convert_statement(arg) for arg in arguments)

def convert_function_call(function: FunctionCall) -> str:
    # HACK
    if (len(function.arguments) == 1
            and isinstance(function.arguments[0], FunctionCall)
            and function.arguments[0].type == FunctionType.FUNCTION):
        return convert_function_call(function.arguments[0]) + " | " + function.name

    result = function.name
    if function.type != FunctionType.PROPERTY:
            result += f"({convert_arguments(cast(list[Expression], function.arguments))})"
    return result

def convert_statement(statement: Statement) -> str:
    if isinstance(statement, Identifier):
        return f'"${statement}"'
    elif isinstance(statement, FunctionCall):
        return convert_function_call(statement)
    elif isinstance(statement, Value):
        return convert_value(statement)
    elif isinstance(statement, VariableAssignment):
        result = f"{statement.variable}="
        if isinstance(statement.expression, FunctionCall):
            result += f"$({convert_statement(statement.expression)})"
        else:
            result += convert_statement(statement.expression)
    raise AssertionError(f"Unknown statement: {statement!r}")

indent = " " * 4

def convert_execution_unit(pu: PreparedExecutionUnit) -> str:
    includes = []
    if any(isinstance(tc.input, MainInput) for ctx in pu.contexts for tc in ctx.testcases):
        includes.append("solution_main")

    for ctx in pu.contexts:
        for tc in ctx.testcases:
            if isinstance(tc.input, PreparedTestcaseStatement):
                includes.append(tc.input.unwrapped_input_statement().name)
    result = f"""include {{ {"; ".join(includes)} }} from './{pu.submission_name}'

value_file = file("${{projectDir}}/{pu.value_file}")
exception_file = file("${{projectDir}}/{pu.exception_file}")

def write_context_separator() {{
    value_file     << "--{pu.context_separator_secret}-- SEP"
    exception_file << "--{pu.context_separator_secret}-- SEP"
    System.out     << "--{pu.context_separator_secret}-- SEP"
    System.err     << "--{pu.context_separator_secret}-- SEP"
}}

def write_separator() {{
    value_file     << "--{pu.testcase_separator_secret}-- SEP"
    exception_file << "--{pu.testcase_separator_secret}-- SEP"
    System.out     << "--{pu.testcase_separator_secret}-- SEP"
    System.err     << "--{pu.testcase_separator_secret}-- SEP"
}}

process send_value {{
    input:
    val x

    exec:
    value_file << groovy.json.JsonOutput.toJson([type: 'text', data: "${{x}}"])
}}

"""
    # Generate code for each context.
    ctx: PreparedContext
    for i, ctx in enumerate(pu.contexts):
        result += f"workflow context_{i} {{\n"
        result += indent + ctx.before + "\n"

        # Generate code for each testcase
        tc: PreparedTestcase
        for j, tc in enumerate(ctx.testcases):
            result += indent + "write_separator()\n"
            # Prepare command arguments if needed.
            if tc.testcase.is_main_testcase():
                assert isinstance(tc.input, MainInput)
                result += f"{indent}solution_main()\n"
            else:
                assert isinstance(tc.input, PreparedTestcaseStatement)
                result += indent + convert_statement(tc.input.input_statement()) + "\n"
            result += "\n"

        result += indent + ctx.after + "\n"
        result += "}\n"

    result += f"""
workflow {{
"""

    for i, ctx in enumerate(pu.contexts):
        result += f"{indent}write_context_separator()\n"
        result += f"{indent}context_{i}()\n"

    result += "}\n"

    return result
