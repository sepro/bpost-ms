from flask import Flask, request, Response

import json
from jsonschema import validate, ValidationError

app = Flask(__name__)

address_schema = {
    "type": "object",
    "properties": {
        "Title": {"type": "string"},
        "FirstName": {"type": "string"},
        "LastName": {"type": "string"},
        "StreetName": {"type": "string"},
        "StreetNumber": {
            "oneOf": [
                {"type": "string"},
                {"type": "number"}
            ]},
        "BoxNumber": {
            "oneOf": [
                {"type": "string"},
                {"type": "number"}
            ]},
        "PostalCode": {
            "oneOf": [
                {"type": "string"},
                {"type": "number"}
            ]},
        "MunicipalityName": {"type": "string"},
        "Country": {"type": "string"},
    },
    "required": [
        "StreetName",
        "StreetNumber",
        "PostalCode",
        "MunicipalityName"
    ]
}


@app.route('/validate', methods=['POST'])
def validate_address():
    data = request.get_json()

    try:
        validate(instance=data, schema=address_schema)
    except ValidationError as e:
        exception = {
            "status": "error",
            "message": str(e)
        }

        return Response(json.dumps(exception), mimetype='application/json', status=405)

    return Response(json.dumps(data), mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=True)
