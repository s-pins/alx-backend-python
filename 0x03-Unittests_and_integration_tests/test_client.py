#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand([
        ("google"),
        ("abc"),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the expected value"""

        # mock return value
        expected_payload = {"payload": True}
        mock_get_json.return_value = expected_payload

        # instantiate client
        client = GithubOrgClient(org_name)

        # call property
        result = client.org

        # test behavior
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, expected_payload)

    
    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct URL from org payload"""

        # Mocked org payload
        mocked_payload = {"repos_url": "https://api.github.com/orgs/test/repos"}

        # Patch GithubOrgClient.org as a property
        with patch("client.GithubOrgClient.org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = mocked_payload

            client = GithubOrgClient("test")
            result = client._public_repos_url

            # Assert returned URL matches mocked payload
            self.assertEqual(result, mocked_payload["repos_url"])


if __name__ == "__main__":
    unittest.main()
