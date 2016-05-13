import RPi.GPIO as GPIO
from flask import Flask, render_template, request, Response
from functools import wraps

app = Flask(__name__)

def check_auth(username, password):
    return username == 'admin' and password == 'secret'

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

GPIO.setmode(GPIO.BCM)

pins = {
  23 : {'name' : 'GPIO 23', 'state' : GPIO.LOW},
  24 : {'name' : 'GPIO 24', 'state' : GPIO.LOW}
  }

for pin in pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, GPIO.LOW)

@app.route("/")
@requires_auth
def main():
  for pin in pins:
    pins[pin]['state'] = GPIO.input(pin)

  templateData = {
    'pins' : pins
    }
  return render_template('index.html', **templateData)

@app.route("/<changePin>/<action>")
@requires_auth
def action(changePin, action):
  changePin = int(changePin)
  deviceName = pins[changePin]['name']
  if action == "on":
    GPIO.output(changePin, GPIO.HIGH)
    message = "Turned " + deviceName + " on."
  if action == "off":
    GPIO.output(changePin, GPIO.LOW)
    message = "Turned" + deviceName + " on."

  for pin in pins:
    pins[pin]['state'] = GPIO.input(pin)

    templateData = {
      'pins' : pins
    }
  return render_template('index.html', **templateData)

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
