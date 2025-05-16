import base64

def encode_data(data: str) -> str:
    try:
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')
    except Exception as e:
        raise ValueError("Encoding failed") from e

def decode_data(data: str) -> str:
    try:
        return base64.b64decode(data).decode('utf-8')
    except Exception as e:
        raise ValueError("Decoding failed: invalid base64 or encoding") from e