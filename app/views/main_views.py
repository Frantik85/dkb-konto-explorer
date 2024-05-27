from flask import Blueprint, render_template
from ..models import dkb_visa
from ..utils import get_paginated_data

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    active_tab = 'dkb_visa'
    dkb_visa_data = get_paginated_data(dkb_visa, 0)
    return render_template('dkb_data.html', dkb_visa_data=dkb_visa_data, active_tab=active_tab)
