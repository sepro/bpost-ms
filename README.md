# BPost Microservice
Flask based microservice to quickly validate Belgian addresses. An easy request if forwarded to the bpost.be API and met with a simplified response.

## In a nutshell

A simple post request, structured as indicated below, needs to be submitted to the /validate endpoint. This address will
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


## Various examples

### Example with valid input

Example payload to submit
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

The response will contain for each field a key if it is valid or not and a suggestion.

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

### Example with a small error

Example payload to submit (note the typo in *Wetstraat*)
```json
{
	"Title": "Mr",
	"FirstName": "John",
	"LastName": "Doe",
	"StreetName": "Wetqstraat",
	"StreetNumber": "16",
	"BoxNumber": "",
	"PostalCode": "1000",
	"MunicipalityName": "Brussel",
	"CountryName": "Belgie"
}
```

The response will contain for each field a key if it is valid or not and a suggestion.

Example output
```json
{
	"status": "validated",
	"fields": {
		"StreetName": {
			"valid": false,
			"suggestion": "Wetstraat"
		},
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
			"Wetqstraat 16",
			"1000 Brussel"
		],
		"validated": [
			"Mr John Doe",
			"WETSTRAAT 16",
			"1000 BRUSSEL"
		]
	},
	"result": "warning",
	"counts": {
		"errors": 0,
		"warnings": 1
	}
}
```

### Example with many mistakes
Here the address contains so many mistakes it can no longer be validated.

Example payload to submit
```json
{
	"Title": "Mr",
	"FirstName": "John",
	"LastName": "Doe",
	"StreetName": "Wetstraat",
	"StreetNumber": "16000",
	"BoxNumber": "",
	"PostalCode": "2000",
	"MunicipalityName": "Hasselt",
	"CountryName": "Belgie"
}
```

The response will contain for each field a key if it is valid or not and a suggestion.

Example output
```json
{
	"status": "validated",
	"fields": {
		"StreetNumber": {
			"valid": false,
			"suggestion": ""
		},
		"StreetName": {
			"valid": false,
			"suggestion": "Rietstraat"
		},
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
		"BoxNumber": {
			"valid": true,
			"suggestion": ""
		},
		"PostalCode": {
			"valid": false,
			"suggestion": "3500"
		},
		"MunicipalityName": {
			"valid": true,
			"suggestion": "Hasselt"
		},
		"CountryName": {
			"valid": true,
			"suggestion": "Belgie"
		}
	},
	"formatted": {
		"submitted": [
			"Mr John Doe",
			"Wetstraat 16000",
			"2000 Hasselt"
		],
		"validated": [
			"Mr John Doe",
			"RIETSTRAAT",
			"3500 HASSELT"
		]
	},
	"result": "error",
	"counts": {
		"errors": 1,
		"warnings": 3
	}
}
```