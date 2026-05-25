import pytest

from paperchase.runtimes.base import Message, Runtime, ToolSchema, register, get_runtime, registered_runtimes


def test_message_dataclass():
    m = Message(role="user", content="hello")
    assert m.role == "user"
    assert m.content == "hello"


def test_registry_roundtrip():
    class FakeRuntime:
        name = "fake"

        def chat(self, messages, tools=None):
            return {"content": "fake"}

        def stream(self, messages, tools=None):
            yield {"content": "fake"}

    register(FakeRuntime())
    assert "fake" in registered_runtimes()
    assert get_runtime("fake").name == "fake"
