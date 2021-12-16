import sqlite3
from typing import Text
from fastapi import FastAPI, Request
import uvicorn
import requests

app = FastAPI()

dbase = sqlite3.connect('digit.db', isolation_level=None)
print('Database opened')

dbase.execute('''DROP TABLE IF EXISTS Customers''')
dbase.execute('''DROP TABLE IF EXISTS Companies''')
dbase.execute('''DROP TABLE IF EXISTS Quote''')
dbase.execute('''DROP TABLE IF EXISTS Quote_lines''')
dbase.execute('''DROP TABLE IF EXISTS Invoice''')
dbase.execute('''DROP TABLE IF EXISTS Subscription''')

dbase.execute(''' 
            CREATE TABLE IF NOT EXISTS Customers(
            User_name INTEGER PRIMARY KEY,
            Family_name TEXT NOT NULL,
            First_name TEXT NOT NULL,
            Bank_account INTEGER NOT NULL) 
            ''')

dbase.execute(''' 
        CREATE TABLE IF NOT EXISTS Companies(
            VAT_id INTEGER PRIMARY KEY NOT NULL,
            Company_name TEXT NOT NULL,
            Bank_account INT NOT NULL,
            City TEXT NOT NULL,
            Zip_code INTEGER NOT NULL,
            Street_name TEXT NOT NULL,
            Box_number INTEGER NOT NULL) 
            ''')

dbase.execute(''' 
        CREATE TABLE IF NOT EXISTS Invoice(
            Reference_number INTEGER PRIMARY KEY AUTOINCREMENT,
            Price INT NOT NULL,
            Payment_status BOOL NOT NULL,
            Month TEXT NOT NULL,
            Year INT NOT NULL,
            Credit_card_validated BOOL NOT NULL,
            Quotation_id INTEGER NOT NULL,
            FOREIGN KEY (Quotation_id) REFERENCES Quote(Quote_id))
            ''')


dbase.execute (''' 
        CREATE TABLE IF NOT EXISTS Subscription(
            Subscription_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            Activation_status BOOL NOT NULL)
            ''')

dbase.execute (''' 
        CREATE TABLE IF NOT EXISTS Quote(
            Quote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Total_price INT NOT NULL,
            Customer_id INT NOT NULL,
            Company_id INT NOT NULL,
            Activation_status BOOL,
            FOREIGN KEY (Customer_id) REFERENCES Customers(User_name),
            FOREIGN KEY (Company_id) REFERENCES Companies(VAT_id))
            ''')

dbase.execute (''' 
        CREATE TABLE IF NOT EXISTS Quote_lines(
            Quote_lines_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Currency TEXT NOT NULL,
            Quantity INTEGER NOT NULL,
            Price FLOAT NOT NULL,
            Quote_id INT NOT NULL,
            FOREIGN KEY (Quote_id) REFERENCES Quote(Quote_id))
            ''')

dbase.close()
print("databse closed")



@app.get("/Customers_Number")
async def Customers_Number(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    customers_number_query = dbase.execute('''
        SELECT count(*)
        FROM Quote
        WHERE Company_id = "{Company_id}" AND Activation_status = 1 '''.format(str(Company_id = values_dict['Company_id'])))
    number_of_customers = customers_number_query.fetchall()
    return number_of_customers

@app.get("/Customers_and_Current_Subscriptions")
async def Customers_and_Current_Subscriptions(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    customers_and_current_subscriptions_query = dbase.execute('''
        SELECT Customer_id, Quantity, Price 
        FROM Quote
        INNER JOIN quote_lines ON Quote_lines.Quote_id = Quote.Quote_id
        WHERE Company_id = ? AND Activation_status = 1'''.format(str(Company_id = values_dict['Company_id'])))
    customers_and_current_subscriptions = customers_and_current_subscriptions_query.fetchall()
    return customers_and_current_subscriptions

@app.get("/Monthly_Recurring_Revenue")
async def Monthly_Recurring_Revenue(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    monthly_recurring_revenue_query = dbase.execute('''
        SELECT SUM(Price)
        FROM Invoice
        GROUP BY Year, Month
        INNER JOIN Quote ON Quote.Quote_id = Invoice.Quotation_id
        WHERE Company_id = ? AND Activation_status = 1'''.format(str(Company_id = values_dict['Company_id'])))
    monthly_recurring_revenue = monthly_recurring_revenue_query.fetchall()
    return monthly_recurring_revenue

@app.get("/Annual_Recurring_Revenue")
async def Annual_Recurring_Revenue(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    annual_recurring_revenue_query = dbase.execute('''
        SELECT SUM(Price)
        FROM Invoice
        Group BY Year
        INNER JOIN Quote ON Quote.Quote_id = Invoice.Quotation_id
        WHERE Company_id = ? AND Activation_status = 1'''.format(str(Company_id = values_dict['Company_id'])))
    annual_recurring_revenue = annual_recurring_revenue_query.fetchone()
    return annual_recurring_revenue

@app.get("/Average_Revenues_per_Customer")
async def session_grades(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    customers_number_query = dbase.execute('''
        SELECT count(*)
        FROM Subscription
        WHERE Company_id = ? AND Activation_status = 1 '''.format(str(companies_id = values_dict['Company_id'])))
    number_of_customers = customers_number_query.fetchone()
    annual_recurring_revenue_query = dbase.execute('''
        SELECT SUM(Price)
        FROM Invoice
        Group BY Year
        INNER JOIN Quote ON Quote.Quote_id = Invoice.Quotation_id
        WHERE Company_id = ?
        WHERE Activation_status = 1'''.format(str(Company_id = values_dict['Company_id'])))
    annual_recurring_revenue = annual_recurring_revenue_query.fetchone()
    average_revenues_per_customer = annual_recurring_revenue/number_of_customers
    return average_revenues_per_customer

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=6000)
    
    
    
    
    
####

GET http://127.0.0.1:6000//Customers_Number HTTP/1.1
Content-Type: application/json

{
    "Company_id": "1"

}

###

GET http://127.0.0.1:6000/Customers_and_Current_Subscriptions HTTP/1.1
Content-Type: application/json

{
    "Company’_id": "1"

}

###

GET http://127.0.0.1:6000/Monthly_Recurring_Revenue HTTP/1.1
Content-Type: application/json

{
    "Company_id": "1"

}

###

GET http://127.0.0.1:6000/Annual_Recurring_Revenue HTTP/1.1
Content-Type: application/json

{
    "Company_id": "1"

}

###

GET http://127.0.0.1:6000/Average_Revenues_per_Customer HTTP/1.1
Content-Type: application/json

{
    "Company_id": "1"

}