import scrapy
import psycopg2
from scrapy import Request
from settings import POSTGRES_DB_USER, POSTGRES_DB_PWD, POSTGRES_DB_HOST, POSTGRES_DB_PORT, POSTGRES_DB_NAME


class BibleSpider(scrapy.Spider):
    name = "bible_spider"

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
        # Étape 1: Parcourir et insérer les versets en français
        print("Début de l'insertion des versets en français.")
        self.cur.execute("""
            SELECT c.id, c.url_french, b.abbreviation, c.chapter_number
            FROM chapters c
            JOIN books b ON c.book_id = b.id
            WHERE c.url_french IS NOT NULL
        """)
        chapters_fr = self.cur.fetchall()
        for chapter_id, url_chapter, abbreviation, chapter_number in chapters_fr:
            yield Request(
                url_chapter,
                meta={
                    'chapter_id': chapter_id,
                    'abbreviation': abbreviation,
                    'chapter_number': chapter_number,
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
                print(f"Inserting French text for Chapter ID: {chapter_id}, Verse: {verse_number}")
                self.cur.execute("""
                    INSERT INTO verses (chapter_id, verse_number, text_french) 
                    VALUES (%s, %s, %s) 
                    ON CONFLICT (chapter_id, verse_number) DO UPDATE SET text_french = EXCLUDED.text_french
                """, (chapter_id, int(verse_number), full_text))
                self.conn.commit()

            except psycopg2.Error as e:
                print(f"Erreur lors de l'accès à la base : {e}")
                self.conn.rollback()

    def close(self, reason):
        self.cur.close()
        self.conn.close()
        print("Insertion des versets en français terminée.")
