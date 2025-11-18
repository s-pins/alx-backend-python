#!/usr/bin/env python3
"""
Tests the utils module
"""
from parameterized import (
    parameterized,
    parameterized_class)
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import client
from typing import (
    Mapping,
    Sequence,
    Dict,
)
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """
    class to test the client module that exits in this folder
    """
    @parameterized.expand(
        [
            ('google', {"name": "Google", "id": 1}),
            ('abc', {"name": "ABC", "id": 2}),
        ]
    )
    @patch('client.get_json')
    def test_org(self, org_name: str,
                 result: dict,
                 mocked_object: MagicMock):
        """
        Test to test that the org is called correctly
        """
        mocked_object.return_value = result
        org = client.GithubOrgClient(org_name)
        self.assertEqual(org.org, result)
        mocked_object.assert_called_once_with(
            client.GithubOrgClient.ORG_URL.format(org=org_name)
        )

    def test_public_repos_url(self):
        """
        Test to test the public repos urls
        """
        known_org_payload = {
            "repos_url": "https://api.github.com/orgs/test/repos"
        }
        with patch("client.GithubOrgClient.org",
                   new_callable=PropertyMock,
                   return_value=known_org_payload) as mock_method:
            dummy = client.GithubOrgClient('google')

            result_url = dummy._public_repos_url

            self.assertEqual(
                result_url, known_org_payload['repos_url']
            )
            mock_method.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mocked_object: MagicMock):
        """
        Test to test the public repos url method
        """
        mocked_object.return_value = [
            {"name": "repo-one"},
            {"name": "repo-two"},
            {"name": "repo-three"},
        ]
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock,
                   return_value="https://api.github.com/" +
                   "orgs/test/repos") as mocked_method:
            dummy = client.GithubOrgClient("google")
            self.assertEqual(dummy.public_repos(), [
                "repo-one", "repo-two", "repo-three"
            ])
            mocked_method.assert_called_once()
            mocked_object.assert_called_once()
            mocked_object.assert_called_once_with(
                "https://api.github.com/orgs/test/repos"
            )

    @parameterized.expand(
        [
            ({"license": {"key": "my_license"}}, "my_license", True),
            ({"license": {"key": "other_license"}}, "my_license", False),
        ]
    )
    def test_has_license(self, repo, license_key, result):
        """
        test the has_license method in the gihub repo file
        """
        self.assertEqual(
            client.GithubOrgClient.has_license(
                repo=repo, license_key=license_key
            ),
            result
        )


@parameterized_class(
    ('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test class for GithubOrgClient.
    This class mocks the external 'requests.get' calls to test
    the 'public_repos' method.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the class by patching 'requests.get'.

        The patcher uses a side_effect function to return different
        JSON payloads based on the URL being requested.
        """

        def requests_get_side_effect(url: str):
            """
            Custom side effect to mock requests.get(url).json()
            """
            mock_response = MagicMock()

            org_url = "https://api.github.com/orgs/google"

            repos_url = cls.org_payload["repos_url"]

            if url == org_url:
                mock_response.json.return_value = cls.org_payload
            elif url == repos_url:
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.status_code = 404
                mock_response.json.return_value = {"message": "Not Found"}

            return mock_response

        cls.get_patcher = patch('utils.requests.get')

        mock_requests_get = cls.get_patcher.start()
        mock_requests_get.side_effect = requests_get_side_effect

    @classmethod
    def tearDownClass(cls):
        """
        Stop the patcher after all tests are run.
        """
        cls.get_patcher.stop()

    # --- Task 9: Implement the tests ---

    def test_public_repos(self):
        """
        Test the 'public_repos' method without a license.

        It should return all repo names from the 'repos_payload'.
        """
        client_instance = client.GithubOrgClient("google")

        repos = client_instance.public_repos()

        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """
        Test the 'public_repos' method with the 'apache-2.0' license.

        It should return only the repos matching that license.
        """
        client_instance = client.GithubOrgClient("google")

        repos = client_instance.public_repos(license="apache-2.0")

        self.assertEqual(repos, self.apache2_repos)
