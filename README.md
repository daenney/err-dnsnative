# err-dnsnative

[![Build Status](https://travis-ci.org/daenney/err-dnsnative.png)](https://travis-ci.org/daenney/err-dnsnative)
[![Coverage Status](https://coveralls.io/repos/daenney/err-dnsnative/badge.png)](https://coveralls.io/r/daenney/err-dnsnative)

The aim of this plugin is to implement all kinds of DNS lookup actions but
sticking to Python libraries.

It currently has no dependencies except for the Python Standard Library.

It requires Python 2.7 or 3.3 and higher.

## Install

```
!repos install https://github.com/daenney/err-dnsnative.git
```

## Commands

| Command | argument                         | result                                                          |
|---------|----------------------------------|-----------------------------------------------------------------|
| !host   |                                  | Prints the help                                                 |
|         | help                             | Prints the help                                                 |
|         | \<hostname>                      | Returns the associated IP(s). This is an A/AAAA-record lookup.  |
|         | \<ip>                            | Returns the associated hostname. This is a PTR-record lookup.   |
|         | \<multiple IPs and/or hostnames> | Does the correct lookup for every entry and returns the result. |

## License

This code is licensed under the GPLv3, see the LICENSE file.

## Contributing

This plugin is fully tested and uses py.test as a testing framework. Pull
requests for features or fixes must ship with new or updated tests.

In order to install the development dependencies:

```
pip install -r requirements-test.txt
```

You can then simply run the tests with:

```
py.test --pep8
```

### PEP8

PEP8 is a hard requirement for this module. Regardless of its merits or
personal dislike of it, it is the style this module is written in and
code is checked during CI for PEP8 compliance.
