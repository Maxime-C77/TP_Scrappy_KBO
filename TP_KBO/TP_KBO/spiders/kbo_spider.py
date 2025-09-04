import scrapy
import csv
import random

class KboSpider(scrapy.Spider):
    name = "kbo_spider"

    def start_requests(self):
        with open("../KBO/enterprise.csv", newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            # choisir 10 entreprises au hasard
            sample = random.sample(reader, min(10, len(reader)))

            for row in sample:
                numero = row["EnterpriseNumber"].replace(".", "")  # enlever les points
                url = f"https://kbopub.economie.fgov.be/kbopub/toonondernemingps.html?lang=fr&ondernemingsnummer={numero}"
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
            "donnees": response.css("td.QL::text, td.RL::text").getall(),


            # "statut": response.css("td span:nth-child(1)::text").getall(),
            # "situation juridique": response.css("td span:nth-child(2)::text").getall(),
            # "date de debut": response.css("td span:nth-child(3)::text").getall(),
            # # "denomination": response.css("td.QL::text, td.RL::text").getall(),
            # # "adresse": response.css("td.QL::text, td.RL::text").getall(),
            # # "telephone": response.css("td.QL::text, td.RL::text").getall(),
            # # "fax": response.css("td.QL::text, td.RL::text").getall(),
            # # "mail": response.css("td.QL::text, td.RL::text").getall(),
            # # "web": response.css("td.QL::text, td.RL::text").getall(),
            # # "type d'entite": response.css("td.QL::text, td.RL::text").getall(),
            # # "forme d'entite": response.css("td.QL::text, td.RL::text").getall(),
            # # "nombre d'unite d'etablissement (UE)": response.css("td.QL::text, td.RL::text").getall(),
            
            # "donnees": response.css("td.QL::text, td.RL::text").getall(),
            # "donnees": response.css("td.QL::text, td.RL::text").getall(),
            # "donnees": response.css("td.QL::text, td.RL::text").getall(),
            # "donnees": response.css("td.QL::text, td.RL::text").getall(),
        }