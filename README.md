# err-dnsnative

The aim of this plugin is to implement all kinds of DNS lookup actions but
sticking to Python libraries.

It currently has no dependencies except for the Python Standard Library.

It requires Python 3.2 or higher until Err can successfully be installed on
Python 2 so the tests can run.

## Install

```
!repos install https://github.com/daenney/err-dnsnative.git
```

## Commands

 * ``!host``: This command will take one or multiple hostnames or IP addresses
              and look them up through your system's resolver.
              It uses Python's ``socket`` library which currently limits us to
              only being able to resolve IP -> hostname or hostname -> IP.
   * ``help``: This subcommand will print out some usage instructions.

## License

This code is licensed under the GPLv3, see the LICENSE file.
