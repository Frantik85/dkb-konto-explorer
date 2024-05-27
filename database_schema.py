import sqlite3

def create_tables():
    # Connect to SQLite database (create if not exists)
    conn = sqlite3.connect('umsatz.db')
    cursor = conn.cursor()

    # Create DKB_UMSATZ table
    cursor.execute('''CREATE TABLE IF NOT EXISTS dkb_konto (
                        id INTEGER PRIMARY KEY,
                        Kontonummer TEXT,
                        Kontoinhaber TEXT,
                        Buchungsdatum TEXT,
                        Wertstellung TEXT,
                        Zahlungspflichtiger TEXT,
                        Zahlungsempfänger TEXT,
                        Verwendungszweck TEXT DEFAULT NULL,
                        Umsatztyp TEXT,
                        IBAN TEXT,
                        Betrag REAL,
                        Gläubiger_ID TEXT DEFAULT NULL,
                        Mandatsreferenz TEXT DEFAULT NULL,
                        Kundenreferenz TEXT DEFAULT NULL,
                        Kategorie_id INTEGER DEFAULT 1,
                        FOREIGN KEY(Kategorie_id) REFERENCES KATEGORIEN(id)
                    )''')

    # Create DKB_VISA table
    cursor.execute('''CREATE TABLE IF NOT EXISTS dkb_visa (
                        id INTEGER PRIMARY KEY,
                        Visa_Kartennummer INTEGER,
                        Visa_Karteninhaber TEXT,
                        Belegdatum TEXT,
                        Wertstellung TEXT,
                        Beschreibung TEXT DEFAULT NULL,
                        Umsatztyp TEXT,
                        Betrag REAL,
                        Fremdwährungsbetrag TEXT DEFAULT "-",
                        Kategorie_id INTEGER DEFAULT 1,
                        FOREIGN KEY(Kategorie_id) REFERENCES KATEGORIEN(id)
                    )''')

    # Create DATA_QUELLE
    cursor.execute('''CREATE TABLE IF NOT EXISTS DATEN_QUELLE (
                            id INTEGER PRIMARY KEY,
                            daten_quelle TEXT type UNIQUE
                        )''')
    
    cursor.execute('''INSERT INTO DATEN_QUELLE (daten_quelle)
                        VALUES ('DKB_VISA'), ('DKB_KONTO')
                   ''')

    # Create KATEGORIEN table
    # Datenquellen_id: DKB account or visa?
    # Kategorie_marker: IBAN für DKB Konto, Beschreibung bei DKB Visa !
    cursor.execute('''CREATE TABLE IF NOT EXISTS KATEGORIEN (
                        id INTEGER PRIMARY KEY,
                        Kategorie_name TEXT type UNIQUE,
                        Datenquellen_id,
                        FOREIGN KEY(Datenquellen_id) REFERENCES DATEN_QUELLEN(id)
                    )''')
    
    # add test data to the kategorie database
#    cursor.execute('''INSERT INTO KATEGORIEN (Kategorie_name)
#                        VALUES ('Nicht zugeordnet'),
#                        ('Auto'),
#                        ('Tanken'),
#                        ('Shopping'),
#                        ('Baumarkt'),
#                        ('Hausbau'),
#                        ('Täglicher Bedarf'),
#                        ('Hauskredit'),
#                        ('Mittagessen'),
#                        ('Urlaub'),
#                        ('Friseur'),
#                        ('Abos'),
#                        ('Bargeld'),
#                        ('Geschenke'),
#                        ('Freizeit')
#                   ''')
    
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS kategorie_schlagwoerter (
                        id INTEGER PRIMARY KEY,
                        Schlagwort TEXT,
                        Kategorie_id INTEGER,
                        FOREIGN KEY(Kategorie_id) REFERENCES KATEGORIEN(id)
                    )''')
   
   
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS DKB_KONTO_KATEGORIEZUORDNUNG (
                        id INTEGER PRIMARY KEY,
                        DKB_Konto_id INTEGER,
                        Kategorie_id INTEGER,
                        FOREIGN KEY(DKB_Konto_id) REFERENCES dkb_konto(id),
                        FOREIGN KEY(Kategorie_id) REFERENCES KATEGORIEN(id)
                        )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS DKB_VISA_KATEGORIEZUORDNUNG (
                        id INTEGER PRIMARY KEY,
                        DKB_Visa_id INTEGER,
                        Kategorie_id INTEGER,
                        FOREIGN KEY(DKB_Visa_id) REFERENCES dkb_visa(id),
                        FOREIGN KEY(Kategorie_id) REFERENCES KATEGORIEN(id)
                        )''')


    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()