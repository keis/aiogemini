from dataclasses import dataclass, field
from typing import Optional, Type, TypeVar

from yarl import URL

from . import Status, GEMINI_MEDIA_TYPE

_Request = TypeVar('_Request', bound='BaseRequest')
_Response = TypeVar('_Response', bound='BaseResponse')


@dataclass
class BaseRequest:
    url: URL

    @classmethod
    def from_str(cls: Type[_Request], url: str) -> _Request:
        return cls(url=URL(url))


@dataclass
class BaseResponse:
    status: Status = Status.SUCCESS
    reason: Optional[str] = None
    content_type: str = GEMINI_MEDIA_TYPE

    @property
    def meta(self) -> str:
        if self.status == Status.SUCCESS:
            return self.content_type
        if self.reason:
            return self.reason
        return self.status.name

    @classmethod
    def from_meta(
        cls: Type[_Response],
        status: Status,
        meta: str
    ) -> _Response:
        return cls(
            status=status,
            **(
                {'content_type': meta} if status == Status.SUCCESS else
                {'reason': meta}
            )
        )
