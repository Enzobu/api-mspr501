from flask import Blueprint, jsonify, request

# Créer un Blueprint pour le contrôleur
continent_controller = Blueprint('continent_controller', __name__)

# Exemple de données (simulateur de base de données)
data = [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"},
]

# Route GET pour récupérer les données
@continent_controller.route('/continents', methods=['GET'])
def get_items():
    return jsonify(data)

# Route GET pour récupérer un item spécifique par ID
@continent_controller.route('/continent/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((item for item in data if item["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)

# Route POST pour ajouter un nouvel item
@continent_controller.route('/continent', methods=['POST'])
def create_item():
    new_item = request.json
    new_item["id"] = max(item["id"] for item in data) + 1 if data else 1
    data.append(new_item)
    return jsonify(new_item), 201

# Route PUT pour modifier un item existant
@continent_controller.route('/continent/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = next((item for item in data if item["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    updates = request.json
    item.update(updates)
    return jsonify(item)

# Route DELETE pour supprimer un item
@continent_controller.route('/continent/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global data
    data = [item for item in data if item["id"] != item_id]
    return '', 204