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

    # Sections du site KBO / Ejustice / Consult
    sections = scrapy.Field()

    def clean_section(self, section_data):
        """
        Nettoie une section (dict ou list).
        - Supprime les champs vides
        - Supprime retours à la ligne et tabulations
        """

        # Cas dictionnaire (clé → valeur)
        if isinstance(section_data, dict):
            cleaned = {}
            for key, value in section_data.items():
                if isinstance(value, dict):
                    text = " ".join(value.get("text", "").split()).strip()
                    links = value.get("links", [])
                    if text or links:
                        cleaned[key] = {"text": text, "links": links}
                elif isinstance(value, list):
                    sublist = []
                    for v in value:
                        if not v:
                            continue
                        text = " ".join(v.get("text", "").split()) if "text" in v else ""
                        links = v.get("links", [])
                        if text.strip() or links:
                            sublist.append({"text": text.strip(), "links": links})
                    if sublist:
                        cleaned[key] = sublist
                else:
                    if value:
                        cleaned[key] = value
            return cleaned

        # Cas liste (utilisé dans ejustice ou consult)
        elif isinstance(section_data, list):
            cleaned_list = []
            for v in section_data:
                if isinstance(v, dict):
                    text = " ".join(v.get("text", "").split()) if "text" in v else ""
                    links = v.get("links", [])
                    if text.strip() or links:
                        cleaned_list.append({"text": text.strip(), "links": links})
                else:
                    if v:
                        cleaned_list.append(v)
            return cleaned_list

        # Cas valeur simple (string, int, etc.)
        else:
            return section_data

    def clean_item(self):
        """
        Nettoie toutes les sections de l'item.
        """
        if "sections" in self:
            self["sections"] = {k: self.clean_section(v) for k, v in self["sections"].items()}
        return self
