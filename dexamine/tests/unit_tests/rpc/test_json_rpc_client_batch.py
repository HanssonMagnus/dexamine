from __future__ import annotations

from unittest.mock import patch

import pytest

from dexamine.rpc.json_rpc_client import JsonRpcClient, JsonRpcError


def test_batch_call_returns_results_by_id() -> None:
    def side_effect(*_args, **_kwargs):
        class Response:
            def json(self):
                return [
                    {"jsonrpc": "2.0", "id": 2, "result": {"b": 2}},
                    {"jsonrpc": "2.0", "id": 1, "result": {"a": 1}},
                ]

        return Response()

    client = JsonRpcClient(node_url="http://node")

    with patch("requests.post", side_effect=side_effect):
        out = client.batch_call(
            [
                ("methodA", [], 1),
                ("methodB", [], 2),
            ]
        )

    assert out == {1: {"a": 1}, 2: {"b": 2}}


def test_batch_call_raises_on_error_object() -> None:
    def side_effect(*_args, **_kwargs):
        class Response:
            def json(self):
                return [{"jsonrpc": "2.0", "id": 1, "error": {"code": -1, "message": "x"}}]

        return Response()

    client = JsonRpcClient(node_url="http://node")

    with patch("requests.post", side_effect=side_effect):
        with pytest.raises(JsonRpcError, match=r"JSON-RPC error"):
            client.batch_call([("methodA", [], 1)])

