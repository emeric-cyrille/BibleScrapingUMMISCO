import scrapy
import psycopg2
from scrapy import Request
from settings import POSTGRES_DB_USER, POSTGRES_DB_PWD, POSTGRES_DB_HOST, POSTGRES_DB_PORT, POSTGRES_DB_NAME


class NgomalahUpdateSpider(scrapy.Spider):
    name = "ngomalah_update_spider"

    def __init__(self):
        self.conn = psycopg2.connect(
            user=POSTGRES_DB_USER,
            password=POSTGRES_DB_PWD,
            host=POSTGRES_DB_HOST,
            port=POSTGRES_DB_PORT,
            database=POSTGRES_DB_NAME
        )
        self.cur = self.conn.cursor()

    def start_requests(self):
        print("Début de la mise à jour des versets en Ngomalah.")
        self.cur.execute("""
            SELECT c.id, c.url_fulfube, b.abbreviation, c.chapter_number
            FROM chapters c
            JOIN books b ON c.book_id = b.id
            WHERE c.url_fulfube IS NOT NULL
        """)
        chapters_nghomala = self.cur.fetchall()

        for chapter_id, url_nghomala, abbreviation, chapter_number in chapters_nghomala:
            yield Request(
                url=url_nghomala,
                meta={
                    'chapter_id': chapter_id,
                    'abbreviation': abbreviation,
                    'chapter_number': chapter_number
                }
            )

    def parse(self, response):
        chapter_id = response.meta['chapter_id']
        abbreviation = response.meta['abbreviation']
        chapter_number = response.meta['chapter_number']

        # Sélectionner les spans contenant les versets
        verses = response.xpath(f'//span[starts-with(@data-usfm, "{abbreviation}.{chapter_number}.")]')
        verses_dict = {}

        # Concaténer les textes des spans "ChapterContent_content__RrUqA"
        for verse in verses:
            data_usfm = verse.xpath('@data-usfm').get()

            # Récupérer tous les spans avec la classe "ChapterContent_content__RrUqA"
            content_parts = verse.xpath('.//span[contains(@class, "ChapterContent_content__RrUqA")]/text()').extract()
            full_text = ' '.join(content_parts).strip()

            if data_usfm not in verses_dict:
                verses_dict[data_usfm] = full_text
            else:
                verses_dict[data_usfm] += ' ' + full_text

        # Insérer les données dans la base de données
        for data_usfm, full_text in verses_dict.items():
            verse_number = data_usfm.split(".")[-1]

            if full_text and full_text[0].isdigit():
                full_text = full_text.split(" ", 1)[-1]

            try:
                if verse_number.isdigit():
                    print(f"Updating Ngomalah text for Chapter ID: {chapter_id}, Verse: {verse_number}")
                    self.cur.execute("""
                        UPDATE verses 
                        SET text_fulfube = %s 
                        WHERE chapter_id = %s AND verse_number = %s
                    """, (full_text, chapter_id, int(verse_number)))
                    self.conn.commit()
            except psycopg2.Error as e:
                print(f"Erreur lors de la mise à jour : {e}")
                self.conn.rollback()

    def close(self, reason):
        self.cur.close()
        self.conn.close()
        print("Mise à jour des versets en Ngomalah terminée.")
