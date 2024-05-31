from .models import dkb_visa, KATEGORIEN, kategorie_schlagwoerter, dkb_konto
from . import db
from sqlalchemy import func


def get_expenses_summarized_by_category(start_date, end_date):
    data = db.session.query(
        KATEGORIEN.Kategorie_name,
        func.sum(dkb_visa.Betrag).label('total_amount')
    ).join(
        KATEGORIEN, dkb_visa.Kategorie_id == KATEGORIEN.id
    ).group_by(
        KATEGORIEN.Kategorie_name
    ).filter(
        dkb_visa.Belegdatum.between(start_date, end_date)
    ).all()
    return data    


def get_paginated_data(table_class, offset):
    return table_class.query.order_by(
        table_class.id.asc()
    ).limit(10).offset(offset).all()


def get_paginated_konto_data(offset, limit: int = None):
    query = db.session.query(
        dkb_konto.Kontonummer,
        dkb_konto.Kontoinhaber,
        dkb_konto.Buchungsdatum,
        dkb_konto.Wertstellung,
        dkb_konto.Zahlungspflichtiger,
        dkb_konto.Zahlungsempfänger,
        dkb_konto.Verwendungszweck,
        dkb_konto.Umsatztyp,
        dkb_konto.IBAN,
        dkb_konto.Betrag,       
        KATEGORIEN.Kategorie_name
    ).join(
        KATEGORIEN, dkb_konto.Kategorie_id == KATEGORIEN.id
    ).order_by(
        func.date(dkb_konto.Buchungsdatum).desc()
    )
    
    if limit is not None:
        query = query.limit(limit)

    data = query.all()
    return data
    

def get_paginated_visa_data(offset, limit: int = None):
    query = db.session.query(
        dkb_visa.Belegdatum,
        dkb_visa.Beschreibung,
        dkb_visa.id,
        dkb_visa.Wertstellung,
        dkb_visa.Visa_Kartennummer,
        dkb_visa.Visa_Karteninhaber,
        dkb_visa.Umsatztyp,
        dkb_visa.Betrag,
        dkb_visa.Fremdwährungsbetrag,
        KATEGORIEN.Kategorie_name
    ).join(
        KATEGORIEN, dkb_visa.Kategorie_id == KATEGORIEN.id
    ).order_by(
        func.date(dkb_visa.Belegdatum).desc()
    )
    
    if limit is not None:
        query = query.limit(limit)

    data = query.all()

    return data


def get_unique_non_categorized_data(limit: int = None):
    query = db.session.query(
        dkb_visa.Beschreibung,
        dkb_visa.id,
        dkb_visa.Wertstellung,
        dkb_visa.Visa_Kartennummer,
        dkb_visa.Visa_Karteninhaber,
        dkb_visa.Umsatztyp,
        dkb_visa.Betrag,
        KATEGORIEN.Kategorie_name
    ).join(
        KATEGORIEN, dkb_visa.Kategorie_id == KATEGORIEN.id
    ).filter(
        KATEGORIEN.id == 1, dkb_visa.Umsatztyp!="Bargeldabhebung", dkb_visa.Umsatztyp!="Unbekannt"  # Filter out entries where the category id is equal to 1
    ).group_by(
        dkb_visa.Beschreibung
    ).order_by(
        func.date(dkb_visa.Belegdatum).desc()
    )

    if limit is not None:
        query = query.limit(limit)

    query.all()

    return query.all()


def get_all_categories():
    return KATEGORIEN.query.order_by(KATEGORIEN.Kategorie_name).all()


def get_keyword_to_category_mapping():
    query = db.session.query(
        kategorie_schlagwoerter.Schlagwort,
        kategorie_schlagwoerter.id,
        kategorie_schlagwoerter.Kategorie_id,
        KATEGORIEN.Kategorie_name
        ).join(
            KATEGORIEN, kategorie_schlagwoerter.Kategorie_id == KATEGORIEN.id
        ).order_by(
            KATEGORIEN.Kategorie_name
        )
    return query.all()