# osx-config-check

Checks your OSX machine against various hardened configuration settings.

You can specify your own preferred configuration baseline by supplying your own [HJson](https://hjson.org/) file instead of the provided one.

## Disclaimer

I am not responsible if hardening your computer's configuration using this app breaks stuff.

Configurations come from sites like:
* [drduh's OS X Security and Privacy Guide](https://github.com/drduh/OS-X-Security-and-Privacy-Guide)

## Usage

**You should download and run this application once for each OS X user account you have on your machine.** Each user may be configured differently, and so each should be audited.

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
CHECK #1: Current user is a non-admin account. (Create a new account if this fails!)... PASSED!
CHECK #2: The OSX application firewall is enabled.... PASSED!
CHECK #3: Logging is enabled for the operating system.... PASSED!
CHECK #4: Homebrew analytics are disabled. (NOTE: Fix requires you to login/logout.)... PASSED!
CHECK #5: Stealth mode is enabled for OSX: Computer does not respond to ICMP ping requests or connection attempts from a closed TCP/UDP port.... PASSED!
CHECK #6: Automatic whitelisting of Apple-signed applications for firewall is disabled.... PASSED!
CHECK #7: Captive portal for connecting to new networks is disabled to prevent MITM attacks.... PASSED!
CHECK #8: OpenSSL is up-to-date.... PASSED!
CHECK #9: The File Vault key is destroyed when going to standby mode.... PASSED!
CHECK #10: The system will store a copy of memory to persistent storage, and will remove power to memory.... PASSED!
CHECK #11: git is up to date or is not installed... PASSED!
CHECK #12: Apple Push Notifications are disabled.... PASSED!
CHECK #13: Google DNS servers are used by default on all network interfaces.... FAILED!
    Apply the following RECOMMENDED  fix? This will execute this command:
        'networksetup listallnetworkservices | grep -v 'An asterisk' | xargs -I{} networksetup -setdnsservers '{}' 8.8.8.8 8.8.4.4' [Y/n]
CHECK #13: Google DNS servers are used by default on all network interfaces.... PASSED!
CHECK #14: The curl utility is up to date or absent from the system.... PASSED!
```

## Troubleshooting

### Errors related to "sudo" or "sudoers"

If you receive an error message referencing these terms, the user you are currently logged in as may not be permitted to temporarily assume elevated priviledges, preventing this tool from fully auditing and/or fixing your user's configuration. If you have added a non-Administrator user to your machine to help secure it, you will find that your non-Administrator user is not part of the "sudoers" list by default. To learn about how to add your user to the "sudoers" list, please [http://osxdaily.com/2014/02/06/add-user-sudoers-file-mac/](refer to this link).

## Developers

If you would like to propose changes to the default configuration file included with this project, please edit the `osx-config.hjson` file. You MUST include the JSON version of the modified file along with your change by executing the `hjson_to_json.py` script. You can use the pre-commit hook included in `hooks/pre-commit` to do this automatically.

## Similar Projects

* https://github.com/SummitRoute/osxlockdown

## Primary Authors

* [Kristov Atlas](https://twitter.com/kristovatlas/)
