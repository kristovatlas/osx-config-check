# osx-config-check

Checks your OSX machine against various hardened configuration settings.

You can specify your own preferred configuration baseline by supplying your own [Hjson](https://hjson.org/) file instead of the provided one.

## Disclaimer

The authors of this tool are not responsible if running it breaks stuff; disabling features of your operating system and applications may disrupt normal functionality.

Once applied, the security configurations do not not guarantee security. You will still need to make good decisions in order to stay secure. The configurations will generally not help you if your computer has been previously compromised.

Configurations come from sites like:
* [drduh's OS X Security and Privacy Guide](https://github.com/drduh/OS-X-Security-and-Privacy-Guide)

## Usage

**You should download and run this application once for each OS X user account you have on your machine.** Each user may be configured differently, and so each should be audited.

Download this app using Git, GitHub Desktop, or the "download as zip" option offered by GitHub. If you choose the zip option, unarchive the zip file after.

In the `Terminal` application, navigate to the directory that contains this app. You can use the `cd` command (see example below) to change directories. If you've downloaded the file to your "Downloads" directory, you might find the app here:

```bash
cd ~/Downloads/osx-config-check
```

If that directory doesn't exist because the folder you retrieved is named slightly different (such as 'osx-config-check-master' or 'osx-config-check-1.0.0'), you can always type in a portion of the directory name and hit the [TAB] key in Terminal to auto-complete the rest.

Next run the app as follows:

```bash
python app.py
```

This will take you through a series of interactive steps that checks your machine's configuration, and offers to fix misconfigurations for you.

Intermediate users and advanced users can also invoke various command-line arguments:
```
Usage: python app.py [OPTIONS]
OPTIONS:
	--debug-print        Enables verbose output for debugging the tool.
	--report-only        Only reports on compliance and does not offer to fix broken configurations.
	--disable-logs       Refrain from creating a log file with the results.
	--disable-prompt     Refrain from prompting user before applying fixes.
	--skip-sudo-checks   Do not perform checks that require sudo privileges.
	--help -h            Print this usage information.
```

## Sample Output

```
osx-config-check v1.1.0 (ivysaur)
Download the latest copy of this tool at: https://github.com/kristovatlas/osx-config-check
Report bugs/issues:
	* GitHub: https://github.com/kristovatlas/osx-config-check/issues
	* Twitter: https://twitter.com/kristovatlas
------------------------------------------------------------------------------------------


CHECK #1: Homebrew is installed.... PASSED!

CHECK #2: Binaries installed to /usr/local/bin are preferred over those in /usr/bin (Note: If this check does not pass, other tests will fail)... PASSED!

CHECK #3: Java Runtime Environment is up to date.... PASSED!

CHECK #4: The System Preferences application is currently closed.... PASSED!

CHECK #5: Current user is a non-admin account.... FAILED!

CHECK #6: The OSX application firewall is enabled (system-wide).... PASSED!

CHECK #7: The OSX application firewall is enabled (current user only).... PASSED!

CHECK #8: A password is required to wake the computer from sleep or screen saver (system-wide).... PASSED!

CHECK #9: A password is required to wake the computer from sleep or screen saver (current user only).... PASSED!

CHECK #10: There is no delay between starting the screen saver and locking the machine (system-wide).... PASSED!

CHECK #11: There is no delay between starting the screen saver and locking the machine (current user only).... PASSED!

CHECK #12: Logging is enabled for the operating system.... PASSED!

CHECK #13: Homebrew analytics are disabled.... PASSED!

CHECK #14: Stealth mode is enabled for OSX: Computer does not respond to ICMP ping requests or connection attempts from a closed TCP/UDP port. (system-wide)... PASSED!

CHECK #15: Stealth mode is enabled for OSX: Computer does not respond to ICMP ping requests or connection attempts from a closed TCP/UDP port. (current user only)... PASSED!

CHECK #16: Automatic whitelisting of Apple-signed applications through the firewall is disabled (system-wide).... PASSED!

CHECK #17: Automatic whitelisting of Apple-signed applications through the firewall is disabled (current user only).... PASSED!

CHECK #18: Captive portal for connecting to new networks is disabled to prevent MITM attacks.... PASSED!

CHECK #19: OpenSSL is up to date.... PASSED!

CHECK #20: Hidden files are displayed in Finder.... PASSED!

CHECK #21: All application software is currently up to date.... PASSED!

CHECK #22: Automatic check for software updates is enabled.... SKIPPED!

CHECK #23: GateKeeper protection against untrusted applications is enabled.... PASSED!

CHECK #24: Bluetooth is disabled.... FAILED!

CHECK #25: The infrared receiver is disabled.... PASSED!

CHECK #26: AirDrop file sharing is disabled.... PASSED!

CHECK #27: File sharing is disabled.... PASSED!

CHECK #28: Printer sharing is disabled.... PASSED!

CHECK #29: Remote login is disabled.... FAILED!

CHECK #30: Remote Management is disabled.... PASSED!

CHECK #31: Remote Apple events are disabled.... FAILED!

CHECK #32: Internet Sharing is disabled on all network interfaces.... PASSED!

CHECK #33: Wake on Network Access feature is disabled.... FAILED!

CHECK #34: Automatic setting of time and date is disabled.... FAILED!

CHECK #35: IPv6 is disabled on all network interfaces.... PASSED!

CHECK #36: An administrator password is required to change system-wide preferences.... PASSED!

CHECK #37: Documents are not stored to iCloud Drive by default. (May be mistaken if iCloud is disabled)... PASSED!

CHECK #38: The File Vault key is protected when going to standby mode.... PASSED!

CHECK #39: The system will store a copy of memory to persistent storage, and will remove power to memory.... PASSED!

CHECK #40: git is up to date or is not installed... PASSED!

CHECK #41: Apple Push Notifications are disabled.... PASSED!

CHECK #42: Google DNS servers are used by default on all network interfaces.... PASSED!

CHECK #43: The curl utility is up to date or absent from the system.... PASSED!

CHECK #44: FileVault file system encryption is enabled.... PASSED!

CHECK #45: FileVault file system encryption is enabled at the root directory.... PASSED!

CHECK #46: The idle timer for screen saver activation is set to 10 minutes or less.... PASSED!

CHECK #47: System Integrity Protection (SIP) is enabled.... PASSED!

CHECK #48: The Safari application is currently closed.... PASSED!

CHECK #49: Safari will not auto-fill credit card data.... PASSED!

CHECK #50: Safari will not auto-fill your contact data.... PASSED!

CHECK #51: Safari will not auto-fill miscellaneous forms.... PASSED!

CHECK #52: Safari will not auto-fill usernames or passwords.... PASSED!

CHECK #53: Files downloaded in Safari are not automatically opened.... PASSED!

CHECK #54: Cookies and local storage are always blocked in Safari.... PASSED!

CHECK #55: Safari extensions are disabled.... PASSED!

CHECK #56: The Safari web browser will warn when visiting known fraudulent websites.... PASSED!

CHECK #57: JavaScript is disabled in the Safari web browser.... PASSED!

CHECK #58: JavaScript is disabled in the Safari web browser (Legacy version).... PASSED!

CHECK #59: Pop-up windows are blocked in the Safari web browser.... PASSED!

CHECK #60: Pop-up windows are blocked in the Safari web browser (Legacy version).... PASSED!

CHECK #61: The WebGL plug-in is disabled in the Safari web browser.... PASSED!

CHECK #62: Plug-ins are disabled in the Safari web browser.... PASSED!

CHECK #63: Plug-ins are disabled in the Safari web browser (Legacy version).... PASSED!

CHECK #64: Plug-ins are blocked by default in the Safari web browser unless a site is explicitly added to a list of allowed sites.... PASSED!

CHECK #65: The Java plug-in for Safari web browser is blocked unless a site is explicitly added to a list of allowed sites.... PASSED!

CHECK #66: The Java plug-in is disabled in the Safari web browser.... PASSED!

CHECK #67: The Java plug-in is disabled in the Safari web browser (Legacy version).... PASSED!

CHECK #68: The Safari web browser is configured to treat SHA-1 certificates as insecure.... PASSED!

CHECK #69: The Safari web browser will not pre-load webpages that rank highly as search matches.... PASSED!

CHECK #70: The Safari web browser will not include search engine suggestions for text typed in the location bar.... PASSED!

CHECK #71: The Safari web browser's search suggestions are disabled.... PASSED!

CHECK #72: The Safari web browser uses the Do-Not-Track HTTP header.... PASSED!

CHECK #73: PDF viewing is disabled in the Safari web browser.... PASSED!

CHECK #74: Full website addresses are displayed in the location bar of the Safari web browser.... PASSED!

CHECK #75: The Mail application is currently closed.... PASSED!

CHECK #76: Apple Mail does not automatically load remote content in e-mails.... PASSED!

CHECK #77: Mail identified by Apple Mail as junk is sent to the Junk mailbox.... PASSED!

CHECK #78: GPGMail is in use.... PASSED!

CHECK #79: New e-mails composed in Apple Mail are encrypted by GPGMail if the receiver's PGP is present in the keychain.... PASSED!

CHECK #80: New e-mails composed in Apple Mail and saved as drafts are encrypted by GPGMail.... PASSED!

CHECK #81: New e-mails composed in Apple Mail are signed by GPGMail.... PASSED!

CHECK #82: Apple Mail automatically checks for updates to GPGMail.... PASSED!

CHECK #83: The Google Chrome browser is currently closed.... FAILED!

CHECK #84: All Google Chrome web browser profiles prevent information leakage through navigation errors.... PASSED!

CHECK #85: All Google Chrome web browser profiles prevent information leakage through URL suggestions.... PASSED!

CHECK #86: All Google Chrome web browser profiles prevent information leakage through network prediction.... PASSED!

CHECK #87: All Google Chrome web browser profiles prevent information leakage by blocking security incidents reports to Google.... FAILED!

CHECK #88: All Google Chrome web browser profiles have Google Safe Browsing enabled.... FAILED!

CHECK #89: All Google Chrome web browser profiles prevent information leakage through spell-checking network services.... FAILED!

CHECK #90: All Google Chrome web browser profiles prevent information leakage through reporting usage statistics to Google.... PASSED!

CHECK #91: All Google Chrome web browser profiles use the Do-Not-Track HTTP header.... PASSED!

CHECK #92: All Google Chrome web browser profiles prevent pop-ups.... PASSED!

CHECK #93: All Google Chrome web browser profiles prevent geolocation by websites.... PASSED!

CHECK #94: All Google Chrome web browser profiles block unsandboxed plug-in software.... PASSED!

CHECK #95: All Google Chrome web browser profiles prevent filling personal information into forms automatically.... PASSED!

CHECK #96: All Google Chrome web browser profiles have disabled Password Manager.... FAILED!

CHECK #97: All Google Chrome web browser profiles have disabled automatic sign-in for stored passwords.... FAILED!

CHECK #98: All Google Chrome web browser profiles have disabled Google CloudPrint.... PASSED!

CHECK #99: All Google Chrome web browser profiles block Flash cookies.... PASSED!

CHECK #100: All Google Chrome web browser profiles have disabled the Chrome Pepper Flash Player plug-in.... PASSED!

CHECK #101: All Google Chrome web browser profiles have disabled the Adobe Shockwave Flash plug-in.... FAILED!

CHECK #102: All Google Chrome web browser profiles have disabled the Adobe Flash Player plug-in.... PASSED!

CHECK #103: All Google Chrome web browser profiles have disabled the Native Client plug-in.... FAILED!

CHECK #104: All Google Chrome web browser profiles have disabled the Widevine Content Decryption Module plug-in.... PASSED!

CHECK #105: All Google Chrome web browser profiles have enabled the uBlock Origin extension.... FAILED!

CHECK #106: All Google Chrome web browser profiles have enabled the Ghostery extension.... FAILED!

CHECK #107: All Google Chrome web browser profiles have enabled the ScriptSafe extension.... FAILED!

CHECK #108: Google Chrome is the default web browser.... PASSED!

CHECK #109: OSX/Keydnap malware is not present.... PASSED!
Configurations passed total:                 91 (83.49%)
Configurations failed or skipped total:      18 (16.51%)
Configurations passed without applying fix:  91 (83.49%)
Configurations passed after applying fix:    0 (0.00%)
Configurations failed and fix failed:        0 (0.00%)
Configurations failed and fix skipped:       17 (15.60%)
Configurations failed and fix declined:      0 (0.00%)
Configuration checks skipped:                1 (0.92%)
Wrote results to '~/Documents/osx-config-check_2016-09-15_17-44-48.log'. Please review the contents before submitting them to third parties, as they may contain sensitive information about your system.
==========================
```

## Troubleshooting

### Errors related to "sudo" or "sudoers"

If you receive an error message referencing these terms, the user you are currently logged in as may not be permitted to temporarily assume elevated privileges, preventing this tool from fully auditing and/or fixing your user's configuration. If you have added a non-Administrator user to your machine to help secure it, you will find that your non-Administrator user is not part of the "sudoers" list by default. To learn about how to add your user to the "sudoers" list, please [refer to this link](http://osxdaily.com/2014/02/06/add-user-sudoers-file-mac/).

### Trouble Connecting to Wi-Fi

This tool encourages users to use DNS servers run by the Google corporation. This can break some wi-fi networks that use "active portals" to login, like those found at cafes, airports, etc. If you're having trouble connecting to a wi-fi network after using this tool, please use the "dns_helper" tool included. From the terminal application, run:

    bash dns_helper.sh

And follow the instructions on the screen carefully.

### Something in OS X broke!

A few users have observed that features like screen saver activation with hot corners stopped working after applying configuration fixes. These problems have so far been remedied simply by restarting the system.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests to the repository.

## Similar Projects

* https://github.com/SummitRoute/osxlockdown

## Contributors

* [Kristov Atlas](https://twitter.com/kristovatlas/) (maintainer)
