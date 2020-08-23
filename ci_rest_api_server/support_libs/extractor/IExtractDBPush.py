# This is an interface file for the Composition based Singleton pattern desing
# for the Producer side of the code.
# Description: This Producer module has the following responsibilities
# 1. Pull data for various forms using the secedgar git repo
# 2. create object which each form class can fill and supply the data
# 3. It will then connect to each DB(form based) in Mongo DB and save
#    the extracted financial data

# This import has been adpoted from the git repo: coyo8/sec-edgar
# It's used to pull the txt files on form type basis
#  "PEP 8 unto thyself, not unto others. Brilliant."
# - By Raymond hettengier
from typing import (List,
                    Any,
                    Dict,
                    )
import os
import re
from datetime import datetime
import logging
from pymongo import MongoClient
import pymongo
from pymongo.errors import (ConnectionFailure,
                            WriteError,
                            WriteConcernError,
                            )
from secedgar.filings import (Filing,
                              FilingType,
                              )
from secedgar.utils.exceptions import (EDGARQueryError,
                                       EDGARFieldError,
                                       CIKError,
                                       FilingTypeError,
                                       )
from ci_rest_api_server.support_libs.extractor.GFormParse import GeneralFormParser

# set logging file name and non-root names
# TODO: Improve the logger to write to Json files also, this will help in data analytics
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Set up the formatter
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
# Setup the console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
logger.addHandler(console_handler)

# Set up the file handler for the log file , log everything there
file_handler = logging.FileHandler('../Extractor.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class ExtractParseForms:
    # TODO : Add repr to class
    """
    Description: This class is a Interface type class for the producer side of
                 things where it has the following jobs
                 1. Based in security type pull the needed form type from the
                    EDGAR data base
                2. Save those text files in a temproary location
                3. In the save folder start opening the files and parsing
                4. the parsing is done by each class where it provides the form type
                interface for extraction
                5. Once the parsed data is created then save that to MongoDB according
                to the type of DB on per form basis
                eg : form 10k = DB type form10k in MongoDB
                     each company ticker symbol is a collection
                     each year is a row or document in the collection
    """
    # Used by consumer to pull data from DB only
    # Reason for use: opening and closing connections to Mongp DB are expensive the time
    # consuming, this will make the operation fast by keeping the connection open for 
    # fast requests
    _client_handle_pull_db = None

    def __init__(self,
                 path_to_save_file: str):
        self.__path_to_save_file = path_to_save_file
        self.__form_to_enum_mapper = {
            '10-K': FilingType.FILING_10K,
            '10-Q': FilingType.FILING_10Q,
        }
        self.client_handle = None

    @classmethod
    def from_db(cls):
        cls._client_handle_pull_db: "MongoClient" = pymongo.MongoClient("mongodb://localhost:27017/")
        return cls('None')

    def pull_ticker_symbol(self, ticker_symbol: str,
                           form_type: str,
                           years_to_pull: int = 10):
        """
        Pulls data from SEC EDGAR database and stores them in a folder os
        per structure
        e.g - form 10k
        - CIK -> form type -> txt file for each year as it's a realy form
        :param ticker_symbol: Compaany ticker symbol as per SEC filings
        :type ticker_symbol: string
        :param form_type: SEC form type
        :type form_type: string
        :param years_to_pull: No of years user has requested a pull for
        :type years_to_pull: integer
        :return: None
        :rtype: None
        """
        # 1. Invoke sec Edgar to pull all data to files for the given years
        #    remember all the validation is done by this API. Just handle exceptions
        # 2. Lof of filing types do not have good structured data so just take data
        #    back till year 2005 only as a max safe limit
        today = datetime.today()
        if today.year - years_to_pull < 2005:
            years_to_pull = 15
        logger.info("%s %s %s %s %s %s %s %s",
                    "Pulling info for ticker:",
                    ticker_symbol,
                    "from",
                    today.year - years_to_pull,
                    "to",
                    today.year,
                    "saving at",
                    self.__path_to_save_file)

        try:
            my_filings = Filing(cik_lookup=ticker_symbol.lower(),
                                filing_type=self.__form_to_enum_mapper[form_type],
                                count=years_to_pull)
            my_filings.save(self.__path_to_save_file)
        except EDGARQueryError as eq:
            logger.exception(f"Unable to get data from EDGAR Webpage for {ticker_symbol}"
                             f"Err-msg: {eq.args}")
            raise
        except EDGARFieldError as fe:
            logger.exception(f"Invalid field provided from for {ticker_symbol}"
                             f"Err-msg: {fe.args}")
            raise
        except CIKError as ce:
            logger.exception(f"Invalid ticker symbol:{ticker_symbol}"
                             f"Err-msg: {ce.args}")
            raise
        except FilingTypeError as fte:
            logger.exception(f"Invalid filing type {form_type} for {ticker_symbol}"
                             f"Err-msg: {fte.args}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected Error for {ticker_symbol} Err-msg: {e.args}")
            raise

    @staticmethod
    def file_sort_year_wise(value: str) -> int:
        """
        Function to extract year from the file name and pass to sort function as key
        :param value: file name
        :type value: string
        :return: 2 digit year
        :rtype: integer
        """
        # pattern here is filernumber-year-submissioncode.txt
        pattern = re.compile(r'(\d+\-)(\d+)(\-\d+)(\.txt)')
        # Extract year only
        matches = pattern.sub(r'\2', value)
        return int(matches)

    def prepare_list_of_files(self,
                              ticker: str,
                              form_type: str) -> list:
        """ 
        Prepares the list of text files in sorted order year wise for parsing
        :param ticker: ticker symbol
        :type ticker: str
        :param form_type: type of SEC form
        :type form_type: str
        :return: List of sorted files
        :rtype: List
        """
        set_list_of_files = set(os.listdir(self.__path_to_save_file))
        final_file_list = []
        first_level_path = self.__path_to_save_file + '/' + ticker.lower()
        second_level_path = first_level_path + '/' + form_type.lower()
        if ticker in set_list_of_files:
            if os.path.exists(second_level_path):
                # list all the file with txt extension and ignore all other type of files
                with os.scandir(second_level_path) as file_it:
                    for file in file_it:
                        if file.name.endswith('txt'):
                            final_file_list.append(file.name)
            else:
                logger.critical("%s <%s>",
                                "Unable to find form path:",
                                second_level_path)
                raise FileNotFoundError
        else:
            logger.critical("%s <%s>",
                            "Unable to find ticker-path :",
                            first_level_path)
            raise FileNotFoundError
        # make sure to sort all the files in year wise order
        try:
            final_file_list.sort(key=self.file_sort_year_wise)
        except ValueError as ve:
            logger.exception("%s %s",
                             "Unable to sort file list due to ",
                             "ve")
            raise ve
        # create full path for each file by adding pre-fix
        final_file_list = [second_level_path + '/' + file
                           for file in final_file_list]
        return final_file_list

    def parse_form(self,
                   ticker: str,
                   form_type: str) -> list:
        """
        Parses the needed form and retunrs a dictionary of all fields needed on per
        form type
        :param ticker: ticker symbol
        :type ticker: str
        :param form_type: type of SEC form
        :type form_type: str
        :return: a list of all the dictionaries which are extracted per year
        :rtype: list
        """
        # 1. This is a common method for all form types
        # 2. Uses OOP compostion to figure out form type and extracts information from that form
        ret_dict_list: List[Dict[Any, Any]] = []
        parser_operator = GeneralFormParser()
        for file in self.prepare_list_of_files(ticker,
                                               form_type):
            form_type, year_filed = parser_operator.get_form_type_and_filing_year(file)

            form_data_extracted = parser_operator.extract_form_data(file,
                                                                    form_type,
                                                                    year_filed,
                                                                    ticker)
            logger.debug(f"Parsed {form_type} and year {year_filed}")
            # create a list of dict's which will contain all years
            ret_dict_list.append(form_data_extracted.copy())

        return ret_dict_list

    def open_db_connection(self, name_of_db: str,
                           name_of_collection: str) -> 'MongoClient':
        """
        Opens a connection to Mongo DB for writing to mongo DB. Here the DB type is
        the SEC form type 10-K, 10Q etc. The collection name is the ticker symbol
        which is the stock symbol for a particular company listed on the S&P 500
        Important Note: This method is only used when pushing data to Mongo DB
                        After the data push this connection is closed. This was done
                        as opening and tearing connections to Mongo DB is expensive but
                        this method will be called one in a quater or year depending on
                        form type so that expense is ok for now
        :param name_of_db: is the SEC form type like 10-k, 10-q etc
        :type name_of_db: str
        :param name_of_collection: Is the SEC ticker symbol eg aapl, msft, amzn
        :type name_of_collection: str
        :return: Connection handle of the DB
        :rtype: Mongo DB connection handle type - MongoClient
        """
        try:
            self.client_handle = pymongo.MongoClient("mongodb://localhost:27017/")
            db = self.client_handle[name_of_db]
            collection_handle = db[name_of_collection]
        except ConnectionFailure as cf:
            logger.exception(cf)
            raise
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"DB {name_of_db} and collection:{name_of_collection} connected")
        return collection_handle

    def push_to_db(self,
                   list_of_dicts: list):
        """
        This pushes the extracted data for the company to the DB
        :param list_of_dicts: list of all dict value pulled from the form
        :type list_of_dicts: list 
        :return: None
        :rtype: None
        """
        db_name = list_of_dicts[0]['filing-type']
        collection_name = list_of_dicts[0]['ticker']
        logger.info(f'Connecting to DB:{db_name} collection:{collection_name}')
        collection = self.open_db_connection(db_name,
                                             collection_name)
        for record in list_of_dicts:
            try:
                collection.insert_one({'data': record})
            except (WriteError, WriteConcernError,) as werr:
                logger.warning(f"Unable to write data for ticker symbol:{collection_name} "
                               f"in {db_name} year:{record['filing-year']} err:{werr}")
                raise
            except Exception as err:
                logger.exception(err)
                raise
            finally:
                # remember to close connection, this is expensive than keeping connection open
                # push operations will be once in a year and not rapid so we should close conneciton
                self.client_handle.close()
                logger.info("Closing MongoDB connection")

            logger.info(f"Pushed ticker symbol {collection_name} "
                        f"year:{record['filing-year']} data in DB")

    def pull_from_db(self,
                     ticker: str,
                     db_name: str):
        """
        Returns all the data typically 10 years history for a given ticker symbol and 
        DB type. Note DB type is Mongo DB type
        NOTE: To use this function use alternative constructor which is the data pulling 
              constructor 
        :param ticker: Company for which data is needed eg. 'aapl', 'csco'
        :type ticker: str
        :param db_name: This is the DB type for mongo DB, can have values like 10-K, 10-Q
                        these are the form types, each DB type = SEC form type 
        :type db_name: str
        :return: a collection of dictionaries for all years 
        :rtype: dict
        """
        data_from_db = {}
        try:
            # remember this is a pull connection, has to be independent of push connection 
            db = self._client_handle_pull_db[db_name.upper()]
            collection_info = db.validate_collection(ticker.lower())
            logger.debug("%s %s %s %s %s %s",
                         "collection:",
                         ticker.lower(),
                         "has",
                         collection_info['nrecords'],
                         " records in DB:",
                         db_name.upper())
            collection = db[ticker.lower()]
            # Get all the records for this collection
            db_cursor = collection.find({})
            for item in db_cursor:
                key = str(item['data']['filing-year'])
                # store as key: str(year) , value: all the extracted fields
                data_from_db[key] = item['data']
        except Exception as err:
            logger.exception("%s %s %s %s %s %s",
                             "Unable to extract ticker :",
                             ticker,
                             "from db type:",
                             db_name,
                             " Error: ",
                             err)
            raise err

        logger.info("%s %s %s %s",
                    "Extracted data for ticker : ",
                    ticker,
                    "from DB : ",
                    db_name)
        return data_from_db


if __name__ == '__main__':
#    Data pushing code test
    obj = ExtractParseForms('/Users/rahmathu/Documents/personal_projects/sec-reports')
    obj.pull_ticker_symbol('nvda', '10-K', 10)
    ticker_data_list = obj.parse_form('nvda', '10-K')
    print(ticker_data_list)
    obj.push_to_db(ticker_data_list)
#    Data pulling code test=================
    obj = ExtractParseForms.from_db()
    returned_dict = obj.pull_from_db(ticker='nvda', db_name='10-k')
    print(returned_dict.keys())

