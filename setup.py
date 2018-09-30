# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dacite_ext']

package_data = \
{'': ['*']}

install_requires = \
['dacite']

setup_kwargs = {
    'name': 'dacite-ext',
    'version': '0.1.0',
    'description': 'Dacite library extended',
    'long_description': '# dacite-ext - dacite library extended\nThis library provides missing feature for [dacite](https://github.com/konradhalas/dacite) library: dynamically add `data_class` fields, based on input `data` dictionary on `data_class` creation in `from_dict` function. This library is drop-in replacement for `dacite` library and has no other dependencies. The only difference is an optional argument `add_extra_fields`. If `add_extra_fields` is `True`, then new `data_class` based on argument `data_class` will be created.\n\n',
    'author': 'Roman Inflianskas',
    'author_email': 'infroma@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
