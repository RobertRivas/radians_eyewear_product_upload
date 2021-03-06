import os
# from dotenv import load_dotenv
#
# load_dotenv()

import pandas as pd

from woocommerce import API



from ast import literal_eval

import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


session = requests.Session()
session.auth = (os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])

session.verify = False
URL = f"{os.environ['URL']}"+"/wp-json/"+f"{os.environ['VERSION']}/"
response = session.get(url=URL)

print(response)
# couldn't use woo-commerce library because of issue with requests default changing white spaces to +.
#
# So had to use just straight requests library to override default setting

# wcapi = API(
#     url=os.environ['URL'],
#     consumer_key=os.environ['CONSUMER_KEY'],
#     consumer_secret=os.environ['CONSUMER_SECRET'],
#     version=os.environ['VERSION'],
#     wp_api=True,
#     timeout=30
# )

def profit_margin(csv_price):

    # 27 percent profit margin col II

    equip_direct_cost = csv_price
    twenty_five_percent_profit_margin_function = (equip_direct_cost / (1 - 0.27))
    profit_margin_calculation = round(twenty_five_percent_profit_margin_function, 2)

    return profit_margin_calculation


def variable_switch_function(parent_sku):

    data = {
        "type": "variable"
    }


    # updates product to variable product type



    print(session.get(f"{URL}products?sku={parent_sku}").json())

    json_for_id = session.get(f"{URL}products?sku={parent_sku}").json()

    product_dict = json_for_id[0]
    product_id = product_dict['id']

    print(session.put(f"{URL}products/{product_id}", json=data).json())


def attribute_post(list_of_skus, radians_catalog, parent_sku):

    colors = []
    for i in list_of_skus:
        i = i.upper()
        option = radians_catalog['DESCRIPTION'].loc[radians_catalog['PART'].str.contains(pat=i, na=False)]
        if len(option) == 0:

            continue

        else:
            option = option.iloc[0]
            option = option.encode("ascii", "ignore")
            option = "{0}{1}".format(option, '')
            option = option.lstrip('b,\'')
            option = option.rstrip('\'')
            colors.append(option)

    product_json = session.get(f"{URL}products?sku={parent_sku}").json()
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

    print(attribute_data)

    print(session.put(f"{URL}products/{product_id}", json=attribute_data).json())


def batch_variation_post_function(sku_array, radians_catalog, parent_sku):
    variation_dict = []

    variable_switch_function(parent_sku)

    for i in sku_array:

        i = i.upper()
        i = i.strip()



        price = radians_catalog['Col II'].loc[radians_catalog['PART'].str.contains(pat=i, na=False)]

        if len(price) == 0 :
            continue
        else:

            price = price.iloc[0]

        color = radians_catalog['DESCRIPTION'].loc[radians_catalog['PART'].str.contains(pat=i, na=False)]
        if len(color) == 0:
            continue
        else:


            color = color.iloc[0]
            color = color.encode("ascii", "ignore")
            color = "{0}{1}".format(color, '')
            color = color.lstrip('b,\'')
            color = color.rstrip('\'')


        price_profit_margined = profit_margin(price)
        print(price_profit_margined)

        variation_dict.append(
            {
                "sku": i,
                "regular_price": price_profit_margined,
                "weight": 0.1,
                "attributes": [
                    {
                        "name": "Color",

                        "option": color
                    }
                ]
            }
        )

    json_for_id = session.get(f"{URL}products?sku={parent_sku}").json()
    product_dict = json_for_id[0]
    product_id = product_dict['id']

    variation_batch_post ={
        "create": variation_dict,
        "update": [
            {
                "id": product_id

            }
        ]
    }

    print(variation_batch_post)

    print(session.post(f"{URL}products/{product_id}/variations/batch", json=variation_batch_post).json())


radians_catalog = pd.read_excel(r'5036_2021_Radians_Industrial_PriceList_REV01 - FINAL.xlsx', header=78)

web_scraping = pd.read_csv(r'radians_eyewear_web_data.csv')

woo_commerce_category_export = pd.read_csv(r'woo_commerce_export_for_sku_reference.csv')




for index, row in woo_commerce_category_export.iterrows():

    variations_string = web_scraping['Variations'].loc[web_scraping['Description'].str.contains(row['Description'])]

    if len(row) == 0 or len(variations_string) == 0:

        continue

    else:
        print(row['SKU'])

        print(type(literal_eval(variations_string.iloc[0])))
        sku_array = literal_eval(variations_string.iloc[0])

        attribute_post(sku_array, radians_catalog, row['SKU'])


        batch_variation_post_function(sku_array, radians_catalog, row['SKU'])



