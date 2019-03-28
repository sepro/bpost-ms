from flask import Flask, request, Response, render_template

import json
import requests
from jsonschema import validate, ValidationError

from utils import find

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


def validate_on_bpost(StreetName="", StreetNumber="", PostalCode="", MunicipalityName="", BoxNumber="", Country="",
                      Title="", FirstName="", LastName="",
                      **kwargs):
    """
    Takes parts from a standard (Belgian) address, validates using the BPost Webservice and returns the full response


    :param StreetName: Name of the street (string)
    :param StreetNumber: Number of the residence (string or int)
    :param BoxNumber: Designation of the box/apartment (string or int)
    :param PostalCode: Postal code of the municipality (string or int)
    :param MunicipalityName: Name of the municipality (string)
    :param Country: Name of the country (string)
    :param Title: Designation of the addressee (string)
    :param FirstName: First name of the addressee (string)
    :param LastName: Last name of the addressee (string)

    :param kwargs: catch remaining kwargs (to avoid keyword argument error in case more details are provided)
    :return: dict with validation for each keyword
    """

    url = "https://webservices-pub.bpost.be/ws/ExternalMailingAddressProofingCSREST_v1/address/validateAddresses"

    payload = {
        "ValidateAddressesRequest": {
            "AddressToValidateList": {
                "AddressToValidate": [
                    {
                        "@id": "1",
                        "MaileeAndAddressee": {
                            "AddresseeIndividualIdentification": {
                                "StructuredAddresseeIndividualIdentification": {
                                    "AddresseeFormOfAddress": Title,
                                    "AddresseeGivenName": FirstName,
                                    "AddresseeSurname": LastName
                                }
                            }
                        },
                        "PostalAddress": {
                            "DeliveryPointLocation": {
                                "StructuredDeliveryPointLocation": {
                                    "StreetName": StreetName,
                                    "StreetNumber": str(StreetNumber),
                                    "BoxNumber": str(BoxNumber)
                                }
                            },
                            "PostalCodeMunicipality": {
                                "StructuredPostalCodeMunicipality": {
                                    "PostalCode": str(PostalCode),
                                    "MunicipalityName": MunicipalityName
                                }
                            },
                            "CountryName": Country
                        },
                        "DispatchingCountryISOCode": "BE",
                        "DeliveringCountryISOCode": "BE"
                    }
                ]
            },
            "ValidateAddressOptions": {
                "IncludeFormatting": True,
                "IncludeSuggestions": True,
                "IncludeSubmittedAddress": True,
                "IncludeDefaultGeoLocation": True,
                "IncludeListOfBoxes": False,
                "IncludeNumberOfBoxes": False
            },
            "CallerIdentification": {
                "CallerName": "VIB KULeuven"
            }
        }
    }

    r = requests.post(url, data=json.dumps(payload))

    return r.json()


def parse_bpost_validation(response):
    """
    Parses the response (as dict) from the BPost webservice

    :param response: Dictionary from BPost validation
    :return: Simplified dictionary
    """
    errors = 0
    warnings = 0
    output = {
        'status': 'validated',
        'fields': {}
    }

    response_errors = list(find("Error", response))

    # If 0 < length of list, there are errors which need to be handled
    if 0 < len(response_errors):
        for response_error in response_errors[0]:
            if isinstance(response_error, dict) and 'ErrorSeverity' in response_error.keys():
                if response_error['ErrorSeverity'] == 'warning':
                    warnings += 1
                elif response_error['ErrorSeverity'] == 'error':
                    errors += 1

            if isinstance(response_error, dict) and 'ComponentRef' in response_error.keys():
                if response_error['ComponentRef'] != '':
                    component = find(response_error['ComponentRef'], response)

                    output['fields'][response_error['ComponentRef']] = {
                        'valid': False,
                        'suggestion': ','.join(list(component))
                    }

    if 0 < errors:
        output['result'] = 'error'
    elif 0 < warnings:
        output['result'] = 'warning'
    else:
        output['result'] = 'valid'

    return {'ori': response, 'simple': output}


@app.route('/validate', methods=['POST'])
def validate_address():
    """
    API endpoint that takes a JSON object with an address, checks if key components (StreetName, ...) are included,
    validates that address on the BPost Webservice and returns a JSON response with the result in a simplified format.

    :return:
    """
    data = request.get_json()

    try:
        validate(instance=data, schema=address_schema)
    except ValidationError as e:
        # If the input doesn't match the expectation, capture the error and return an object with details and
        # the appropriate http error code (417, Expectation Error)
        exception = {
            "status": "error",
            "message": str(e)
        }
        return Response(json.dumps(exception), mimetype='application/json', status=417)

    try:
        bpost_validation = validate_on_bpost(**data)
    except Exception as e:
        # If this step fails the bpost service is unavailable, capture error and return an object with details and
        # the appropriate http error code (503, Service Unavailable)
        exception = {
            "status": "error",
            "message": str(e)
        }

        return Response(json.dumps(exception), mimetype='application/json', status=503)

    output = parse_bpost_validation(bpost_validation)

    return Response(json.dumps(output), mimetype='application/json')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
