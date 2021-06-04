import subprocess
import textwrap
import re


def start_asterisk():
    with open(extensions_conf, "a") as f:
        f.write(textwrap.dedent(f"""
            exten => _.!,1,Answer()
            same => n,Playback(cannot-complete-as-dialed)
        """))
    subprocess.run("asterisk -vvvvv", shell=True)


def reload_asterisk():
	subprocess.run('asterisk -rx "core restart now"', shell=True, check=True)


class Utils():
	def __init__(self, extensions_conf, pjsip_conf):
		self.extensions_conf = extensions_conf
		self.pjsip_conf = pjsip_conf

	def add_user(self, username, password):
		# Add user to extensions.conf
		with open(self.extensions_conf, "a") as f:
			f.write(textwrap.dedent(f"""
                exten => {username},1,Dial(PJSIP/{username},20)
                same = n,Answer()
                same = n,Wait(1)
                same = n,Playback(sorry)
                same = n,Hangup()
            """))
		# Add user to pjsip.conf
		with open(self.pjsip_conf, "a") as f:
			f.write(textwrap.dedent(f"""
                [{username}](template_hackfest)
                auth={username}
                aors={username}

                [{username}](auth_userpass)
                username={username}
                password={password}

                [{username}](aor_dynamic)
            """))

	def remove_user(self, username):

		# Remove user from extensions.conf
		with open(self.extensions_conf, "r") as f:
			file_content = f.read()
		x = re.search(
			f"(?s)(?<=exten => {username},).*?(?=\nexten|\Z)",
			file_content,
			flags=re.MULTILINE,
		)
		if x:
			extensions_conf_user = f"\nexten => {username},{x[0]}"
			file_content = file_content.replace(extensions_conf_user, "")
			with open(self.extensions_conf, "w") as f:
				f.write(file_content)

		# Remove user from pjsip.conf
		with open(self.pjsip_conf, "r") as f:
			file_content = f.read()
		x = re.search(
			f"(?s)(?<=\[{username}\]\(template_hackfest\)).*?(?=\[{username}\]\(aor_dynamic\))",
			file_content,
			flags=re.MULTILINE,
		)
		if x:
			pjsip_conf_user = f"\n[{username}](template_hackfest){x[0]}[{username}](aor_dynamic)\n"
			file_content = file_content.replace(pjsip_conf_user, "")
			with open(self.pjsip_conf, "w") as f:
				f.write(file_content)
