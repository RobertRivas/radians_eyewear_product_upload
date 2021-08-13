import os
# from dotenv import load_dotenv
#
# load_dotenv()

import pandas as pd

from woocommerce import API

from ast import literal_eval

wcapi = API(
    url=os.environ['URL'],
    consumer_key=os.environ['CONSUMER_KEY'],
    consumer_secret=os.environ['CONSUMER_SECRET'],
    version=os.environ['VERSION'],
    wp_api=True,
    timeout=30
)

def profit_margin(csv_price):

    # 27 percent profit margin col II

    equip_direct_cost = csv_price.astype(float)
    twenty_five_percent_profit_margin_function = (equip_direct_cost / (1 - 0.27))
    profit_margin_calculation = round(twenty_five_percent_profit_margin_function, 2)

    return profit_margin_calculation


def variable_switch_function(parent_sku):

    data = {
        "type": "variable"
    }

    # updates product to variable product type

    json_for_id = wcapi.get(f"products?sku={parent_sku}").json()

    product_dict_prev = json_for_id[0]
    product_id_prev = product_dict_prev['id']

    # print(wcapi.put(f"products/{product_id_prev}", data).json())


def attribute_post(list_of_skus, radians_catalog, parent_sku):

    colors = []
    for i in list_of_skus:

        attributes = radians_catalog['DESCRIPTION'].loc[
            radians_catalog['PART'].str.contains(pat=i, na=False)]
        if len(attributes) == 0:

            continue

        else:
            colors.append(attributes)

    product_json = wcapi.get(f"products?sku={parent_sku}").json()
    product_dict = product_json[0]
    product_id = product_dict['id']

    attribute_data = {
        "attributes": [

            {
                "id": 0,
                "name": "Color",
                "position": 0,
                "visible": "true",
                "variation": "true",
                "options":

                    colors

            }
        ]
    }

    # print(wcapi.put(f"products/{product_id}", attribute_data).json())


def batch_variation_post_function(sku, price, color, parent_sku):
    variation_dict = []

    variable_switch_function(parent_sku)

    price_profit_margined = profit_margin(price)
    # color = color.tolist()

    variation_dict.append(
        {
            "sku": sku.iloc[0],
            "regular_price": price_profit_margined.iloc[0],
            "weight": 0.8,
            "attributes": [
                {
                    "name": "Color",
                    # need to remove prefix instead of strip
                    "option": color
                }
            ]
        }
    )

    json_for_id = wcapi.get(f"products?sku={parent_sku}").json()
    product_dict_prev = json_for_id[0]
    product_id_prev = product_dict_prev['id']

    variation_batch_post = {
        "create": variation_dict,
        "update": [
            {
                "id": product_id_prev

            }
        ]
    }

    print(variation_batch_post)

    # print(wcapi.post(f"products/{product_id_prev}/variations/batch", variation_batch_post).json())


radians_catalog = pd.read_excel(r'5036_2021_Radians_Industrial_PriceList_REV01 - FINAL.xlsx', header=78)

web_scraping = pd.read_csv(r'radians_eyewear_web_data.csv')

woo_commerce_category_export = pd.read_csv(r'woo_commerce_export_for_sku_reference.csv')


# print(woo_commerce_category_export['Description'])

for index, row in woo_commerce_category_export.iterrows():

    variations_string = web_scraping['Variations'].loc[web_scraping['Description'].str.contains(row['Description'])]

    if len(row) == 0 or len(variations_string) == 0:

        continue

    else:
        print(row['SKU'])
        print(variations_string.iloc[0])

        print(type(literal_eval(variations_string.iloc[0])))
        sku_array = literal_eval(variations_string.iloc[0])

        variable_switch_function(row['SKU'])

        attribute_post(sku_array, radians_catalog, row['SKU'])



