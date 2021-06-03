#!/usr/bin/env python3

import logging
import subprocess
import textwrap
import re

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus

logger = logging.getLogger(__name__)

extensions_conf = "/etc/asterisk/extensions.conf"
pjsip_conf = "/etc/asterisk/pjsip.conf"


class NativeCharmCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)

        # Listen to charm events
        self.framework.observe(self.on.config_changed, self.on_config_changed)
        self.framework.observe(self.on.install, self.on_install)
        self.framework.observe(self.on.start, self.on_start)

        self.framework.observe(self.on.startasterisk_action, self.on_start_asterisk)
        self.framework.observe(self.on.adduser_action, self.on_add_user)
        self.framework.observe(self.on.removeuser_action, self.on_remove_user)

    def on_config_changed(self, event):
        """Handle changes in configuration"""
        self.model.unit.status = ActiveStatus()

    def on_install(self, event):
        """Called when the charm is being installed"""
        self.model.unit.status = ActiveStatus()

    def on_start(self, event):
        """Called when the charm is being started"""
        self.model.unit.status = ActiveStatus()

    def on_start_asterisk(self, event):
        subprocess.run("asterisk -cvvvvv", shell=True)

    def on_add_user(self, event):
        all_params = event.params
        username = all_params["username"]
        password = all_params["password"]

        # Add user to extensions.conf
        with open(extensions_conf, "a") as f:
            f.write(f"exten => {username},1,Dial(PJSIP/{username},20)\n")

        # Add user to pjsip.conf
        with open(pjsip_conf, "a") as f:
            f.write(
                textwrap.dedent(
                    f"""
				[{username}](template_hackfest)
				auth={username}
				aors={username}

				[{username}](auth_userpass)
				username={username}
				password={password}

				[{username}](aor_dynamic)
				"""
                )
            )

        subprocess.run('asterisk -rx "reload"', shell=True)

    def on_remove_user(self, event):
        all_params = event.params
        username = all_params["username"]

        # Remove user from extensions.conf
        with open(extensions_conf, "r") as f:
            lines = f.readlines()
        with open(extensions_conf, "w") as f:
            for line in lines:
                if (
                    line.strip("\n")
                    != f"exten => {username},1,Dial(PJSIP/{username},20)"
                ):
                    f.write(line)

        # Remove user from pjsip.conf
        with open(pjsip_conf, "r") as f:
            file_content = f.read()
        x = re.search(
            f"(?s)(?<=\[{username}\]\(template_hackfest\)).*?(?=\[{username}\]\(aor_dynamic\))",
            file_content,
            flags=re.MULTILINE,
        )
        if not x:
            return
        user_settings = (
            f"\n[{username}](template_hackfest){x[0]}[{username}](aor_dynamic)\n"
        )
        file_content = file_content.replace(user_settings, "")
        with open(pjsip_conf, "w") as f:
            f.write(file_content)

        subprocess.run('asterisk -rx "reload"', shell=True)


if __name__ == "__main__":
    main(NativeCharmCharm)
