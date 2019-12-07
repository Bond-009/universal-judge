from typing import List

from humps import decamelize

from runners.runner import LanguageConfig
from testplan import Context


class PythonConfig(LanguageConfig):
    """Configuration for the Python language."""

    def value_writer(self, name):
        return f"def {name}(value): send(value)"

    def exception_writer(self, name):
        return f"def {name}(exception): send_exception(exception)"

    def needs_compilation(self) -> bool:
        return True

    def compilation_command(self, files: List[str]) -> List[str]:
        return ["python", "-m", "py_compile", *files]

    def execution_command(self) -> List[str]:
        context = f"{self.context_name()}.{self.file_extension()}"
        return ["python", context]

    def execute_evaluator(self, evaluator_name: str) -> List[str]:
        file = f"{self.evaluator_name()}.{self.file_extension()}"
        return ["python", file]

    def file_extension(self) -> str:
        return "py"

    def submission_name(self, context: Context) -> str:
        return f"submission"

    def context_name(self) -> str:
        return f"context"

    def evaluator_name(self) -> str:
        return f"evaluator"

    def additional_files(self) -> List[str]:
        return ["values.py"]

    def conventionalise(self, function_name: str) -> str:
        return decamelize(function_name)
