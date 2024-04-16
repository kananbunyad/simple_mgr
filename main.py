from cart import Cart
from exporter import get_exporter
from importer import get_importer
from utils import find_logger
import argparse
from importer import ShopifyImporter


logger = find_logger(__name__)


def process(source: Cart, target: Cart):
    importer = get_importer(cart=source)
    source_data = importer.start()
    logger.info("Source data count %s", len(source_data))

    exporter = get_exporter(source_data, cart=target)
    number_of_entity_count = exporter.start()
    logger.info("Number of the entities migrated %s", number_of_entity_count)


# acb243-92.myshopify.com

if __name__ == "__main__":
    # extract the values FOR these variables from the command line options (flags)
    # python main.py --source_url http://source.com --source_token SOURCE --target_url http://target.com --target_token TARGET
    
    # python main.py --source_url https://acb243-92.myshopify.com/ --source_token TOKEN --target_url http://target.com --target_token TARGET

    parser = argparse.ArgumentParser()

    parser.add_argument("-su", "--source_url",
                        help="URL of the source from which data is to be fetched")
    parser.add_argument("-st", "--source_token",
                        help="Authentication token for accessing the source URL.")
    parser.add_argument("-tu", "--target_url",
                        help="URL of the target to which data will be sent")
    parser.add_argument("-tt", "--target_token",
                        help="Authentication token for the target URL.")


    args = parser.parse_args()

    source_url = args.source_url
    source_token = args.source_token

    target_url = args.target_url
    target_token = args.target_token

    

    source_cart = Cart(source_url, source_token)
    target_cart = Cart(target_url, target_token)
    process(source_cart, target_cart)
