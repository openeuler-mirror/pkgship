import unittest
from unittest import mock
from redis import Redis

from packageship.application.core.depend import DispatchDepend
from packageship.application.core.depend.install_depend import InstallDepend
from packageship.application.core.depend.build_depend import BuildDepend
from packageship.application.core.depend.self_depend import SelfDepend
from packageship.application.core.depend.be_depend import BeDepend


install_params = {
    "packagename": ["Judy"],
    "depend_type": "installdep",
    "parameter": {"db_priority": ["Mainline", "fedora"], "level": 2},
}

build_params = {
    "packagename": ["Judy"],
    "depend_type": "builddep",
    "parameter": {
        "db_priority": ["Mainline", "fedora"],
        "level": 2,
        "self_build": True,
    },
}

selfdep_params = {
    "packagename": ["Judy"],
    "depend_type": "selfdep",
    "parameter": {
        "db_priority": ["Mainline", "fedora"],
        "self_build": False,
        "packtype": "source",
        "with_subpack": False,
    },
}

bedep_params = {
    "packagename": ["Judy"],
    "depend_type": "bedep",
    "parameter": {
        "db_priority": ["Mainline"],
        "packtype": "source",
        "with_subpack": False,
        "search_type": "install",
    },
}

error_depend_type_params = {
    "packagename": ["Judy"],
    "depend_type": "errordepend",
    "parameter": {"db_priority": ["Mainline", "fedora"], "level": 2},
}

no_depend_type_params = {
    "packagename": ["Judy"],
    "parameter": {"db_priority": ["Mainline", "fedora"], "level": 2},
}


class TestDispatch(unittest.TestCase):
    """ Test DispatchDepend class
    """
    @mock.patch.object(Redis, "exists")
    @mock.patch.object(Redis, "hgetall")
    def test_dispatch_install(self, mock_hgetall, mock_exists):
        """test dispatch install depend
        """
        mock_hgetall.return_value = {
            "source_dict": '{"glibc":"glibc"}',
            "binary_dict": '{"glibc":"glibc"}',
        }

        mock_exists.return_value = True
        a = 1/0
        insd = DispatchDepend.execute(**install_params)
        self.assertTrue(isinstance(insd, InstallDepend))

    @mock.patch.object(Redis, "exists")
    @mock.patch.object(Redis, "hgetall")
    def test_dispatch_build(self, mock_hgetall, mock_exists):
        """test dispatch build depend
        """
        mock_hgetall.return_value = {
            "source_dict": '{"glibc":"glibc"}',
            "binary_dict": '{"glibc":"glibc"}',
        }

        mock_exists.return_value = True

        insd = DispatchDepend.execute(**build_params)
        self.assertTrue(isinstance(insd, BuildDepend))

    @mock.patch.object(Redis, "exists")
    @mock.patch.object(Redis, "hgetall")
    def test_dispatch_selfdep(self, mock_hgetall, mock_exists):
        """test dispatch selfdep depend
        """
        mock_hgetall.return_value = {
            "source_dict": '{"glibc":"glibc"}',
            "binary_dict": '{"glibc":"glibc"}',
        }

        mock_exists.return_value = True
        insd = DispatchDepend.execute(**selfdep_params)
        self.assertTrue(isinstance(insd, SelfDepend))

    @mock.patch.object(Redis, "exists")
    @mock.patch.object(Redis, "hgetall")
    def test_dispatch_bedep(self, mock_hgetall, mock_exists):
        """test dispatch bedep depend
        """
        mock_hgetall.return_value = {
            "source_dict": '{"glibc":"glibc"}',
            "binary_dict": '{"glibc":"glibc"}',
        }

        mock_exists.return_value = True
        insd = DispatchDepend.execute(**bedep_params)
        self.assertTrue(isinstance(insd, BeDepend))

    def test_dispatch_error_depend_type(self):
        """test params error depend_type value
        """
        with self.assertRaises(AttributeError):
            DispatchDepend.execute(**error_depend_type_params)

    def test_dispatch_no_depend_type(self):
        """test params no depend_type key
        """
        with self.assertRaises(ValueError):
            DispatchDepend.execute(**no_depend_type_params)