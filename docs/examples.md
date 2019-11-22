# Examples

There are three possibilities (excluding failures), the input can be 100% valid, there can be a small (correctable) 
error and there could be a major mistake that cannot be corrected. Below are examples showing the request and the response
for each of those cases.

## Example with valid input

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
	},
	"GeographicalLocation": {
		"Latitude": {
			"Value": "50.9009339173",
			"CoordinateType": "DEGDEC"
		},
		"Longitude": {
			"Value": "4.6706534454",
			"CoordinateType": "DEGDEC"
		}
	}
}
```

## Example with a small error

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
	},
	"GeographicalLocation": {
		"Latitude": {
			"Value": "50.9009339173",
			"CoordinateType": "DEGDEC"
		},
		"Longitude": {
			"Value": "4.6706534454",
			"CoordinateType": "DEGDEC"
		}
	}
}
```

## Example with many mistakes
Here the address contains so many mistakes it can no longer be validated. The street number is invalid, the postal code,
municipality and street don't match.

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
	},
	"GeographicalLocation": {}
}
```