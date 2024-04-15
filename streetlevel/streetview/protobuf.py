# Some code to deal with the URL-encoded protobuf Google uses in Maps.
from enum import Enum
from decimal import Decimal

class ProtobufType(Enum):
    """
    Data types found in protobuf and their identifier in the URL encoded version.
    """
    # There are more data types in protobuf,
    # these are just the ones I've encountered in this project
    MESSAGE = "m"
    BOOL = "b"
    DOUBLE = "d"
    ENUM = "e"
    INT = "i"
    STRING = "s"


class ProtobufEnum:
    """
    There's an enum datatype in protobuf that I needed to deal with somehow
    and this nonsense is what I ended up with.
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"ProtobufEnum({str(self.value)})"

    def __str__(self):
        return f"ProtobufEnum({str(self.value)})"


def to_protobuf_url(fields):
    return _to_protobuf_url(fields)[1]


def _to_protobuf_url(fields):
    serialized = ""
    child_count = 0
    for field in fields.items():
        tag = field[0]
        value = field[1]
        sub_child_count, sub_serialized = _field_to_string(tag, value)
        serialized += sub_serialized
        child_count += sub_child_count
    return child_count, serialized


def _message_to_string(tag, value):
    sub_child_count, sub_serialized = _to_protobuf_url(value)
    serialized = f"!{tag}m{sub_child_count}" + sub_serialized
    return sub_child_count + 1, serialized


def _list_to_string(tag, value):
    serialized = ""
    child_count = 0
    for entry in value:
        sub_child_count, sub_serialized = _field_to_string(tag, entry)
        serialized += sub_serialized
        child_count += sub_child_count
    return child_count, serialized


def _field_to_string(tag, value):
    if isinstance(value, list):
        return _list_to_string(tag, value)
    else:
        datatype = _get_datatype_str(value)
        if datatype is ProtobufType.MESSAGE:
            return _message_to_string(tag, value)
        elif datatype is ProtobufType.BOOL:
            value = 1 if value else 0
        elif datatype is ProtobufType.ENUM:
            value = value.value
        return 1, f"!{tag}{datatype.value}{value}"


def _get_datatype_str(value):
    if isinstance(value, str):
        datatype = ProtobufType.STRING
    elif isinstance(value, bool):
        datatype = ProtobufType.BOOL
    elif isinstance(value, ProtobufEnum):
        datatype = ProtobufType.ENUM
    elif isinstance(value, int):
        datatype = ProtobufType.INT
    elif isinstance(value, float):
        datatype = ProtobufType.DOUBLE
    elif isinstance(value, Decimal):
        datatype = ProtobufType.DOUBLE
    elif isinstance(value, dict):
        datatype = ProtobufType.MESSAGE
    else:
        raise NotImplementedError(value)
    return datatype
