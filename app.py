from flask import Flask, render_template, request, redirect, url_for, jsonify 
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/daniel/Kostenanalyse/umsatz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Recommended for production
db = SQLAlchemy(app)
Bootstrap(app)  # Initialize Bootstrap

SQL_TABLE_DKB_VISA = "dkb_visa"
SQL_TABLE_DKB_KONTO = "dkb_konto"

# Define your database models (replace with your actual table structures)
class dkb_visa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Visa_Kartennummer       = db.Column(db.Integer)
    Visa_Karteninhaber      = db.Column(db.String(255))
    Belegdatum              = db.Column(db.String(255))
    Wertstellung            = db.Column(db.String(255))
    Beschreibung            = db.Column(db.String(255))
    Umsatztyp               = db.Column(db.String(255))
    Betrag                  = db.Column(db.Float)
    Fremdwährungsbetrag     = db.Column(db.String(255))
    Kategorie_id            = db.Column(db.Integer)
    # Add your DKB-VISA table columns here (e.g., date, amount, category)

class dkb_konto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Kontonummer=db.Column(db.String(255))
    Kontoinhaber=db.Column(db.String(255))
    Buchungsdatum=db.Column(db.String(255))
    Wertstellung=db.Column(db.String(255))
    Zahlungspflichtiger=db.Column(db.String(255))
    Zahlungsempfänger=db.Column(db.String(255))
    Verwendungszweck=db.Column(db.String(255))
    Umsatztyp=db.Column(db.String(255))
    IBAN=db.Column(db.String(255))
    Betrag=db.Column(db.Float)
    Gläubiger_ID=db.Column(db.String(255))
    Mandatsreferenz=db.Column(db.String(255))
    Kundenreferenz=db.Column(db.String(255))
    Kategorie_id=db.Column(db.Integer)
    # Add your DKB-Konto table columns here (e.g., date, transaction_type, balance)


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
    __tablename__   = 'kategorie_schlagwoerter'
    id              = db.Column(db.Integer, primary_key=True)
    Schlagwort      = db.Column(db.String(255))
    Kategorie_id    = db.Column(db.Integer)

# Helper function to fetch and paginate data based on table and offset
def get_paginated_data(table_class, offset):
    return table_class.query.order_by(
        table_class.id.asc()
        ).limit(10).offset(offset).all()


def get_paginated_visa_data(offest, limit: int = None):
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


@app.route('/')
def index():
    active_tab = 'dkb_visa'  # Default active tab
    dkb_visa_data = get_paginated_data(dkb_visa, 0)
    return render_template('dkb_data.html', dkb_visa_data=dkb_visa_data, active_tab=active_tab)


@app.route('/dkb_data/<table_name>/<int:offset>')
def load_more_data(table_name, offset):
    if table_name == 'dkb_visa':
        table_class = dkb_visa
    elif table_name == 'dkb_konto':
        table_class = dkb_konto
    else:
        return redirect(url_for('index'))  # Handle invalid table name
    data = get_paginated_data(table_class, offset)
    return render_template('data_snippet.html', data=data)


@app.route('/switch_tab/<string:tab_name>')
def switch_tab(tab_name):
    active_tab = tab_name
    if tab_name == 'dkb_visa':
        dkb_visa_data = get_paginated_visa_data(offest = 0)
        return render_template('dkb_data.html', dkb_visa_data=dkb_visa_data, active_tab=active_tab)
    elif tab_name == 'dkb_konto':
        dkb_konto_data = get_paginated_data(dkb_konto, 0)
        return render_template('dkb_data.html', dkb_konto_data=dkb_konto_data, active_tab=active_tab)
    elif tab_name == 'dkb_visa_categorize':
        unique_data = get_unique_non_categorized_data(20)
        categories = get_all_categories()
        return render_template('dkb_visa_categorize.html', unique_data=unique_data, categories=categories, active_tab=active_tab)
    else:
        return redirect(url_for('index'))  # Handle invalid tab selection


@app.route('/upload', methods=['GET', 'POST'])
def upload_data():
    if request.method == 'POST':
        # Implement data upload logic for CSV files based on selected table
        # Use libraries like pandas to read and process CSV data
        # Validate and insert data into the corresponding database table
        # Flash a success or error message
        pass
    return render_template('upload.html')


def update_categories(category_id: int, keyword: str):
    try:
        # Check if keyword exists in Beschreibung column (case-insensitive)
        entries_to_label = dkb_visa.query.filter(func.lower(dkb_visa.Beschreibung).like('%' + keyword + '%')).all()
        
        for entry in entries_to_label:
            # Label the entry with the provided category_id
            entry.Kategorie_id = category_id
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error when changing categories for dkb_visa entries: {e}")


@app.route('/update_category', methods=['POST'])
def update_category():
    entry_id = request.form['entry_id']
    category_id = request.form['category']
    keyword = request.form['category_keyword']
    
    # Update the category for the entry
    entry = dkb_visa.query.get(entry_id)
    entry.Kategorie_id = category_id
    db.session.commit()
    
    # Check if keyword exists for the given category_id
    keyword_check = kategorie_schlagwoerter.query.filter_by(Schlagwort=keyword, Kategorie_id=category_id).first()
    if keyword_check is None:
        try:
            # If keyword doesn't exist, add a new entry
            new_entry = kategorie_schlagwoerter(Schlagwort=keyword, Kategorie_id=category_id)
            db.session.add(new_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error adding keyword entry: {e}")
    
    update_categories(category_id, keyword)
    
    return redirect(request.referrer)


@app.route("/check_category", methods=["POST"])
def check_category():
    # Access data from form-encoded data in POST request
    category_name = request.form.get("categoryName")
    
    # Handle missing data
    if not category_name:
        return jsonify({"error": "Missing category name"}), 400
    
    # Query the database for the category
    category = KATEGORIEN.query.filter_by(Kategorie_name=category_name).first()
    
    # Return a JSON response indicating whether the category exists
    return jsonify({"exists": category is not None})


@app.route('/add_new_category', methods=['POST'])
def add_new_category():
    category_name = request.form.get("categoryName")

    if category_name:
        try:
            # Add the new category to the database
            new_category = KATEGORIEN(Kategorie_name=category_name)
            db.session.add(new_category)
            db.session.commit()
            #return redirect(url_for('update_category'))  # Correct usage of url_for
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error adding category: {e}")
            return jsonify({"error": "An error occurred while adding the category."}), 500
    else:
        return jsonify({"error": "Category name is required."}), 400


@app.route('/apply_category_to_descriptions', methods=['GET'])
def apply_category_to_descriptions():
    # Retrieve all entries from kategorie_schlagwoerter table
    schlagwoerter = kategorie_schlagwoerter.query.all()

    for schlagwort in schlagwoerter:
        # Query dkb_visa table for entries where any word in the Beschreibung column matches the Schlagwort
        matching_entries = dkb_visa.query.filter(func.lower(dkb_visa.Beschreibung).like('%' + schlagwort.Schlagwort.lower() + '%')).all()
        
        # Apply Kategorie_id to matching entries
        for entry in matching_entries:
            entry.Kategorie_id = schlagwort.Kategorie_id

    # Commit changes to the database
    db.session.commit()

    return "Categories applied to descriptions successfully."


if __name__ == '__main__':
    #db.create_all()  # Create tables if they don't exist
    app.run(debug=True)