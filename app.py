from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///f1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=False)
    championships = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Driver {self.name}>'

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Team {self.name}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()
    return jsonify([{'id': team.id, 'name': team.name} for team in teams])

@app.route('/teams', methods=['POST'])
def add_team():
    data = request.get_json()
    new_team = Team(name=data['name'])
    db.session.add(new_team)
    db.session.commit()
    return jsonify({'message': 'Team added successfully'})

@app.route('/teams/<int:id>', methods=['PUT'])
def update_team(id):
    data = request.get_json()
    team = Team.query.get_or_404(id)
    team.name = data['name']
    db.session.commit()
    return jsonify({'message': 'Team updated successfully'})

@app.route('/teams/<int:id>', methods=['DELETE'])
def delete_team(id):
    team = Team.query.get_or_404(id)
    db.session.delete(team)
    db.session.commit()
    return jsonify({'message': 'Team deleted successfully'})

@app.route('/drivers', methods=['GET'])
def get_drivers():
    drivers = Driver.query.all()
    return jsonify([{'id': driver.id, 'name': driver.name, 'team': driver.team, 'championships': driver.championships} for driver in drivers])

@app.route('/drivers/<int:id>', methods=['GET'])
def get_driver(id):
    driver = Driver.query.get_or_404(id)
    return jsonify({'id': driver.id, 'name': driver.name, 'team': driver.team, 'championships': driver.championships})

@app.route('/drivers', methods=['POST'])
def add_driver():
    data = request.get_json()
    new_driver = Driver(name=data['name'], team=data['team'], championships=data['championships'])
    db.session.add(new_driver)
    db.session.commit()
    return jsonify({'message': 'Driver added successfully'}), 201

@app.route('/drivers/<int:id>', methods=['PUT'])
def update_driver(id):
    data = request.get_json()
    driver = Driver.query.get_or_404(id)
    driver.name = data['name']
    driver.team = data['team']
    driver.championships = data['championships']
    db.session.commit()
    return jsonify({'message': 'Driver updated successfully'})

@app.route('/drivers/<int:id>', methods=['DELETE'])
def delete_driver(id):
    driver = Driver.query.get_or_404(id)
    db.session.delete(driver)
    db.session.commit()
    return jsonify({'message': 'Driver deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', threaded=True, debug=True)
