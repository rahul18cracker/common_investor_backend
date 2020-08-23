# This class implements the composition pattern
from typing import Tuple
import re
from ci_rest_api_server.support_libs.extractor.P10kParser import Parse10KForm
from ci_rest_api_server.support_libs.extractor.P10QParser import Parse10QForm
import ci_rest_api_server.support_libs.extractor.IExtractDBPush


class GeneralFormParser:
    """
    Extracts data from SEC text files, based on form type correct data is extracted and
    returned as a dictionary to caller
    """

    def __init__(self):
        """
        Declare the form types we want to do by composition pattern
        """
        self.__form_types_inventory = {
            '10-K': Parse10KForm(),
            '10-Q': Parse10QForm(),
        }
        # Stores the composed object
        self._form_operator = None
        self._extracted_form_data = {}

    @staticmethod
    def get_form_type_and_filing_year(file_path: str) -> Tuple[str, int]:
        """
        Method extracts form type and form filing year
        :param file_path: path of file to extract information
        :type file_path: string
        :return: form type, year of filing
        :rtype: Tuple[str, int]
        """
        ci_rest_api_server.support_libs.extractor.IExtractDBPush.logger.debug(f"Opening file: {file_path} for parsing")
        try:
            with open(file_path) as file:
                file_contents = file.read()
        except Exception as error:
            ci_rest_api_server.support_libs.extractor.IExtractDBPush.logger.exception(f"Unexpected error opening file:{file_path} Err-{error}")
            raise error

        form_type_pattern = re.compile(r'CONFORMED SUBMISSION TYPE:\s+([0-9]+)\-([a-zA-Z]+)')
        date_filed_type_pattern = re.compile(r'FILED AS OF DATE:\s+([0-9]+)')

        # no need to take the whole file as the form type is in the first 2000 chars
        form_matches = form_type_pattern.search(file_contents[0:2000])
        # group 1 = form type numeric , group(2) is the form type alphabet(s)
        try:
            extracted_form_type = form_matches.group(1) + "-" + form_matches.group(2)
        except AttributeError as ae:
            ci_rest_api_server.support_libs.extractor.IExtractDBPush.logger.exception(f"Unable to get form type :{file_path} Err-{ae}")
        # Get filing date
        date_filed_matches = date_filed_type_pattern.search(file_contents[0:2000])
        ci_rest_api_server.support_libs.extractor.IExtractDBPush.logger.debug(f"Form matches {form_matches} date matches {date_filed_matches}")
        extracted_year_filed = 0
        try:
            # get only the first 4 digits as it denotes the year
            extracted_year_filed = int(date_filed_matches.group(1)[:4])
        except ValueError as ve:
            ci_rest_api_server.support_libs.extractor.IExtractDBPush.logger.exception(f"Unable to get filing year:{file_path} Err-{ve}")
        ci_rest_api_server.support_libs.extractor.IExtractDBPush.logger.info(f"Extracted form type: {extracted_form_type} year: {extracted_year_filed}")
        return (extracted_form_type,
                extracted_year_filed)

    def extract_form_data(self, file_path: str,
                          form_type: str,
                          year_of_filing: int,
                          ticker: str) -> dict:
        """
        Based on Form type extracts data and sends back as a dict

        :param year_of_filing: year the form was filed
        :type year_of_filing: int
        :param file_path: Path to the text file
        :type file_path: string
        :param form_type:
        :type form_type: type of SEC form
        :param ticker: ticker symbol
        :type ticker: string
        :return: Key value pairs extracted form form data
        :rtype: dict
        """
        logtime_data = {}
        try:
            self._form_operator = self.__form_types_inventory.get(form_type)
            ci_rest_api_server.support_libs.extractor.IExtractDBPush.logger.debug(f"Form class from mapping {self._form_operator.__class__.__name__}")
            self._extracted_form_data = self._form_operator.get_form_data(file_path=file_path,
                                                                          year=year_of_filing,
                                                                          ticker=ticker,
                                                                          log_time=logtime_data)
        except Exception as err:
            ci_rest_api_server.support_libs.extractor.IExtractDBPush.logger.exception(f"Form extraction failed for {file_path} "
                             f"form type: {form_type} year:{year_of_filing}")
            ci_rest_api_server.support_libs.extractor.IExtractDBPush.logger.warning(f"Unable to extract form data for {file_path}")
            raise err
        finally:
            # TODO: Remove the file after parsing is good to save space
            ci_rest_api_server.support_libs.extractor.IExtractDBPush.logger.debug(f"Exectution time is {logtime_data}")
            pass
        return self._extracted_form_data

    def __repr__(self):
        return "GeneralFormParser()"
