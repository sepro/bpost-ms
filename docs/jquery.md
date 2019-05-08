# jQuery integration

To integrate this webservice into you own projects we recommend [jQuery](https://jquery.com/). Also note that the app 
comes with a demo-page to see full example code in action.

## Form validation, highlight errors

Make sure to include jQuery in the page's header. 

```html
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
```

HTML code for the actual form, here milligram.css is used for the grid structure. 

```html
<form>
    <fieldset>
        <div class="row">
            <div class="column column-20">
                <label for="titleField">Title</label>
                <select id="titleField">
                  <option value="Mr">Mr</option>
                  <option value="Ms">Ms</option>
                  <option value="Dr">Dr</option>
                </select>
            </div>
            <div class="column column-40">
                <label for="firstNameField">First Name</label>
                <input type="text" value="John" id="firstNameField">
            </div>
            <div class="column column-40">
                <label for="lastNameField">Last Name</label>
                <input type="text" value="Doe" id="lastNameField">
            </div>
        </div>

        <div class="row">
            <div class="column column-60">
                <label for="streetNameField">Street</label>
                <input type="text" value="Wetstraat" id="streetNameField">
            </div>
            <div class="column column-20">
                <label for="streetNumberField">Number</label>
                <input type="text" value="16" id="streetNumberField">
            </div>
            <div class="column column-20">
                <label for="boxNumberField">Box</label>
                <input type="text" value="" id="boxNumberField">
            </div>
        </div>

        <div class="row">
            <div class="column column-40">
                <label for="postalCodeField">Postal code</label>
                <input type="text" value="1000" id="postalCodeField">
            </div>
            <div class="column column-60">
                <label for="cityField">City</label>
                <input type="text" value="Brussel" id="cityField">
            </div>
        </div>
        <label for="countryField">Country</label>
        <input type="text" value="Belgie" id="countryField">
      <input class="button-primary float-right" type="submit" id="validation_button" value="Validate">
    </fieldset>
</form>         
<h2>Request</h2>
<pre>
    <code id="request"></code>
</pre>
<h2>Response</h2>
<pre>
    <code id="response"></code>
</pre>
```

An error class is required to light up fields containing an error.

```css
.error {
    border: 0.1rem solid #ca1f1f !important;
    background-color: #ff9999 !important;
}
```

Javascript code to make everything work. It will create a properly formatted payload and send this to the webservice. 
Based on the response, if an error is found, the fields containing a potential mistake will be highlighted.

```js
<script>
$(function() {

    $("#validation_button").click(function(ev) {
        ev.preventDefault();

        let payload = {
            'Title': $("#titleField").val(),
            'FirstName': $("#firstNameField").val(),
            'LastName': $("#lastNameField").val(),

            'StreetName': $("#streetNameField").val(),
            'StreetNumber': $("#streetNumberField").val(),
            'BoxNumber': $("#boxNumberField").val(),
            'PostalCode': $("#postalCodeField").val(),
            'MunicipalityName': $("#cityField").val(),
            'CountryName': $("#countryField").val()
        }

        $('#request').text(JSON.stringify(payload, null, '\t'));

        $.ajax({
            type: "POST",
            url: '{{ url_for('validate_address') }}',
            contentType: 'application/json;charset=UTF-8',
            data : JSON.stringify(payload, null, '\t'),
            timeout: 3000,
            success: function(data) {
                $('#response').text(JSON.stringify(data, null, '\t'));

                if (data['fields']['StreetName']['valid']) {
                    $("#streetNameField").removeClass('error');
                } else {
                    $("#streetNameField").addClass('error');
                }

                if (data['fields']['StreetNumber']['valid']) {
                    $("#streetNumberField").removeClass('error');
                } else {
                    $("#streetNumberField").addClass('error');
                }

                if (data['fields']['BoxNumber']['valid']) {
                    $("#boxNumberField").removeClass('error');
                } else {
                    $("#boxNumberField").addClass('error');
                }

                if (data['fields']['PostalCode']['valid']) {
                    $("#postalCodeField").removeClass('error');
                } else {
                    $("#postalCodeField").addClass('error');
                }

                if (data['fields']['MunicipalityName']['valid']) {
                    $("#cityField").removeClass('error');
                } else {
                    $("#cityField").addClass('error');
                }

                if (data['fields']['CountryName']['valid']) {
                    $("#countryField").removeClass('error');
                } else {
                    $("#countryField").addClass('error');
                }

            },
            statusCode: {
                503: function(data) {
                  console.log(data);
                  alert("Could not validate data on remote server.");
                }
              }
        });
    });
 });
 </script>   
```