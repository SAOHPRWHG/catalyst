from typing import TYPE_CHECKING  # isort:skip

from catalyst import utils
from catalyst.core import Callback, CallbackNode, CallbackOrder

if TYPE_CHECKING:
    from catalyst.core import _State


class ExceptionCallback(Callback):
    def __init__(self):
        order = CallbackOrder.Other + 1
        super().__init__(order=order, node=CallbackNode.All)

    def on_exception(self, state: "_State"):
        exception = state.exception
        if not utils.is_exception(exception):
            return

        if state.need_exception_reraise:
            raise exception
