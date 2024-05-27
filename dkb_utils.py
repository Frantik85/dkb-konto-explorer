import pandas as pd
from datetime import datetime

BETRAG = 'Betrag (€)'
ZAHLUNGSEMPFAENGER = 'Zahlungsempfänger*in'
VERWENDUNGSZWECK = 'Verwendungszweck'

# Mapping für df --> sql-db
column_mapping_dkb_account = {
    'Betrag (€)': 'Betrag',
    'Gläubiger-ID': 'Gläubiger_ID',
    'Zahlungspflichtige*r':'Zahlungspflichtiger',
    'Zahlungsempfänger*in':'Zahlungsempfänger'    
}

column_mapping_dkb_visa = {
    'Betrag (€)': 'Betrag'
}


sql_column_names_dkb_account = [
    'Kontonummer', 
    'Kontoinhaber', 
    'Buchungsdatum', 
    'Wertstellung', 
    'Zahlungspflichtiger', 
    'Zahlungsempfänger', 
    'Verwendungszweck', 
    'Umsatztyp',
    'IBAN',
    'Betrag',
    'Gläubiger_ID',
    'Mandatsreferenz',
    'Kundenreferenz'
    ]

sql_column_names_dkb_visa = [
    'Visa_Kartennummer',
    'Visa_Karteninhaber',
    'Belegdatum',
    'Wertstellung',
    'Beschreibung',
    'Umsatztyp',
    'Betrag',
    'Fremdwährungsbetrag'
]


def post_process_dkb_visa_daten( df: pd.DataFrame, kartennummer: str, karteninhaber: str ) -> pd.DataFrame:
    df[BETRAG] = df[BETRAG].str.replace('.','').str.replace(',','.').astype(float)
    df['Visa_Kartennummer'] = kartennummer
    df['Visa_Karteninhaber'] = karteninhaber
    df['Belegdatum'] = df['Belegdatum'].apply(__preporcess_date__)
    df['Wertstellung'] = df['Wertstellung'].apply(__preporcess_date__)
    __rename_data_frame_columns_to_db_column_names__(df, column_mapping_dkb_visa)
    return df
    

def post_process_dkb_konto_daten( df: pd.DataFrame, kontonummer: str, kontoinhaber: str ) -> pd.DataFrame:
    df[VERWENDUNGSZWECK].fillna('', inplace=True)
    df[BETRAG] = df[BETRAG].str.replace('.','').str.replace(',','.').astype(float)
    df['Kategorie'] = ''
    df['Kontonummer'] = kontonummer
    df['Kontoinhaber'] = kontoinhaber
    df['Buchungsdatum'] = df['Buchungsdatum'].apply(__preporcess_date__)
    df['Wertstellung'] = df['Wertstellung'].apply(__preporcess_date__)
    __rename_data_frame_columns_to_db_column_names__(df, column_mapping_dkb_account)
    return df


def __rename_data_frame_columns_to_db_column_names__(df: pd.DataFrame, mapping: dict):
    df.rename(columns=mapping, inplace=True)


def __filter_for_new_data__(new_data: pd.DataFrame, sql_data: pd.DataFrame, database_columns: list) -> pd.DataFrame:
    # Check if any entry in the DataFrame already exists in the database
    df_to_insert = new_data.copy()
    for column in database_columns:
        df_to_insert = df_to_insert[~df_to_insert[column].isin(sql_data[column])]
    return df_to_insert


def __preporcess_date__(date_string):
    # Parse the date string and convert it to the desired format
    if not pd.isna(date_string):
        date_object = datetime.strptime(date_string, '%d.%m.%y').date()  # Adjust format to match your input format
        return date_object.strftime('%Y-%m-%d')  # Convert to ISO 8601 format
    else:
        return 0


def check_and_insert_df(df: pd.DataFrame, conn, table_name: str, database_columns: list):
    # Get existing entries from the database
    existing_entries = pd.read_sql(f"SELECT {', '.join(database_columns)} FROM {table_name}", conn)

    df_to_insert = __filter_for_new_data__(df, existing_entries, database_columns)

    if not df_to_insert.empty:
        df_reduced = pd.DataFrame()
        # Insert the new entries into the database
        for column in database_columns:
            df_reduced[column] = df_to_insert[column]
        df_reduced.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"{len(df_reduced)} - new entries added to the database {table_name}.")
    else:
        print(f"All entries already exist in the database {table_name}.")