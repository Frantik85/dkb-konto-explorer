from flask import Blueprint, render_template
from ..models import dkb_visa, KATEGORIEN
from .. import db
from sqlalchemy import func
from ..utils import get_paginated_data

main_bp = Blueprint('main', __name__)

def get_paginated_visa_data(offset, limit=None):
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

def get_unique_non_categorized_data(limit=None):
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
        KATEGORIEN.id == 1, dkb_visa.Umsatztyp != "Bargeldabhebung", dkb_visa.Umsatztyp != "Unbekannt"
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

@main_bp.route('/')
def index():
    active_tab = 'dkb_visa'
    dkb_visa_data = get_paginated_data(dkb_visa, 0)
    return render_template('dkb_data.html', dkb_visa_data=dkb_visa_data, active_tab=active_tab)
