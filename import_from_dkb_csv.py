import pandas as pd
import dkb_utils
import sqlite3

# TODO: Check csvs for double >""< as they may break the csv import

file_path_dkb_csv       = 'daten/25-04-2024_Umsatzliste_Girokonto_DE15120300001017927466.csv'
file_path_dkb_visa_csv  = 'daten/25-04-2024_Umsatzliste_Visa Kreditkarte_8961.csv'
file_path_sql_db        = 'umsatz.db'

db = sqlite3.connect(file_path_sql_db)

# Lese & speichere DKB Kontodaten
umsatzdaten_konto = pd.read_csv(file_path_dkb_csv, sep=";", header=4)
umsatzdaten_konto = dkb_utils.post_process_dkb_konto_daten(umsatzdaten_konto, 'DE15120300001017927466', 'Daniel Findeisen')
dkb_utils.check_and_insert_df(umsatzdaten_konto, db, 'dkb_konto', dkb_utils.sql_column_names_dkb_account)


# Lese & speichere DKB Kontodaten
umsatzdaten_visa = pd.read_csv(file_path_dkb_visa_csv, sep=";", header=4)
umsatzdaten_visa = dkb_utils.post_process_dkb_visa_daten(umsatzdaten_visa, '4998970312868961', 'Daniel Findeisen')
dkb_utils.check_and_insert_df(umsatzdaten_visa, db, 'dkb_visa', dkb_utils.sql_column_names_dkb_visa)

db.close()