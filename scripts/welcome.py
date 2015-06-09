#! /usr/bin/env python3

import locale
import os
import subprocess
from dialog import Dialog, PythonDialogBug


locale.setlocale(locale.LC_ALL, '')

d = Dialog(dialog="dialog", autowidgetsize=True)
d.set_background_title("GNS3")


def mode():
    if d.yesno("This feature is for testers only. You can break your GNS3 install. Are you REALLY sure you want to continue?", yes_label="Exit (Safe option)", no_label="Continue") == d.OK:
        return
    d.msgbox("You have been warned...")
    code, tag = d.menu("Select the GNS3 version",
                       choices=[("Stable", "Last stable GNS3 version RECOMMENDED"),
                                ("Testing", "Next stable release"),
                                ("Unstable", "Totaly unstable version")
                               ])
    d.clear()
    if code == Dialog.OK:
        os.makedirs(os.path.expanduser("~/.config/gns3"), exist_ok=True)
        with open(os.path.expanduser("~/.config/gns3/gns3_release"), "w+") as f:
            if tag == "Stable":
                f.write("stable")
            elif tag == "Testing":
                f.write("testing")
            elif tag == "Unstable":
                f.write("unstable")
            else:
                assert False

        update(force=True)


def get_release():
    try:
        with open(os.path.expanduser("~/.config/gns3/gns3_release")) as f:
            return f.read()
    except OSError:
        return "stable"


def update(force=False):
    if not force:
        if d.yesno("The server will reboot at the end of the update process. Continue?") != d.OK:
            return
    if get_release() == "stable":
        os.system("curl https://raw.githubusercontent.com/GNS3/gns3-packer/master/scripts/update.sh |bash && sudo reboot")
    elif get_release() == "testing":
        os.system("curl https://raw.githubusercontent.com/GNS3/gns3-packer/master/scripts/update_testing.sh |bash && sudo reboot")
    elif get_release() == "unstable":
        os.system("curl https://raw.githubusercontent.com/GNS3/gns3-packer/master/scripts/update_unstable.sh |bash && sudo reboot")


def gns3_version():
    """
    Return the GNS3 server version
    """
    try:
        return subprocess.check_output(["gns3server", "--version"]).strip().decode()
    except subprocess.CalledProcessError:
        return ""


def informations():
    """
    Show IP, SSH settings....
    """
    try:
        with open('/etc/issue') as f:
            content = f.read()
    except FileNotFoundError:
        content = """Welcome to GNS3 appliance"""

    content += "\nRelease channel: " + get_release()

    try:
        d.msgbox(content)
    # If it's an scp command or any bugs
    except:
        os.execvp("bash", ['/bin/bash'])

informations()

while True:
    code, tag = d.menu("GNS3 {}".format(gns3_version()),
                       choices=[("Update", "Update GNS3"),
                        ("Shell", "Open a console"),
                        ("Informations", "Show IP, SSH informations"),
                        ("Version", "Select the GNS3 version"),
                        ("Reboot", "Reboot the VM"),
                        ("Shutdown", "Shutdown the VM")])
    d.clear()
    if code == Dialog.OK:
        if tag == "Shell":
            os.execvp("bash", ['/bin/bash'])
        elif tag == "Version":
            mode()
        elif tag == "Reboot":
            os.execvp("sudo", ['/usr/bin/sudo', "reboot"])
        elif tag == "Shutdown":
            os.execvp("sudo", ['/usr/bin/sudo', "poweroff"])
        elif tag == "Update":
            update()
        elif tag == "Informations":
            informations()
