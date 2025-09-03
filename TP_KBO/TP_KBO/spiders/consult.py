import scrapy
import csv

class ConsultSpider(scrapy.Spider):
    name = "consult"

    def start_requests(self):
        with open("../KBO/enterprise.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                numero = row["numero"]
                url = f"https://consult.cbso.nbb.be/consult-enterprise/{numero}"
                yield scrapy.Request(url, callback=self.parse, meta={"numero": numero})

    def parse(self, response):
        numero = response.meta["numero"]

        for dep in response.css("div.publication"):
            yield {
                "numero": numero,
                "titre": dep.css("h3::text").get(),
                "reference": dep.css("span.ref::text").get(),
                "date_depot": dep.css("span.deposit-date::text").get(),
                "date_fin_exercice": dep.css("span.end-date::text").get(),
                "langue": dep.css("span.language::text").get(),
            }
