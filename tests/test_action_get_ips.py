import yaml
import requests_mock
from mock import patch

from st2tests.base import BaseActionTestCase

from get_ips import GetIPsAction

__all__ = [
    'GetIPsActionTestCase'
]

MOCK_CONFIG_FULL = yaml.safe_load(open(
    'tests/fixture/config_full.yaml').read())

MOCK_DATA_INVALID_JSON = "{'dd': doo}"
MOCK_DATA_SUCCESS = open(
    'tests/fixture/get_ips_success.json').read()
MOCK_DATA_FAIL = open(
    'tests/fixture/common_fail.json').read()


class GetIPsActionTestCase(BaseActionTestCase):
    action_cls = GetIPsAction

    def test_run_is_instance(self):
        action = self.get_action_instance(MOCK_CONFIG_FULL)

        self.assertIsInstance(action, self.action_cls)
        self.assertEqual(action.api_key, "API-Key")
        self.assertEqual(action.API_HOST, "https://api.cloudflare.com")

    @patch('get_ips.GetIPsAction.API_HOST', "mock://api.cloudflare.com")
    def test_run_status_404(self):
        action = self.get_action_instance(MOCK_CONFIG_FULL)

        adapter = requests_mock.Adapter()
        action.session.mount('mock', adapter)

        adapter.register_uri('GET',
                             "mock://api.cloudflare.com/client/v4/ips",
                             status_code=404)

        self.assertRaises(ValueError,
                          action.run)

    @patch('get_ips.GetIPsAction.API_HOST', "mock://api.cloudflare.com")
    def test_run_invalid_json(self):
        action = self.get_action_instance(MOCK_CONFIG_FULL)

        adapter = requests_mock.Adapter()
        action.session.mount('mock', adapter)

        adapter.register_uri('GET',
                             "mock://api.cloudflare.com/client/v4/ips",
                             text=MOCK_DATA_INVALID_JSON)

        self.assertRaises(ValueError,
                          action.run)

    @patch('get_ips.GetIPsAction.API_HOST', "mock://api.cloudflare.com")
    def test_run_success_true(self):
        expected = {'ipv4_cidrs': [u'199.27.128.0/21'],
                    'ipv6_cidrs': [u'2400:cb00::/32'],
                    'messages': []}

        action = self.get_action_instance(MOCK_CONFIG_FULL)

        adapter = requests_mock.Adapter()
        action.session.mount('mock', adapter)

        adapter.register_uri('GET',
                             "mock://api.cloudflare.com/client/v4/ips",
                             text=MOCK_DATA_SUCCESS)

        result = action.run()
        self.assertEqual(result, expected)

    @patch('get_ips.GetIPsAction.API_HOST', "mock://api.cloudflare.com")
    def test_run_success_false(self):
        action = self.get_action_instance(MOCK_CONFIG_FULL)

        adapter = requests_mock.Adapter()
        action.session.mount('mock', adapter)

        adapter.register_uri('GET',
                             "mock://api.cloudflare.com/client/v4/ips",
                             text=MOCK_DATA_FAIL)
        self.assertRaises(Exception,
                          action.run)
