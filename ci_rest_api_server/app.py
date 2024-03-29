# Flask backend app file
import os
from flask import (
    Flask,
    make_response,
    request,
)
from bson import json_util
from ci_rest_api_server.support_libs.extractor.IExtractDBPush import ExtractParseForms

app = Flask(__name__)

@app.route("/security/10-k/<string:ticker_symbol>/",
           methods=['GET'])
def get_10k_ticker_data(ticker_symbol):
    """
    :param ticker_symbol: specifices the sec ticker symbol for the company, e.g Apple = appl
    :type str:
    :return: a dictionary fetched for particular security type to
             the client
    :rtype: dictionary
    """
    # Get the data from the DB
    data_get_obj = ExtractParseForms.from_db()
    try:
        returned_dict = data_get_obj.pull_from_db(ticker=ticker_symbol,
                                                  db_name='10-k')
    except Exception as err:
        # logger.exception(f"Unable to find ticker {ticker_symbol} err:{err}")
        return make_response(f"Opps ticker: {ticker_symbol} data not found {err}",
                             501)
    # logger.debug(f"Success data returned for ticker: {ticker_symbol}")
    return make_response(json_util.dumps(returned_dict),
                         200)

@app.route('/')
def hello():
    # TODO(rahul): Just remove this default root later when container work is stabalized
    return "<h1>Hello from CI backend </h1>"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)