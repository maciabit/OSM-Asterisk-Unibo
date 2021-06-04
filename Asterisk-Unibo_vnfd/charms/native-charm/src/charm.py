#!/usr/bin/env python3

import logging
import pathlib

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus

from src.utils import (
	Utils,
	start_asterisk,
	reload_asterisk
)

logger = logging.getLogger(__name__)

class NativeCharmCharm(CharmBase):
	_stored = StoredState()

	def __init__(self, *args):
		super().__init__(*args)
		self._stored.set_default(users=set())

		# Listen to charm events
		self.framework.observe(self.on.config_changed, self.on_config_changed)
		self.framework.observe(self.on.install, self.on_install)
		self.framework.observe(self.on.start, self.on_start)

		self.framework.observe(self.on.startasterisk_action, self.on_start_asterisk)
		self.framework.observe(self.on.adduser_action, self.on_add_user)
		self.framework.observe(self.on.removeuser_action, self.on_remove_user)

		if self.config['testing']:
			self.utils = Utils(extensions_conf=f"{pathlib.Path(__file__).parent.parent.absolute()}/tests/mocked_config_files"
			                                   f"/extensions.conf",
			                   pjsip_conf=f"{pathlib.Path(__file__).parent.parent.absolute()}/tests/mocked_config_files"
			                              f"/pjsip.conf")
		else:
			self.utils = Utils(extensions_conf="/etc/asterisk/extensions.conf",
			                   pjsip_conf="/etc/asterisk/pjsip.conf")

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
		try:
			start_asterisk()
			event.set_results({"message": "Asterisk started correctly"})
		except Exception as e:
			event.fail(message=f'Error: {str(e)}')

	def on_add_user(self, event):
		all_params = event.params
		username = all_params["username"]
		password = all_params["password"]

		if username in self._stored.users:
			event.fail(message=f'Username {username} already exists')
			return

		try:
			self.utils.add_user(username, password)
			self._stored.users.add(username)
			if not self.config['testing']:
				reload_asterisk()
			event.set_results({"message": f"User {username} successfully added"})
		except Exception as e:
			event.fail(message=f'Error: {str(e)}')

	def on_remove_user(self, event):
		all_params = event.params
		username = all_params["username"]

		if username not in self._stored.users:
			event.fail(message=f'Username {username} doesn\'t exist')
			return

		try:
			self.utils.remove_user(username)
			self._stored.users.remove(username)
			if not self.config['testing']:
				reload_asterisk()
			event.set_results({"message": f"User {username} successfully removed"})
		except Exception as e:
			event.fail(message=f'Error: {str(e)}')


if __name__ == "__main__":
	main(NativeCharmCharm)
