from typing import Optional, List

from dataclasses import dataclass, fields

from dacite_ext import from_dict


# noinspection PyUnresolvedReferences
def test_from_dict_with_additional_keys_in_data():
    @dataclass
    class X:
        i: int

    result = from_dict(X, {'i': 42, 's': 'text'}, add_extra_fields=True)
    result_fields = fields(result)

    assert [(f.name, f.type) for f in result_fields] == [('i', Optional[int]), ('s', Optional[str])]
    assert result.i == 42
    assert result.s == 'text'


# noinspection PyUnresolvedReferences
def test_from_dict_with_nested_data_classes_and_additional_keys_in_data():
    @dataclass
    class X:
        i: int

    @dataclass
    class Y:
        f: float

    @dataclass
    class Z:
        x: X
        y: Y
        a: List[int]

    result = from_dict(Z, {'x': {'i': 42, 's': 'text'}, 'y': {'f': 0.0}, 'b': True, 'a': [1]}, add_extra_fields=True)
    x_fields = fields(result.x)
    result_fields = fields(result)

    assert [(f.name, f.type) for f in x_fields] == [('i', Optional[int]), ('s', Optional[str])]
    assert ([(f.name, f.type) for f in result_fields if f.name in ['y', 'a', 'b']] ==
            [('y', Optional[Y]), ('a', Optional[List[int]]), ('b', Optional[bool])])
    assert result.x.s == 'text'
    assert result.x.i == 42
    assert result.y.f == 0.0
    assert result.b
    assert result.a == [1]


# noinspection PyUnresolvedReferences
def test_from_dict_with_data_class_with_default_values_and_additional_keys_in_data():
    @dataclass
    class X:
        i: int = 0

    result = from_dict(X, {'s': 'text', 'i': 42}, add_extra_fields=True)
    result_fields = fields(result)

    assert [(f.name, f.type) for f in result_fields] == [('i', Optional[int]), ('s', Optional[str])]
    assert result.i == 42
    assert result.s == 'text'
