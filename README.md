# osx-config-check

Checks your OSX machine against various hardened configuration settings.

You can specify your own preferred configuration baseline by supplying your own [HJson](https://hjson.org/) file instead of the provided one.

## Disclaimer

I am not responsible if hardening your computer's configuration using this app breaks stuff.

Configurations come from sites like:
* [drduh's OS X Security and Privacy Guide](https://github.com/drduh/OS-X-Security-and-Privacy-Guide)

## Usage

Download this app using Git, GitHub Desktop, or the "download as zip" option offered by GitHub. If you choose the zip option, unarchive the zip file after.

In the `Terminal` application, navigate to the directory that contains this app. You can use the `cd` command (see example below) to change directories. If you've downloaded the file to your "Downloads" directory, you might find the app here:

```bash
cd ~/Downloads/osx-config-check
```

Next run the app as follows:

```bash
python app.py
```

This will take you through a series of interactive steps that checks your machine's configuration, and offers to fix mixconfigurations for you.

If you run the program and get an error message such as: `-bash: pip: command not found` or `ImportError: No module named enum` or `ImportError: No module named hjson`

In this case, you are missing some libraries you need to run this app. Try pasting these commands into Terminal and pressing [enter] to run them:
```bash
sudo easy_install pip
sudo pip install hjson
```

## Sample Output

```bash
$ python app.py
Current user is a non-admin account. (Create a new account if this fails!)... PASSED!
The OSX application firewall is enabled.... PASSED!
Logging is enabled for the operating system.... PASSED!
Automatic whitelisting of Apple-signed applications for firewall is disabled.... PASSED!
The File Vault key is destroyed when going to standby mode.... PASSED!
The system will store a copy of memory to persistent storage, and will remove power to memory.... PASSED!
git is up to date or is not installed... PASSED!
About to execute this command to check configuration -- may require administrator privileges: 'sudo launchctl list'
Password:
Apple Push Notifications are disabled.... Insufficient privileges to perform this check. Skipping.
```

## Developers

If you would like to propose changes to the default configuration file included with this project, please edit the `osx-config.hjson` file. You MUST include the JSON version of the modified file along with your change by executing the `hjson_to_json.py` script. You can use the pre-commit hook included in `hooks/pre-commit` to do this automatically.

## Similar Projects

* https://github.com/SummitRoute/osxlockdown

## Primary Authors

* [Kristov Atlas](https://twitter.com/kristovatlas/)
