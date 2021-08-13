import os
# from dotenv import load_dotenv
#
# load_dotenv()

import pandas as pd

import numpy as np

from woocommerce import API

wcapi = API(
    url=os.environ['URL'],
    consumer_key=os.environ['CONSUMER_KEY'],
    consumer_secret=os.environ['CONSUMER_SECRET'],
    version=os.environ['VERSION'],
    wp_api=True,
    timeout=30
)


def retrieve_needed_data_from_parent_sku(parent_sku, web_scraping):

    row = web_scraping.loc[web_scraping['Parent_sku'].str.contains(parent_sku)]

    # print()
    #

    if len(row) == 0:

        return None, None, None

    else:
        print(row)


        return row['Title'].iloc[0], row['Description'].iloc[0], parent_sku


def create_dict_for_api_post(name, description, parent_sku):
    data_post = {
        "name": f"{name} ",
        "type": "simple",
        "description": f'''{description}''',
        "status": "private",
        "sku": parent_sku,
        "weight": f"0.1",
        "categories": [
            {
                "id": 749,
                "id": 762
            }
        ]
        ,
                    "images": [
                        {
                            "src": f"https://www.equipdirect.com/wp-content/uploads/2021/08/{name}.jpg"
                        }
                    ]
    }
    return data_post


def api_post(data_post):

    print(data_post)

    # print(wcapi.post("products", data_post).json())


radians_catalog = pd.read_excel(r'5036_2021_Radians_Industrial_PriceList_REV01 - FINAL.xlsx', header=78)

web_scraping = pd.read_csv(r'radians_eyewear_web_data.csv')

# capitalize columns for matching rows

radians_catalog['PART'] = radians_catalog['PART'].str.upper()

web_scraping['Parent_sku'] = web_scraping['Parent_sku'].str.upper()

web_scraping['Parent_sku'] = web_scraping['Parent_sku'].str.replace('-', ' ')

web_scraping['Parent_sku'] = web_scraping['Parent_sku'].str.replace('  ', ' ')

# print(web_scraping['Parent_sku'].iloc[0])

web_scraping['Variations'] = web_scraping['Variations'].str.upper()



# print(web_scraping['Parent_sku'])
# print(radians_catalog['PART'])
#
# print(web_scraping['Variations'])

for index, row in radians_catalog.iterrows():
    # print(index)
    # print(row)

    if row['STYLE'] is not np.nan:
        row['STYLE'] = row['STYLE'].encode("ascii", "ignore")
        # print(row['STYLE'])
        row['STYLE'] = "{0}{1}".format(row['STYLE'], '')
        # print(row['STYLE'])
        row['STYLE'] = row['STYLE'].lstrip('b,\'')
        row['STYLE'] = row['STYLE'].rstrip('\'')

        print('here')
        print(row['STYLE'])

        retrieve_needed_data_from_parent_sku(row['STYLE'], web_scraping)

        name, description, parent_sku = retrieve_needed_data_from_parent_sku(row['STYLE'], web_scraping)

        print(name, description, parent_sku)

        dict_for_api_post = create_dict_for_api_post(name, description, parent_sku)
        # print(dict_for_api_post)

        api_post(dict_for_api_post)

    else:

        continue

