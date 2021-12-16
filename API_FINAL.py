from typing import Text
from fastapi import FastAPI, Request
import uvicorn
import sqlite3
import requests

app = FastAPI()

@app.post("/create_company_account")
async def create_company_account(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    if not ("Company_id" in values_dict) \
            or not ("company_name" in values_dict) \
            or not ("bank_account" in values_dict)\
            or not ("city" in values_dict)\
            or not ("zip_code" in values_dict)\
            or not ("street_name" in values_dict)\
            or not ("box_number" in values_dict):
        return {"Error, Please complete the fields"}
    
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
    dbase = sqlite3.connect('digit.db', isolation_level=None)
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
        dbase.close()
        return True
    else :
        return "error"

@app.post("/create_quote")
async def editQuote(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    dbase.execute('''
            INSERT INTO Quote(
            Customer_id, Company_id, Activation_status, Total_price)
            VALUES(
            "{Customer}",
            "{Company}",
            "{Status}",
            "{Total}")    
         '''.format(
          Customer = str(values_dict['Customer_id']),
          Company=str(values_dict['Company_id']),
          Status = str(values_dict['Activation_status']),
          Total=str(values_dict['Total_price'])))
    dbase.close()
    return True
   
   
@app.post("/create_subscription")
async def editQuote(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    dbase.execute('''
        INSERT INTO Subscription(Activation_status)
        VALUES(
            "{Status}")    
        '''.format(
          Status = str(values_dict['Activation_status'])))
    dbase.close()
    return True
    

@app.post("/create-quote-line-item")
async def createQuoteLineItem(payload: Request):
    values_dict = await payload.json()

    # Open the DB
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    # Step 1: 

    # check that the correct data is sent
    # i.e. a subscription, a quantity, a price and a currency
    if not ("quantity" in values_dict)\
       or not ("price" in values_dict)\
       or not ("Currency" in values_dict)\
       or not ("quote_id" in values_dict):

        return {"Error, Please complete the fields"}

    # make a db call to insert the quote into the quotes table
    VATPrice = float(values_dict["price"])* 1.21 #multiplier par la quantité si prix par unité
    #fonction currency?? plus tard
    dbase.execute(''' 
            INSERT INTO Quote_lines(Quantity, Price, Currency, Quote_id)
            VALUES(?,?,?,?) ''', (values_dict["quantity"], VATPrice,values_dict["Currency"], values_dict["quote_id"]))
    
    dbase.close()
    return True

@app.post("/update_quote")
async def UpdateQuote(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)

    url = "https://v6.exchangerate-api.com/v6/1d87a25927f327d52c8b48ff/latest/USD"

    response = requests.get(url)
    json_data = response.json()
    conv_rate = json_data.get("conversion_rates").get("EUR")
    price_request = dbase.execute(''' SELECT Price FROM Quote_lines WHERE Quote_id={quote_id} '''
    .format(quote_id = str(values_dict["quote_id"])))
    price_results=price_request.fetchall()
    currency_request=dbase.execute(''' SELECT Currency FROM Quote_lines WHERE Quote_id={quote_id} '''
    .format(quote_id = str(values_dict["quote_id"])))
    currency_results=currency_request.fetchall()
    quantity_request=dbase.execute('''SELECT Quantity FROM Quote_lines WHERE Quote_id={quote_id} '''
    .format(quote_id = str(values_dict["quote_id"])))
    quantity_result=quantity_request.fetchall()
    total_price=0
    for id in range(len(price_results)):
        my_val=str(currency_results[id-1][0])
        if (my_val != "EUR"):
            price_adj = price_results[id-1][0]*conv_rate
        else: 
            price_adj = price_results[id-1][0]
        total_price+=price_adj*quantity_result[id-1][0]
    dbase.execute('''
        UPDATE Quote
        SET Total_price = ?
        WHERE Quote_id = ? 
        ''', (str(total_price), values_dict["quote_id"]))
    dbase.close()
    return True

#creationOFquoteForClient
@app.get("/check_quote")
async def quoteChecking(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    quote = dbase.execute('''SELECT Total_price 
    FROM Quote WHERE Customer_id= {custom} '''.format(custom=values_dict['customer_id']))
    quote_return=quote.fetchone()
    dbase.close()
    return {'The total price is:',quote_return}

@app.post("/change-quote-status")
async def changeSubscriptionStatus(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    query_quote = dbase.execute('''SELECT Quote_id 
    FROM Quote
    WHERE Customer_id = {custom_id} '''.format(custom_id=str(values_dict['Custom_id'])))
    Quote_result=query_quote
    dbase.execute('''
    UPDATE  Quote 
    SET Activation_status = 1
    WHERE Quote_id = {Quote_id} '''.format(Quote_id=str(values_dict['Quote_id'])))
    dbase.close()
    return True

@app.post("/create_invoice")
async def create_invoice (payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None) 
    if not ("quote_id" in values_dict) \
            or not ("payment_status" in values_dict) \
            or not ("month" in values_dict) \
            or not ("year" in values_dict)\
            or not ("customer_id" in values_dict):
        return "Error: an error occured. Please try again."


    url = "https://v6.exchangerate-api.com/v6/1d87a25927f327d52c8b48ff/latest/USD"

    response = requests.get(url)
    json_data = response.json()
    conv_rate = json_data.get("conversion_rates").get("EUR")
    price_request = dbase.execute(''' SELECT Price FROM Quote_lines WHERE Quote_id={quote_id} '''
    .format(quote_id = str(values_dict["quote_id"])))
    price_results=price_request.fetchall()
    currency_request=dbase.execute(''' SELECT Currency FROM Quote_lines WHERE Quote_id={quote_id} '''
    .format(quote_id = str(values_dict["quote_id"])))
    currency_results=currency_request.fetchall()
    quantity_request=dbase.execute('''SELECT Quantity FROM Quote_lines WHERE Quote_id={quote_id} '''
    .format(quote_id = str(values_dict["quote_id"])))
    quantity_result=quantity_request.fetchall()
    total_price=0
    for id in range(len(price_results)):
        my_val=str(currency_results[id-1][0])
        if (my_val != "EUR"):
            price_adj = price_results[id-1][0]*conv_rate
        else: 
            price_adj = price_results[id-1][0]
        total_price+=price_adj*quantity_result[id-1][0]

    dbase.execute('''
            INSERT INTO Invoice(Quotation_id, Price, Payment_status, Month, Year, Credit_card_validated) 
          VALUES ("{Quote}", "{Price}", "{Status}", "{Month}", "{Year}","{Credit_card_validated}")             
            '''.format(Quote=str(values_dict['quote_id']), Price=total_price, Status=values_dict['payment_status'] , Month = values_dict['month'], Year = values_dict['year'],Credit_card_validated = values_dict['Credit_card_validated']))
    dbase.close()
    return 'invoice_created'

@app.get("/get_quote_number")
async def Reference_Number(payload : Request):   
    value_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level = None)
    query_quote_number = dbase.execute('''
        SELECT Quote_id
        FROM Quote
        WHERE Customer_id ={Customer_id}'''.format(Customer_id = value_dict['Customer_id']))
    Quote_results = query_quote_number.fetchone()
    dbase.close()
    return {'Your quote number is:',Quote_results}

@app.get("/get-pending-invoices")
async def getPendingInvoices(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    dbase = sqlite3.connect('digit.db', isolation_level=None)
    query = dbase.execute('''SELECT * from Invoice WHERE Quotation_id = ?''', values_dict['Quotation_id'])
    result = query.fetchall()
    dbase.close()
    return result


#PAYMENT

@app.post("/credit_card_number_validation")
async def credit_card_number_validation(payload: Request):
    values_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level=None)
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
        dbase.execute('''
        UPDATE Invoice SET Credit_card_validated = 1 
        WHERE Quotation_id ="{quotation}" AND Month="{Month}"'''.format(quotation=values_dict['quote_id'], Month=values_dict['month']))
        return 'Credit card valid'
    else:
        'Error : Credit card not valid'

@app.post("/ref_num_validation")
async def reference_number_validation(payload : Request):   
    value_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level = None)
    query_session = dbase.execute('''
                SELECT Reference_number
                FROM Invoice 
                WHERE Quotation_id = "{quotation}" 
                AND Month = "{month}"
                AND Credit_card_validated = 1'''.format(quotation=value_dict['quote_id'],month=value_dict['month']))
    refnum = query_session.fetchone()[0]
    print(refnum)
    if refnum != int(value_dict['reference_number']):
            print(refnum)
            return 'error'
    else :
            status = dbase.execute('''
                UPDATE invoice
                SET Payment_status = 1
                WHERE reference_number = "{reference_number}" 
                AND Month = "{month}" 
                AND Credit_card_validated = 1'''.format(reference_number=value_dict['reference_number'],month=value_dict['month']))

            dbase.close
            return 'Payment accepted'
   
            
@app.get("/MRR")
async def MRR(payload : Request):   
    value_dict = await payload.json()
    dbase = sqlite3.connect('digit.db', isolation_level = None)
    query = ('''SELECT SUM(price)
                FROM invoice
                GROUP BY month
                WHERE activation_status = 1
                WHERE companies_id = ''' + 'VAT_id')

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=6000)
