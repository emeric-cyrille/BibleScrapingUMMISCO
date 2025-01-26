import psycopg2
import csv
import xml.etree.ElementTree as ET
from settings import *

# Fichiers de sortie
OUTPUT_TXT = "verses_output.txt"
OUTPUT_CSV = "verses_output.csv"
OUTPUT_XML = "verses_output.xml"

def export_verses():
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
        print("Connexion réussie à la base de données.")

        # Requête SQL pour sélectionner les versets
        query = """
            SELECT 
                b.abbreviation || ' ' || c.chapter_number || ':' || v.verse_number AS reference,
                v.text_french AS text_french,
                v.text_nghomala,
                v.text_english
            FROM verses v
            JOIN chapters c ON v.chapter_id = c.id
            JOIN books b ON c.book_id = b.id
            WHERE v.text_nghomala IS NOT NULL
        """
        cur.execute(query)
        rows = cur.fetchall()

        # Écriture dans le fichier texte
        with open(OUTPUT_TXT, 'w', encoding='utf-8') as txt_file:
            txt_file.write("Reference\tText_French\tText_Nghomala\tText_English\n")
            for row in rows:
                reference, text_french, text_nghomala, text_english = row
                txt_file.write(f"{reference}\t{text_french or ''}\t{text_nghomala or ''}\t{text_english or ''}\n")
        print(f"Fichier TXT généré : {OUTPUT_TXT}")

        # Écriture dans le fichier CSV
        with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(["Reference", "Text_French", "Text_Nghomala", "Text_English"])
            for row in rows:
                writer.writerow(row)
        print(f"Fichier CSV généré : {OUTPUT_CSV}")

        # Écriture dans le fichier XML
        root = ET.Element("Verses")
        for row in rows:
            reference, text_french, text_nghomala, text_english = row
            verse_element = ET.SubElement(root, "Verse")
            ET.SubElement(verse_element, "Reference").text = reference
            ET.SubElement(verse_element, "Text_French").text = text_french or ""
            ET.SubElement(verse_element, "Text_Nghomala").text = text_nghomala or ""
            ET.SubElement(verse_element, "Text_English").text = text_english or ""
        tree = ET.ElementTree(root)
        tree.write(OUTPUT_XML, encoding='utf-8', xml_declaration=True)
        print(f"Fichier XML généré : {OUTPUT_XML}")

    except psycopg2.Error as e:
        print(f"Erreur lors de la connexion ou de l'exécution : {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Connexion à la base de données fermée.")

if __name__ == "__main__":
    export_verses()
