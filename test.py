import unittest
from unittest import mock
from client import Client


class TestClient(unittest.TestCase):
    """Test create and delete method of the customer class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = Client({"groupId": "ami-0b0dcb5067f052a63"})

    def test_create_group_success_in_all_hosts(self):
        """Test create groups in all hosts."""
        self.client.create_group_in_host = mock.Mock(return_value=201)
        self.assertEqual(self.client.create_groups(), "Create success")

    def test_create_group_failed_in_first_host(self):
        """Test create group when this group already exist in hosts."""
        self.client.create_group_in_host = mock.Mock(return_value=400)
        self.assertEqual(
            self.client.create_groups(), "Error, create group failed in first host"
        )

    @mock.patch("client.Client.create_group_in_host", side_effect=[201, 201, 500])
    @mock.patch("client.Client.delete_group_in_host", side_effect=[200, 200, 200])
    def test_create_group_failed_in_last_host(self, delete, create):
        """Test create group in all hosts, but failed in last host."""
        self.assertEqual(
            self.client.create_groups(),
            "Error, create group failed, rolled back created group",
        )

    @mock.patch("client.Client.create_group_in_host", side_effect=[201, 201, 500])
    @mock.patch("client.Client.delete_group_in_host", side_effect=[200, 200, 400])
    def test_create_group_failed_in_last_host_and_failed_in_last_rollback(
        self, delete, create
    ):
        """Test fail to create group and one rollback has error."""
        self.assertEqual(
            self.client.create_groups(),
            "Error, create group failed, rolled back created group",
        )

    @mock.patch(
        "client.Client.create_group_in_host", side_effect=[201, 201, Exception("oops")]
    )
    @mock.patch("client.Client.delete_group_in_host", side_effect=[200, 200, 200])
    def test_create_group_failed_in_last_group_with_exception_raised(
        self, delete, create
    ):
        """Test create group in all hosts, but failed in last host due to Exception occurs."""

        self.assertEqual(
            self.client.create_groups(),
            "Error, create group failed, rolled back created group",
        )

    @mock.patch(
        "client.Client.create_group_in_host", side_effect=[201, 201, Exception("oops")]
    )
    @mock.patch("client.Client.delete_group_in_host", side_effect=[400, 200, 200])
    def test_create_group_failed_in_last_group_with_exception_raised_and_failed_on_first_rollback(
        self, delete, create
    ):
        """
        Test create group in all hosts, but failed in last host due to Exception occurs
        And error hanppens when rollback.
        """

        self.assertEqual(
            self.client.create_groups(),
            "Error, create group failed, rolled back created group",
        )

    @mock.patch("client.Client.create_group_in_host", side_effect=[Exception("oops")])
    def test_create_group_failed_with_exception_raised_in_first_host(self, create):
        """Test create group in all hosts, but failed in first host due to Exception occurs."""
        self.assertEqual(
            self.client.create_groups(),
            "Error, create group failed in first host",
        )

    def test_delete_group_success_in_all_hosts(self):
        """Test delete group from all hosts successfully."""
        self.client.delete_group_in_host = mock.Mock(return_value=200)
        self.assertEqual(self.client.delete_groups(), "Delete successfully")

    def test_delete_group_failed_in_first_host(self):
        """Test delete group failed"""
        self.client.delete_group_in_host = mock.Mock(return_value=400)
        self.assertEqual(
            self.client.delete_groups(), "Error, delete failed in first host"
        )

    @mock.patch("client.Client.delete_group_in_host", side_effect=[200, 200, 500])
    @mock.patch("client.Client.create_group_in_host", side_effect=[201, 201, 201])
    def test_delete_group_failed_in_last_group(self, create, delete):
        """Test delete group fail in last host and all rollbacks are successful."""
        self.assertEqual(
            self.client.delete_groups(),
            "Error, Failed to delete from all hosts and deleted group(s) were rolled back",
        )

    @mock.patch("client.Client.delete_group_in_host", side_effect=[200, 200, 500])
    @mock.patch("client.Client.create_group_in_host", side_effect=[201, 201, 400])
    def test_delete_group_failed_in_last_host_and_failed_in_last_rollback(
        self, create, delete
    ):
        """Test delete group failed in last host and error occured when rollback."""
        self.assertEqual(
            self.client.delete_groups(),
            "Error, Failed to delete from all hosts and deleted group(s) were rolled back",
        )

    @mock.patch(
        "client.Client.delete_group_in_host", side_effect=[200, 200, Exception("oops")]
    )
    @mock.patch("client.Client.create_group_in_host", side_effect=[201, 201, 201])
    def test_delete_group_failed_in_last_host_with_exception_raised(
        self, delete, create
    ):
        """Test delete group in all hosts, but failed in last host due to Exception occurs."""

        self.assertEqual(
            self.client.delete_groups(),
            "Error, Failed to delete from all hosts and deleted group(s) were rolled back",
        )

    @mock.patch(
        "client.Client.delete_group_in_host", side_effect=[200, 200, Exception("oops")]
    )
    @mock.patch("client.Client.create_group_in_host", side_effect=[400, 201, 201, 201])
    def test_delete_group_failed_in_last_host_with_exception_raised_and_failed_to_rollback(
        self, delete, create
    ):
        """
        Test delete group in all hosts, but failed in last host due to Exception occurs
        and error happens in rollback.
        """

        self.assertEqual(
            self.client.delete_groups(),
            "Error, Failed to delete from all hosts and deleted group(s) were rolled back",
        )

    @mock.patch("client.Client.delete_group_in_host", side_effect=[Exception("oops")])
    def test_delete_group_failed_in_first_host_with_exception_raised(self, delete):
        """Test delete group in all hosts, but failed in first host due to Exception occurs."""

        self.assertEqual(
            self.client.delete_groups(),
            "Error, delete failed in first host",
        )


if __name__ == "__main__":
    unittest.main()
