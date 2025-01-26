import psycopg2
from settings import *

def build_chapter_urls():
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(
            user=POSTGRES_DB_USER,
            password=POSTGRES_DB_PWD,
            host=POSTGRES_DB_HOST,
            port=POSTGRES_DB_PORT,
            database=POSTGRES_DB_NAME
        )
        cur = conn.cursor()

        # Requête pour récupérer les chapitres, abréviations et le code de langue
        cur.execute("""
            SELECT c.id, c.chapter_number, b.abbreviation, l.code, l.code_lang
            FROM chapters c
            JOIN books b ON c.book_id = b.id
            JOIN languages l ON b.language_id = l.id
            WHERE l.name = 'French'
        """)

        chapters = cur.fetchall()

        # Génération et mise à jour des URLs
        for chapter_id, chapter_number, abbreviation, code, code_lang in chapters:
            url_chapter = f"https://www.bible.com/fr/bible/{code}/{abbreviation}.{chapter_number}.{code_lang}"
            #url_chapter = url_chapter.replace('PDV2017','FB').replace('133','906')
            cur.execute("""
                UPDATE chapters 
                SET url_fulfube = %s 
                WHERE id = %s
            """, (url_chapter, chapter_id))

        # Validation des changements
        conn.commit()
        print("Mise à jour des URLs terminée avec succès.")

    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    build_chapter_urls()
