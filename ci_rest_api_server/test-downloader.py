from secedgar.filings import Filing, FilingType

my_filings = Filing(cik_lookup='aapl',
                            filing_type=FilingType.FILING_10Q,
                            count=1,
                            user_agent='Name (email)')
my_filings.save('/tmp')
