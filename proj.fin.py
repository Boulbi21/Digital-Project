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

@app.post("/credi_card_number_validation")
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
    else:
        'Error : Credit card not valid'

@app.post("/reference_number_validation")
async def reference_number_validation(payload : Request):   
    value_dict = await payload.json()
    dbase = sqlite3.connect('M3_database.db', isolation_level = None)

    query_session = dbase.execute('''
                    SELECT reference_number
                    FROM invoice 
                    WHERE subscription_id = {}'''.format(str(value_dict['subscription_id'])))
    refnum = query_session.fetchone
    if refnum != value_dict['reference_number']:
        return 'error'
    status = dbase.execute('''
            UPDATE invoice
            SET status = 1
            WHERE reference_number = {reference_number} 
            '''.format(reference_number = value_dict['reference_number']))
    dbase.close
    return "Reference number {reference_number} is correct".format(reference_number = value_dict['reference_number'])

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=4000)
