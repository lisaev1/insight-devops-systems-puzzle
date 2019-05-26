import datetime
import os

from flask import Flask, render_template, redirect, url_for
from forms import ItemForm
from models import Items
from database import db_session

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']

@app.route("/", methods=('GET', 'POST'))
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        try:
            _ = int(form.quantity.data)
        except ValueError:
            return "The \"quantity\" field must contain an integer. No items were added, and the database was NOT updated."

        if (len(form.name.data) > 256):
            _l = "name"
        elif (len(form.description.data) > 256):
            _l = "description"
        else:
            _l = "x"

        if (_l != "x"):
            return "Length of the \"{}\" field must not exceed 256 characters. No items were added, and the database was NOT updated.".format(_l)

        item = Items(name=form.name.data,
                     quantity=form.quantity.data,
                     description=form.description.data,
                     date_added=datetime.datetime.now())
        db_session.add(item)
        db_session.commit()

        return redirect(url_for('success'))

    return render_template('index.html', form=form)

@app.route("/success")
def success():
    results = []
 
    qry = db_session.query(Items)
    for i in qry.all():
        v = vars(i)
        results.append({d: str(v[d]) for d in v.keys()
            if ((not d.startswith("_")) and (not d.endswith("_")))})

    return "Your last 3 placed items: " + str(results[-3:])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5001)
