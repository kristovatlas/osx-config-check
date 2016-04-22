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

## Primary Authors

* [Kristov Atlas](https://twitter.com/kristovatlas/)
