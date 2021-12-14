from fastapi import FastAPI, Request
import uvicorn
import sqlite3


app = FastAPI()

@app.post("/create_company_account")
async def create_company_account(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
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
    dbase = sqlite3.connect('digit_project.db', isolation_level=None)
    query_customers = dbase.execute(''' 
                    SELECT user_id FROM Customers
                    WHERE customer_id = {user_id}               
                    '''.format(customer_id=str(values_dict['user_id'])))
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
        custom_id = dbase.execute(''' SELECT Custom_id FROM Customers where custom_id = {}'''
        .format(values_dict['custom_id']))
        customer_id = custom_id[0]
        dbase.execute('''INSERT INTO Subscription(Companies_id, Customer_id, Activation_status)
        VALUES (?,?,?) '''.format(str(values_dict['Companies_id'], customer_id, 0))
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

@app.post("/create_quote")
async def editQuote(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('M3_database.db', isolation_level=None)
    total_price = dbase.execute('''SELECT SUM(price) 
    FROM quote_line_item JOIN subscription ON subscription.sub_id = quote_line_item.sub_id
    WHERE customer_id = {} '''.format(str(values_dict['customer_id'])))
    dbase.execute('''INSERT INTO quote(total_price,currency, custom_id)
    VALUES(?) '''.format(str(total_price, values_dict['currency'], values_dict['customer_id'])
    return "Quote inserted"

#creationOFquoteForClient
@app.get("/check_quote")
async def quoteChecking(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('M3_database.db', isolation_level=None)
    quote = dbase.execute('''SELECT * 
    FROM quote WHERE customer_id= {} ''',(values_dict['customer_id']))
    return quote

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
    query = dbase.execute('''SELECT * from subscription 
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
    dbase = sqlite3.connect('M3_database.db', isolation_level=None) 
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
            '''.format(student=str(values_dict['quote_id']), 0, Month = values_dict['month']))
        return 'invoice_created'

@app.get("/get-pending-invoices")
async def getPendingInvoices(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    dbase = sqlite3.connect('M3_database.db', isolation_level=None)
    query = dbase.execute('''SELECT * from invoice WHERE customer_id = ?;''', values_dict['custom_id'])
    res = query.fetchall()
    dbase.close()
    return res


#PAYMENT

@app.post("/payment_validation")
async def credit_card_number_validation(payload: Request):
    values_dict = await payload.json()
    if : 
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
        elif:
            async def reference_number_validation(payload : Request):   
            value_dict = await payload.json()
            dbase = sqlite3.connect('M3_database.db', isolation_level = None)

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
        else :
            return 'Error : Payment not accepted'
            
@app.get("/MRR")
async def MRR(payload : Request):   
    value_dict = await payload.json()
    dbase = sqlite3.connect('M3_database.db', isolation_level = None)
    query = ('''SELECT SUM(price)
                FROM invoice
                GROUP BY month
                WHERE activation_status = 1
                WHERE companies_id = ''' + 'VAT_id')

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=4000)
