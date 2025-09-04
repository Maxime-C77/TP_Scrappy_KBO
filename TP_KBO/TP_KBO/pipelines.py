# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


# class TpKboPipeline:
#     def process_item(self, item, spider):
#         return item

import pymongo

class MongoDBPipeline:
    def open_spider(self, spider):
        self.client = pymongo.MongoClient("mongodb+srv://maxime:BzfgER0W7fgsdaQZ@tp.5rrgnek.mongodb.net/")
        self.db = self.client["kbo_db"]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection = self.db[spider.name]  # chaque spider a sa collection
        collection.update_one(
            {"_id": item.get("_id", item.get("numero"))},  # clé unique
            {"$set": dict(item)},
            upsert=True
        )
        return item
