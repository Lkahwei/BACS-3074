# import flask dependencies
import urllib
import json
import os
import datetime

# Generate Random Appointment id
import random
import string

from flask import Flask, request, make_response, jsonify, render_template
from flask_mysqldb import MySQL

# initialize the flask app
app = Flask(__name__)

# SQL SERVER DATABASE 
app.config['MYSQL_USER'] = 'sql12363525'
app.config['MYSQL_PASSWORD'] = 'Vx2cqjrftm'
app.config['MYSQL_HOST'] = 'sql12.freemysqlhosting.net'
app.config['MYSQL_DB'] = 'sql12363525'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

skinProblemName = [""]
skinType = ''
appointment_date = ''
appointment_time = ''

@app.route('/')
def index():
  cur = mysql.connection.cursor()
  cur.execute('''SELECT * FROM appointment_table''')
  appointment_Details = cur.fetchall()

  print(appointment_Details)

  return 'Done!'

# create a route for webhook
@app.route('/webhook', methods=['POST'])
def webhook():
  data = request.get_json(silent=True)
  # find user skin type based on information given
  if data['queryResult']['action'] == 'findSkinType':
    reply = skinTypeDetermination(data)
    return reply

  elif data['queryResult']['action'] == 'confirmSkinType':
    reply = determineSkinType()
    return reply

  elif data['queryResult']['action'] == 'findProductDetails':
    reply = findProductDetails(data)
    return reply
   
  elif data['queryResult']['action'] == 'skinProblem':
    global skinProblemName
    skinProblemName = getSkinProblemName(data)
    reply = skinProblemProducts(data)
    return reply

  elif data['queryResult']['action'] == 'askProductDetails':
    reply = skinProblemProductDetails(skinProblemName)
    return reply

  elif data['queryResult']['action'] == 'appointmentDateandTime':
    reply = makeAppointment(data)
    return reply

  elif data['queryResult']['action'] == 'confirmAppointment':
    reply = confirmAppointmentDateTime()
    return reply

  elif data['queryResult']['action'] == 'findAppointment':
    reply = findMyAppointment(data)
    return reply

def skinTypeDetermination(req):
  global skinType
  skinCharacteristicsGiven = req.get("queryResult").get("parameters", None).get("skin-characteristics")
  counter = 0
  normalSkinCharacteristicsNotGiven = ["smooth texture", "few breakouts", "fine pores"]
  oilySkinCharacteristicsNotGiven = ["greasy", "prone to breakouts", "big pores"]
  drySkinCharacteristicsNotGiven = ["dry", "uneven texture", "tight"]
  combinationSkinCharacteristicsNotGiven = ["oily t-zone", "dry cheeks", "breakouts on forehead"]

  while counter < len(skinCharacteristicsGiven):
    if skinCharacteristicsGiven[counter] == 'smooth texture' or skinCharacteristicsGiven[counter] == 'few breakouts' or skinCharacteristicsGiven[counter] == 'fine pores':
      if skinCharacteristicsGiven[counter] == 'smooth texture':
        normalSkinCharacteristicsNotGiven.remove("smooth texture")
      elif skinCharacteristicsGiven[counter] == 'few breakouts':
        normalSkinCharacteristicsNotGiven.remove("few breakouts")
      else:
        normalSkinCharacteristicsNotGiven.remove("fine pores")

    elif skinCharacteristicsGiven[counter] == 'greasy' or skinCharacteristicsGiven[counter] == 'prone to breakouts' or skinCharacteristicsGiven[counter] == 'big pores':
      if skinCharacteristicsGiven[counter] == 'greasy':
        oilySkinCharacteristicsNotGiven.remove("greasy")
      elif skinCharacteristicsGiven[counter] == 'prone to breakouts':
        oilySkinCharacteristicsNotGiven.remove("prone to breakouts")
      else:
        oilySkinCharacteristicsNotGiven.remove("big pores")

    elif skinCharacteristicsGiven[counter] == 'dry' or skinCharacteristicsGiven[counter] == 'uneven texture' or skinCharacteristicsGiven[counter] == 'tight':
      if skinCharacteristicsGiven[counter] == 'dry':
        oilySkinCharacteristicsNotGiven.remove("dry")
      elif skinCharacteristicsGiven[counter] == 'uneven texture':
        oilySkinCharacteristicsNotGiven.remove("uneven texture")
      else:
        oilySkinCharacteristicsNotGiven.remove("tight")
    counter += 1
  counter = 0
  speech = "Do you experience any of these characteristics which "
  if len(normalSkinCharacteristicsNotGiven) < 3:
    if len(normalSkinCharacteristicsNotGiven) == 2:
      speech = speech + "are "
      while counter < len(normalSkinCharacteristicsNotGiven):
        speech =  speech + normalSkinCharacteristicsNotGiven[counter] + ", "
        counter += 1
    else:
      speech = speech + "is "
      while counter < len(normalSkinCharacteristicsNotGiven):
        speech =  speech + normalSkinCharacteristicsNotGiven[counter] + ", "
        counter += 1
    skinType = 'Normal Skin'

  elif len(oilySkinCharacteristicsNotGiven) < 3:
    if len(oilySkinCharacteristicsNotGiven) == 2:
      speech = speech + "are "
      while counter < len(oilySkinCharacteristicsNotGiven):
        speech =  speech + oilySkinCharacteristicsNotGiven[counter] + ", "
        counter += 1
    else:
      speech = speech + "is "
      while counter < len(oilySkinCharacteristicsNotGiven):
        speech =  speech + oilySkinCharacteristicsNotGiven[counter] + ", "
        counter += 1
    skinType = 'Oily Skin'

  elif len(drySkinCharacteristicsNotGiven) < 3:
    if len(drySkinCharacteristicsNotGiven) == 2:
      speech = speech + "are "
      while counter < len(drySkinCharacteristicsNotGiven):
        speech =  speech + drySkinCharacteristicsNotGiven[counter] + ", "
        counter += 1
    else:
      speech = speech + "is "
      while counter < len(drySkinCharacteristicsNotGiven):
        speech =  speech + drySkinCharacteristicsNotGiven[counter] + ", "
        counter += 1
    skinType = 'Dry Skin'
  return jsonify(
    {"fulfillmentText": speech}
  )

def determineSkinType():
  return jsonify({"fulfillmentText": "Based on the information you provided, I can ensure that your skin type is " + skinType + ". Would you need any other helps? "})

def findProductDetails(req):
  speech = ""

  cur = mysql.connection.cursor()
  cur.execute('''SELECT * FROM skin_product''')
  skin_product_details = cur.fetchall()

  skinProductName = req.get("queryResult").get("parameters", None).get("product")
  counter1 = 0

  while counter1 < len(skinProductName):
    counter = 0
    while counter < len(skin_product_details):
      if skinProductName[counter1] == skin_product_details[counter]['product_category']:
        speech = speech + "For " + skinProductName[counter1] + ", the product(s) that available is/are " + skin_product_details[counter]['product_name'] + ". Its price is RM " + str(skin_product_details[counter]['product_price']) + ' and its is mainly for ' + skin_product_details[counter]['for_skin_type'] + ' type with ' + skin_product_details[counter]['for_skin_problem'] + ' skin problem. '
      counter += 1

    if speech == "":
      speech = speech + "Sorry, for " + skinProductName[counter1] + ", none of the product(s) that is/are available. " 
    counter1 += 1
  speech = speech + "Would you need any others helps?"
  return jsonify({"fulfillmentText": speech})

def skinProblemProducts(req):
  speech = ""
  # My Sql query
  
  cur = mysql.connection.cursor()
  cur.execute('''SELECT * FROM skin_product''')
  skin_product_details = cur.fetchall()
  # Json Response from Dialogflow
  skinProblemName = req.get("queryResult").get("parameters", None).get("skin-problem")
  skin_type = req.get("queryResult").get("parameters", None).get("skin-type")
  counter = 0
  
  while counter < len(skin_product_details):
    counter1 = 0
    while counter1 < len(skinProblemName):
      if skinProblemName[counter1] == skin_product_details[counter]['for_skin_problem']:
        speech = speech + "For your " + skinProblemName[counter1] + " problem, I would recommend you the " + skin_product_details[counter]['product_name'] + ".\n" 
      counter1 += 1
    counter += 1
  speech = speech + " Would you like to know more about both products?"
  return jsonify({"fulfillmentText": speech})


def getSkinProblemName(req):
  # Json Response from Dialogflow
  skinProblemName = req.get("queryResult").get("parameters", None).get("skin-problem")
  return skinProblemName

def skinProblemProductDetails(skinProblemName):
  speech = ""
  cur = mysql.connection.cursor()
  cur.execute('''SELECT * FROM skin_product''')
  skin_product_details = cur.fetchall()

  counter = 0
  
  while counter < len(skin_product_details):
    counter1 = 0
    while counter1 < len(skinProblemName):
      if skinProblemName[counter1] == skin_product_details[counter]['for_skin_problem']:
        speech = speech + "For " + skin_product_details[counter]['product_name'] + ", " + skin_product_details[counter]['product_details'] + "."
      counter1 += 1
    counter += 1
  speech = speech + " Would you like to make an appointment with our doctor to have further consultation?"
  return jsonify({"fulfillmentText": speech})


def makeAppointment(req):
  cur = mysql.connection.cursor()
  cur.execute('''SELECT * FROM appointment_table''')
  appointment_Details = cur.fetchall()

  appointmentDateTime = req.get("queryResult").get("parameters", None).get("appointment-date-time")
  appointmentDate = appointmentDateTime["date_time"][0:10]
  appointmentTime = appointmentDateTime["date_time"][11:16]

  global appointment_date, appointment_time

  appointment_date = appointmentDate
  appointment_time = appointmentDateTime["date_time"][11:19]

  return jsonify(
        {"fulfillmentText": "Confirm to make appointment on " + appointmentDate + " at " + appointmentTime + " ?"}
      )

# Insert appointment made by customer into sql server
def confirmAppointmentDateTime():
  # generate random string
  appointment_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 7))

  # SQL cursor for query purpose
  cur = mysql.connection.cursor()
  my_sql_insert_query = """INSERT INTO appointment_table VALUES (%s, %s, %s, %s)"""
  global appointment_date, appointment_time
  appointment_date_time = appointment_date + " " + appointment_time
  values = (appointment_id, datetime.datetime.strptime(appointment_date_time, '%Y-%m-%d %H:%M:%S') , 'consultation', 'Lee')
  cur.execute(my_sql_insert_query, values)
  mysql.connection.commit()

  return jsonify(
    {"fulfillmentText": "Done! Your appointment id is " + appointment_id + ". Be remember to come on " + appointment_date + " at " + appointment_time + ". Would you need any other help?"}
  )

# find customer appointment with appointment id given by customer
def findMyAppointment(req):
  appointment_id_given = req.get("queryResult").get("parameters", None).get("appointment-id")
  cur = mysql.connection.cursor()
  cur.execute('''SELECT * FROM appointment_table''')
  appointment_Details = cur.fetchall()

  counter = 0
  while counter < len(appointment_Details):
    if appointment_id_given == appointment_Details[counter]['appointment_id']:
      return jsonify(
        {"fulfillmentText": "Your appointment with id of " + appointment_id_given + " is on " + appointment_Details[counter]['appointment_date'].strftime("%Y-%m-%d") + " at " + appointment_Details[counter]['appointment_date'].strftime("%H:%M") + " with doctor " + appointment_Details[counter]['appointment_doctor'] + ". Would you need another help?"}
      )
    counter += 1
  return jsonify({
    "fulfillmentText": "Sorry, no appointment found with this id " + appointment_id_given + ". Would you need another help?"
  })

  
# run the app
if __name__ == "__main__":
  port = int(os.getenv('PORT', 5000))
  print("Starting app on port %d" %(port))
  app.run(debug=True, port=port, host='127.0.0.1')
