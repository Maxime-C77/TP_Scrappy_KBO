import scrapy
import csv

class EjusticeSpider(scrapy.Spider):
    name = "ejustice"

    def start_requests(self):
        with open("../KBO/enterprise.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                numero = row["numero"]
                url = f"https://www.ejustice.just.fgov.be/cgi_tsv/list.pl?btw={numero}"
                yield scrapy.Request(url, callback=self.parse, meta={"numero": numero})

    def parse(self, response):
        numero = response.meta["numero"]

        for pub in response.css("table tr"):
            yield {
                "numero": numero,
                "numero_publication": pub.css("td:nth-child(1)::text").get(),
                "titre": pub.css("td:nth-child(2)::text").get(),
                "adresse": pub.css("td:nth-child(3)::text").get(),
                "type": pub.css("td:nth-child(4)::text").get(),
                "date": pub.css("td:nth-child(5)::text").get(),
                "reference": pub.css("td:nth-child(6)::text").get(),
                "image_url": pub.css("td img::attr(src)").get(),
            }
