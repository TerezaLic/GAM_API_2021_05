import json
import dateparser
from keboola.component import CommonInterface
import logging

DEFAULT_MAX_RETRIES = 5
DEFAULT_DIMENSIONS = [
    'MONTH_AND_YEAR'
]
DEFAULT_METRICS = [
    'AD_SERVER_IMPRESSIONS'
]


class Config:

    @staticmethod
    def private_key_file(params: dict, path: str) -> str:
        with open(path, 'w') as outfile:
            json.dump({
                "private_key": params["#private_key"],
                "client_email": params["#client_email"],
                "token_uri": params["token_uri"]
            }, outfile)
        return path

    @staticmethod
    def load() -> dict:

        #cfg = docker.Config('/data/')
        ci = CommonInterface(data_folder_path='data')
        logging.info(ci.environment_variables.project_id)
        cfg = ci.configuration
        params = cfg.parameters

        # check required fields      
        ## TL :  prozkoumat moznost nahrazeni nove: ..ci.validate_configuration(REQUIRED_PARAMETERS)  

        required = ("network_code", "report_type","#private_key",
                    "#client_email", "token_uri")

        for r in required:
            if r not in params:
                raise ValueError(f'Missing required field "{r}".')

        # validate timezone type
        allowed_timezones = ('PUBLISHER', 'PROPOSAL_LOCAL', 'AD_EXCHANGE')
        if params['timezone'] not in allowed_timezones:
            raise ValueError(
                f"Invalid timezone. Choose one from {allowed_timezones}"
            )

        # handle default dimensions
        if "dimensions" not in params:
            print("[INFO]: Dimensions field is empty -> use default")
            params['dimensions'] = DEFAULT_DIMENSIONS


        print(f"[INFO]: Selected dimensions: {params['dimensions']}")

        # handle default metrics
        if "metrics" not in params:
            print("[INFO]:Metrics field is empty -> use default")
            params['metrics'] = DEFAULT_METRICS

        print(f"[INFO]: Selected metrics: {params['metrics']}")

        # parse date range
        date_from = dateparser.parse(params['date_from'])
        date_to = dateparser.parse(params['date_to'])
        report_type = params['report_type']

        # validate report type
        allowed_types = ('HISTORICAL', 'AD_EXCHANGE', 'FUTURE','REACH')
        allowed_types_with_date = ('HISTORICAL', 'AD_EXCHANGE','FUTURE',)
        if params['report_type'] not in allowed_types:
            raise ValueError(
                f"Invalid report type. Choose one from {allowed_types}"
            )

        if not date_from and report_type  in allowed_types_with_date:
            raise ValueError(f"Invalid date format '{params['date_from']}'")

        if not date_to and report_type  in allowed_types_with_date:
            raise ValueError(f"Invalid date format '{params['date_to']}'")

        params['date_from'] = date_from.date()
        params['date_to'] = date_to.date()

        # create file with private key     ## TL pro GAM musim byt input ve formatu 'private_key_file' s keys bez #
        key_file = "tmp/private_key.json"
        params['private_key_file'] = Config.private_key_file(params, key_file)

        # set max retries count for retryable decorator
        if 'max_retries' not in params:
            params["max_retries"] = DEFAULT_MAX_RETRIES

        if 'dimension_attributes' in params:
            print(
                "[INFO]: Selected dimension attributes:"
                f" {params['dimension_attributes']}"
            )

        if 'currency' not in params:
            for metric in params['metrics']:
                if metric.startswith("AD_EXCHANGE"):
                    print("[INFO]: Currency is not set, but AD_EXCHANGE metric"
                          " is present. Using CZK as default currency")
                    params['currency'] = "CZK"
                    break

        return params