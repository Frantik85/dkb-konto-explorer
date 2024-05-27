from . import db

class dkb_visa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Visa_Kartennummer = db.Column(db.Integer)
    Visa_Karteninhaber = db.Column(db.String(255))
    Belegdatum = db.Column(db.String(255))
    Wertstellung = db.Column(db.String(255))
    Beschreibung = db.Column(db.String(255))
    Umsatztyp = db.Column(db.String(255))
    Betrag = db.Column(db.Float)
    Fremdwährungsbetrag = db.Column(db.String(255))
    Kategorie_id = db.Column(db.Integer)

class dkb_konto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Kontonummer = db.Column(db.String(255))
    Kontoinhaber = db.Column(db.String(255))
    Buchungsdatum = db.Column(db.String(255))
    Wertstellung = db.Column(db.String(255))
    Zahlungspflichtiger = db.Column(db.String(255))
    Zahlungsempfänger = db.Column(db.String(255))
    Verwendungszweck = db.Column(db.String(255))
    Umsatztyp = db.Column(db.String(255))
    IBAN = db.Column(db.String(255))
    Betrag = db.Column(db.Float)
    Gläubiger_ID = db.Column(db.String(255))
    Mandatsreferenz = db.Column(db.String(255))
    Kundenreferenz = db.Column(db.String(255))
    Kategorie_id = db.Column(db.Integer)

class KATEGORIEN(db.Model):
    __tablename__ = 'KATEGORIEN'
    id = db.Column(db.Integer, primary_key=True)
    Kategorie_name = db.Column(db.String(255))

    @staticmethod
    def add(name):
        new_category = KATEGORIEN(Kategorie_name=name)
        db.session.add(new_category)
        db.session.commit()

class kategorie_schlagwoerter(db.Model):
    __tablename__ = 'kategorie_schlagwoerter'
    id = db.Column(db.Integer, primary_key=True)
    Schlagwort = db.Column(db.String(255))
    Kategorie_id = db.Column(db.Integer)
