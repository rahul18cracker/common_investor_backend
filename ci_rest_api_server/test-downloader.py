#from secedgar.filings import Filing, FilingType

# from secedgar.filings import FilingType

# my_filings = Filing(cik_lookup='aapl',
#                             filing_type=FilingType.FILING_10Q,
#                             count=1,
#                             user_agent='Name (email)')
# my_filings.save('/tmp')

from secedgar import filings, FilingType

# 10Q filings for Apple (ticker "aapl")
my_filings = filings(cik_lookup="aapl",
                     filing_type=FilingType.FILING_10Q,
                     user_agent="Your name (your email)")
my_filings.save('/tmp/')
