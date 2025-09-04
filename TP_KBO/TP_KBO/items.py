# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# import scrapy


# class TpKboItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass

import scrapy

class KboItem(scrapy.Item):
    """
    Item Scrapy pour les données KBO.
    Chaque section est un dictionnaire dynamique.
    """

    # Identifiant unique de l'entreprise (numero d'entreprise)
    _id = scrapy.Field()  # type: str
    numero = scrapy.Field()  # type: str

    # Sections du site KBO
    # Structure générale :
    # sections = {
    #   "generalites": { "numero_d_entreprise": {"text": "", "links": []}, ... },
    #   "fonctions": { "administrateur": [{"text": "", "links": []}, ...], ... },
    #   "qualites": [{"text": "", "links": []}, ...],
    #   "activites": [{"text": "", "links": []}, ...],
    #   "liens_externes": [{"text": "", "links": []}, ...],
    #   ...
    # }
    sections = scrapy.Field()

    def clean_section(self, section_data):
        """
        Nettoie une section : supprime items vides, supprime retours à la ligne et tabulations.
        """
        cleaned = {}
        for key, value in section_data.items():
            if isinstance(value, dict):
                text = " ".join(value.get("text", "").split()).strip()
                links = value.get("links", [])
                cleaned[key] = {"text": text, "links": links}
            elif isinstance(value, list):
                new_list = []
                for v in value:
                    if not v or (v.get("text", "").strip() == "" and not v.get("links")):
                        continue
                    text = " ".join(v.get("text", "").split()).strip()
                    links = v.get("links", [])
                    new_list.append({"text": text, "links": links})
                if new_list:
                    cleaned[key] = new_list
            else:
                cleaned[key] = value
        return cleaned

    def clean_item(self):
        """
        Nettoie toutes les sections de l'item.
        """
        if "sections" in self:
            self["sections"] = {k: self.clean_section(v) for k, v in self["sections"].items()}
        return self
