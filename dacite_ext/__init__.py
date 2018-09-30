from typing import Any, Type, List, Optional, Tuple

from dataclasses import fields as dc_fields, MISSING, is_dataclass, Field, field as dc_field, make_dataclass

# noinspection PyProtectedMember,PyUnresolvedReferences
from dacite import (DaciteError, WrongTypeError, MissingValueError, UnionMatchError, InvalidConfigurationError, Config,
                    T, Data, _is_optional)
import dacite


def from_dict(data_class: Type[T], data: Data, config: Optional[Config] = None, add_extra_fields: bool = False) -> T:
    """Create a data class instance from a dictionary.

    :param data_class: a data class type
    :param data: a dictionary of a input data
    :param config: a configuration of the creation process
    :param add_extra_fields: a flag for adding extra fields to resulting data class instance (recursively produces \
    data classes, inherited from original data classes)
    :return: an instance of a data class
    """
    config = config or Config()
    if add_extra_fields:
        data_class = _with_extra_fields(data_class=data_class, data=data, config=config)
    return dacite.from_dict(data_class=data_class, data=data, config=config)


def _with_extra_fields(data_class: Type[T], data: Data, config: Optional[Config]) -> Type[T]:
    # noinspection PyPep8Naming
    NewField = Tuple[str, type, Field]
    # noinspection PyPep8Naming
    NewFieldList = List[NewField]

    def wrap_field_in_optional_and_provide_default_none_value(field_name: str = None, field_type: type = None,
                                                              field: Field = None) -> NewField:
        new_field = dc_field()
        if field is not None:
            if field_name is None:
                field_name = field.name
            if field_type is None:
                field_type = field.type
        new_field.name = field_name
        new_field.type = field_type if _is_optional(field_type) else Optional[field_type]
        if field is None or (field.default is MISSING and field.default_factory is MISSING):
            new_field.default = None
        return new_field.name, new_field.type, new_field

    def extract_type_from_possible_optional_type(possible_optional_type: type):
        # noinspection PyUnresolvedReferences
        return (possible_optional_type.__args__[0]
                if _is_optional(possible_optional_type) else
                possible_optional_type)

    def data_class_fields(class_or_instance: Any):
        x = extract_type_from_possible_optional_type(possible_optional_type=class_or_instance)
        return dc_fields(class_or_instance=x)

    # We need to wrap all field types in Optional, because new (optional with default value) fields could be inserted
    # in the middle of the data class
    def get_fields_wrapped_in_optional_with_default_none_value() -> NewFieldList:
        return [wrap_field_in_optional_and_provide_default_none_value(field=field)
                for field in data_class_fields(class_or_instance=data_class)]

    def data_key_name_for_field(field: Field) -> str:
        if field.name in config.prefixed:
            prefix = config.prefixed[field.name]
            prefix_len = len(prefix)
            for key in data.keys():
                if key.startswith(prefix):
                    return key[prefix_len:]
        else:
            return config.remap.get(field.name, field.name)

    def get_data_key_names_for_fields() -> List[str]:
        return [data_key_name_for_field(field=field) for field in data_class_fields(class_or_instance=data_class)]

    def get_new_data_classes_fields() -> NewFieldList:
        def get_new_data_class_field(field: Field) -> NewField:
            # noinspection PyShadowingNames
            result = wrap_field_in_optional_and_provide_default_none_value(
                field_type=Optional[_with_extra_fields(data_class=field.type,
                                                       data=data[data_key_name_for_field(field=field)],
                                                       config=config)],
                field=field)
            return result if result[2] != field else None

        def is_data_class_or_optional_data_class(field_type: type):
            return is_dataclass(obj=extract_type_from_possible_optional_type(possible_optional_type=field_type))

        result = (get_new_data_class_field(field=field) for field in data_class_fields(class_or_instance=data_class)
                  if is_data_class_or_optional_data_class(field_type=field.type))
        return [field for field in result if field is not None]

    def get_extra_fields() -> NewFieldList:
        # noinspection PyShadowingNames
        def drop_field_by_name(list_of_fields: NewFieldList, name: str) -> None:
            def find_field_by_name() -> int:
                for i, (field_name, _, _) in enumerate(list_of_fields):
                    if field_name == name:
                        return i

            drop_index = find_field_by_name()
            if drop_index is not None:
                list_of_fields.pop(drop_index)

        fields_for_data_keys = [
            wrap_field_in_optional_and_provide_default_none_value(field_name=field_name, field_type=field_type)
            for field_name, field_type in
            zip(data.keys(), (Optional[type(value)] for value in data.values()))]
        data_key_names_for_fields = get_data_key_names_for_fields()
        for name in data_key_names_for_fields:
            drop_field_by_name(list_of_fields=fields_for_data_keys, name=name)
        return fields_for_data_keys

    def merge_field_lists(*args) -> NewFieldList:
        result = []
        for field_list in args:
            for new_field in field_list:
                replaced = False
                for i, existing_field in enumerate(result):
                    if new_field[0] == existing_field[0]:
                        result[i] = new_field
                        replaced = True
                if not replaced:
                    result.append(new_field)
        return result

    def new_data_class_name():
        return extract_type_from_possible_optional_type(possible_optional_type=data_class).__name__ + 'WithExtraFields'

    new_data_class_fields = get_new_data_classes_fields()
    new_extra_fields = get_extra_fields()
    if new_data_class_fields or new_extra_fields:
        fields_wrapped_in_optional_with_default_none_value = get_fields_wrapped_in_optional_with_default_none_value()
        fields = merge_field_lists(fields_wrapped_in_optional_with_default_none_value, new_data_class_fields,
                                   new_extra_fields)
        bases = (extract_type_from_possible_optional_type(possible_optional_type=data_class), )
        return make_dataclass(cls_name=new_data_class_name(), fields=fields, bases=bases)
    else:
        return data_class
