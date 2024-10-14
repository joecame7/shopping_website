from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

# Shopping basket dictionary to store books
shopping_basket = {}

# Allow user to enter X amount of books
class QuantityForm(FlaskForm):
    quantity = StringField('Enter quantity: ', validators=[DataRequired(), Length(min=0, max=100)])
    submit = SubmitField('Submit')

# Create Database
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), index=True, unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    cover = db.Column(db.Text)
    environmental_impact = db.Column(db.Integer)

@app.route('/')
def galleryPage():
    # Sort the books
    sort_by = request.args.get('sort_by')
    if sort_by == 'name':
        books = Book.query.order_by(Book.title)
    elif sort_by == 'price_low_to_high':
        books = Book.query.order_by(Book.price)
    elif sort_by == 'price_high_to_low':
        books = Book.query.order_by(Book.price.desc())
    elif sort_by == 'environmental_impact_low_to_high':
        books = Book.query.order_by(Book.environmental_impact)
    elif sort_by == 'environmental_impact_high_to_low':
        books = Book.query.order_by(Book.environmental_impact.desc())
    else:
        books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/book/<int:bookId>', methods=['GET', 'POST'])
def singleProductPage(bookId):
    form = QuantityForm()
    book = Book.query.get(bookId)
    if form.validate_on_submit():
        quantity = int(form.quantity.data)
        shopping_basket[bookId] = quantity
        return render_template('SingleBookQuantity.html', book=book, quantity=form.quantity.data)
    else:
        return render_template('SingleBook.html', book=book, form=form)
    
@app.route('/basket')
def shoppingBasket():
    basket_items = []
    total_price = 0
    for book_id, quantity in shopping_basket.items():
        book = Book.query.get(book_id)
        if book:
            total_price += book.price * quantity
            basket_items.append({'book': book, 'quantity': quantity})
    total_price = round(total_price, 2)
    if total_price == 0:
        total_price = None
    return render_template('basket.html', basket_items=basket_items, total_price=total_price)

@app.route('/remove/<int:book_id>', methods=['GET', 'POST'])
def removeFromBasket(book_id):
    if book_id in shopping_basket:
        del shopping_basket[book_id]
    return redirect(url_for('shoppingBasket'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    error = False
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        cardholder = request.form.get('cardholder_name')
        month = request.form.get('month')
        year = request.form.get('year')
        cvv = request.form.get('cvv')
        
        # Validate the card details
        if card_number or cardholder or month or year or cvv:
            card_number = card_number.replace(" ", "")
            card_number = card_number.replace("-", "")

            valid_card_number = card_number.isdigit() and len(card_number) == 16
            valid_month = month.isdigit() and len(month) <= 2 and (int(month) >= 1 and int(month) <= 12)
            valid_year = year.isdigit() and (len(year) == 2 or len(year) == 4)
            valid_cvv = cvv.isdigit() and len(cvv) == 3

            if valid_card_number and valid_month and valid_year and valid_cvv:
                return redirect(url_for('success'))
            else:
                error = True

    return render_template('checkout.html', error=error)

@app.route('/success', methods=['GET', 'POST'])
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')