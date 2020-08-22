import unittest
import shutil
import os
from IExtractDBPush import ExtractParseForms

TEST_FILE_LOCATION = "/tmp"


class TestExtractParseForms(unittest.TestCase):
    """
    Remember to test the cases in order as they build on each other and cannot be
    executed in isolation
    """
    @classmethod
    def setUpClass(cls) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        """
        Delete all allocated folder resources
        """
        path = TEST_FILE_LOCATION + '/aapl'
        shutil.rmtree(path)

    def test_missing_folder_path(self):
        """
        If the folder where all files are is non-existent it will throw a FileNotFoundError
        """
        test_obj = ExtractParseForms(TEST_FILE_LOCATION)
        with self.assertRaises(FileNotFoundError):
            test_obj.prepare_list_of_files('random',
                                           '10-k')

    def test_missing_files(self):
        """
        Test case to see we get empty list when there are no files in the directory
        NOTE: THis case there is an existent path to the directory
        """
        # create the folder structure
        os.makedirs(TEST_FILE_LOCATION + '/aapl/10-k')
        test_obj = ExtractParseForms(TEST_FILE_LOCATION)
        self.assertEqual([], test_obj.prepare_list_of_files('aapl',
                                                            '10-k'))

    def test_wrong_file_naming_format(self):
        """
        Generate wrong file naming format to see files cannot be parsed and
        we see a ValueError
        """
        # Setup fake files
        list_of_files = {
            '/aapl/10-k/test1.txt',
            '/aapl/10-k/test2.txt',
            '/aapl/10-k/test3.txt',
        }
        test_obj = ExtractParseForms(TEST_FILE_LOCATION)
        # create those fake files
        for file in list_of_files:
            path = TEST_FILE_LOCATION + file
            with open(path, "w+") as file:
                file.write("THis is a test line \n")

        # check for assertion
        with self.assertRaises(ValueError):
            test_obj.prepare_list_of_files('aapl',
                                           '10-K')

    # UT case for parse_form() is not written as it's a wrapper over extract_form_data()
    # TODO : Write unit test cases for Mongo DB functions, currently do not know how to write

if __name__ == '__main__':
    unittest.main()
