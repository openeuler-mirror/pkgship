import unittest

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
    def test_dispatch_install(self):
        insd = DispatchDepend.execute(**install_params)
        self.assertTrue(isinstance(insd, InstallDepend))
    
    def test_dispatch_build(self):
        insd = DispatchDepend.execute(**build_params)
        self.assertTrue(isinstance(insd, BuildDepend))
    
    def test_dispatch_selfdep(self):
        insd = DispatchDepend.execute(**selfdep_params)
        self.assertTrue(isinstance(insd, SelfDepend))
    
    def test_dispatch_bedep(self):
        insd = DispatchDepend.execute(**bedep_params)
        self.assertTrue(isinstance(insd, BeDepend))
        
    def test_dispatch_error_depend_type(self):
        with self.assertRaises(AttributeError):
            DispatchDepend.execute(**error_depend_type_params)
    
    def test_dispatch_no_depend_type(self):
        with self.assertRaises(ValueError):
            DispatchDepend.execute(**no_depend_type_params)