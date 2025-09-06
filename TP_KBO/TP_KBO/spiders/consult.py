import scrapy
import csv
import os
import random
from dotenv import load_dotenv
from TP_KBO.items import KboItem

load_dotenv()

class ConsultSpider(scrapy.Spider):
    name = "consult"

    CSV_PATH = os.getenv("CSV_PATH", "../KBO")
    CRAWL_LIMIT = int(os.getenv("CRAWL_LIMIT", 10))
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0 Safari/537.36"
    )

    def start_requests(self):
        csv_file = os.path.join(self.CSV_PATH, "enterprise.csv")
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            sample = random.sample(reader, min(self.CRAWL_LIMIT, len(reader)))

            for row in sample:
                numero = row["EnterpriseNumber"].replace(".", "")
                url = f"https://consult.cbso.nbb.be/consult-enterprise/{numero}"
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    meta={"numero": numero},
                    headers={"User-Agent": self.USER_AGENT}
                )

    def parse(self, response):
        numero = response.meta["numero"]
        depots = []

        for row in response.css("tr"):
            depot = {
                "titre": row.css("td:nth-child(1)::text").get(),
                "reference": row.css("td:nth-child(2)::text").get(),
                "date_depot": row.css("td:nth-child(3)::text").get(),
                "date_fin_exercice": row.css("td:nth-child(4)::text").get(),
                "langue": row.css("td:nth-child(5)::text").get(),
            }
            if any(depot.values()):
                depots.append(depot)

        item = KboItem()
        item["_id"] = numero
        item["numero"] = numero
        item["sections"] = {"comptes_annuels": depots}
        item.clean_item()
        yield item
