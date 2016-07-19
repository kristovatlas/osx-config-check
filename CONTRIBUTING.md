## Modifying default configuration checks

All default configuration checks -- that is, the set of configurations that will be checked and fixed if insecure when the user runs `app.py` -- are expressed in the `osx-config.hjson` file. This file is written in [Hjson](http://hjson.org/) to make it easy to read and modify.

In order to avoid requiring non-developer users of the tool to install the Hjson Python module, a pure JSON file is also included in this repository: `osx-config.json`. Contributors MUST follow these rules:
* You MUST NOT directly modify the `osx-config.json` file.
* If you modify the `osx-config.hjson` file, you MUST include any appropriate updates to the `osx-config.json` file in your commit. Adding or modifying elements such as comments and whitespace will typically not result in changes to pure JSON file, but many other changes will.

An updated version of the `osx-config.json` file SHOULD be generated using the `hjson_to_json.py` script:

    $ python hjson_to_json.py

Use of this script requires the `hjson` Python module. To install it on your system, you can use:

    $ pip install hjson

 or

    $ sudo pip install hjson

If you'd like to make sure your changes to `osx-config.hjson` are automatically reflected in `osx-config.json`, you MAY install a git pre-commit hook to do so. Use this file: [hooks/pre-commit](hooks/pre-commit)

To "install" this pre-commit hook, copy it to the `.git/hooks` directory contained in your local copy of this repository. More resources on Git hooks can be found [here](http://githooks.com/).

## Modifying Python files

You SHOULD use `pylint` on any Python files you modify before submitting your modifications. Please attempt to avoid lowering the `pylint` score of these files.
