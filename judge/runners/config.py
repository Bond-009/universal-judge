"""Configuration for languages, making implementing runners fairly easy."""
from typing import List

from testplan import Context


class LanguageConfig:
    """
    Configuration for the runner
    """

    def compilation_command(self, files: List[str]) -> List[str]:
        """Compile some files."""
        return []

    def execution_command(self) -> List[str]:
        """Get the command for executing the code."""
        raise NotImplementedError

    def execute_evaluator(self, evaluator_name: str) -> List[str]:
        """Get the command for evaluating an evaluator."""
        raise NotImplementedError

    def file_extension(self) -> str:
        """The file extension for this language, without dot."""
        raise NotImplementedError

    def submission_name(self, context: Context) -> str:
        """The name for the submission file."""
        raise NotImplementedError

    def user_friendly_submission_name(self, context: Context):
        if context.object:
            return context.object
        else:
            return ""

    def context_name(self) -> str:
        """The name of the context file."""
        raise NotImplementedError

    def evaluator_name(self) -> str:
        """The name for the evaluator file."""
        raise NotImplementedError

    def additional_files(self) -> List[str]:
        """Additional files that will be available to the context tests."""
        raise NotImplementedError

    def value_writer(self, name):
        """Return the code needed to write values to the file."""
        raise NotImplementedError

    def exception_writer(self, name):
        """Return the code needed to write exceptions to the file."""
        raise NotImplementedError

    def conventionalise(self, function_name: str) -> str:
        """Apply a language's conventions to function name."""
        raise NotImplementedError

    def rename_evaluator(self, code, name):
        """Replace the evaluate function name"""
        return code.replace("evaluate", name, 1)
