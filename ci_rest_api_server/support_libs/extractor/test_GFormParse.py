import datetime
import os
import shutil
import unittest

from ci_rest_api_server.support_libs.extractor.GFormParse import GeneralFormParser
from secedgar.filings import Filing, FilingType

TEST_FILE_LOCATION = "/tmp"
FILE_TYPES = {
    'test_missing_data': '/test_file.txt',
    'test_correct_form_type_year_extraction': '/aapl/10-k/0000320193-18-000145.txt',
}


class TestGeneralFormParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Setups up files for testing cases
        """
        # create a file with junk data -
        path = TEST_FILE_LOCATION + FILE_TYPES['test_missing_data']
        with open(path, "w+") as file:
            for _ in range(1, 10):
                file.write("THis is a test line \n")

        # file will be used for test_correct_form_type_year_extraction
        # This will make sure that we are pulling 2018 records only as they parse well
        start_date, end_date = datetime.datetime(2018, 8, 1), datetime.datetime(2019, 1, 1)
        # Get a known good company and a single 10-k form
        my_filings = Filing(cik_lookup='aapl',
                            filing_type=FilingType.FILING_10K,
                            count=1,
                            start_date=start_date,
                            end_date=end_date)
        my_filings.save(TEST_FILE_LOCATION)

    @classmethod
    def tearDownClass(cls):
        """
        Tear down file resources
        """
        # remember to remove all the temp files
        for value in FILE_TYPES.values():
            path = TEST_FILE_LOCATION + value
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            else:
                print(f"Unable to delete file(s) at {path}")

    def test_non_exisitent_file(self):
        """
        This case will test parsing a non existent file
        """
        test_obj = GeneralFormParser()
        with self.assertRaises(FileNotFoundError):
            test_obj.get_form_type_and_filing_year('tmp/text.txt')

    def test_missing_data(self):
        """
        This test case will put a non SEC content based file to see correct
        error reporting from the function
        """

        test_obj = GeneralFormParser()
        path = TEST_FILE_LOCATION + FILE_TYPES['test_missing_data']
        with self.assertRaises(AttributeError):
            test_obj.get_form_type_and_filing_year(path)

    def test_correct_form_type_year_extraction(self):
        """
        Verify that correct data can be parsed from file. Here we are explicitly supplying
        a file which is a 10-k SEC form.
        """

        path = TEST_FILE_LOCATION + FILE_TYPES['test_correct_form_type_year_extraction']
        test_obj = GeneralFormParser()
        self.assertEqual(('10-K', 2018),
                         test_obj.get_form_type_and_filing_year(path))

    # NOTE : Test case for extract_form_data() as this is a composition wrapper over
    #        Parse10KForm(): get_form_data() which is already tested in test_P10KParse.py
