# (generated with --quick)

from typing import Any, TypeVar, Union

dest: str
f1: Any
f2: Any
f_src1: Any
f_src2: Any
src1: str
src2: str
sys: module

_AnyPath = TypeVar('_AnyPath', str, _PathLike[str])

def __getattr__(name) -> Any: ...
def copyfile(src: Union[str, _PathLike[str]], dst: _AnyPath, *, follow_symlinks: bool = ...) -> _AnyPath: ...
