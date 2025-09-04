import scrapy
import csv
import random
import re
import unidecode
import os
from dotenv import load_dotenv

from TP_KBO.items import KboItem

# Charger les variables du .env
load_dotenv()

def normalize(label: str) -> str:
    """Nettoie les labels pour MongoDB (minuscules, sans accents, espaces -> _)"""
    label = unidecode.unidecode(label)
    label = re.sub(r"[^a-z0-9]+", "_", label.lower())
    return label.strip("_")


class KboSpider(scrapy.Spider):
    name = "kbo_spider"

    # Variables depuis le .env
    CSV_PATH = os.getenv("CSV_PATH", "../KBO")
    CRAWL_LIMIT = int(os.getenv("CRAWL_LIMIT", 10))
    KBO_LANG = os.getenv("KBO_LANG", "fr")
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )

    def start_requests(self):
        csv_file = os.path.join(self.CSV_PATH, "enterprise.csv")
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            sample = random.sample(reader, min(self.CRAWL_LIMIT, len(reader)))

            for row in sample:
                numero = row["EnterpriseNumber"].replace(".", "")
                url = f"https://kbopub.economie.fgov.be/kbopub/toonondernemingps.html?lang={self.KBO_LANG}&ondernemingsnummer={numero}"
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    meta={"numero": numero},
                    headers={"Accept-Language": self.KBO_LANG, "User-Agent": self.USER_AGENT}
                )

    def parse(self, response):
        numero = response.meta["numero"]
        sections = {}
        current_section = "generalites"

        for row in response.css("tr"):
            section_title = row.css(
                "h2::text, th.sectiontitle::text, td.sectiontitle::text"
            ).get()
            if section_title:
                current_section = normalize(section_title)
                sections.setdefault(current_section, {})
                continue

            cells = row.css("td")
            if not cells:
                continue

            cell_texts = []
            cell_links = []
            for cell in cells:
                texts = [t.strip() for t in cell.css("*::text").getall() if t.strip()]
                links = cell.css("a::attr(href)").getall()
                cell_texts.append(" ".join(texts))
                cell_links.append(links)

            if len(cells) >= 2:
                key_text = cell_texts[0]
                key = normalize(key_text.replace(":", ""))
                val_text = " ".join(cell_texts[1:]).strip()
                val_links = [link for sublist in cell_links[1:] for link in sublist]

                if len(cells) > 2 or current_section in ["fonctions", "qualites", "activites", "liens_externes"]:
                    row_data = {"text": val_text, "links": val_links}
                    sections[current_section].setdefault(key, []).append(row_data)
                else:
                    sections[current_section][key] = {"text": val_text, "links": val_links}

            elif len(cells) == 1:
                val_text = cell_texts[0]
                val_links = cell_links[0]
                sections[current_section].setdefault("items", []).append(
                    {"text": val_text, "links": val_links}
                )

        item = KboItem()
        item["_id"] = numero
        item["numero"] = numero
        item["sections"] = sections

        item.clean_item()
        yield item
