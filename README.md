# dacite-ext - dacite library extended
This library provides missing feature for [dacite](https://github.com/konradhalas/dacite) library: dynamically add `data_class` fields, based on input `data` dictionary on `data_class` creation in `from_dict` function. This library is drop-in replacement for `dacite` library and has no other dependencies. The only difference is an optional argument `add_extra_fields`. If `add_extra_fields` is `True`, then new `data_class` based on argument `data_class` will be created.

## Installation
To install from [PyPI](https://pypi.org/project/dacite-ext/) run:

```shell
$ pip install dacite-ext
```
