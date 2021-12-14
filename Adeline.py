from fastapi import FastAPI, Request
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
    else :
        return "error"

@app.post("/create-quote-line-item")
async def createQuoteLineItem(payload: Request):
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
            INSERT INTO quote_line_item(sub_id, quantity, price, currency)
            VALUES(?,?,?,?) ''', (values_dict["subID"], values_dict["quantity"], VATPrice, values_dict["currency"]))
    dbase.close()
    return "Quote_item correcty inserted to Company {} with quantity {} and VAT price {} {}".format(values_dict["subID"],values_dict["quantity"],VATPrice,values_dict['currency']) 

#creationOFquoteForClient
@app.get("/create_quote")
async def quoteChecking(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('M3_database.db', isolation_level=None)
    quote_lines = dbase.execute('''SELECT * 
    FROM quote_line_item JOIN subscription ON subscription.sub_id = quote_line_item.sub_id
    WHERE customer_id = {} '''(values_dict['customer_id']))
    return quote_lines
