import requests


class Client:
    """
    A class to represent a client.

    """

    path = "/v1/group"
    hosts = [
        "node1.example.com",
        "node2.example.com",
        "node3.example.com",
    ]

    def __init__(self, group):
        """
        :param group: dict
            group id of the client
        """
        self.group = group

    def create_group_in_host(self, host):
        """
        Request to create group.
        :return: status code.
        """

        url = host + self.path
        response = requests.post(url, json=self.group)
        return response.status_code

    def delete_group_in_host(self, host):
        """
        Request to delete group.
        :return: status code.
        """

        url = host + self.path
        response = requests.delete(url, json=self.group)
        return response.status_code

    def rollback_created_group_in_hosts(self, index):
        """
        Rollback host(s) which created, if no host was created then return failed message.
        :param index: index of group which failed to create in host.
        :return: Error information.
        """

        created_host_list = self.hosts[0:index]

        if len(created_host_list) > 0:
            for i, created_host in enumerate(created_host_list):
                rolled_back = False
                while not rolled_back:
                    try:
                        status_code = self.delete_group_in_host(
                            created_host + self.path, json=self.group
                        )
                        if status_code == 200:
                            rolled_back = True
                    except:
                        rolled_back = False
            return "Error, create group failed, rolled back created group"

        return "Error, create group failed in first host"

    def create_groups(self):
        """
        Create groups in all hosts, if failed to create in one host, then rollback created group(s).
        :return: Message
        """
        for index, host in enumerate(self.hosts):
            try:
                status_code = self.create_group_in_host(host)

                # if status code is not 201 which means error happened in creating, then will roll back created group(s),then will roll back created group(s),then will roll back created group(s)
                if status_code != 201:
                    return self.rollback_created_group_in_hosts(index)
            except:
                # roll back group from host(s) which was created successfully
                # keep on rolling back if not success in deleting group
                return self.rollback_created_group_in_hosts(index)

        return "Create success"

    def rollback_deleted_group_in_hosts(self, index):
        """
        Rollback deleted group(s).
        :param index: index of group which failed to delete.
        :return: Error information.
        """
        deleted_host_list = self.hosts[0:index]
        if len(deleted_host_list) > 0:
            for i, deleted_host in enumerate(deleted_host_list):
                # keep rolling back until success.
                rolled_back = False
                while not rolled_back:
                    try:
                        status_code = self.create_group_in_host(
                            deleted_host + self.path, json=self.group
                        )
                        if status_code == 201:
                            rolled_back = True
                    except:
                        rolled_back = False
            return "Error, Failed to delete from all hosts and deleted group(s) were rolled back"
        return "Error, delete failed in first host"

    def delete_groups(self):
        """
        Delete groups from all hosts, if failed to delete in one host, then rollback deleted group(s).
        :return: message
        """
        for index, host in enumerate(self.hosts):
            try:
                # Delete group from host, if success continue on deleting group from next host,
                # If failed, rollback all deleted group(s).
                #
                status_code = self.delete_group_in_host(host)
                if status_code != 200:
                    return self.rollback_deleted_group_in_hosts(index)
            except:
                return self.rollback_deleted_group_in_hosts(index)
        return "Delete successfully"
