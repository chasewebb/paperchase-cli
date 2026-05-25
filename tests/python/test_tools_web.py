from unittest.mock import patch, MagicMock

import pytest

from paperchase.tools.web import web_fetch


def test_web_fetch_https_ok():
    with patch("paperchase.tools.web.httpx.Client") as ClientCls:
        client = MagicMock()
        ClientCls.return_value.__enter__.return_value = client
        client.get.return_value.text = "<html>hi</html>"
        client.get.return_value.status_code = 200
        client.get.return_value.headers = {"content-type": "text/html"}
        result = web_fetch("https://example.com")
        assert result["status"] == "ok"
        assert result["body"] == "<html>hi</html>"
        assert result["status_code"] == 200


def test_web_fetch_http_denied():
    result = web_fetch("http://example.com")
    assert result["status"] == "denied"
