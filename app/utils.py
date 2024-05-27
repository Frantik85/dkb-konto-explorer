from .models import dkb_visa, KATEGORIEN
from . import db
from sqlalchemy import func


def get_paginated_data(table_class, offset):
    return table_class.query.order_by(
        table_class.id.asc()
    ).limit(10).offset(offset).all()
    

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

    unique_descriptions = query.all()

    return unique_descriptions


def get_all_categories():
    return KATEGORIEN.query.order_by(KATEGORIEN.Kategorie_name).all()