import sqlite3

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
            Reference_number INTEGER PRIMARY KEY AUTOINCREMENT,
            Payment_status BOOL,
            Month TEXT NOT NULL,
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
            Quote_id INTEGER PRIMARY KEY,
            Total_price INT NOT NULL,
            Customer_id INT NOT NULL,
            Company_id INT NOT NULL,
            Activation_status BOOL,
            FOREIGN KEY (Customer_id) REFERENCES Customers(User_name),
            FOREIGN KEY (Company_id) REFERENCES Companies(VAT_id))
            ''')

dbase.execute (''' 
        CREATE TABLE IF NOT EXISTS Quote_lines(
            Quote_lines_id INTEGER PRIMARY KEY,
            Subscription_id INTEGER NOT NULL,
            Currency TEXT NOT NULL,
            Quantity INTEGER NOT NULL,
            Price FLOAT NOT NULL,
            Quote_id INT NOT NULL,
            FOREIGN KEY (Subscription_id) REFERENCES Subscription(subscription_id),
            FOREIGN KEY (Quote_id) REFERENCES Quote(Quote_id))
            ''')
            
###########
from fastapi import FastAPI, Request
import uvicorn
import sqlite3

app = FastAPI()

@app.post("/create_company_account")
async def create_company_account(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    if not ("Company_id" in values_dict) \
            or not ("company_name" in values_dict) \
            or not ("bank_account" in values_dict)\
            or not ("city" in values_dict)\
            or not ("zip_code" in values_dict)\
            or not ("street_name" in values_dict)\
            or not ("box_number" in values_dict):
        return {"Error, Please complete the fields"}

  #  if type(values_dict["VAT_id"]) is not int \
   #     or type(values_dict["company_name"]) is not str \
   #     or type(values_dict["bank_account"]) is not int \
    #    or type(values_dict["city"]) is not str \
    #    or type(values_dict["zip_code"]) is not int \
     #   or type(values_dict["street_name"]) is not str \
     #   or type(values_dict["box_number"]) is not int :
     #    return {"Error, Please try again"}
    
    query_companies = dbase.execute(''' 
                    SELECT VAT_id FROM Companies
                    WHERE VAT_id = {Company_id}               
                    '''.format(Company_id=str(values_dict['Company_id'])))
  # We then store the results of the query with fetchall.
    companies_results = query_companies.fetchall()
  # Check condition: no customer found
    if len(companies_results) == 0:
  # Create new customer
        dbase.execute('''
        INSERT INTO Companies(VAT_id, Company_name, Bank_account, City, Zip_code, Street_name, Box_number)
        VALUES (
            "{Company_id}",
            "{Company_name}",
            "{Bank_account}",
            "{City}",
            "{Zip_code}",
            "{Street_name}",
            "{Box_number}")  
        '''.format(Company_id=str(values_dict["Company_id"]),
            Company_name=values_dict["company_name"],
            Bank_account=str(values_dict["bank_account"]),
            City=str(values_dict["city"]),
            Zip_code=str(values_dict["zip_code"]),
            Street_name=str(values_dict["street_name"]),
            Box_number=str(values_dict["box_number"])))
        dbase.close()
        return "New company inserted"
    else :
        return "error"
   

@app.post("/create_customer_account")
async def create_customer_account(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    if not ("User_name" in values_dict) \
            or not ("family_name" in values_dict) \
            or not ("first_name" in values_dict)\
            or not ("bank_account" in values_dict)\
            or not ("Companies_id" in values_dict):
        return {"Error, Please complete the fields"}

    query_customers = dbase.execute(''' 
                    SELECT User_name FROM Customers
                    WHERE User_name = {User_name}               
                    '''.format(User_name=str(values_dict['User_name'])))
  # We then store the results of the query with fetchall.
    customers_results = query_customers.fetchall()
  # Check condition: no customer found
    if len(customers_results) == 0:
  # Create new customer
        dbase.execute('''
        INSERT INTO Customers(
        User_name, Family_name, First_name, Bank_account)
        VALUES(
            "{customer_id}",
            "{family_name}",
            "{first_name}",
            "{bank_account}")    
        '''.format(
          customer_id = str(values_dict['User_name']),
          family_name = str(values_dict['family_name']),
          first_name=str(values_dict['first_name']),
          bank_account=str(values_dict['bank_account'])))
        return True
    else :
        return "error"

@app.post("/create_quote")
async def editQuote(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    dbase.execute('''
        INSERT INTO Quote(
        Quote_id, Customer_id, Company_id, Activation_status, Total_price, Currency)
        VALUES(
            "{Quote}",
            "{Customer}",
            "{Company}",
            "{Status}",
            "{Total}",
            "{Currency}")    
        '''.format(
          Quote = str(values_dict['Quote_id']),
          Customer = str(values_dict['Customer_id']),
          Company=str(values_dict['Company_id']),
          Status = str(values_dict['Activation_status']),
          Total=str(values_dict['Total_price']),
          Currency=str(values_dict['Currency'])))
    return True
    

@app.post("/create_subscription")
async def editQuote(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    dbase.execute('''
        INSERT INTO Subscription(
        Subscription_id, Activation_status)
        VALUES(
            "{Subscription}",
            "{Status}")    
        '''.format(
          Subscription = str(values_dict['Subscription_id']),
          Status = str(values_dict['Activation_status'])))
    return True

@app.post("/create-quote-line-item")
async def createQuoteLineItem(payload: Request):
    values_dict = await payload.json()

    # Open the DB
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    # Step 1: 

    # check that the correct data is sent
    # i.e. a subscription, a quantity, a price and a currency
    if not ("quote_lines_id" in values_dict) \
            or not ("quantity" in values_dict) \
            or not ("price" in values_dict)\
            or not ("subscription_id" in values_dict)\
            or not ("quote_id" in values_dict):

        return {"Error, Please complete the fields"}

  # if type(values_dict["subID"]) is not int \
    #    or type(values_dict["quantity"]) is not int \
    #    or type(values_dict["price"]) is not float \
     #   or type(values_dict["currency"]) is not str :
     #    return {"Error, Please try again"}

    # make a db call to insert the quote into the quotes table
    VATPrice = float(values_dict["price"])* 1.21 #multiplier par la quantité si prix par unité
    #fonction currency?? plus tard
    dbase.execute(''' 
            INSERT INTO Quote_lines(Quote_lines_id, Quantity, Price, Currency, Subscription_id, Quote_id)
            VALUES(?,?,?,?,?,?) ''', (values_dict["quote_lines_id"], values_dict["quantity"], VATPrice,values_dict["Currency"],values_dict["subscription_id"], values_dict["quote_id"]))
    
    dbase.close()
    return True

@app.post("/create_quote")
async def editQuote(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    total_price = dbase.execute('''SELECT SUM(price) 
    FROM quote_line_item JOIN subscription ON subscription.sub_id = quote_line_item.sub_id
    WHERE customer_id = {} '''.format(str(values_dict['customer_id'])))
    dbase.execute('''INSERT INTO quote(total_price,currency, custom_id)
    VALUES(?) '''.format(str(total_price, values_dict['currency'], values_dict['customer_id'])))
    return "Quote inserted"

#creationOFquoteForClient
@app.get("/check_quote")
async def quoteChecking(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    quote = dbase.execute('''SELECT * 
    FROM quote WHERE customer_id= {} ''',(values_dict['customer_id']))
    return quote

@app.post("/change-subscription-status")
async def changeSubscriptionStatus(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    # Step 1: 
   
    # check that the correct data is sent
    # i.e. a company id, a customer id, and an activation status price 
    if not ("companies_ID" in values_dict) \
            or not ("custom_ID" in values_dict) \
            or not ("activation_status" in values_dict):
        return "Error: an error occured. Please try again."

    if type(values_dict["companies_ID"]) is not int \
        or type(values_dict["custom_ID"]) is not int \
        or type(values_dict["activation_status"]) is not int :
        return "Error: an error occured. Please try again."

    # make a db call to insert the subscription into the subscription table
    # check if a subscription exists for the given customer and company ids
    query = dbase.execute('''SELECT * from Subscription 
    WHERE companies_id=? AND custom_id=?;''', 
    (values_dict["companies_ID"], values_dict["custom_ID"]))
    res = query.fetchone()
    if not res :
        dbase.execute(''' 
        INSERT INTO subscription(companies_id, custom_id, activation_status)
        VALUES(?,?,?)
        ''', (values_dict['companies_id'], values_dict["custom_id"], values_dict["activation_status"]))
    else :
        dbase.execute('''
        UPDATE subscription
        SET activation_status = ?
        WHERE companies_id = ? AND custom_id = ?
        ''', (1, values_dict["companyID"], values_dict["customerID"]))
        dbase.close()
        return True
   

@app.post("/create_invoice")
async def create_invoice (payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None) 
    if not ("companies_id" in values_dict) \
            or not ("quote_id" in values_dict) \
            or not ("customer_id" in values_dict) \
            or not ("payment_status" in values_dict):
        return "Error: an error occured. Please try again."

    if type(values_dict["companies_id"]) is not int \
        or type(values_dict["quote_id"]) is not int \
        or type(values_dict["customer_id"]) is not int \
        or type(values_dict["payment_status"]) is not bool :

        return "Error: an error occured. Please try again."

   #ajouter custom_id dans quote (=relation one to many de custom vers quote dans la dbase)
    query_price= dbase.execute(''' 
                    SELECT total_price FROM quote
                    WHERE customer_id = {}               
                    '''.format(str(values_dict['customer_id'])))
    price_invoice = query_price.fetchall()[0][0]
    #ajouter quote_id dans invoice (=relation one to many de custom vers quote)
    dbase.execute('''
            INSERT INTO invoice(quote_id, payment_status, month) 
            VALUES ({Quote}, {Status}, {Month})             
            '''.format(Quote=str(values_dict['quote_id']), Status=values_dict['payment_status'] , Month = values_dict['month']))
    return 'invoice_created'

@app.get("/get-pending-invoices")
async def getPendingInvoices(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    query = dbase.execute('''SELECT * from invoice WHERE customer_id = ?;''', values_dict['custom_id'])
    res = query.fetchall()
    dbase.close()
    return res


#PAYMENT

@app.post("/payment_validation")
async def credit_card_number_validation(payload: Request):
    values_dict = await payload.json()
    credit_card_number = values_dict['credit_card_number']
    a = len(credit_card_number)
    def digit(n):
        return [int(d) for d in str(n)]
    cardlist = (digit(credit_card_number))  
    checking_digit = cardlist[a-1]        
    del cardlist[a-1]
    print(cardlist, checking_digit)
    def reverse(n):
        idx = a-2
        newlist = []
        while idx >= 0:
            newlist.append(n[idx])
            idx = idx - 1
        return newlist

    new_list = reverse(cardlist)
    print(new_list)

    def odd_function(n):
        index = 0
        while index < a-1:
            if index % 2 == 0:  
                n[index] = n[index]*2
                if n[index] > 9 :
                    n[index] = n[index] - 9
            index = index + 1
        return(n)

    odd_list = odd_function(new_list)
    print(odd_list)

    total = 0
    ind = 0
    while ind < a-1:
        total = total + odd_list[ind]
        ind = ind + 1
    print(total)
    print(checking_digit)
    Total_amount = total + checking_digit
    print(Total_amount)
    if Total_amount % 10 == 0:
        return 'Credit card valid'
    async def reference_number_validation(payload : Request):   
            value_dict = await payload.json()
            dbase = sqlite3.connect('digit_project.db', isolation_level = None)

            query_session = dbase.execute('''
                    SELECT reference_number
                    FROM invoice 
                    WHERE customer_id = {}'''.format(str(value_dict['customer_id'])))
            refnum = query_session.fetchone
            if refnum != value_dict['reference_number']:
                return 'error'
            else :
                status = dbase.execute('''
                UPDATE invoice
                SET status = 1
                WHERE reference_number = {reference_number} 
                '''.format(reference_number = value_dict['reference_number']))
                dbase.close
                return 'Payment accepted'
    return 'Error : Payment not accepted'
            
@app.get("/MRR")
async def MRR(payload : Request):   
    value_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level = None)
    query = ('''SELECT SUM(price)
                FROM invoice
                GROUP BY month
                WHERE activation_status = 1
                WHERE companies_id = ''' + 'VAT_id')

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=6000)
