import sqlite3
from fastapi import FastAPI, Request
import uvicorn
import sqlite3

app = FastAPI()

dbase = sqlite3.connect('digit_project.db', isolation_level=None)
cursor = dbase.cursor()
print('Database opened')

dbase.execute('''DROP TABLE IF EXISTS Customers''')
dbase.execute('''DROP TABLE IF EXISTS Companies''')
dbase.execute('''DROP TABLE IF EXISTS Quote''')
dbase.execute('''DROP TABLE IF EXISTS Quote_lines''')
dbase.execute('''DROP TABLE IF EXISTS Invoice''')
dbase.execute('''DROP TABLE IF EXISTS Subscription''')

dbase.execute(''' 
            CREATE TABLE IF NOT EXISTS Customers(
            User_name INTEGER PRIMARY KEY AUTOINCREMENT,
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
            Reference_number INTEGER PRIMARY KEY NOT NULL AUTOINCREMENT,
            Payment_status BOOL,
            Month TEXT NOT NULL,
            Quotation_id INTEGER NOT NULL,
            FOREIGN KEY (Quotation_id) REFERENCES Quote(Quote_id))
            ''')


dbase.execute (''' 
        CREATE TABLE IF NOT EXISTS Subscription(
            Subscription_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            Companies_id INTEGER NOT NULL,
            Customer_id INTEGER NOT NULL,
            Activation_status BOOL NOT NULL,
            FOREIGN KEY (Companies_id) REFERENCES Companies(VAT_id),
            FOREIGN KEY (Customer_id) REFERENCES Customer(User_name))
            ''')

dbase.execute (''' 
        CREATE TABLE IF NOT EXISTS Quote(
            Quote_id INTEGER PRIMARY KEY,
            Currency TEXT NOT NULL,
            Customer_id INT NOT NULL,
            Total_price INT NOT NULL,
            FOREIGN KEY (Customer_id) REFERENCES Customers(User_name))
            ''')

dbase.execute (''' 
        CREATE TABLE IF NOT EXISTS Quote_lines(
            Quote_lines_id INTEGER PRIMARY KEY,
            Subscription_id INTEGER NOT NULL,
            Quantity INTEGER NOT NULL,
            Price FLOAT NOT NULL,
            Quote_id INT NOT NULL,
            FOREIGN KEY (Subscription_id) REFERENCES Subscription(subscription_id),
            FOREIGN KEY (Quote_id) REFERENCES Quote(Quote_id))
            ''')

@app.get("/Customers_Number")
async def session_grades(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    customers_number_query = dbase.execute('''
        SELECT count(*)
        FROM Subscription
        WHERE companies_id = ?
        WHERE Activation_status = ? '''.format(str(companies_id = values_dict['VAT_id'], Activation_status = 1))
    number_of_customers = customers_number_query.fetchone()
    return number_of_customers

@app.get("/Customers_and_Current_Subscriptions")
async def session_grades(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    customers_and_current_subscriptions_query = dbase.execute('''
        SELECT Quantity, Price, Customer_id, Subscription_id
        FROM Subscription
        INNER JOIN quote_lines ON Quote_lines.Subscription_id = Subscription.Subscription_id
        WHERE Companies_id = ?
        WHERE Activation_status = ?'''.format(str(Companies_id = values_dict['VAT_id'], Activation_status = 1)))
        #WHERE End Datum =< now
    customers_and_current_subscriptions = customers_and_current_subscriptions_query.fetchall()
    return customers_and_current_subscriptions

@app.get("Monthly_Recurring_Revenue")
async def session_grades(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    monthly_recurring_revenue_query = dbase.execute('''
        SELECT SUM(Total_price)
        FROM Invoice
        GROUP BY Month
        INNER JOIN Quote ON Quote.Quote_id = Invoice.Quotation_id
        INNER JOIN Quote ON Quote.Customer_id = Subscription.Customer_id
        WHERE Companies_id = ?
        WHERE Activation_status = ?''').format(str(Companies_id = values_dict['VAT_id']), Activation_status = 1)
    monthly_recurring_revenue = monthly_recurring_revenue_query.fetchall()
    return monthly_recurring_revenue

@app.get("Annual_Recurring_Revenue")
async def session_grades(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    annual_recurring_revenue_query = dbase.execute('''
    SELECT SUM(Total_price)
        FROM Invoice
        INNER JOIN Quote ON Quote.Quote_id = Invoice.Quotation_id
        INNER JOIN Quote ON Quote.Customer_id = Subscription.Customer_id
        WHERE Companies_id = ?
        WHERE Activation_status = ?''').format(str(Companies_id = values_dict['VAT_id']), Activation_status = 1)
    annual_recurring_revenue = mannual_recurring_revenue_query.fetchall()
    return annual_recurring_revenue)

@app.get("Average_Revenues_per_Customer")
async def session_grades(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    customers_number_query = dbase.execute('''
        SELECT count(*)
        FROM Subscription
        WHERE companies_id = ?
        WHERE Activation_status = ? '''.format(str(companies_id = values_dict['VAT_id'], Activation_status = 1))
    number_of_customers = customers_number_query.fetchone()
    annual_recurring_revenue_query = dbase.execute('''
    SELECT SUM(Total_price)
        FROM Invoice
        INNER JOIN Quote ON Quote.Quote_id = Invoice.Quotation_id
        INNER JOIN Quote ON Quote.Customer_id = Subscription.Customer_id
        WHERE Companies_id = ?
        WHERE Activation_status = ?''').format(str(Companies_id = values_dict['VAT_id']), Activation_status = 1)
    annual_recurring_revenue = mannual_recurring_revenue_query.fetchone()
    average_revenues_per_customer = annual_recurring_revenue/number_of_customers
    return average_revenues_per_customer


    

