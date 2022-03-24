from typing import Any, Dict
import pytest

from mynotes.adapter.utils import encode_dict_to_base64, decode_str_as_dict


SAMPLE_CONTINUATION_TOKEN = {"creation_time": {"S": "2022-03-23T22:02:36.233752+0000"}, "author_id_and_type": {"S": "__PUBLIC__#F"}, "id": {"S": "1"}}
SAMPLE_CONTINUATION_TOKEN_BASE64 = "eyJjcmVhdGlvbl90aW1lIjogeyJTIjogIjIwMjItMDMtMjNUMjI6MDI6MzYuMjMzNzUyKzAwMDAifSwgImF1dGhvcl9pZF9hbmRfdHlwZSI6IHsiUyI6ICJfX1BVQkxJQ19fI0YifSwgImlkIjogeyJTIjogIjEifX0="

test_encode_test_data = [
    (SAMPLE_CONTINUATION_TOKEN, SAMPLE_CONTINUATION_TOKEN_BASE64)
]

@pytest.mark.parametrize("continuation_token_dict,expected_string", test_encode_test_data)
def test_encode(continuation_token_dict: Dict[str,Any], expected_string: str) -> None:
    assert encode_dict_to_base64(continuation_token_dict) == expected_string

test_decode_test_data = [
    (SAMPLE_CONTINUATION_TOKEN_BASE64, SAMPLE_CONTINUATION_TOKEN),
    (None, None)
]

@pytest.mark.parametrize("continuation_token_as_base64,expected_token_dict", test_decode_test_data)
def test_decode(continuation_token_as_base64: str, expected_token_dict: Dict[str,Any]) -> None:
    assert decode_str_as_dict(continuation_token_as_base64) == expected_token_dict

