rom fastapi import FastAPI, Request
import uvicorn
import sqlite3


app = FastAPI()

@app.post("/create_company_account")
async def create_company_account(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('M3_database.db', isolation_level=None)
    query = dbase.execute('''SELECT * FROM companies 
    WHERE VAT_id = ?'''.format(str(values_dict['VAT_id'])))
    query_VAT = query.fetchall[0]
    if len(query_VAT) == 0:
        dbase.execute('''
        INSERT INTO companies(VAT_id, company_name, bank_account, city, zip_code, street_name, box_number)
        VALUES (?,?,?,?,?,?,?) '''.format(values_dict["VAT_id"],values_dict["company_name"],values_dict["bank_account"],values_dict["city"],values_dict["zip_code"],values_dict["street_name"],values_dict["box_number"]))
        return "New company inserted"
    else : 
        return "Error your company is already in our database"

@app.post("/create_customer_account")
async def create_customer_account(payload: Request):
    values_dict = await payload.json()
    #open DB 
    dbase = sqlite3.connect('M3_database.db', isolation_level=None)
    # Retrieve customer on email address
    query_customers = dbase.execute(''' 
                    SELECT ID FROM Customers
                    WHERE customer_id = {customer_id}               
                    '''.format(customer_id=str(values_dict['customer_id'])))
  # We then store the results of the query with fetchall.
    customers_results = query_customers.fetchall()
  # Check condition: no customer found
    if len(customers_results) == 0:
  # Create new customer
        dbase.execute('''
        INSERT INTO Customers(
        customer_id, family_name, first_name, bank_account)
        VALUES(
            {customer_id},
            {family_name},
            {first_name},
            {bank_account},    
        '''.format(
          customer_id = str(values_dict['customer_id']),
          family_name = str(values_dict['family_name']),
          first_name=str(values_dict['first_name']),
          bank_account=str(values_dict['bank_account'])))
        return True
    else:
        return "error"

@app.post("/create-quote")
async def createQuote(payload: Request):
    values_dict = await payload.json()

    # Open the DB
    dbase = sqlite3.connect('M3_database.db', isolation_level=None)
    # Step 1: 

    # check that the correct data is sent
    # i.e. a subscription, a quantity, a price and a currency
    if not ("subID" in values_dict) \
            or not ("quantity" in values_dict) \
            or not ("price" in values_dict)\
            or not ("currency" in values_dict):
        return {"Error, Please complete the fields"}

    if type(values_dict["subID"]) is not int \
        or type(values_dict["quantity"]) is not int \
        or type(values_dict["price"]) is not float \
        or type(values_dict["currency"]) is not str :
         return {"Error, Please try again"}

    # make a db call to insert the quote into the quotes table
    VATPrice = values_dict["price"] + values_dict["price"] * 21 / 100
    dbase.execute(''' 
            INSERT INTO quote(sub_id, quantity, price, currency)
            VALUES(?,?,?,?) ''', (values_dict["subID"], values_dict["quantity"], VATPrice, values_dict["currency"]))
    dbase.close()
    return "Quote correcty inserted to Company {} with quantity {} and VAT price {} {}".format(values_dict["subID"],values_dict["quantity"],VATPrice,values_dict['currency']) 
    

@app.post("/change-subscription-status")
async def changeSubscriptionStatus(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    dbase = sqlite3.connect('M3_database.db', isolation_level=None)
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
    query = dbase.execute('''SELECT * from subscription WHERE companies_id=? AND custom_id=?;''', (values_dict["companies_ID"], values_dict["custom_ID"]))
    res = query.fetchone()
    if not res :
        dbase.execute(''' 
        INSERT INTO subscription(companies_id, custom_id, activation_status)
        VALUES(?,?,?)
        ''', (values_dict["companies_id"], values_dict["custom_id"], values_dict["activation_status"]))
    else :
        dbase.execute('''
        UPDATE subscription
        SET activation_status = ?
        WHERE companies_id = ? AND custom_id = ?
        ''', (values_dict["activationStatus"], values_dict["companyID"], values_dict["customerID"]))
        dbase.close()
        return True
   


@app.get("/get-pending-invoices")
async def getPendingInvoices(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    dbase = sqlite3.connect('M3_database.db', isolation_level=None)
    query = dbase.execute('''SELECT * from invoice WHERE customer_id = ?;''', values_dict['custom_id'])
    res = query.fetchall()
    dbase.close()
    return res

