# imported modules
import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, render_template
from signalwire.rest import Client as signalwire_client
import re
from pyngrok import ngrok
# Load our .env for our credentials.
load_dotenv()

# SIGNALWIRE credentials.
projectID = os.getenv('SIGNALWIRE_PROJECT')
authToken = os.getenv('SIGNALWIRE_TOKEN')
spaceURL = os.getenv('SIGNALWIRE_SPACE')
sw_phone_number = os.getenv('PHONE_NUMBER')
weather_api = os.getenv('OPENWEATHER_API')

# SIGNALWIRE variable
client = signalwire_client(projectID, authToken, signalwire_space_url=spaceURL)

# initializing Flask
app = Flask(__name__)


# Our home page.
@app.route('/')
def index():
    return render_template('index.html')


# The page for our weather app
@app.route('/weather', methods=['GET', 'POST'])
def weather():
    return render_template('weather.html')


# The page for our SMS texting app
@app.route("/sms", methods=['GET', 'POST'])
def sms():
    return render_template('sms.html')


# This is what we use to send and receive HTTP request relating to our SMS.
@app.route("/sms_handle", methods=['GET', 'POST'])
def sms_handle():
    p_number = request.args.get("p_number")
    body = request.args.get("sms_body")
    verified = p_validation(p_number)

# Here we check to see if the number was invalid
    if verified is False:
        output = "Invalid Phone Number"
        return render_template('return_sms.html', output=output)
# If the numer is correct we send out the message and let the user know.
    else:
        success_message = client.messages.create(to=p_number, from_=sw_phone_number, body=body)
        output = "Message was successfully sent!"
        return render_template('return_sms.html', output=output)


# Handler for weather, this will use OpenWeathers API
@app.route("/weather_handle", methods=['GET', 'POST'])
def weather_handle():
    country = request.args.get("c_int")
    zipcode = request.args.get("zip_c")
    url_lat = f"http://api.openweathermap.org/geo/1.0/zip?zip={zipcode},{country}&appid={weather_api}"
    response_lat_check = requests.get(url_lat).status_code

    # Here we check if the zipcode and country code works.
    if response_lat_check == 200:
        lat_lon = requests.get(url_lat).json()
        lon = lat_lon["lon"]
        lat = lat_lon["lat"]
        url_weather = f"https://api.openweathermap.org/data/2.5/weather?lat=" \
                      f"{lat}&lon={lon}&appid={weather_api}&units"f"=imperial"

        # We begin to parse the weather data and other user information.

        weather_r = requests.get(url_weather).json()
        temp = weather_r["main"]["temp"]
        temp_feel = weather_r["main"]["feels_like"]
        humidity = weather_r["main"]["humidity"]
        temp = int(temp)
        temp_feel = int(temp_feel)
        name_place = weather_r["name"]
        # Here we begin to gather userdata from the Weather page of the site.
        p_number_weather = request.args.get("phone_weather")
        value = request.args.get('check')
        verified_weather = p_validation_weather(p_number_weather)
        # We begin to print out the response to the user.
        # If the user checks the checkbox, we will send an SMS with the weather data.

        if value == "on":
            body_weather = f"In {name_place} it is currently {temp} degrees fahrenheit and it feels like {temp_feel}" \
                           f" degrees fahrenheit. The humidity is currently {humidity}%"
            success_message = client.messages.create(to=verified_weather, from_=sw_phone_number, body=body_weather)
            return render_template('return_weather_sms.html')

        # With the checkbox being left uncheck, The user didn't enter a number. So we will send it to their browser
        elif value is None:
            output = f"In {name_place} it is currently {temp} degrees fahrenheit and it feels like {temp_feel}" \
                     f" degrees fahrenheit. The humidity is currently {humidity}%"
            return render_template('return_weather.html', output=output)

    # If either the user enters a wrong country code or zipcode, we return an error message.
    else:
        output = "Sorry I didn't understand that. Let's try that again."
        return render_template('return_weather_failed.html', output=output)


# Here we verify if the number is a working number for our SMS app. We make use of the Regex module to do this.
def p_validation(p_number):
    pattern = re.compile(r'\d{10,11}$')
    filtered = re.sub("[^0-9]", "", p_number)
    matches = pattern.findall(filtered)

    for match in matches:
        if len(match) == 11 and match[0] == "1":
            match = "+" + match
            return match
        if len(match) == 10:
            match = "+1" + match
            return match
    else:
        return False


# Here we verify if the number is a working number for our OpenWeather app. We make use of the Regex module to do this.
def p_validation_weather(p_number_weather):
    pattern = re.compile(r'\d{10,11}$')
    filtered = re.sub("[^0-9]", "", p_number_weather)
    matches = pattern.findall(filtered)

    for match in matches:
        if len(match) == 11 and match[0] == "1":
            match = "+" + match
            return match
        if len(match) == 10:
            match = "+1" + match
            return match
    else:
        return False


def start_ngrok():
    # Set up a tunnel on port 5000 for our Flask object to interact locally
    url = ngrok.connect(5000).public_url
    print(' * Tunnel URL:', url)


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        start_ngrok()
# What we use to boot up flask and run it in debug mode.
app.run(debug=True)
