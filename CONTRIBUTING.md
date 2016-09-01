## Git organization and Pull Request process

This project uses a Gitflow-like organization for code:

* The [`master`](https://github.com/kristovatlas/osx-config-check/tree/master) branch represents a stable version of the project at any given time.
* Releases are tags on the [`master`](https://github.com/kristovatlas/osx-config-check/tree/master) branch.
* All features and bug fixes are performed against the [`develop`](https://github.com/kristovatlas/osx-config-check/tree/develop) branch.
* New features are allocated their own branch based on the [`develop`](https://github.com/kristovatlas/osx-config-check/tree/develop) branch, and pull requests are made from the new feature branch to the [`develop`](https://github.com/kristovatlas/osx-config-check/tree/develop) branch.

Developers who wish to submit a pull request should perform the following protocol:

1. Fork the project on GitHub
2. Create a special-purpose branch from the [`develop`](https://github.com/kristovatlas/osx-config-check/tree/develop) branch, e.g. 'fix-filevault' or 'disable-apple-mail'
3. Implement the changes in the branch
4. Follow the guidelines in the sections below depending on whether you are modifying configuration checks, Python code, or any combination therefore
5. Make a pull request from your feature branch to the [`develop`](https://github.com/kristovatlas/osx-config-check/tree/develop) branch.

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

## Versioning

The osx-config-check project aims to use [Semantic Versioning 2.0.0](http://semver.org/spec/v2.0.0.html).

1. A major version number is incremented when an incompatible change is made either to the Hjson syntax for a config check or when an incompatible change is made to api.sh functions (e.g. a function is removed or its prototype modified).
2. A minor version number is incremented when a feature is added that is backwards-compatible, including:
  * A new element is added to the Hjson syntax that is compatible with existing config checks
  * A new function is added to api.sh
3. A patch version number is incremented when a bug is fixed in a backward-compatible way, including:
  * Changes to bash commands
  * Changes to the contents of scripts
  * Typos in code or documentation

New versions are produced by merging stable changes from the [`develop`](https://github.com/kristovatlas/osx-config-check/tree/develop) branch to the [`master`](https://github.com/kristovatlas/osx-config-check/tree/master) branch, and by tagging them as a new release.
