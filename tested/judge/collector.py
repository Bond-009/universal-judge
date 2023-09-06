import logging
from collections.abc import Iterable
from typing import IO, Literal, Optional, Tuple, Union

from tested.dodona import (
    AppendMessage,
    CloseContext,
    CloseJudgement,
    CloseTab,
    CloseTest,
    CloseTestcase,
    EscalateStatus,
    ExtendedMessage,
    Message,
    StartTestcase,
    Status,
    StatusMessage,
    Update,
    report_update,
)

_logger = logging.getLogger(__name__)


class OutputManager:
    """
    Collects results and directs it towards the output.

    One important task of this class is to ensure that the final ouptut generated by
    TESTed is valid.

    Another is to track which output has been seen. This enables us to later add
    output we have not seen as "non-executed".
    """

    __slots__ = [
        "finalized",
        "open_stack",
        "closed",
        "out",
    ]

    finalized: bool
    open_stack: list[str]
    closed: Tuple[int, int, int]
    out: IO

    def __init__(self, out: IO):
        self.finalized = False
        self.open_stack = []
        self.closed = (0, 0, 0)
        self.out = out

    def add_all(self, commands: Iterable[Update]):
        for command in commands:
            self.add(command)

    def add_messages(self, messages: Iterable[Message]):
        self.add_all(AppendMessage(message=m) for m in messages)

    def add(self, command: Update, index: Optional[int] = None):
        """
        Add and report a command.

        If the command is structure command (i.e. it opens or closes a level), it
        will be tracked to ensure a proper structure.
        """
        assert not self.finalized, "OutputManager already finished!"
        action, type_ = command.command.split("-")
        _logger.debug(f"Adding {command}")
        _logger.debug(f"Stack is {self.open_stack}")
        if action == "start":
            self.open_stack.append(type_)
        elif action == "close":
            previous = self.open_stack.pop()
            assert previous == type_, "Closing a different update type"

        # If the output should be counted or not.
        if index is not None:
            if isinstance(command, CloseTab):
                self.closed = (index + 1, 0, 0)
            elif isinstance(command, CloseContext):
                tabs, _, _ = self.closed
                self.closed = (tabs, index + 1, 0)
            elif isinstance(command, CloseTestcase):
                tabs, contexts, _ = self.closed
                self.closed = (tabs, contexts, index + 1)

        _logger.debug(f"After adding, stack is {self.open_stack}")
        report_update(self.out, command)

    def terminate(
        self,
        status_if_unclosed: Union[Status, StatusMessage],
        until: Literal["testcase", "context", "tab", "judgement"] = "judgement",
    ):
        """
        Close the current levels until the given level if they are open.

        :param until: The maximal level to close. For example, passing "tab" will close the curent tab.
        :param status_if_unclosed: The status to use if unclosed.
        """
        assert not self.finalized, "OutputManager already finished!"

        if not self.open_stack:
            self.finalized = True
            return

        if isinstance(status_if_unclosed, Status):
            status = StatusMessage(enum=status_if_unclosed)
        else:
            assert isinstance(status_if_unclosed, StatusMessage)
            status = status_if_unclosed

        self.add(EscalateStatus(status=status))

        while self.open_stack:
            open_level = self.open_stack[-1]
            if open_level == "test":
                self.add(CloseTest(generated="", status=status))
            elif open_level == "testcase":
                self.add(CloseTestcase(accepted=False))
                if until == open_level:
                    return
            elif open_level == "context":
                if until == "testcase":
                    return
                self.add(CloseContext())
                if until == open_level:
                    return
            elif open_level == "tab":
                if until in ("context", "testcase"):
                    return
                self.add(CloseTab())
                if until == open_level:
                    return
            elif open_level == "judgement":
                if until in ("tab", "context", "testcase"):
                    return
                self.add(CloseJudgement())
                self.finalized = True


class TestcaseCollector:
    """
    Collects updates for a testcase, but only outputs them if the testcase has
    content (children). This is intended to be used to evaluate testcases: they can
    be started without problem, but if nothing is written during evaluation, they
    will not be shown in Dodona.
    """

    __slots__ = ["start", "content"]

    def __init__(self, start: StartTestcase):
        assert isinstance(start, StartTestcase)
        self.start = start
        self.content = []

    def add(self, update: Update):
        self.content.append(update)

    def to_manager(self, manager: OutputManager, end: CloseTestcase, index: int):
        assert end is None or isinstance(end, CloseTestcase)
        has_text = isinstance(self.start.description, str) and self.start.description
        has_extended = (
            isinstance(self.start.description, ExtendedMessage)
            and self.start.description.description
        )
        if has_text or has_extended:
            manager.add(self.start)
            for content in self.content:
                manager.add(content)
            manager.add(end, index)
