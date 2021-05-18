import sys
from json.decoder import JSONDecodeError
from extractor_gam import GoogleAdMangerExtractor
from config import Config

# Deprecation = Feb 2022
# Sunset = May 2022
API_VERSION = "v202105"

APPLICATION_NAME = "TO_BE_ADDED"
OUTPUT_FILE = '/data/out/tables/output.csv'
EXTRACTOR_VERSION = "__VERSION__"


def main():
    print("[INFO]: Run the GAM Report Service Extractor")

    try:
        extractor = GoogleAdMangerExtractor(
            application_name=APPLICATION_NAME,
            extractor_version=EXTRACTOR_VERSION,
            api_version=API_VERSION,
            params=Config.load(),
        )
        extractor.download_report(OUTPUT_FILE)
        print("[SUCCESS] Extractor is done")
    except JSONDecodeError as e:
        print(f"[ERROR]: Check your JSON format: {e}")
        sys.exit(1)
    except (Exception, ValueError) as e:
        print(f"[ERROR]: {type(e)} {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()