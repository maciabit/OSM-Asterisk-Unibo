#!/usr/bin/env python3

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus

from string_utils import roman_encode
from utils import (
	write
)

logger = logging.getLogger(__name__)


class NativeCharmCharm(CharmBase):

	def __init__(self, *args):
		super().__init__(*args)

		# Listen to charm events
		self.framework.observe(self.on.config_changed, self.on_config_changed)
		self.framework.observe(self.on.install, self.on_install)
		self.framework.observe(self.on.start, self.on_start)

		self.framework.observe(self.on.writetofile_action, self.on_write_to_file)

	def on_config_changed(self, event):
		"""Handle changes in configuration"""
		self.model.unit.status = ActiveStatus()

	def on_install(self, event):
		"""Called when the charm is being installed"""
		self.model.unit.status = ActiveStatus()

	def on_start(self, event):
		"""Called when the charm is being started"""
		self.model.unit.status = ActiveStatus()

	def on_write_to_file(self, event):
		all_params = event.params
		filename = all_params['filename']
		write(filename)
		logger.info("Trying the string util lib: roman encode of 37 is {}".format(roman_encode(37)))
		event.set_results({"edited": True, "filename": filename})


if __name__ == "__main__":
	main(NativeCharmCharm)
