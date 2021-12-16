import sqlite3

dbase = sqlite3.connect('digit_project.db', isolation_level=None)
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
            Price INT NOT NULL,
            Total_VAT_price INT NOT NULL,
            Payment_status BOOL,
            Month TEXT NOT NULL,
            Year INT NOT NULL,
            Credit_card_validated BOOL NOT NULL,
            Quotation_id INTEGER NOT NULL,
            FOREIGN KEY (Quotation_id) REFERENCES Quote(Quote_id))
            ''')

dbase.execute (''' 
        CREATE TABLE IF NOT EXISTS Quote(
            Quote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Total_price INT NOT NULL,
            Total_VAT_price INT NOT NULL,
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
print('database is closed')
