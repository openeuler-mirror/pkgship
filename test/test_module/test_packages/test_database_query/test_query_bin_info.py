from unittest import TestCase
from unittest.mock import MagicMock

from packageship.application.query.pkg import QueryPackage
from test.test_module.test_packages.test_database_query.get_mock_data import ObtainMockData


class TestQueryBinaryPkgInfo(TestCase):
    ALL_BINARY_RPM_INFO = ObtainMockData.get_data("allBinaryNoPaging.json")
    ALL_BINARY_INFO_PAGING = ObtainMockData.get_data("allBinaryPaging.json")
    JUDY_BINARY_INFO = ObtainMockData.get_data("JudyBinary.json")

    def setUp(self):
        self.query_package = QueryPackage()
        self.session = self.query_package._db_session

    def test_query_all_no_paging(self):
        """
        Test query all binary packages, used for cli
        Returns:
        """
        self.session.scan = MagicMock(return_value=self.ALL_BINARY_RPM_INFO)
        query_result = self.query_package.get_bin_info(binary_list=[], database='openeuler', page_num=1, page_size=20,
                                                       query_all=True)
        self.assertIsNotNone(query_result['data'])

    def test_query_all_paging(self):
        """
        Test query all binary packages and paging, used for RESTful
        Returns:
        """
        self.session.query = MagicMock(return_value=self.ALL_BINARY_INFO_PAGING)
        query_result = self.query_package.get_bin_info(binary_list=[], database='openeuler', page_num=1, page_size=5,
                                                       query_all=False)
        self.assertEqual(len(query_result['data']), 5)

    def test_query_specify(self):
        """
        Test query specify binary packages and paging
        Returns:
        """
        self.session.query = MagicMock(return_value=self.JUDY_BINARY_INFO)
        query_result = self.query_package.get_bin_info(binary_list=['Judy'], database='openeuler', page_num=1,
                                                       page_size=5, query_all=False)
        self.assertIsNotNone(query_result['data'][0]['Judy'])

    def test_query_no_data(self):
        """
        Test query not exist binary packages and paging
        Returns:
        """
        self.session.query = MagicMock(return_value=[])
        query_result = self.query_package.get_bin_info(binary_list=['Judy'], database='openeuler', page_num=1,
                                                       page_size=5, query_all=False)
        self.assertListEqual(query_result['data'], [])
