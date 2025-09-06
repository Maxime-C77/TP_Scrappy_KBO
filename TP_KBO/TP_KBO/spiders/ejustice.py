import scrapy
import csv
import os
import random
from dotenv import load_dotenv
from TP_KBO.items import KboItem

load_dotenv()

class EjusticeSpider(scrapy.Spider):
    name = "ejustice"

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
                url = f"https://www.ejustice.just.fgov.be/cgi_tsv/list.pl?btw={numero}"
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    meta={"numero": numero},
                    headers={"User-Agent": self.USER_AGENT}
                )

    def parse(self, response):
        numero = response.meta["numero"]
        publications = []

        for block in response.css("div.list-item"):
            # Numéro + petit titre
            subtitle = block.css("p.list-item--subtitle::text").get()
            if subtitle:
                subtitle = subtitle.strip()

            # Lien principal qui contient plusieurs lignes (séparées par <br>)
            title_block = block.css("a.list-item--title")
            title_parts = [t.strip() for t in title_block.xpath(".//text()").getall() if t.strip()]

            # PDF éventuel
            image_url = block.css("a.standard::attr(href)").get()

            # Lien détail
            detail_url = block.css("a.button.read-more::attr(href)").get()

            # Construction de l’objet
            pub = {
                "numero_publication": subtitle,
                "titre": title_parts[0] if len(title_parts) > 0 else None,
                "adresse": title_parts[1] if len(title_parts) > 1 else None,
                "type": title_parts[2] if len(title_parts) > 2 else None,
                "date_reference": title_parts[3] if len(title_parts) > 3 else None,
                "reference": response.urljoin(detail_url) if detail_url else None,
                "image_url": response.urljoin(image_url) if image_url else None,
            }
            publications.append(pub)

        item = KboItem()
        item["_id"] = numero
        item["numero"] = numero
        item["sections"] = {"publications": publications}
        item.clean_item()
        yield item

