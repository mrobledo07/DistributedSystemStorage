from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PutRequest(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class PutResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class GetResponse(_message.Message):
    __slots__ = ("value", "found")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    value: str
    found: bool
    def __init__(self, value: _Optional[str] = ..., found: bool = ...) -> None: ...

class CanCommitPetition(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class CanCommitResponse(_message.Message):
    __slots__ = ("available",)
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    available: bool
    def __init__(self, available: bool = ...) -> None: ...

class HaveCommited(_message.Message):
    __slots__ = ("haveCommited",)
    HAVECOMMITED_FIELD_NUMBER: _ClassVar[int]
    haveCommited: bool
    def __init__(self, haveCommited: bool = ...) -> None: ...

class VoteRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class VoteResponse(_message.Message):
    __slots__ = ("vote",)
    VOTE_FIELD_NUMBER: _ClassVar[int]
    vote: int
    def __init__(self, vote: _Optional[int] = ...) -> None: ...

class SlowDownRequest(_message.Message):
    __slots__ = ("seconds",)
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    seconds: int
    def __init__(self, seconds: _Optional[int] = ...) -> None: ...

class SlowDownResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class RestoreRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RestoreResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class SlaveConfiguration(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: str
    def __init__(self, config: _Optional[str] = ...) -> None: ...

class NotifySuccess(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
