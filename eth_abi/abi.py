from typing import (
    Any,
    Iterable,
    Tuple,
)

from eth_typing.abi import (
    Decodable,
    TypeStr,
)
from eth_utils import (
    is_bytes,
)

from eth_abi.decoding import (
    ContextFramesBytesIO,
    TupleDecoder,
)
from eth_abi.encoding import (
    TupleEncoder,
)
from eth_abi.exceptions import (
    EncodingError,
)
from eth_abi.registry import (
    registry,
)


def encode_single(typ: TypeStr, arg: Any) -> bytes:
    """
    Encodes the python value ``arg`` as a binary value of the ABI type ``typ``.

    :param typ: The string representation of the ABI type that will be used for
        encoding e.g. ``'uint256'``, ``'bytes[]'``, ``'(int,int)'``, etc.
    :param arg: The python value to be encoded.

    :returns: The binary representation of the python value ``arg`` as a value
        of the ABI type ``typ``.
    """
    encoder = registry.get_encoder(typ)

    return encoder(arg)


def encode_abi(types: Iterable[TypeStr], args: Iterable[Any]) -> bytes:
    """
    Encodes the python values in ``args`` as a sequence of binary values of the
    ABI types in ``types`` via the head-tail mechanism.

    :param types: An iterable of string representations of the ABI types that
        will be used for encoding e.g.  ``('uint256', 'bytes[]', '(int,int)')``
    :param args: An iterable of python values to be encoded.

    :returns: The head-tail encoded binary representation of the python values
        in ``args`` as values of the ABI types in ``types``.
    """
    encoders = [
        registry.get_encoder(type_str)
        for type_str in types
    ]

    encoder = TupleEncoder(encoders=encoders)

    return encoder(args)


def is_encodable(typ: TypeStr, arg: Any) -> bool:
    """
    Determines if the python value ``arg`` is encodable as a value of the ABI
    type ``typ``.

    :param typ: A string representation for the ABI type against which the
        python value ``arg`` will be checked e.g. ``'uint256'``, ``'bytes[]'``,
        ``'(int,int)'``, etc.
    :param arg: The python value whose encodability should be checked.

    :returns: ``True`` if ``arg`` is encodable as a value of the ABI type
        ``typ``.  Otherwise, ``False``.
    """
    encoder = registry.get_encoder(typ)

    try:
        encoder.validate_value(arg)
    except EncodingError:
        return False
    except AttributeError:
        try:
            encoder(arg)
        except EncodingError:
            return False

    return True


def decode_single(typ: TypeStr, data: Decodable) -> Any:
    """
    Decodes the binary value ``data`` of the ABI type ``typ`` into its
    equivalent python value.

    :param typ: The string representation of the ABI type that will be used for
        decoding e.g. ``'uint256'``, ``'bytes[]'``, ``'(int,int)'``, etc.
    :param data: The binary value to be decoded.

    :returns: The equivalent python value of the ABI value represented in
        ``data``.
    """
    if not is_bytes(data):
        raise TypeError("The `data` value must be of bytes type.  Got {0}".format(type(data)))

    decoder = registry.get_decoder(typ)
    stream = ContextFramesBytesIO(data)

    return decoder(stream)


def decode_abi(types: Iterable[TypeStr], data: Decodable) -> Tuple[Any, ...]:
    """
    Decodes the binary value ``data`` as a sequence of values of the ABI types
    in ``types`` via the head-tail mechanism into a tuple of equivalent python
    values.

    :param types: An iterable of string representations of the ABI types that
        will be used for decoding e.g. ``('uint256', 'bytes[]', '(int,int)')``
    :param data: The binary value to be decoded.

    :returns: A tuple of equivalent python values for the ABI values
        represented in ``data``.
    """
    if not is_bytes(data):
        raise TypeError("The `data` value must be of bytes type.  Got {0}".format(type(data)))

    decoders = [
        registry.get_decoder(type_str)
        for type_str in types
    ]

    decoder = TupleDecoder(decoders=decoders)
    stream = ContextFramesBytesIO(data)

    return decoder(stream)
