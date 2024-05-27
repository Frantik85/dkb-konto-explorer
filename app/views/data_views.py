from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from ..models import dkb_visa, dkb_konto, KATEGORIEN, kategorie_schlagwoerter
from .. import db
from sqlalchemy import func
from ..utils import get_paginated_data, \
                    get_paginated_visa_data, \
                    get_unique_non_categorized_data, \
                    get_all_categories, \
                    get_expenses_summarized_by_category

data_bp = Blueprint('data', __name__)
charts_bp = Blueprint('charts', __name__)


@data_bp.route('/switch_tab/<string:tab_name>')
def switch_tab(tab_name):
    active_tab = tab_name
    if tab_name == 'dkb_visa':
        dkb_visa_data = get_paginated_visa_data(offset=0)
        return render_template('dkb_data.html', dkb_visa_data=dkb_visa_data, active_tab=active_tab)
    elif tab_name == 'dkb_konto':
        dkb_konto_data = get_paginated_data(dkb_konto, 0)
        return render_template('dkb_data.html', dkb_konto_data=dkb_konto_data, active_tab=active_tab)
    elif tab_name == 'dkb_visa_categorize':
        unique_data = get_unique_non_categorized_data(20)
        categories = get_all_categories()
        return render_template('dkb_visa_categorize.html', unique_data=unique_data, categories=categories, active_tab=active_tab)
    elif tab_name == 'charts':
        return render_template('charts.html')
    else:
        return redirect(url_for('main.index'))


@data_bp.route('/upload', methods=['GET', 'POST'])
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
        entries_to_label = dkb_visa.query.filter(func.lower(dkb_visa.Beschreibung).like('%' + keyword + '%')).all()

        for entry in entries_to_label:
            entry.Kategorie_id = category_id

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error when changing categories for dkb_visa entries: {e}")


@data_bp.route('/update_category', methods=['POST'])
def update_category():
    entry_id = request.form['entry_id']
    category_id = request.form['category']
    keyword = request.form['category_keyword']

    entry = dkb_visa.query.get(entry_id)
    entry.Kategorie_id = category_id
    db.session.commit()

    keyword_check = kategorie_schlagwoerter.query.filter_by(Schlagwort=keyword, Kategorie_id=category_id).first()
    if keyword_check is None:
        try:
            new_entry = kategorie_schlagwoerter(Schlagwort=keyword, Kategorie_id=category_id)
            db.session.add(new_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error adding keyword entry: {e}")

    update_categories(category_id, keyword)

    return redirect(request.referrer)


@data_bp.route("/check_category", methods=["POST"])
def check_category():
    category_name = request.form.get("categoryName")

    if not category_name:
        return jsonify({"error": "Missing category name"}), 400

    category = KATEGORIEN.query.filter_by(Kategorie_name=category_name).first()

    return jsonify({"exists": category is not None})


@data_bp.route('/add_new_category', methods=['POST'])
def add_new_category():
    category_name = request.form.get("categoryName")

    if category_name:
        try:
            new_category = KATEGORIEN(Kategorie_name=category_name)
            db.session.add(new_category)
            db.session.commit()
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error adding category: {e}")
            return jsonify({"error": "An error occurred while adding the category."}), 500
    else:
        return jsonify({"error": "Category name is required."}), 400


@data_bp.route('/apply_category_to_descriptions', methods=['GET'])
def apply_category_to_descriptions():
    schlagwoerter = kategorie_schlagwoerter.query.all()

    for schlagwort in schlagwoerter:
        matching_entries = dkb_visa.query.filter(func.lower(dkb_visa.Beschreibung).like('%' + schlagwort.Schlagwort.lower() + '%')).all()

        for entry in matching_entries:
            entry.Kategorie_id = schlagwort.Kategorie_id

    db.session.commit()

    return "Categories applied to descriptions successfully."


@charts_bp.route('/charts', methods=['GET', 'POST'])
def view_chart():
    if request.method == 'POST':
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Query to summarize expenses within the date range
        summarized_expenses = get_expenses_summarized_by_category(start_date, end_date)
        
        # Prepare data for Chart.js
        labels = [expense[0] for expense in summarized_expenses]
        data = [expense[1] for expense in summarized_expenses]
        
        # Prepare data for monthly expenses per category
        monthly_expenses = {}
        categories = get_all_categories()  # Assuming you have a function to fetch all categories
        for category in categories:
            category_expenses = db.session.query(
                func.strftime('%Y-%m', dkb_visa.Belegdatum).label('month'),
                func.sum(dkb_visa.Betrag).label('total_amount')
            ).join(
                KATEGORIEN, dkb_visa.Kategorie_id == KATEGORIEN.id
            ).filter(
                KATEGORIEN.id == category.id,
                dkb_visa.Belegdatum.between(start_date, end_date)
            ).group_by(
                func.strftime('%Y-%m', dkb_visa.Belegdatum)
            ).all()
            
            if category_expenses != []:
                monthly_expenses[category.Kategorie_name] = category_expenses

                monthly_expenses[category.Kategorie_name] = [
                        {'month': expense.month, 'total_amount': expense.total_amount}
                        for expense in category_expenses
                    ]
        
        return jsonify({
            'pie_chart': {'labels': labels, 'data': data},
            'monthly_expenses': monthly_expenses
        })

    return render_template('charts.html')


@charts_bp.route('/max_date_range', methods=['GET'])
def get_max_date_range():
    max_date = db.session.query(func.max(dkb_visa.Belegdatum)).scalar()
    min_date = db.session.query(func.min(dkb_visa.Belegdatum)).scalar()
    
    if max_date and min_date:
        return jsonify({'min_date': min_date, 'max_date': max_date})
    else:
        return jsonify({'error': 'No data available'}), 404