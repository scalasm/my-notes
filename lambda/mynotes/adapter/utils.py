from typing import Any, Dict

import json
import base64

# The character encoding that we use during Base64 encoding/deconding operations
INTERNAL_CHAR_ENCODING = "utf-8"

def encode_dict_to_base64(dictionary: Dict[str,Any]) -> str:
    """
    Encode a dictionary into a Base64 string. This method is designed to work as a companio 
    to 'decode_str_as_dict' in this same module

    Args:
        - dictionary the object to encode
    
    Returns:
        - the encoded string representing this input object.
    """
    json_content = json.dumps(dictionary)
    json_content_bytes = json_content.encode(INTERNAL_CHAR_ENCODING)

    return base64.b64encode(json_content_bytes).decode(INTERNAL_CHAR_ENCODING)

def decode_str_as_dict(base64_str: str) -> Dict[str,Any]:
    """
    Decode a Base64 encoded dictionary. This method is designed to work as a companio 
    to 'encode_dict_to_base64' in this same module

    Args:
        - base64_str the encoded dictionary object
    
    Returns:
        - the decoded dictionary object or None if the input string was None.
    """
    if not base64_str:
        return None
    
    json_content = base64.b64decode(base64_str).decode(INTERNAL_CHAR_ENCODING)
    return json.loads(json_content)
