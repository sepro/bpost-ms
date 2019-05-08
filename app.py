import csv
import json
import re
import string
import unicodedata

import requests
from flask import Flask, request, Response, render_template
from flask_cors import CORS
from jsonschema import validate, ValidationError

from utils import find


def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def text_to_id(text):
    """
    Convert input text to id.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    text = strip_accents(text.lower())
    text = re.sub('[ ]+', '', text)
    text = re.sub('[^0-9a-zA-Z_]', '', text)
    return text


def read_zip_codes(filename):
    output = {}

    with open(filename, mode='r', encoding='cp1252') as infile:
        reader = csv.reader(infile, delimiter=";")

        _ = next(reader, None)  # skip the header

        for row in reader:
            try:
                output[int(row[0])] = {
                    text_to_id(row[1]): row[3]
                }
            except Exception as _:
                # skip if there is an error on the row
                pass

    return output


app = Flask(__name__)
CORS(app)

address_schema = {
    "type": "object",
    "properties": {
        "Title": {"type": "string"},
        "FirstName": {"type": "string"},
        "LastName": {"type": "string"},
        "StreetName": {"type": "string"},
        "StreetNumber": {"oneOf": [{"type": "string"}, {"type": "number"}]},
        "BoxNumber": {"oneOf": [{"type": "string"}, {"type": "number"}]},
        "PostalCode": {"oneOf": [{"type": "string"}, {"type": "number"}]},
        "MunicipalityName": {"type": "string"},
        "CountryName": {"type": "string"},
    },
    "required": ["StreetName", "StreetNumber", "PostalCode", "MunicipalityName"],
}
zipcodes = read_zip_codes('./data/zipcodes_alpha_nl.csv')


def validate_on_bpost(
    StreetName="",
    StreetNumber="",
    PostalCode="",
    MunicipalityName="",
    BoxNumber="",
    CountryName="",
    Title="",
    FirstName="",
    LastName="",
    timeout=3000,
    **kwargs
):
    """
    Takes parts from a standard (Belgian) address, validates using the BPost Webservice and returns the full response


    :param StreetName: Name of the street (string)
    :param StreetNumber: Number of the residence (string or int)
    :param BoxNumber: Designation of the box/apartment (string or int)
    :param PostalCode: Postal code of the municipality (string or int)
    :param MunicipalityName: Name of the municipality (string)
    :param CountryName: Name of the country (string)
    :param Title: Designation of the addressee (string)
    :param FirstName: First name of the addressee (string)
    :param LastName: Last name of the addressee (string)
    :param timeout: number of milliseconds before the request times out

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
                                    "AddresseeSurname": LastName,
                                }
                            }
                        },
                        "PostalAddress": {
                            "DeliveryPointLocation": {
                                "StructuredDeliveryPointLocation": {
                                    "StreetName": StreetName,
                                    "StreetNumber": str(StreetNumber),
                                    "BoxNumber": str(BoxNumber),
                                }
                            },
                            "PostalCodeMunicipality": {
                                "StructuredPostalCodeMunicipality": {
                                    "PostalCode": str(PostalCode),
                                    "MunicipalityName": MunicipalityName,
                                }
                            },
                            "CountryName": CountryName,
                        },
                        "DispatchingCountryISOCode": "BE",
                        "DeliveringCountryISOCode": "BE",
                    }
                ]
            },
            "ValidateAddressOptions": {
                "IncludeFormatting": True,
                "IncludeSuggestions": True,
                "IncludeSubmittedAddress": True,
                "IncludeDefaultGeoLocation": True,
                "IncludeListOfBoxes": False,
                "IncludeNumberOfBoxes": False,
            },
            "CallerIdentification": {"CallerName": "VIB KULeuven"},
        }
    }

    r = requests.post(url, data=json.dumps(payload), timeout=timeout / 1000)

    return r.json()


def parse_bpost_validation(payload, response):
    """
    Parses the response (as dict) from the BPost webservice

    :param payload: Dictionary with address send to this service
    :param response: Dictionary from BPost validation
    :return: Simplified dictionary
    """
    errors = 0
    warnings = 0
    output = {"status": "validated", "fields": {}, "formatted": {}}

    response_errors = list(find("Error", response))

    # If 0 < length of list, there are errors which need to be handled
    if 0 < len(response_errors):
        for response_error in response_errors[0]:
            if (
                isinstance(response_error, dict)
                and "ErrorSeverity" in response_error.keys()
            ):
                if response_error["ErrorSeverity"] == "warning":
                    warnings += 1
                elif response_error["ErrorSeverity"] == "error":
                    errors += 1

            if (
                isinstance(response_error, dict)
                and "ComponentRef" in response_error.keys()
            ):
                if response_error["ComponentRef"] != "":
                    component = list(find(response_error["ComponentRef"], response))

                    output["fields"][response_error["ComponentRef"]] = {
                        "valid": False,
                        "suggestion": string.capwords(component[0])
                        if 0 < len(component)
                        else "",
                    }

    # Add fields without a specific error to output
    # Some fields that are considered valid, are still different from the suggestion (!) this code will
    # include these as well.
    for field in payload.keys():
        if field not in output["fields"].keys():

            validated_field = "".join(list(find(field, response)))

            if (
                0 < len(validated_field)
                and str(payload[field]).strip().lower()
                != str(validated_field).strip().lower()
            ):
                output["fields"][field] = {
                    "valid": False,
                    "suggestion": string.capwords(validated_field),
                }

                warnings += 1
            else:
                output["fields"][field] = {"valid": True, "suggestion": payload[field]}

    if 0 < errors:
        output["result"] = "error"
    elif 0 < warnings:
        output["result"] = "warning"
    else:
        output["result"] = "valid"

    output["counts"] = {"errors": errors, "warnings": warnings}

    # Add formatted address to output
    formatted_submitted_address = list(find("FormattedSubmittedAddress", response))
    formatted_validated_address = list(find("Label", response))

    if 0 < len(formatted_submitted_address):
        if "Line" in formatted_submitted_address[0].keys():
            output["formatted"]["submitted"] = formatted_submitted_address[0]["Line"]
        else:
            output["formatted"]["submitted"] = []

    if 0 < len(formatted_validated_address):
        if "Line" in formatted_validated_address[0].keys():
            output["formatted"]["validated"] = formatted_validated_address[0]["Line"]
        else:
            output["formatted"]["validated"] = []

    # output['full'] = response

    return output


@app.route("/validate", methods=["POST"])
def validate_address():
    """
    API endpoint that takes a JSON object with an address, checks if key components (StreetName, ...) are included,
    validates that address on the BPost Webservice and returns a JSON response with the result in a simplified format.

    :return:
    """
    data = request.get_json()

    # Try to replace 'deelgemeente' with 'gemeente'
    try:
        municipality = zipcodes[int(data["PostalCode"])][text_to_id(data["MunicipalityName"])]
        data["MunicipalityName"] = municipality
    except Exception as _:
        # If this fails it couldn't convert a 'deelgemeente' to 'gemeente', just skip
        pass

    try:
        validate(instance=data, schema=address_schema)
    except ValidationError as e:
        # If the input doesn't match the expectation, capture the error and return an object with details and
        # the appropriate http error code (417, Expectation Error)
        exception = {"status": "error", "message": str(e)}
        return Response(json.dumps(exception), mimetype="application/json", status=417)

    try:
        bpost_validation = validate_on_bpost(**data)
    except Exception as e:
        # If this step fails the bpost service is unavailable, capture error and return an object with details and
        # the appropriate http error code (503, Service Unavailable)
        exception = {"status": "error", "message": str(e)}

        return Response(json.dumps(exception), mimetype="application/json", status=503)

    output = parse_bpost_validation(data, bpost_validation)

    return Response(json.dumps(output), mimetype="application/json")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
