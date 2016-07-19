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

Next run the app as follows:

```bash
python app.py
```

This will take you through a series of interactive steps that checks your machine's configuration, and offers to fix mixconfigurations for you.

## Sample Output

```bash
$ python app.py
CHECK #1: The System Preferences application is currently closed.... PASSED!
CHECK #2: Current user is a non-admin account. (Create a new account if this fails!)... PASSED!
CHECK #3: The OSX application firewall is enabled (system-wide).... PASSED!
CHECK #4: The OSX application firewall is enabled (current user only).... PASSED!
CHECK #5: A password is required to wake the computer from sleep or screen saver (system-wide).... PASSED!
CHECK #6: A password is required to wake the computer from sleep or screen saver (current user only).... PASSED!
CHECK #7: There is no delay between starting the screen saver and locking the machine (system-wide).... PASSED!
CHECK #8: There is no delay between starting the screen saver and locking the machine (current user only).... PASSED!
CHECK #9: Logging is enabled for the operating system.... PASSED!
CHECK #10: Homebrew analytics are disabled. (NOTE: Fix requires you to login/logout.)... PASSED!
CHECK #11: Stealth mode is enabled for OSX: Computer does not respond to ICMP ping requests or connection attempts from a closed TCP/UDP port. (system-wide)... PASSED!
CHECK #12: Stealth mode is enabled for OSX: Computer does not respond to ICMP ping requests or connection attempts from a closed TCP/UDP port. (current user only)... PASSED!
CHECK #13: Automatic whitelisting of Apple-signed applications for firewall is disabled (system-wide).... PASSED!
CHECK #14: Automatic whitelisting of Apple-signed applications for firewall is disabled (current user only).... PASSED!
CHECK #15: Captive portal for connecting to new networks is disabled to prevent MITM attacks.... PASSED!
CHECK #16: OpenSSL is up-to-date.... PASSED!
CHECK #17: Hidden files are displayed in Finder.... PASSED!
CHECK #18: All application software is currently up to date.... PASSED!
The next configuration check requires elevated privileges; you may be prompted for your current OS X user's password below. The command to be executed is: 'sudo softwareupdate --schedule | grep 'Automatic check is on''
CHECK #19: Automatic check for software updates is enabled.... PASSED!
CHECK #20: GateKeeper protection against untrusted applications is enabled.... PASSED!
The next configuration check requires elevated privileges; you may be prompted for your current OS X user's password below. The command to be executed is: 'sudo defaults read /Library/Preferences/com.apple.Bluetooth ControllerPowerState'
CHECK #21: Bluetooth is disabled.... FAILED!
    Apply the following EXPERIMENTAL  fix? This will execute this command:
        'defaults write /Library/Preferences/com.apple.Bluetooth ControllerPowerState -bool false; killall -HUP blued' [y/N]
CHECK #22: The infrared receiver is disabled.... PASSED!
CHECK #23: AirDrop file sharing is disabled.... PASSED!
CHECK #24: File sharing is disabled.... PASSED!
CHECK #25: Printer sharing is disabled.... PASSED!
The next configuration check requires elevated privileges; you may be prompted for your current OS X user's password below. The command to be executed is: 'sudo systemsetup -getremotelogin'
CHECK #26: Remote login is disabled.... PASSED!
CHECK #27: Remote Management is disabled.... PASSED!
The next configuration check requires elevated privileges; you may be prompted for your current OS X user's password below. The command to be executed is: 'sudo systemsetup -getremoteappleevents'
CHECK #28: Remote Apple events are disabled.... PASSED!
CHECK #29: Internet Sharing is disabled on all network interfaces.... PASSED!
The next configuration check requires elevated privileges; you may be prompted for your current OS X user's password below. The command to be executed is: 'sudo systemsetup getwakeonnetworkaccess'
CHECK #30: Wake on Network Access feature is disabled.... PASSED!
The next configuration check requires elevated privileges; you may be prompted for your current OS X user's password below. The command to be executed is: 'sudo systemsetup getusingnetworktime'
CHECK #31: Automatic setting of time and date is disabled.... PASSED!
CHECK #32: IPv6 is disabled on all network interfaces.... PASSED!
CHECK #33: An administrator password is required to change system-wide preferences.... PASSED!
CHECK #34: Documents are not stored to iCloud Drive by default. (May be mistaken if iCloud is disabled)... PASSED!
CHECK #35: The File Vault key is destroyed when going to standby mode.... PASSED!
CHECK #36: The system will store a copy of memory to persistent storage, and will remove power to memory.... PASSED!
CHECK #37: git is up to date or is not installed... PASSED!
CHECK #38: Apple Push Notifications are disabled.... PASSED!
CHECK #39: Google DNS servers are used by default on all network interfaces.... PASSED!
CHECK #40: The curl utility is up to date or absent from the system.... PASSED!
CHECK #41: FileVault file system encryption is enabled.... PASSED!
CHECK #42: FileVault file system encryption is enabled at the root directory.... PASSED!
CHECK #43: The idle timer for screen saver activation is set to 10 minutes or less.... PASSED!
CHECK #44: The Safari application is currently closed.... PASSED!
CHECK #45: Safari will not auto-fill credit card data.... PASSED!
CHECK #46: Safari will not auto-fill your contact data.... PASSED!
CHECK #47: Safari will not auto-fill miscellaneous forms.... PASSED!
CHECK #48: Safari will not auto-fill usernames or passwords.... PASSED!
CHECK #49: Files downloaded in Safari are not automatically opened.... PASSED!
CHECK #50: Cookies and local storage are always blocked in Safari.... PASSED!
CHECK #51: Safari extensions are disabled.... PASSED!
CHECK #52: The Safari web browser will warn when visiting known fraudulent websites.... PASSED!
CHECK #53: JavaScript disabled in the Safari web browser.... PASSED!
CHECK #54: JavaScript disabled in the Safari web browser (Legacy version).... PASSED!
CHECK #55: Pop-up windows are blocked in the Safari web browser.... PASSED!
CHECK #56: Pop-up windows are blocked in the Safari web browser (Legacy version).... PASSED!
CHECK #57: The WebGL plug-in is disabled in the Safari web browser.... PASSED!
CHECK #58: Plug-ins are disabled in the Safari web browser.... PASSED!
CHECK #59: Plug-ins are disabled in the Safari web browser (Legacy version).... PASSED!
CHECK #60: Plug-ins are blocked by default in the Safari web browser unless a site is explicitly added to a list of allowed sites.... PASSED!
CHECK #61: The Java plug-in for Safari web browser is blocked unless a site is explicitly added to a list of allowed sites.... PASSED!
CHECK #62: The Java plug-in is disabled in the Safari web browser.... PASSED!
CHECK #63: The Java plug-in is disabled in the Safari web browser (Legacy version).... PASSED!
CHECK #64: The Safari web browser is configured to treat SHA-1 certificates as insecure.... PASSED!
CHECK #65: The Safari web browser will not pre-load webpages that rank highly as search matches.... PASSED!
CHECK #66: The Safari web browser will not include search engine suggestions for text typed in the location bar.... PASSED!
CHECK #67: The Safari web browser's search suggestions are disabled.... PASSED!
CHECK #68: The Safari web browser uses the Do-Not-Track HTTP header.... PASSED!
CHECK #69: PDF viewing is disabled in the Safari web browser.... PASSED!
CHECK #70: Full website addresses are disabled in the location bar of the Safari web browser.... PASSED!
CHECK #71: The Mail application is currently closed.... PASSED!
CHECK #72: Apple Mail does not automatically load remote content in e-mails.... PASSED!
CHECK #73: Mail identified by Apple Mail as junk is sent to the Junk mailbox.... PASSED!
CHECK #74: New e-mails composed in Apple Mail are encrypted by GPGMail if the receiver's PGP is present in the keychain.... PASSED!
CHECK #75: New e-mails composed in Apple Mail and saved as drafts are encrypted by GPGMail.... PASSED!
CHECK #76: New e-mails composed in Apple Mail are signed by GPGMail.... PASSED!
CHECK #77: Apple Mail with automatically check for updates to GPGMail.... PASSED!
CHECK #78: The Google Chrome browser is currently closed.... PASSED!
CHECK #79: All Google Chrome web browser profiles prevent information leakage through navigation errors.... PASSED!
CHECK #80: All Google Chrome web browser profiles prevent information leakage through URL suggestions.... PASSED!
CHECK #81: All Google Chrome web browser profiles prevent information leakage through network prediction.... PASSED!
CHECK #82: All Google Chrome web browser profiles prevent information leakage through report security incidents to Google.... PASSED!
CHECK #83: All Google Chrome web browser profiles have Google Safe Browsing enabled.... PASSED!
CHECK #84: All Google Chrome web browser profiles prevent information leakage through spell-checking network services.... PASSED!
CHECK #85: All Google Chrome web browser profiles prevent information leakage through reporting usage statistics to Google.... PASSED!
CHECK #86: All Google Chrome web browser profiles use the Do-Not-Track HTTP header.... PASSED!
CHECK #87: All Google Chrome web browser profiles prevent pop-ups.... PASSED!
CHECK #88: All Google Chrome web browser profiles prevent geolocation by websites.... PASSED!
CHECK #89: All Google Chrome web browser profiles block unsandboxed plug-in software.... PASSED!
CHECK #90: All Google Chrome web browser profiles prevent filling personal information into forms automatically.... PASSED!
CHECK #91: All Google Chrome web browser profiles have disabled Password Manager.... PASSED!
CHECK #92: All Google Chrome web browser profiles have disabled automatic sign-in for stored passwords.... PASSED!
CHECK #93: All Google Chrome web browser profiles have disabled Google CloudPrint.... PASSED!
CHECK #94: All Google Chrome web browser profiles have disabled Flash cookies.... PASSED!
CHECK #95: All Google Chrome web browser profiles have disabled the Chrome Pepper Flash Player plug-in.... PASSED!
CHECK #96: All Google Chrome web browser profiles have disabled the Adobe Shockwave Flash plug-in.... PASSED!
CHECK #97: All Google Chrome web browser profiles have disabled the Adobe Flash Player plug-in.... PASSED!
CHECK #98: All Google Chrome web browser profiles have disabled the Native Client plug-in.... PASSED!
CHECK #99: All Google Chrome web browser profiles have disabled the Widevine Content Decryption Module plug-in.... PASSED!
CHECK #100: All Google Chrome web browser profiles have enabled the uBlock Origin extension.... PASSED!
CHECK #100: All Google Chrome web browser profiles have enabled the uBlock Origin extension.... PASSED!
CHECK #101: All Google Chrome web browser profiles have enabled the Ghostery extension.... PASSED!
CHECK #102: All Google Chrome web browser profiles have enabled the ScriptSafe extension.... PASSED!
CHECK #103: Google Chrome is the default web browser.... PASSED!
Wrote results to '~/Documents/osx-config-check_2016-07-08_17-43-50.log'.
==========================
2 tests could not be automatically fixed, but manual instructions are available. Please manually remediate these problems and re-run the tool:
TEST #100: All Google Chrome web browser profiles have enabled the uBlock Origin extension.
1. For each of your Chrome profiles, visit https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm in Google Chrome.
2. Select "Add to Chrome".
3. Complete any required follow-up steps as instructed on the screen.
==========================
TEST #101: All Google Chrome web browser profiles have enabled the Ghostery extension.
1. For each of your Chrome profiles, visit https://chrome.google.com/webstore/detail/ghostery/mlomiejdfkolichcflejclcbmpeaniij in Google Chrome.
2. Select "Add to Chrome".
3. Complete any required follow-up steps as instructed on the screen.
==========================
```

## Troubleshooting

### Errors related to "sudo" or "sudoers"

If you receive an error message referencing these terms, the user you are currently logged in as may not be permitted to temporarily assume elevated privileges, preventing this tool from fully auditing and/or fixing your user's configuration. If you have added a non-Administrator user to your machine to help secure it, you will find that your non-Administrator user is not part of the "sudoers" list by default. To learn about how to add your user to the "sudoers" list, please [refer to this link](http://osxdaily.com/2014/02/06/add-user-sudoers-file-mac/).

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests to the repository.

## Similar Projects

* https://github.com/SummitRoute/osxlockdown

## Contributors

* [Kristov Atlas](https://twitter.com/kristovatlas/) (maintainer)
