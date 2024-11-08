from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'collatz.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

API_KEY = "xyz"


class CollatzResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    sequence = db.Column(db.String, nullable=False)


class LastProcessedNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_number = db.Column(db.Integer, nullable=False)


def init_db():
    db.create_all()

    if LastProcessedNumber.query.first() is None:
        db.session.add(LastProcessedNumber(last_number=1))
        db.session.commit()


with app.app_context():
    init_db()


def require_api_key(func):
    def wrapper(*args, **kwargs):
        if request.headers.get('X-API-KEY') != API_KEY:
            abort(401, description="Unauthorized: Invalid API Key")
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/get_next_range', methods=['GET'])
@require_api_key
def get_next_range():
    range_size = int(request.args.get('range_size', 100))
    last_number_record = LastProcessedNumber.query.first()
    last_number = last_number_record.last_number

    new_start = last_number + 1
    new_end = new_start + range_size - 1

    last_number_record.last_number = new_end
    db.session.commit()

    return jsonify({"start": new_start, "end": new_end})


@app.route('/submit_collatz', methods=['POST'])
@require_api_key
def submit_collatz():
    data = request.json
    number = data.get('number')
    sequence = data.get('sequence')

    if number and sequence:
        if not CollatzResult.query.filter_by(number=number).first():
            new_result = CollatzResult(number=number, sequence=str(sequence))
            db.session.add(new_result)
            db.session.commit()
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Number already processed"}), 400

    return jsonify({"status": "error", "message": "Invalid data"}), 400


@app.route('/get_results', methods=['GET'])
@require_api_key
def get_results():
    results = CollatzResult.query.all()
    results_dict = {r.number: r.sequence for r in results}
    return jsonify(results_dict)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
