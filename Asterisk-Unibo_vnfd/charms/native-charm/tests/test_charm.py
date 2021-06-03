import pathlib
import textwrap
import unittest
from unittest.mock import Mock

from charm import NativeCharmCharm
from ops.testing import Harness

EXTENSION_FILE = f"{pathlib.Path(__file__).parent.absolute()}/mocked_config_files/extensions.conf"
PJSIP_FILE = f"{pathlib.Path(__file__).parent.absolute()}/mocked_config_files/pjsip.conf"


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(NativeCharmCharm, config='{"options": {"testing": {"default": True}}}')
        self.addCleanup(self.harness.cleanup)
        self.__files_cleanup()
        self.harness.begin()

    def __files_cleanup(self):
        open(PJSIP_FILE, 'w').close()
        open(EXTENSION_FILE, 'w').close()

    def __get_file_content(self, filename):
        with open(filename, 'r') as file:
            return file.read()

    def test_add_user(self):
        username = "lampa"
        password = "dina"
        expected_pjsip = textwrap.dedent(f"""
                [{username}](template_hackfest)
                auth={username}
                aors={username}

                [{username}](auth_userpass)
                username={username}
                password={password}

                [{username}](aor_dynamic)
            """)
        extensions_conf = textwrap.dedent(f"""
                exten => {username},1,Dial(PJSIP/{username},20)
                same = n,Answer()
                same = n,Wait(1)
                same = n,Playback(sorry)
                same = n,Hangup()
            """)
        action_event = Mock(params={"username": username, "password": password})
        self.harness.charm.on_add_user(action_event)
        self.assertEqual(expected_pjsip, self.__get_file_content(PJSIP_FILE),
                         "pjsip configurations do not match")
        self.assertEqual(extensions_conf, self.__get_file_content(EXTENSION_FILE),
                         "extensions configurations do not match")

    def test_add_user_twice(self):
        username = "lampa"
        password = "dina"
        expected_pjsip = textwrap.dedent(f"""
                [{username}](template_hackfest)
                auth={username}
                aors={username}

                [{username}](auth_userpass)
                username={username}
                password={password}

                [{username}](aor_dynamic)
            """)
        extensions_conf = textwrap.dedent(f"""
                exten => {username},1,Dial(PJSIP/{username},20)
                same = n,Answer()
                same = n,Wait(1)
                same = n,Playback(sorry)
                same = n,Hangup()
            """)
        action_event = Mock(params={"username": username, "password": password})
        self.harness.charm.on_add_user(action_event)
        self.harness.charm.on_add_user(action_event)
        self.assertEqual(expected_pjsip, self.__get_file_content(PJSIP_FILE),
                         "pjsip configurations do not match")
        self.assertEqual(extensions_conf, self.__get_file_content(EXTENSION_FILE),
                         "extensions configurations do not match")


    def test_remove_user(self):
        username = "lampa"
        password = "dina"
        add_action_event = Mock(params={"username": username, "password": password})
        remove_action_event = Mock(params={"username": username})
        self.harness.charm.on_add_user(add_action_event)
        self.harness.charm.on_remove_user(remove_action_event)
        self.assertEqual("", self.__get_file_content(EXTENSION_FILE), "pjsip configurations do not match")
        self.assertEqual("", self.__get_file_content(PJSIP_FILE), "extensions configurations do not match")

    def test_remove_no_existing_user(self):
        username = "lampa"
        password = "dina"
        remove_action_event = Mock(params={"username": username})
        self.harness.charm.on_remove_user(remove_action_event)
        self.assertTrue(remove_action_event.fail.called)
