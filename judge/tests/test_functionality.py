"""
Testcases for specific functionality. These tests ensure the judge works.
These tests are a compromise: they don't test the complete output, but this does
make them usable for multiple languages.

The configure which languages are tested, modify the `conftest.py` file.

Running the tests should happen in with the root directory (the one with src/ and
tests/) as the working directory.
"""
from pathlib import Path

import pytest

from tests.manual_utils import assert_valid_output, configuration, execute_config

ALL_LANGUAGES = ["python", "java", "haskell", "c"]


@pytest.mark.parametrize("language", ALL_LANGUAGES)
def test_io_exercise(language: str, tmp_path: Path, pytestconfig):
    conf = configuration(pytestconfig, "echo", language, tmp_path, "one.tson", "correct")
    result = execute_config(conf)
    updates = assert_valid_output(result, pytestconfig)
    assert updates.find_status_enum() == ["correct"]


@pytest.mark.parametrize("language", ALL_LANGUAGES)
def test_simple_programmed_eval(language: str, tmp_path: Path, pytestconfig):
    conf = configuration(pytestconfig, "echo", language, tmp_path, "one-programmed-correct.tson", "correct")
    result = execute_config(conf)
    updates = assert_valid_output(result, pytestconfig)
    assert updates.find_status_enum() == ["correct"]


@pytest.mark.parametrize("language", ALL_LANGUAGES)
def test_simple_programmed_eval_wrong(language: str, tmp_path: Path, pytestconfig):
    conf = configuration(pytestconfig, "echo", language, tmp_path, "one-programmed-wrong.tson", "correct")
    result = execute_config(conf)
    updates = assert_valid_output(result, pytestconfig)
    assert updates.find_status_enum() == ["wrong"]


@pytest.mark.parametrize("language", ALL_LANGUAGES)
def test_io_function_exercise(language: str, tmp_path: Path, pytestconfig):
    conf = configuration(pytestconfig, "echo-function", language, tmp_path, "one.tson", "correct")
    result = execute_config(conf)
    updates = assert_valid_output(result, pytestconfig)
    assert updates.find_status_enum() == ["correct"]


@pytest.mark.parametrize("lang", ["python", "java", "haskell"])
def test_language_evaluator_exception(lang: str, tmp_path: Path, pytestconfig):
    conf = configuration(pytestconfig, "division", lang, tmp_path, "plan.json", "correct")
    result = execute_config(conf)
    updates = assert_valid_output(result, pytestconfig)
    assert updates.find_status_enum() == ["correct"]


@pytest.mark.parametrize("lang", ["python", "java"])
def test_assignment_and_use_in_expression(lang: str, tmp_path: Path, pytestconfig):
    conf = configuration(pytestconfig, "isbn", lang, tmp_path, "one-with-assignment.tson", "solution")
    result = execute_config(conf)
    updates = assert_valid_output(result, pytestconfig)
    # Assert that the empty context testcase is not shown, while the assignment
    # and expression testcase are shown.
    assert len(updates.find_all("start-testcase")) == 2
    # Assert the only one test was executed.
    assert updates.find_status_enum() == ["correct"]
    assert len(updates.find_all("start-test")) == 1


@pytest.mark.parametrize("lang", ["python", "java", "haskell"])
def test_assignment_and_use_in_expression_list(lang: str, tmp_path: Path, pytestconfig):
    conf = configuration(pytestconfig, "isbn-list", lang, tmp_path, "one-with-assignment.tson", "solution")
    result = execute_config(conf)
    updates = assert_valid_output(result, pytestconfig)
    # Assert that the empty context testcase is not shown, while the assignment
    # and expression testcase are shown.
    assert len(updates.find_all("start-testcase")) == 2
    # Assert the only one test was executed.
    assert updates.find_status_enum() == ["correct"]
    assert len(updates.find_all("start-test")) == 1


@pytest.mark.parametrize("lang", ["python", "java"])
def test_crashing_assignment_with_before(lang: str, tmp_path: Path, pytestconfig):
    conf = configuration(pytestconfig, "isbn", lang, tmp_path, f"one-with-crashing-assignment-{lang}.tson", "solution")
    result = execute_config(conf)
    updates = assert_valid_output(result, pytestconfig)
    # Only the assignment was started.
    assert len(updates.find_all("start-testcase")) == 1
    assert updates.find_status_enum() == ["wrong"]
    # Assert the exception is included.
    assert updates.find_next("start-test")["channel"] == "exception"


@pytest.mark.parametrize("lang", ["java", "python"])
def test_crashing_assignment_with_before(lang: str, tmp_path: Path, pytestconfig):
    conf = configuration(pytestconfig, "isbn-list", lang, tmp_path, "one-with-assignment.tson", "solution")
    result = execute_config(conf)
    updates = assert_valid_output(result, pytestconfig)
    print(result)
    # Assert that the empty context testcase is not shown, while the assignment
    # and expression testcase are shown.
    assert len(updates.find_all("start-testcase")) == 2
    # Assert the only one test was executed.
    assert updates.find_status_enum() == ["correct"]
    assert len(updates.find_all("start-test")) == 1


@pytest.mark.parametrize("lang", ["haskell", "c"])
def test_heterogeneous_arguments_are_detected(lang: str, tmp_path: Path, pytestconfig):
    conf = configuration(pytestconfig, "isbn", lang, tmp_path, "full.tson", "solution")
    result = execute_config(conf)
    updates = assert_valid_output(result, pytestconfig)
    assert len(updates.find_all("start-testcase")) == 0
    assert updates.find_status_enum() == ["internal error"]
