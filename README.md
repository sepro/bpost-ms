# BPost Microservice
Flask based microservice to quickly validate Belgian addresses. An easy request send to this webservice, is converted and 
forwarded to the official [bpost.be API](https://www.bpost.be/site/en/webservice-address) and met with a simplified response. 

As the official bpost webservice doesn't allow cross-origin resource sharing (CORS) it isn't possible to directly integrate 
the offical webservice with web-applications. This microservice was designed as a workaround for this limitation to 
validate addresses of new participants during the registration procedure  for the [Flemish Gut Flora Project](http://www.vlaamsdarmfloraproject.be).

## In a nutshell

A simple POST request, structured as indicated below, needs to be submitted to the **/validate** endpoint. This address will
be forwarded to the bpost validation server and the response parsed.

The response, a dictionary, will contain a "status" key, which can be "validated" or "error". In case the status is
validated the request was successfully forwarded to the BPost API and a response obtained, if this is error no 
validation was done due to an error.

In the "fields", for each component there is a key "valid" set to True or False, if the field is considered valid or
not and a "suggestion", which the BPost API thinks is the correct value.

The "result" can be "valid", in which case the provided address exists and is formatted correct. If this is 
"warning" there are one or more mistakes found, but they can likely be corrected. If this is "error" the input 
does't appear to be a valid Belgian address. How many errors and warnings where thrown is stored in the "counts" 
field.

Finally, in "formatted" the provided and validated addresses are stored, formatted by the BPost API (e.g. for 
printing on labels). This are in the "submitted" and "validated" fields respectively.

## Integration in your website

This webservice comes with a demo site where jQuery is used to read a form, validate the input and respond in different
ways. More details how to use jQuery to integrate this service with other projects can be found 
[here](./docs/jquery.md).

## Examples

There are a few different scenarios (valid, warning, error) that can occur, examples of each case can be found 
[here](./docs/examples.md). Below there is an example with a valid address as input provided. 

### Example with valid input

Example **payload** to submit
```json
{
	"Title": "Mr",
	"FirstName": "John",
	"LastName": "Doe",
	"StreetName": "Wetstraat",
	"StreetNumber": "16",
	"BoxNumber": "",
	"PostalCode": "1000",
	"MunicipalityName": "Brussel",
	"CountryName": "Belgie"
}
```

The **response** will contain for each field a key if it is valid or not and a suggestion.

Example output
```json
{
	"status": "validated",
	"fields": {
		"Title": {
			"valid": true,
			"suggestion": "Mr"
		},
		"FirstName": {
			"valid": true,
			"suggestion": "John"
		},
		"LastName": {
			"valid": true,
			"suggestion": "Doe"
		},
		"StreetName": {
			"valid": true,
			"suggestion": "Wetstraat"
		},
		"StreetNumber": {
			"valid": true,
			"suggestion": "16"
		},
		"BoxNumber": {
			"valid": true,
			"suggestion": ""
		},
		"PostalCode": {
			"valid": true,
			"suggestion": "1000"
		},
		"MunicipalityName": {
			"valid": true,
			"suggestion": "Brussel"
		},
		"CountryName": {
			"valid": true,
			"suggestion": "Belgie"
		}
	},
	"formatted": {
		"submitted": [
			"Mr John Doe",
			"Wetstraat 16",
			"1000 Brussel"
		],
		"validated": [
			"Mr John Doe",
			"WETSTRAAT 16",
			"1000 BRUSSEL"
		]
	},
	"result": "valid",
	"counts": {
		"errors": 0,
		"warnings": 0
	}
}
```


## Data Source

This webservice handles zip codes of municipalities a little different than the official one. The list of zip codes is available [here](https://www.bpost.be/site/nl/verzenden/adressering/zoek-een-postcode) on the BPost. Requests send to this service are formatted correctly and passed through to the BPost address validation service. 
