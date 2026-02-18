from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample in-memory data
incomes = [
    {'description': 'salario', 'amount': 60000},
    {'description': 'freelanceee', 'amount': 2000}
]

# GET endpoint to retrieve all incomes
@app.route('/incomes', methods=['GET'])
def get_incomes():
    return jsonify(incomes)

# POST endpoint to add a new income
@app.route('/incomes', methods=['POST'])
def add_income():
    # Get JSON data from the request body
    new_income = request.get_json()
    incomes.append(new_income)
    # Return an empty response with a 204 status code (No Content)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)