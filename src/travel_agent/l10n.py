from typing import Any, Self

from fluent_compiler.bundle import FluentBundle


class Localization:
    def __init__(self: Self, bundle: FluentBundle) -> None:
        self.bundle = bundle

    def get(self: Self, message_id: str, **kwargs: Any) -> str:  # noqa: ANN401
        return self.bundle.format(message_id=message_id, args=kwargs)[0]
