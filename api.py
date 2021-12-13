import sqlite3
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

# Router
@app.get("/")
def root():
  return {"message": "It works !"}

#Company payload example
#{ 
#  "Name": "Meta",
#  "AddressCountry":"USA",
#  "AddressState": "LA",
#  "AddressCity": "sillicon valley",
# "AddressStreet": "Beautiful Street",
# "AddressNumber": "546",
# "AddressPostCode": "10200",
# "VATID": "2131231434123",
# "BankAccName" : "MetaCorp"
# "BankAccNumber": "1225345345345"
#}
@app.post("/create_company_account")
async def create_company_account(payload: Request):
  values_dict = await payload.json()
  #open DB 
  dbase = sqlite3.connect('group43.db', isolation_level=None)
  #Check if company exists,based on VAT (unique per company)
  query_companies = dbase.execute(''' 
                    SELECT ID FROM Companies
                    WHERE VATID = {VATID}               
                    '''.format(VATID=str(values_dict['VATID'])))
  # We then store the results of the query with fetchall.
  companies_results = query_companies.fetchall()
  # Verify condition: No company found with that VAT number
  if len(companies_results) == 0:
  # Create new company
      dbase.execute('''
        INSERT INTO Companies(
        Name,
        AddressCountry,
        AddressState,
        AddressCity,
        AddressStreet,
        AddressNumber,
        AddressPostCode,
        VATID, 
        BankAccName,
        BankAccNumber)
        VALUES({Name},
            {AddressCountry},
            {AddressState},
            {AddressCity},
            {AddressStreet},
            {AddressNumber},
            {AddressPostCode},
            {VATID},
            {BankAccName},
            {BankAccNumber})     
        '''.format(
          Name=str(values_dict['Name']),
          AddressCountry=str(values_dict['AddressCountry']),
          AddressState=str(values_dict['AddressState']),
          AddressCity=str(values_dict['AddressCity']),
          AddressStreet=str(values_dict['AddressStreet']),
          AddressNumber=str(values_dict['AddressNumber']),
          AddressPostCode=str(values_dict['AddressPostCode']),
          VATID=str(values_dict['VATID']), 
          BankAccName=str(values_dict['BankAccName']),
          BankAccNumber=str(values_dict['BankAccNumber])))
  #close DB 
  dbase.close()
  return True

#Customer payload example
#{ 
#  "CompanyID": "1",
#  "Name": "Bond",
#  "Surname":"James",
#  "Email":"james.bond@gmail.com",
#  "AddressCountry":"USA",
#  "AddressState": "Statexyz",
#  "AddressCity": "Cityxyz",
#  "AddressStreet": "Streetxyz",
#  "AddressNumber": "101",
#  "AddressPostCode": "1020",
#  "CCNumber": "2233 4455 6677 8899",
#}
@app.post("/create_customer_account")
async def create_customer_account(payload: Request):
  values_dict = await payload.json()
  #open DB 
  dbase = sqlite3.connect('group43.db', isolation_level=None)
  # Retrieve customer on email address
  query_customers = dbase.execute(''' 
                    SELECT ID FROM Customers
                    WHERE Email = {Email}               
                    '''.format(Email=str(values_dict['Email'])))
  # We then store the results of the query with fetchall.
  customers_results = query_customers.fetchall()
  # Check condition: no customer found
  if len(customers_results) == 0:
  # Create new customer
      dbase.execute('''
        INSERT INTO Customers(
        Name,
        Surname,
        Email,
        AddressCountry,
        AddressState,
        AddressCity,
        AddressStreet,
        AddressNumber,
        AddressPostCode, 
        CCNumber)
        VALUES(
            {Name},
            {Surname},
            {Email},
            {AddressCountry},
            {AddressState},
            {AddressCity},
            {AddressStreet},
            {AddressNumber},
            {AddressPostCode},
            {CCNumber})     
        '''.format(
          Name=str(values_dict['Name']),
          Surname=str(values_dict['Surname']),
          Email=str(values_dict['Email']),
          AddressCountry=str(values_dict['AddressCountry']),
          AddressState=str(values_dict['AddressState']),
          AddressCity=str(values_dict['AddressCity']),
          AddressStreet=str(values_dict['AddressStreet']),
          AddressNumber=str(values_dict['AddressNumber']),
          AddressPostCode=str(values_dict['AddressPostCode']),
          CCNumber=str(values_dict['CCNumber'])))
  # Create new customer account 
  query_customers = dbase.execute('''
                            SELECT ID FROM Customers
                            WHERE Email = {Email}
                            '''.format(Email=str(values_dict['Email'])))
  # Store ID with fetchall, found in row 0 col 0
  customerID = query_companies.fetchall()[0][0]
  dbase.execute('''
        INSERT INTO CustomerAccounts(
        CompanyID,
        CustomerID)
        VALUES(
            {CompanyID},
            {CustomerID})  
        '''.format(
          CompanyID=str(values_dict['CompanyID']),
          CustomerID=str(customerID)))
  #close DB 
  dbase.close()
  return True

#Quote payload example
#The function's name is "create_subscription" but it's still a quote at this point. It becomes a subscription when Active = 1, in the "convert_quote" section
#{ 
#  "CustomerAccountID": "1",
#  "ProductID":"1",
#  "Quantity": "2",
#  "StartDate": "01-01-2022",
#  "EndDate": "01-01-2023"
#}
@app.post("/create_subscription")
async def create_subscription(payload: Request):
  values_dict = await payload.json()
  #open DB
  dbase = sqlite3.connect('group43.db', isolation_level=None)
  #TotalPrice calculator 
  query_price = dbase.execute(''' 
                    SELECT priceLocal FROM Products
                    WHERE ProductID = {ProductID}               
                    '''.format(ProductID=str(values_dict['ProductID'])))
  PriceLocal = query_price.fetchall()[0][0]
  Quantity = values_dict['Quantity']
  TotalPriceLocalVATE = Quantity*PriceLocal
  TotalPriceLocalVATI = TotalPriceVATE*1,21
  #Create subscription
  dbase.execute('''
    INSERT INTO Subscriptions(
    CustomerAccountID,
    ProductID,
    Quantity, 
    TotalPriceLocalVATE,
    TotalPriceLocalVATI,
    StartDate,
    EndDate)
    VALUES(
        {CustomerAccountID},
        {ProductID},
        {Quantity},
        {TotalPriceLocalVATE},
        {TotalPriceLocalVATI},
        {StartDate},
        {EndDate})
        '''.format(
          CustomerAccountID=str(values_dict['CustomerAccountID']),
          ProductID=str(values_dict['ProductID']),
          Quantity=str(values_dict['Quantity']),
          TotalPriceLocalVATE=str(TotalPriceLocalVATE),
          TotalPriceLocalVATI=str(TotalPriceLocalVATI),
          StartDate=str(values_dict['StartDate']),
          EndDate=str(values_dict['EndDate'])))
  dbase.close()
  return True

#Review quote payload example
#We assume the customer knows the subscrptionID
#Acceptance = 2 -> refused
#Acceptance = 1 -> accepted
#Acceptance = 0 -> not reviewed yet
#{ 
#  "SubscriptionID":"1",
# "Acceptance":"1"
#}
@app.post("/review_quote")
async def review_quote(payload: Request):
  values_dict = await payload.json()
  #open DB
  dbase = sqlite3.connect('group43.db', isolation_level=None)
  
  dbase.execute(''' 
    UPDATE Subscription
    SET Acceptance = {Acceptance}
    WHERE SubscriptionID = {SubscriptionID}  
    '''.format(Acceptance = values_dict['Acceptance'], SubscriptionID = values_dict['SubscriptionID']))
  dbase.close()
  return True

#Convert quote payload example
#{ 
#  "CompanyID": "1"
#. "SubscriptionID": "5"
#}
@app.post("/convert_quote")
async def convert_quote(payload: Request):
  values_dict = await payload.json()
  #open DB
  dbase = sqlite3.connect('group43.db', isolation_level=None)                                         
  
  dbase.execute(''' 
      UPDATE Subscriptions
      SET Active = 1
      WHERE SubscriptionID = {SubscriptionID}  
      '''.format(SubscriptionID = values_dict["SubscriptionID"]))
  dbase.close()
  return True

#Create invoice payload example
#{ 
#  "CustomerAccountID": "1",
#  "InvoiceDate": "2022-01-31",
#  "CompanyID": "1"                                                       
#}
@app.post("/create_invoice")
async def create_invoice(payload: Request):
  values_dict = await payload.json()
  #open DB
  dbase = sqlite3.connect('group43.db', isolation_level=None)
  query_subscriptions = dbase.execute('''
                            SELECT TotalPriceLocalVATI FROM Subscriptions
                            WHERE Active = 1 AND CustomerAccountID = {CustomerAccountID} AND {InvoiceDate} BETWEEN StartDate AND EndDate
                            '''.format(CustomerAccountID=values_dict['CustomerAccountID']), InvoiceDate=str(values_dict['InvoiceDate'])))
  subscriptions_results = query_subscriptions.fetchall()
  
  TotalDueEuro = 0
  for subscription in subscriptions_results:
    TotalDueEuro += subscription[0]
  #We assumed DueDate to be 30 days after the invoice date
  dbase.execute('''
    INSERT INTO Invoices(
      InvoiceDate,
      DueDate,
      TotalDueEuro,
      CompanyID)
      VALUES(
        {InvoiceDate},
        DATE({InvoiceDate2},'+30 days'),
        {TotalDueEuro},
        CompanyID)
        '''.format(
          InvoiceDate=str(values_dict['InvoiceDate']),
          InvoiceDate2=str(values_dict['InvoiceDate']),
          TotalDueEuro=TotalDueEuro),
          CompanyID=str(values_dict['CompanyID'])))     
  dbase.close()     
  return True

#Check invoices payload example
#{ 
#  "CustomerAccountID": "1"
#}
@app.get("/check_invoices")
async def check_invoices(payload: Request):
  values_dict = await payload.json()

dbase.execute('group43', isolation_level=None)
query_invoices = dbase.execute('''
                            SELECT ID FROM Invoices
                            WHERE CustomerAccountID = {CustomerAccountID} AND Paid = 0
                            '''.format(CustomerAccountID=str(values_dict['CustomerAccountID'])))
  invoices_results = query_invoices_status.fetchall()
dbase.close()
# Encode results in JSON to send it back as response
return json.dumps(invoices_results)
#Customer payment payload example
#{ 
#  "InvoiceID": "1",
#  "CCNumber": "5888 8884 9562 7784"
#}
@app.post("/customer_payment")
async def customer_paymnent():
  values_dict = await payload.json()
  dbase.execute('group43', isolation_level=None)
  CCNumber = values_dict["CCNumber"]
  query_invoices = dbase.execute('''
                            SELECT ID FROM Invoices
                            WHERE InvoiceID = {InvoiceID} 
                            '''.format(InvoiceID=str(values_dict['InvoiceID'])))
  Invoices_results = query_invoices_status.fetchall()
  #Calculation here
  #validationNumber = 
  # There must be one single invoice with that ID and the validation number must be dividable by 10
  if len(Invoices_results) == 1 and validationNumber % 10 == 0:
    dbase.execute(''' 
      UPDATE Invoice
        SET Paid = 1
        WHERE InvoiceID = {InvoiceID}  
      '''.format(InvoiceID = values_dict['InvoiceID']))
   dbase.close() 
   return True

 #Retrieve statistics payload example
#{ 
# "CompanyID" : "1",
# "Month" : "12",
# "Year" : "2021"
#}
@app.post("/retrieve_statistics")
async def retrieve_statistics():
 values_dict = await payload.json()
 dbase.execute('group43', isolation_level=None)
 # Calculate MRR 
 query_statistics = dbase.execute('''
                            SELECT SUM(TotalDueEuro) 
                            FROM Invoices
                            WHERE CompanyID = {CompanyID} AND strftime('%m',DueDate)={Month} AND strftime('%Y', DueDate)={Year}
                            '''.format(CompanyID=str(values_dict['CompanyID']), Month=str(values_dict['Month']), Year=str(values_dict['Year'])))
 MRR = query_statistics.fetchall()[0][0]
 # Calculate ARR - TO CORRECT !! NOT GOOD
 query_statistics = dbase.execute('''
                            SELECT SUM(TotalDueEuro) 
                            FROM Invoices
                            WHERE CompanyID = {CompanyID} AND strftime('%Y', DueDate)={Year}
                            '''.format(CompanyID=str(values_dict['CompanyID']), Year=str(values_dict['Year'])))
 ARR = query_statistics.fetchall()[0][0]
  #Calculation of number of customers                                                                                             
  query_customers = dbase.execute('''
                                SELECT COUNT(CustomerAccountID) FROM CustomerAccounts
                                WHERE CompanyID = {CompanyID}'''.format(CompanyID=str(values_dict['CompanyID'])))  
    
  NumberOfCustomers = query_customers.fetchall()[0][0]
  #Calculation of average revenue per customer per month
  if NumberOfCustomers > 0:
    query_statistics = dbase.execute('''
                            SELECT SUM(TotalDueEuro) 
                            FROM Invoices
                            WHERE CompanyID = {CompanyID} 
                            '''.format(CompanyID=str(values_dict['CompanyID'])))
    AverageTotalRevenuePerCustomer = query_statistics.fetchall()[0][0] / NumberOfCustomers
  else
    AverageTotalRevenuePerCustomer = 0
  # Retrieve list of current active subscriptions: Customer name and surname, product name, start and end date
  # All active subscriptions => Active=1 BUT EndDate not passed as we don't have a system to automatically set a subscription as inactive when end date is passed.
  query_customers = dbase.execute('''
                                SELECT Name, Surname,ProductName, Subscriptions.StartDate, Subscriptions.EndDate
                                FROM Subscriptions
                                LEFT JOIN CustomerAccounts ON CustomerAccounts.ID=Subscriptions.CustomerAccountID
                                LEFT JOIN Customers ON Customers.ID=CustomerAccounts.CustomerID
                                LEFT JOIN Products ON Products.ID=Subscriptions.ProductID
                                WHERE CustomerAccounts.CompanyID={CompanyID} 
                                  AND Subscriptions.Active=1 
                                  AND Subscriptions.EndDate >= date('now')'''.format(CompanyID=str(values_dict['CompanyID'])))
  active_subscriptions_results = query_customers.fetchall()
  # return json.dumps(active_subscriptions_results

  return True
  
if __name__ == '__main__':
  uvicorn.run(app, host='127.0.0.1', port=8000)
