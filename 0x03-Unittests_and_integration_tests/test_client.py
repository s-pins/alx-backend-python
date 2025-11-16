#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""

import unittest
import requests
from unittest.mock import patch, PropertyMock
from parameterized import parameterized

from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the expected value"""
        expected_payload = {"payload": True}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        mock_get_json.assert_called_once_with(
            "https://api.github.com/orgs/{}".format(
                org_name
            )
        )

        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self):
        """Test _public_repos_url returns correct repos_url"""
        mocked_payload = {"repos_url": "https://api.github.com/orgs/test/repos"}

        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = mocked_payload
            client = GithubOrgClient("test")
            result = client._public_repos_url
            self.assertEqual(result, mocked_payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Unit-test GithubOrgClient.public_repos with patched get_json and
        _public_repos_url"""
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
        ]
        expected_repos = ["repo1", "repo2"]

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_repos_url:
            mock_repos_url.return_value = (
                "https://api.github.com/orgs/test/repos"
            )
            client = GithubOrgClient("test")
            repos = client.public_repos()

            self.assertEqual(repos, expected_repos)
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/test/repos"
            )

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license returns correct boolean"""
        client = GithubOrgClient("test")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)

@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [(org_payload, repos_payload, expected_repos, apache2_repos)]
)
class TestIntegrationGithubOrgClient(TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Set up patcher for requests.get with side_effect for fixtures"""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        # side_effect function to return different payloads based on URL
        def side_effect(url, *args, **kwargs):
            mock_response = Mock()
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload['repos_url']:
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = None
            return mock_response

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repos list"""
        client = GithubOrgClient(self.org_payload["login"])
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filtered by license"""
        client = GithubOrgClient(self.org_payload["login"])
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
