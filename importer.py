from typing import List
import requests
from cart import Cart
from product import (
    Product, Image, Variant, Barcode, Weight, Stock,
    ManufacturerEntity, AttributePair, AttributeGroup, Attribute, WeightUnit
)


class ShopifyImporter:
    def __init__(self, cart: Cart) -> None:
        self.cart = cart

    def start(self) -> List[Product]:
        products: List[Product] = []
        response = self.fetch_products()
        for product in response['products']:
            instance=Product(
                id=product["id"],
                name=product["title"],
                description=product["body_html"],
                short_description=product["body_html"],
                meta_title=product["title"],
                sku=product["variants"][0]["sku"],
                is_virtual=product["published_scope"] == "global",
                link_rewrite=product["handle"],
                cost=product["variants"][0]["price"],
                price=product["variants"][0]["price"],
                is_active=product["status"] == "active",
                is_taxable=product["variants"][0]["taxable"],
                lang_id=None,
                shop_id=None,
                created_date=product["created_at"],
                meta_description=product["body_html"],
                updated_date=product["updated_at"],
                images=self.get_images(product),
                variants=self.get_variants(product),
                manufacturers=self.get_manufacturers(product),
                tags=product["tags"],
                stock=self.get_stock(product),
                weight=self.get_weight(product["variants"][0]),
                barcode=Barcode(
                    ean_13=product["variants"][0]["barcode"], upc=None),
            )
            products.append(instance)

        return products
    
    def get_images(self, product, variant=None):
        images: List[Image] = [
            Image(
                id=image["id"],
                name=image["alt"],
                position=image["position"],
                path=image["src"],
                base64_attachment=None,
                is_cover=image["id"] == product["image"]["id"],
            ) for image in product["images"] if variant and image["id"] == variant["image_id"]
        ]
        return images
    
    def get_manufacturers(self, product):
        manufacturers: List[ManufacturerEntity] = [
            ManufacturerEntity(
                id=product["vendor"],
                name=product["vendor"],
                lang_id=None,
                description=None,
                short_description=None,
                meta_title=None,
                meta_description=None,
                created_date=None,
                updated_date=None,
                is_active=True,
            )]
        return manufacturers

    def get_attribute_pairs(self, product):
        attribute_pairs: List[AttributePair] = [
            AttributePair(
                attribute=[
                    Attribute(
                        id=option["id"],
                        name=value,
                        position=option["position"],
                        lang_id=None,
                    ) for value in option["values"]
                ],
                attribute_group=AttributeGroup(
                    id=option["id"],
                    name=option["name"],
                    lang_id=None,
                    attributes=[
                        Attribute(
                            id=option["id"],
                            name=value,
                            position=option["position"],
                            lang_id=None,
                        ) for value in option["values"]
                    ],
                ),
            ) for option in product["options"]
        ]
        return attribute_pairs

    def get_variants(self, product):
        variants: List[Variant] = [
            Variant(
                id=variant["id"],
                price=variant["price"],
                stock=variant["inventory_quantity"],
                sku=variant["sku"],
                specific_prices=self,
                images=self.get_images(product, variant=variant),
                attribute_pairs=self.get_attribute_pairs(product),
                barcode=Barcode(ean_13=variant["barcode"], upc=None),
                weight=self.get_weight(variant),
            ) for variant in product["variants"]
        ]
        return variants
    
    def get_stock(self, product):
        stocks: List[Stock] = [
            Stock(
                quantity=product["variants"][0]["inventory_quantity"],
                out_of_stock_action="deny_backorders" if product["variants"][0][
                    "inventory_policy"] == "deny" else "allow_backorders",
            ),
        ]
        return stocks
    
    def get_weight(self, product):
        weight: List[Weight] = [
            Weight(
                value = product["weight"],
                weight_unit=WeightUnit.KG if product["weight_unit"] == "kg" else WeightUnit.GR
            )
        ]

        return weight
    
    def fetch_products(self):
        url = f"{self.cart.url}/admin/api/2024-04/products.json"
        headers = {
            'X-Shopify-Access-Token': f'{self.cart.token}'
        }
        response = requests.get(url, headers=headers)
        return response.json()


def get_importer(cart):
    return ShopifyImporter(cart)
