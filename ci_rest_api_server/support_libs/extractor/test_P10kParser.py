import unittest
import datetime, os, shutil
from secedgar.filings import Filing, FilingType
from P10kParser import Parse10KForm

# TODO: You can use tempfile module, mkdtemp() ,
# self.scratch_dir = tempfile.mkdtemp()
FOLDER_PATH_10k_EXTRACTION = '/tmp'


class TestParse10KForm(unittest.TestCase):
    def setUp(self) -> None:
        """
        Common setup to pull files in a temporary directory
        for testing and extraction
        """
        # This will make sure that we are pulling 2019 records only as they parse well
        start_date, end_date = datetime.datetime(2018, 8, 1), datetime.datetime(2019, 1, 1)
        # Get a known good company and a single 10-k form
        my_filings = Filing(cik_lookup='aapl',
                            filing_type=FilingType.FILING_10K,
                            count=1,
                            start_date=start_date,
                            end_date=end_date)
        my_filings.save(FOLDER_PATH_10k_EXTRACTION)

    def tearDown(self) -> None:
        """
        Clean up the directory for the 10-k form to reduce excess files
        """
        path = FOLDER_PATH_10k_EXTRACTION + "/aapl"
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"Cleaned up path:{path} after tests ")
        else:
            print(f"ERROR : Unable to find the path: {path} to clean up files."
                  f"Please delete them manually")

    def test_non_existent_file(self):
        """
        Test case for a non-existent file to see exception
        captured is correct
        """
        test_obj = Parse10KForm()
        with self.assertRaises(FileNotFoundError):
            test_obj.get_form_data('tmp/text.txt',
                                   1,
                                   'aapl')

    def test_parsed_form_data(self):
        """
        This function will take a single 10-k report and parse the fields to make
        sure the extraction of fields is working good. It will check the returned
        dict for values to make  sure majority of them are not zero.
        NOTE: Some fields might be 0 but majority cannot be zero, if they are then
              parsing logic has a problem
        """
        test_obj = Parse10KForm()
        path = FOLDER_PATH_10k_EXTRACTION + '/aapl/10-k/0000320193-18-000145.txt'
        parsed_data_dict = {}
        parsed_data_dict = test_obj.get_form_data(file_path=path,
                                                  year=2018,
                                                  ticker='aapl')
        # check if 50% of the dict had values or is just 0 values
        length_of_fields, counter_fields_zero = len(parsed_data_dict), 0
        for value in parsed_data_dict.values():
            if isinstance(value, int):
                if value == 0:
                    counter_fields_zero += 1
        self.assertGreater(length_of_fields // 2,
                           counter_fields_zero,
                           f"found {counter_fields_zero} 0 fields out of "
                           f"{length_of_fields // 2}")


if __name__ == '__main__':
    unittest.main()
