import requests
import json
import csv
import sys


csv.field_size_limit(sys.maxsize)

try:
    with open('cats_ids.csv', 'rb') as f:
        CAT_IDs = json.load(f)
except:
    CAT_IDs = {}


class Product:
    def __init__(self, prodDic):
        keys = ["sku", "status", "media_gallery_entries", "name", "type_id", "price",
                "attribute_set_id", "visibility", "custom_attributes", "extension_attributes"]
        self.product = dict.fromkeys(keys)
        self.productDic = prodDic
        self.createProduct()

    def get(self):
        return {'product': self.product}

    def createProduct(self):
        self.product['sku'] = self.get_sku()
        self.product['name'] = self.get_name()
        self.product['price'] = self.get_price()
        self.product['status'] = "2"
        self.product['media_gallery_entries'] = self.get_media_gallery_entries()
        self.product['type_id'] = self.get_type_id()
        self.product['attribute_set_id'] = "4"
        self.product['visibility'] = "4"
        self.product['custom_attributes'] = self.get_custom_attributes()
        self.product['extension_attributes'] = self.get_extension_attributes()

    def get_sku(self):
        if self.product['sku']:
            return self.product['sku']
        return self.productDic['sku']

    def get_name(self):
        if self.product['name']:
            return self.product['name']
        return self.productDic['name']

    def get_price(self):
        if self.product['price']:
            return self.product['price']
        return self.productDic['price']

    def get_type_id(self):
        if self.product['type_id']:
            return self.product['type_id']
        return "simple"

    def get_media_gallery_entries(self):
        return [{
            "media_type": "image",
            "disabled": "false",
            "content": {
                "base64_encoded_data": self.productDic['encoded_img'],
                "type": "image/jpeg",
                "name": self.productDic['image_name']
            }
        }]

    def get_custom_attributes(self):
        return [
            {
                "attribute_code": "description",
                "value": self.productDic['description']
            },
            {
                "attribute_code": "short_description",
                "value": self.productDic['name']
            },
            {
                "attribute_code": "category_ids",
                "value": self.productDic['category_ids']
            }
        ]

    def get_extension_attributes(self):
        return {"stock_item": {
            "qty": self.productDic['qty'],
            "is_in_stock": "true" if(int(self.productDic['qty'])) else "false"
        }}


class m2api(object):

    def __init__(self, url, username, password):
        super(m2api, self).__init__()
        self.url = url
        self.token = self.getToken(username, password)
        self.ALL_CATS_IDS = self.getAllCats()

    def addBulkProducts(self, csvFile):
        with open(csvFile, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                newProduct = row
                newProduct['category_ids'] = self.getCategorySet(
                    newProduct['categories'])
                new_prd_row = Product(newProduct).get()
                print(self.addProduct(new_prd_row))

    def addProduct(self, data):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + self.token
        }
        product_url = self.url + "rest/V1/products"
        response = self.m2req(
            product_url, headers=headers, data=json.dumps(data))
        if(response):
            print(json.loads(response))
            return True
        else:
            return False

    def getCategorySet(self, cats):
        cats = cats.split('/')
        category_ids = []
        for cat in cats:
            if cat in CAT_IDs.keys():
                category_ids.append(CAT_IDs[cat])
            elif cat in self.ALL_CATS_IDS.keys():
                category_ids.append(self.ALL_CATS_IDS[cat])
                CAT_IDs[cat] = self.ALL_CATS_IDS[cat]
            else:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": "Bearer " + self.token
                }
                data = {
                    "category": {
                        "name": cat,
                        "parent_id": category_ids[-1],
                        "isActive": "false"
                    }
                }
                newcat = self.m2req(
                    self.url+'rest/V1/categories', headers=headers, data=json.dumps(data))
                newcat = json.loads(newcat)
                category_ids.append(newcat['id'])
                CAT_IDs[newcat['name']] = newcat['id']
        return category_ids

    def getAllCats(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + self.token
        }
        allCats = requests.get(
            self.url+'rest/all/V1/categories', headers=headers)
        allCats = json.loads(allCats.content)
        cat_dic = {}
        self.getCatsData(allCats['children_data'], cat_dic)
        return cat_dic

    def getCatsData(self, data, cat_dic):
        for cat in data:
            cat_dic[cat['name']] = str(cat['id'])
            if len(cat['children_data']):
                self.getCatsData(cat['children_data'], cat_dic)

    def getToken(self, username, password):
        payload = {
            "username": username,
            "password": password
        }
        data = json.dumps(payload)
        headers = {
            "Content-Type": 'application/json',
            "Accept": "application/json"
        }
        token_url = self.url + "rest/V1/integration/admin/token"
        return json.loads(self.m2req(token_url, headers=headers, data=data))

    def m2req(self, url, headers, data):
        try:
            res = requests.post(url, headers=headers, data=data)
            if res.status_code == 200:
                return res.content
            else:
                print(res.status_code)
                error = json.loads(res.content)
                print(error)
                print('Error Occoured While connecting to Magento')
                return False
        except Exception as e:
            print(e)
            raise

