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
            Reference_number INTEGER PRIMARY KEY NOT NULL,
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
