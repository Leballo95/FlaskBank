

from flask import Flask, render_template, redirect, request, session, url_for

from datetime import date
from flask_sqlalchemy import SQLAlchemy

import csv
from io import StringIO
from flask import make_response

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)


class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    email_address = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float(20), default=1000)

    def __repr__(self):
        return f'<Welcome {self.first_name}>'


class Transactions(db.Model):
    trans_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    trans_type = db.Column(db.String(200), nullable=False)
    trans_amount = db.Column(db.Float(20), nullable=False)
    trans_date = db.Column(db.Date, default=date)

    def __repr__(self):
        return f'Transaction {self.trans_type}'


# Create database tables
with app.app_context():
    db.create_all()


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('home.html')


@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email_address = request.form.get('signup_email')

        new_account = Accounts(first_name=first_name, last_name=last_name, email_address=email_address)

        try:
            db.session.add(new_account)
            db.session.commit()
            print("Account created")
            return redirect(url_for('index'))


        except Exception as e:
            return f"Error occurred: {e}"


@app.route('/account', methods=['POST', 'GET'])
def account():
    client_email = session.get('client_email')  # Retrieve from session
    if client_email:
        user = Accounts.query.filter_by(email_address=client_email).first()

        if user:
            user_transactions = Transactions.query.filter_by(user_id=user.id).all()
            return render_template('account.html', first_name=user.first_name, user_transactions=user_transactions,
                                   balance=user.balance)
        print('User not found')
    return redirect(url_for('index'))


@app.route('/userLogin', methods=['POST'])
def user_login():
    session['client_email'] = request.form.get('client_email')
    print('session captured')
    return redirect(url_for('account'))


@app.route('/addTransaction', methods=['POST'])
def add_transaction():
    if request.method == 'POST':
        # Retrieve the logged-in user's email from the session
        client_email = session.get('client_email')
        user = Accounts.query.filter_by(email_address=client_email).first()

        # Retrieve transaction details from the form
        transaction_category = request.form.get('transactionOption')

        # Handle "transfer" transaction
        if transaction_category == "transfer":
            recipient_email = request.form.get('transfer-email')
            transfer_recipient = Accounts.query.filter_by(email_address=recipient_email).first()
            trans_amount = float(request.form.get('transfer-amount'))

            if transfer_recipient is None:
                print("Recipient not found")
                return redirect(url_for('account'))


            elif user.balance < trans_amount:
                print("Insufficient funds")  #replace with toast notification
                return redirect(url_for('account'))

            elif user.balance >= trans_amount and transfer_recipient:
                user.balance -= trans_amount
                transfer_recipient.balance += trans_amount

                # Record the transaction for the sender
                sender_transaction = Transactions(
                    user_id=user.id,
                    trans_type=f"transfer to {recipient_email} ({trans_amount})",
                    trans_date=date.today(),
                    trans_amount=trans_amount,

                )

                # Record the transaction for the recipient
                recipient_transaction = Transactions(
                    user_id=transfer_recipient.id,
                    trans_type=f"transfer from {client_email} ({trans_amount})",
                    trans_date=date.today(),
                    trans_amount=trans_amount,

                )
                try:
                    # Commit both the balance changes and the transactions
                    db.session.add(sender_transaction)
                    db.session.add(recipient_transaction)
                    db.session.commit()
                    print("Transaction created and funds transferred")
                    return redirect(url_for('account'))
                except Exception as e:
                    db.session.rollback()  # Rollback in case of an error
                    return f"Error occurred: {e}", 500





        # Handle "buy" transaction
        elif transaction_category == "buy":
            trans_amount = float(request.form.get('buy-amount'))
            buy_category = request.form.get('select-buy')
            trans_type = f"{transaction_category} {buy_category} ({trans_amount})"
            if user.balance >= trans_amount:
                user.balance -= trans_amount
                new_transaction = Transactions(
                    user_id=user.id,
                    trans_type=trans_type,
                    trans_amount=trans_amount,
                    trans_date=date.today()
                )
                try:
                    # Save the transaction and update the user's balance
                    db.session.add(new_transaction)
                    db.session.commit()
                    print("Transaction created")
                    return redirect(url_for('account'))
                except Exception as e:
                    db.session.rollback()  # Rollback in case of an error
                    return f"Error occurred: {e}", 500
            else:
                print("Insufficient funds")
                return redirect(url_for('account'))


@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    print("User logged out")
    return redirect(url_for('index'))



@app.route('/get_statement')
def get_statement():
    si = StringIO()
    cw = csv.writer(si)
    user_email=session.get('client_email')
    user=Accounts.query.filter_by(email_address=user_email).first()
    records = Transactions.query.filter_by(user_id=user.id).all()  # or a filtered set, of course
    # any table method that extracts an iterable will work
    cw.writerows([(r.trans_type, r.trans_amount, r.trans_date) for r in records])
    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=statement.csv'
    response.headers["Content-type"] = 'text/csv'
    return response



if __name__ == "__main__":
    app.run(debug=True)
