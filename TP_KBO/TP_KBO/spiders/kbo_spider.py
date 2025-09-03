import scrapy
import csv

class KboSpider(scrapy.Spider):
    name = "kbo_spider"

    def start_requests(self):
        with open("../KBO/enterprise.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                numero = row["EnterpriseNumber"].replace(".", "")  # enlever les points
                url = f"https://kbopub.economie.fgov.be/kbopub/toonondernemingps.html?ondernemingsnummer={numero}"
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    meta={"numero": numero},
                    headers={"Accept-Language": "fr"}
                )

    def parse(self, response):
        numero = response.meta["numero"]

        yield {
            "_id": numero,
            "numero": numero,
            "generalites": response.css("div#generalities::text").getall(),
            # "fonctions": response.css("div#functions::text").getall(),
            # "capacites": response.css("div#capacities::text").getall(),
            # "qualites": response.css("div#qualities::text").getall(),
            # "autorisations": response.css("div#authorisations::text").getall(),
            # "nace_codes": response.css("div#nace::text").getall(),
            # "donnees_financieres": response.css("div#financial_data::text").getall(),
            # "liens_entites": response.css("div#entity_links a::attr(href)").getall(),
            # "liens_externes": response.css("div#external_links a::attr(href)").getall(),
        }
