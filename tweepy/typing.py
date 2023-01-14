from __future__ import annotations

import sys
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias
    # Remove when support for Python 3.9 is dropped

    T = TypeVar("T")

    LTSType: TypeAlias = list[T] | tuple[T] | set[T]
