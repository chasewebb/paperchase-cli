from unittest.mock import patch, MagicMock

from paperchase.runtimes.base import Message
from paperchase.runtimes.ollama import OllamaRuntime


@patch("paperchase.runtimes.ollama.httpx.Client")
def test_ollama_chat(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_client.post.return_value.json.return_value = {
        "message": {"role": "assistant", "content": "hi"},
        "done": True,
    }
    mock_client.post.return_value.raise_for_status.return_value = None

    rt = OllamaRuntime(host="http://localhost:11434", model="llama3.2")
    response = rt.chat([Message(role="user", content="hello")])
    assert response.content == "hi"
