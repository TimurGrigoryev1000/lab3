import pyrebase
import random
import time
from sense_hat import SenseHat

username = "Timur Grigoryev 101276841"


# Write random numbers to database
def writeData():
  key = 0

  for i in range(3):
    # I'm using dummy sensor data here, you could use your senseHAT
    
    sense = SenseHat()
    
    temp = sense.get_temperature()
    humidity =  sense.get_humidity()
    pressure = sense.get_pressure()
    
    pressure = round(pressure, 1)
    temp = round(temp, 1)
    humidity = round(humidity, 1)

    # Will be written in this form:
    # {
    #   "sensor1" : {
    #     "0" : 0.6336863763908736,
    #     "1" : 0.33321038818190285,
    #     "2" : 0.6069185320998802,
    #     "3" : 0.470459178006184,
    #   }
    # }
    # Each 'child' is a JSON key:value pair
    db.child(username).child("Temperature").child(key).set(temp)
    db.child(username).child("Humidity").child(key).set(humidity)
    db.child(username).child("Pressure").child(key).set(pressure)

    key = key + 1
    time.sleep(1)

def readData():
    sensors = ["Temperature", "Humidity", "Pressure"]

    root = db.get().val()  # whole database
    if root is None:
        print("Database is empty.")
        return

    if not isinstance(root, dict):
        print(f"Unexpected database root type: {type(root)}")
        return

    for user in sorted(root.keys()):
        if user == username:
            continue  # skip yourself (optional)

        print(f"\n=== {user} ===")

        for sensor in sensors:
            snapshot = db.child(user).child(sensor).get()
            data = snapshot.val()

            if data is None:
                print(f"{sensor}: No data")
                continue

            # Case 1: Firebase returns a list (common when keys are 0,1,2,...)
            if isinstance(data, list):
                # filter out any None gaps, keep indices for “keys”
                indexed = [(i, v) for i, v in enumerate(data) if v is not None]
                last_three = indexed[-3:]

                print(f"{sensor} (last {len(last_three)}):")
                for k, v in last_three:
                    print(f"  {k}: {v}")

            # Case 2: Firebase returns dict (string keys)
            elif isinstance(data, dict):
                items = sorted(data.items(), key=lambda kv: int(kv[0]))
                last_three = items[-3:]

                print(f"{sensor} (last {len(last_three)}):")
                for k, v in last_three:
                    print(f"  {k}: {v}")

            else:
                print(f"{sensor}: Unexpected type {type(data)}")



if __name__ == '__main__':
    # Create new Firebase config and database object
    config = {
      "apiKey": "AIzaSyA2a8rPK6u2dnmYPD205XLOOylNMO_5YYk",
      "authDomain": "lab3-cf15c.firebaseapp.com",
      "databaseURL": "https://lab3-cf15c-default-rtdb.firebaseio.com",
      "storageBucket": "lab3-cf15c.firebasestorage.app"
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    dataset = "Wyatt-West-101281536"
    writeData()
    readData()
