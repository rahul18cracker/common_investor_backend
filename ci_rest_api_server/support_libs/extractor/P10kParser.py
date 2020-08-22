from typing import Dict, Any, Union
# TODO : Correct this import for all this is not good
try:
    from my_rest_app.extractor.IExtractDBPush import logger
except ImportError:
    from intellegent_inv_rest_api_server.my_rest_app.extractor.IExtractDBPush import logger

from bs4 import BeautifulSoup
import time

# TODO: Move this to a central location to measure time for function execution using decorators
def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' %
                  (meth od.__name__, (te - ts) * 1000))
        return result

    return timed


class Parse10KForm:
    """
    Will parse the SEC form 10K which is a yearly generated form on per company
    and per year basis. 10K forms are submitted by all companies at Q4 end
    Here we are trying to get specific tags from the form 10 k, this extraction is
    performed using beautifulsoup as this is static html data
    """
    _needed_tags: Dict[Union[str, Any], Union[int, Any]]

    def __init__(self):
        """
        Init the needed fields to 0 for parsing in 10K form
        """
        self._needed_tags = {
            'accountspayablecurrent': 0,
            'accountsreceivablenetcurrent': 0,
            'accruedincometaxescurrent': 0,
            'accruedincometaxesnoncurrent': 0,
            'accumulatedothercomprehensiveincomelossnetoftax': 0,
            'assets': 0,
            'assetscurrent': 0,
            'availableforsalesecuritiescurrent': 0,
            'cashandcashequivalentsatcarryingvalue': 0,
            'cashcashequivalentsandshortterminvestments': 0,
            'commonstocksincludingadditionalpaidincapital': 0,
            'contractwithcustomerliabilitycurrent': 0,
            'contractwithcustomerliabilitynoncurrent': 0,
            'deferredrevenuecurrent': 0,
            'deferredrevenuenoncurrent': 0,
            'deferredtaxassetsliabilitiesnetcurrent': 0,
            'deferredtaxliabilitiesnoncurrent': 0,
            'depositsreceivedforsecuritiesloanedatcarryingvalue': 0,
            'employeerelatedliabilitiescurrent': 0,
            'finitelivedintangibleassetsnet': 0,
            'filing-type': '10-K',
            'filing-year': 0,
            'goodwill': 0,
            'inventorynet': 0,
            'liabilities': 0,
            'liabilitiesandstockholdersequity': 0,
            'liabilitiescurrent': 0,
            'longtermdebtcurrent': 0,
            'longtermdebtnoncurrent': 0,
            'longterminvestments': 0,
            'operatingleaseliabilitynoncurrent': 0,
            'operatingleaserightofuseasset': 0,
            'otherassetscurrent': 0,
            'otherassetsnoncurrent': 0,
            'otherliabilitiescurrent': 0,
            'otherliabilitiesnoncurrent': 0,
            'propertyplantandequipmentnet': 0,
            'retainedearningsaccumulateddeficit': 0,
            'shorttermborrowings': 0,
            'shortterminvestments': 0,
            'stockholdersequity': 0,
            'ticker': 'NONE'
        }

    @timeit
    def get_form_data(self,
                      file_path: str,
                      year: int,
                      ticker: str,
                      **kwargs: object) -> dict:
        """
        Common interface function to parse the 10k SEC form data with specific tag extraction

        :type kwargs: object
        :param file_path: txt file that needs extraction of tags
        :type file_path: string
        :param year: year for the data needed
        :type year: int
        :param kwargs: multiple args
        :type kwargs: can take mutiple args
        :param ticker: ticker symbol
        :type ticker: string
        :return: dict of extracted tag values
        :rtype: dict
        """
        try:
            with open(file_path) as file:
                file_contents = file.read()
        except Exception as error:
            logger.exception(f"Unexpected error opening file:{file_path} Err-{error}")
            raise error
        # open as Beautiful soup object and get the data for each tag
        form_10_k_bs_obj = BeautifulSoup(file_contents, 'lxml')
        for element in self._needed_tags:
            # all tags are part of XBRL format where they are always present
            search_string = "us-gaap:" + element
            for tag in form_10_k_bs_obj.find_all(search_string):
                if tag is not None:
                    # TODO: Find an effecient way to do this string search or
                    #       see if converting this to a generator get better time performance
                    #       see what tag is and then create a generator to filter data out from tag
                    # We want current year and ignore any table data associated is discarded
                    # "Member" helps ignore table values, "contextref" is the main tag
                    if str(year) in tag['contextref'] and 'Member' not in tag['contextref']:
                        # from the main tag get the data for that year
                        self._needed_tags[element] = int(tag.text)
                else:
                    logger.debug(f"Unable to get data for {search_string}")
        # Add the filing year also as we do not extract it above
        self._needed_tags['filing-year'] = year
        # Since beautiful soup cant be used as this not tag based using regex
        # pattern 1 - ticker_type_pattern = re.compile(r'>(\w+)</dei:TradingSymbol>')
        # pattern 1 breaks for some companies
        # ticker_type_pattern = re.compile(r'under the symbol(\s+)?(\W+)?(\w+)')
        # ticker_matches = ticker_type_pattern.search(file_contents)
        self._needed_tags['ticker'] = ticker
        logger.info(f"Completed extraction for year {year} | file: {file_path} "
                    f"| ticker:{self._needed_tags['ticker']}")
        return self._needed_tags

    def __repr__(self):
        return "Parse10KForm()"



