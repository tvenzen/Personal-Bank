
import random
import sqlite3
con = sqlite3.connect('PersonalBank.db')
cur = con.cursor()
con.row_factory = sqlite3.Row

rand = random


accountNumbers = []

#Author: Tyler Venzen


#The user class holds the information of the User while to app is running. Users create an account if they do not have one or login if they do.
class User:
    def __init__(self, ID, username, firstName, lastName, password):
        self.ID = ID
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.password = password
        self.savingsAccounts = []
        self.checkingAccounts = []
        self.transactionHistory = []
    
    
    def generateAccountNumber(self):
        #This is used to generate random 4-digit numbers to be used as account numbers. This function does an internal check to assure repeats aren't used.
        #Account numbers are strings, not integers.

        newAccountNum = '#' + str(rand.randrange(1000,9999))
        cur.execute("SELECT accountID FROM Accounts WHERE accountNumber = ?", [newAccountNum])
        accountCheck = cur.fetchone()

        while not accountCheck is None:
            newAccountNum = '#' + str(rand.randrange(1000, 9999))
            cur.execute("SELECT accountID FROM Accounts WHERE accountNumber = ?", [newAccountNum])
            accountCheck = cur.fetchone()

        return newAccountNum

    def getTransactionTableSize(self):
        #This is solely to obtain the size of the ever-expanding transaction table for ease of coding.

        #Query is ordered in descending to get the largest ID number.
        tableSize = cur.execute("SELECT transactionHistoryID FROM TransactionHistory ORDER BY transactionHistoryID DESC LIMIT 1").fetchone()

        #If an error occurs, or there are no entries in the Transaction History table, returns 1.
        if tableSize is None:
            tableSize = 1
            return tableSize

        #Database Cursor function 'fetchone' returns a tuple, so it is necessary to specify index to obtain integer.
        return tableSize[0] + 1


    def addAccount(self):

        #This is the operation to add either a savings or checking account, and cancel if necessary.
        #The Schema for Accounts is [accountID, accountNumber, accountBalance, userID, accountTypeID]
        #Transaction History is updated at the end of each type of operation.

        print(f"Would you like to add a Savings account or a Checking account?")
        print(f"1: Savings")
        print(f"2: Checkings")
        print(f"3: Cancel")
        
        userInput = input("Please enter now: ")

        while  userInput != "3":

            
            if userInput == "1":

                cur.execute("SELECT accountID FROM Accounts ORDER BY accountID DESC LIMIT 1")
                r = cur.fetchone()

                newAccountNumber = self.generateAccountNumber()

                if r is None:
                    r = 1
                    cur.execute("INSERT INTO Accounts VALUES(?, ?, ?, ?, ?)", [r, newAccountNumber, 0.0 , self.ID, 1])
                    cur.execute("INSERT INTO TransactionHistory VALUES(?, ?, ?, ?, ?, ?)", [self.getTransactionTableSize(), 0, 5, self.ID, r, newAccountNumber])

                    print(f'Account {newAccountNumber} has been created.')
                    con.commit()
                    break

                cur.execute("INSERT INTO Accounts VALUES(?, ?, ?, ?, ?)", [r[0] + 1, newAccountNumber, 0.0 , self.ID, 1])
                cur.execute("INSERT INTO TransactionHistory VALUES(?, ?, ?, ?, ?, ?)", [self.getTransactionTableSize(), 0, 5, self.ID, r[0] + 1, newAccountNumber])
                self.transactionHistory.append("New Savings Account added: " + newAccountNumber)

                print(f'Account {newAccountNumber} has been created.')
                con.commit()
                break

            elif userInput == "2":
                cur.execute("SELECT accountID FROM Accounts ORDER BY accountID DESC LIMIT 1")
                r = cur.fetchone()

                newAccountNumber = self.generateAccountNumber()

                cur.execute("INSERT INTO Accounts VALUES(?, ?, ?, ?, ?)", [r[0] + 1, newAccountNumber, 0.0 , self.ID, 2])
                
                self.transactionHistory.append("New Checking Account added: " + newAccountNumber)
                cur.execute("INSERT INTO TransactionHistory VALUES(?, ?, ?, ?, ?, ?)", [self.getTransactionTableSize(), 0, 7, self.ID, r[0] + 1, newAccountNumber])
                print(f'Account {newAccountNumber} has been created.')
                con.commit()
                break
            
            elif userInput == "3":
                print(f'Account creation cancelled.')
                break
            else:
                userInput = input("Invalid input; Please try again: ")
    
    def deleteAccount(self):
        
        #This is the operation to delete an account. Users will have their account numbers printed before they are able to input a selection.
        #Relevant information is will be set to 'NULL' in Accounts table when deletion occurs.

        #Checks to assure an account exists before progressing with function
        accountCheck = cur.execute("Select accountID FROM Accounts WHERE UserID = ?", [self.ID]).fetchall()

        if accountCheck is None or accountCheck == []:
            print("You don't have any accounts with us.")
            return
        
        print(f"Which account would you like to delete?")
        
        cur.execute("SELECT accountNumber, accountTypeID FROM Accounts WHERE UserID = ?",[self.ID] )
        userAccounts = cur.fetchall()

        #If no accounts are returned, the operation ends.
        if userAccounts is None:
            print("You have no accounts with us.")
            return

        for x in userAccounts:
            if x[1] == 1:
                print(f'Savings Account: {x[0]}')
            elif x[1] == 2:
                print(f'Checking Account: {x[0]}')
        
        userInput = input("Please input now or enter 'EXIT' to cancel: ")
        

        if userInput == "exit" or userInput == "EXIT":
            print("Account deletion cancelled")
            return
 
        cur.execute("SELECT accountID, accountTypeID FROM Accounts WHERE accountNumber = ?", [userInput])
        inputCheck = cur.fetchone()
        
        while inputCheck is None:
            userInput = input("Error: Please re-enter now: ")
            
            if userInput == "exit" or userInput == "EXIT":
                print("Account deletion cancelled")
                return

            cur.execute("SELECT accountID FROM Accounts WHERE accountNumber = ?", [userInput])
            inputCheck = cur.fetchone()

        if inputCheck[1] == 1:
            cur.execute("INSERT INTO TransactionHistory VALUES(?, ?, ?, ?, ?, ?)", [self.getTransactionTableSize(), 0, 6, self.ID, inputCheck[0], userInput])
        elif inputCheck[1] == 2:
            cur.execute("INSERT INTO TransactionHistory VALUES(?, ?, ?, ?, ?, ?)", [self.getTransactionTableSize(), 0, 8, self.ID, inputCheck[0], userInput])
            
        cur.execute("DELETE FROM Accounts WHERE accountID = ?", [inputCheck[0]])
        print(f'Account {userInput} has been deleted.')
        con.commit()

        

    def getAccountBalance(self): 

        #This is the operation that will return the balance of a user's account. 
        #The user will input their account number that that want to know more about.

        #Checks to assure an account exists before progressing with function
        accountCheck = cur.execute("Select accountID FROM Accounts WHERE UserID = ?", [self.ID]).fetchall()

        if accountCheck is None or accountCheck == []:
            print("You don't have any accounts with us.")
            return

        inputAccountNum = input ("What is the account number of the balance you would like to check? (Enter 'EXIT' to cancel): ")

        if inputAccountNum == "exit" or inputAccountNum == "EXIT":
            print("Balance retrieval canceled.")
            return

        inputCheck = cur.execute("SELECT accountID FROM Accounts WHERE accountNumber = ?", [inputAccountNum]).fetchone()
        
        while inputCheck is None:
            inputAccountNum = input("Please enter now: ")

            if inputAccountNum == "exit" or inputAccountNum == "EXIT":
                print("Balance retrieval canceled.")
                return

            cur.execute("SELECT accountID FROM Accounts WHERE accountNumber = ?", [inputAccountNum])
            inputCheck = cur.fetchone()

        balance = cur.execute("SELECT accountBalance FROM Accounts WHERE accountNumber = ?", [inputAccountNum]).fetchone()
        print(f'The account balance of account {inputAccountNum} is: ${balance[0]}')


            
    def getAllAccountBalance(self):

        #This prints the balance of all accounts, with the account number.

        #Checks to assure an account exists before progressing with function
        userAccountList = cur.execute("SELECT accountNumber, accountBalance FROM Accounts WHERE UserID = ?", [self.ID]).fetchall()

        if userAccountList is None or userAccountList == []:
            print("You do not have any accounts with us.")
            return

        
        for x in userAccountList:
            print(f'Account number {x[0]} has a balance of: ${x[1]}')

    def makeDeposit(self):

        #This is the operation for the user add money to an account.
        #The user will enter the correct account number and then input the amount the wish to deposit.
        #The Transaction History table obtains a new row and the account is updated.

        #Checks to assure an account exists before progressing with function
        accountList = cur.execute("SELECT accountNumber FROM Accounts WHERE UserID = ?", [self.ID]).fetchall()

        if accountList is None or accountList == []:
            print("You do not have any accounts with us.")
            return

        print(f'Your account numbers are: ')

        for x in accountList:
            print(x[0])

        inputAccountNum = input("Please enter the account number of the account you wish to deposit in or enter 'EXIT' to cancel: ")

        if inputAccountNum == "exit" or inputAccountNum == "EXIT":
            print("Withdrawal cancelled")
            return

        accountBalance = cur.execute("SELECT accountID, accountBalance from Accounts WHERE accountNumber = ?", [inputAccountNum]).fetchone()

        while accountBalance is None:
            inputAccountNum = input("Error: Please re-enter the account number: ")

            if inputAccountNum == "exit" or inputAccountNum == "EXIT":
                print("Deposit cancelled")
                return

            accountBalance = cur.execute("SELECT accountID, accountBalance from Accounts WHERE accountNumber = ?", [inputAccountNum]).fetchone()
                
        inputDepositAmount = float(input("Please enter the amount you wish to deposit: "))

        #Tuple does not allow index reassignment; Must have separate variable to interact with the balance float itself.
        updatedBalance = accountBalance[1]
        updatedBalance += inputDepositAmount
                
        cur.execute("INSERT INTO TransactionHistory VALUES(?, ?, ?, ?, ?, ?)", [self.getTransactionTableSize(), inputDepositAmount, 3, self.ID, accountBalance[0], inputAccountNum])
        cur.execute("UPDATE Accounts SET accountBalance = ? WHERE accountNumber = ?", [updatedBalance, inputAccountNum])
        con.commit()

    def makeWithdrawal(self):

        #This is the operation for the user subtract money from an account.
        #The user will enter the correct account number and then input the amount they wish to withdraw.
        #The Transaction History table obtains a new row and the account is updated.

        #Checks to assure an account exists before progressing with function
        accountList = cur.execute("SELECT accountNumber FROM Accounts WHERE UserID = ?", [self.ID]).fetchall()
        

        if accountList is None or accountList == []:
            print("You do not have any accounts with us.")
            return

        print(f'Your account numbers are: ')

        for x in accountList:
            print(x[0])

        inputAccountNum = input("Please enter the account number of the account you wish to withdraw from or enter 'EXIT' to cancel: ")

        if inputAccountNum == "exit" or inputAccountNum == "EXIT":
            print("Withdrawal cancelled")
            return

        accountBalance = cur.execute("SELECT accountID, accountBalance from Accounts WHERE accountNumber = ?", [inputAccountNum]).fetchone()

        while accountBalance is None:
            inputAccountNum = input("Error: Please re-enter the account number: ")

            if inputAccountNum == "exit" or inputAccountNum == "EXIT":
                print("Withdrawal cancelled")
                return

            accountBalance = cur.execute("SELECT accountID, accountBalance from Accounts WHERE accountNumber = ?", [inputAccountNum]).fetchone()
                
        inputWithdrawAmount = float(input("Please enter the amount you wish to withdraw: "))

        #Tuple does not allow index reassignment; Must have separate variable to interact with the balance float itself.
        updatedBalance = accountBalance[1]
        updatedBalance -= inputWithdrawAmount
                
        cur.execute("INSERT INTO TransactionHistory VALUES(?, ?, ?, ?, ?, ?)", [self.getTransactionTableSize(), inputWithdrawAmount, 4, self.ID, accountBalance[0], inputAccountNum])
        cur.execute("UPDATE Accounts SET accountBalance = ? WHERE accountNumber = ?", [updatedBalance, inputAccountNum])
        con.commit()
    
    def getTransactionHistory(self):
        #This will print the recorded list of actions corresponding the the ID of the User.
        

        transactionList = cur.execute("SELECT logTypeID, accountNumber, transactionAmount FROM TransactionHistory WHERE UserID = ?", [self.ID]).fetchall()

        #TransactionList should never be empty as creating the account is a type of transaction for the database, but a case was added if something goes wrong.
        if transactionList is None or transactionList == []:
            print("No transactions for this user")
            return

        for x in transactionList:
            if x[0] == 1:
                print(f'You created your account.')
            elif x[0] == 2:
                print(f'You logged in.')
            elif x[0] == 3:
                print(f'You made a deposit of {x[2]} in account {x[1]}')
            elif x[0] == 4:
                print(f'You made a withdrawal of {x[2]} in account {x[1]}')
            elif x[0] == 5:
                print(f'You created a savings account with number: {x[1]}')
            elif x[0] == 6:
                print(f"You deleted a savings account with number: {x[1]}")
            elif x[0] == 7:
                print(f"you created a checking account with number {x[1]}")
            elif x[0] == 8:
                print(f'You deleted a savings account with number {x[1]}')
                
        
        



class Bank:

    #This houses the logic for the app, while creating, initializing, and maintaining the completeness of the database.

    def __init__(self):
        self.bankName = "Python Bank"
        self.totalUsers = []
        self.totalAccounts = []
        self.masterEventHistory = []


    def databaseIntegrityCheck(self):
        #This is the operation to initalize the database if not already created.
        #If, for some reason, tables or data are missing, they will be created or repaired with these scripts

        listOfTables = []

        #logTypes is used to initialize the LogType table.
        logTypes = [
            (1, 'New User Created'),
            (2, 'User Login'),
            (3, 'Deposit'),
            (4, 'Withdrawal'),
            (5, 'Account created: Savings'),
            (6, 'Account deleted: Savings'),
            (7, 'Account created: Checkings'),
            (8, 'Account deleted: Checkings'),
            (9, 'User deleted')
        ]

        #accountTypes is used to initialize the AccountType table
        accountTypes = [
            (1, 'Savings Account'),
            (2, 'Checking Account')
        ]

        cur.execute('''
            CREATE TABLE IF NOT EXISTS Users(
                userID INTEGER PRIMARY KEY,
                username TEXT,
                firstName TEXT,
                lastName TEXT,
                password TEXT
            );
        ''')

        #Labeling columns as 'UNIQUE' prevents duplicate data from being inserted if table is already populated.
        cur.executescript('''
            CREATE TABLE IF NOT EXISTS LogType(
                logTypeID INTEGER PRIMARY KEY,
                logType TEXT,
                UNIQUE(logTypeID, logType)
            );
        ''')

        #This populates the LogType table
        cur.executemany("INSERT OR IGNORE INTO  LogType VALUES(?,?)", logTypes)

        cur.execute('''
            CREATE TABLE IF NOT EXISTS AccountType(
                accountTypeID INTEGER PRIMARY KEY,
                accountType TEXT,
                UNIQUE(accountTypeID, accountType)
            );
        ''')

        #This populates to AccountType table
        cur.executemany("INSERT OR IGNORE INTO AccountType VALUES(?,?)", accountTypes)

        cur.executescript("""
            CREATE TABLE IF NOT EXISTS Accounts(
                accountID INTEGER PRIMARY KEY,
                accountNumber TEXT,
                accountBalance REAL,
                userID INTEGER,
                accountTypeID INTEGER,
                FOREIGN KEY (userID) 
                REFERENCES Users (userID) 
                ON DELETE SET NULL,
                FOREIGN KEY (accountTypeID)
                REFERENCES AccountType (accountTypeID)
                ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS TransactionHistory(
                transactionHistoryID INTEGER PRIMARY KEY,
                transactionAmount REAL,
                logTypeID INTEGER,
                userID INTEGER,
                accountID INTEGER,
                accountNumber TEXT,
                FOREIGN KEY (logTypeID)
                REFERENCES LogType (logTypeID)
                On DELETE SET NULL,
                FOREIGN Key (userID)
                REFERENCES Users (userID)
                ON DELETE SET NULL,
                FOREIGN KEY (accountID)
                REFERENCES Accounts (accountID)
                ON DELETE SET NULL,
                FOREIGN KEY (accountNumber)
                REFERENCES Accounts (accountNumber)
                ON DELETE SET NULL
            );
        """)

        



    def Login(self):

        #This is the operation for accessing the program.
        #Users will be prompted to either log in or create an account.
        #Both creating an account, and logging in are recorded in Transaction History.
        #A user object is initialized either by database request when logging in, or user input when being created and is then returned.

        print(f'Welcome! Are you a new or returning user?')
        print(f'1: Login')
        print(f'2: Create account')

        userInput = input("Please enter the number of the action you'd like to take (Ex. '1', '2') ")

        while not userInput is None:
            if userInput == "1":
                inputUsername = input("Please enter your username: ")
                inputPassword = input("Please enter your password: ")

                userInfo = cur.execute("SELECT userID, username, firstName, lastName, password FROM Users WHERE username = ? AND password = ?", [inputUsername, inputPassword]).fetchone()
                
                while userInfo is None:
                    print("Invalid username or password. Please try again.")
                    inputUsername = input("Please enter your username: ")
                    inputPassword = input("Please enter your password: ")
                    userInfo = cur.execute("SELECT userID, username, firstName, lastName, password FROM Users WHERE username = ? AND password = ?", [inputUsername, inputPassword]).fetchone()

                returningUser = User(userInfo[0], userInfo[1], userInfo[2], userInfo[3], userInfo[4])

                transactionTableSize = cur.execute("SELECT transactionHistoryID FROM TransactionHistory ORDER BY transactionHistoryID DESC LIMIT 1").fetchone()
                cur.execute("INSERT INTO TransactionHistory VALUES (?, ?, ?, ?, ?, ?)", [transactionTableSize[0] + 1, 0, 2, userInfo[0], None, None])
                con.commit()
                return returningUser
        
            elif userInput == "2":
                username = input("Please enter a username: ")
                firstName = input("Please enter your first name: ")
                lastName = input("Please enter your last name: ")
                password = input("Please enter your password: ")

                userTableSize = cur.execute("SELECT userID FROM Users ORDER BY userID DESC LIMIT 1").fetchone()

                #If Users has no entries, or an error occurs, userTableSize is set to 1.
                if userTableSize is None:
                    userTableSize = 1
                    newUser =  User(userTableSize, username, firstName, lastName, password)
                    userTableSize = cur.execute("SELECT userID FROM Users ORDER BY userID DESC LIMIT 1").fetchone()
                    transactionTableSize = cur.execute("SELECT transactionHistoryID FROM TransactionHistory ORDER BY transactionHistoryID DESC LIMIT 1").fetchone()

                    #If Transaction History has no entries, or an error occurs, userTableSize is set to 1.
                    if transactionTableSize is None:
                        transactionTableSize = 1
                        cur.execute("INSERT INTO TransactionHistory VALUES (?, ?, ?, ?, ?, ?)", [transactionTableSize, 0, 1, userTableSize, None, None])
                        cur.execute("INSERT INTO Users VALUES(?, ?, ?, ?, ?)", [userTableSize, username, firstName, lastName, password])
                        con.commit()
                        return newUser

                    cur.execute("INSERT INTO TransactionHistory VALUES (?, ?, ?, ?, ?, ?)", [transactionTableSize[0] + 1, 0, 1, userTableSize, None, None])
                    cur.execute("INSERT INTO Users VALUES(?, ?, ?, ?, ?)", [userTableSize, username, firstName, lastName, password])
                    con.commit()
                    return newUser

                newUser =  User(userTableSize[0] + 1, username, firstName, lastName, password)

                userTableSize = cur.execute("SELECT userID FROM Users ORDER BY userID DESC LIMIT 1").fetchone()
                transactionTableSize = cur.execute("SELECT transactionHistoryID FROM TransactionHistory ORDER BY transactionHistoryID DESC LIMIT 1").fetchone()

                cur.execute("INSERT INTO TransactionHistory VALUES (?, ?, ?, ?, ?, ?)", [transactionTableSize[0] + 1, 0, 1, userTableSize[0] + 1, None, None])
                cur.execute("INSERT INTO Users VALUES(?, ?, ?, ?, ?)", [userTableSize[0] + 1, username, firstName, lastName, password])
                con.commit()
                return newUser

            else:
                userInput = input("Invalid input; Please try again: ")

    def userOptions(self):

        #This is solely for saving lines of code when the user needs the selections again.

        print(f'1: Check balance of a account')
        print(f'2: Check balance of all accounts')
        print(f'3: Make a deposit')
        print(f'4: Make a withdrawal')
        print(f'5: Check transaction history')
        print(f'6: Create new account')
        print(f'7: Delete an account')
        print(f'8: Exit')
    
    def App(self):

        #The app itself. Users will be prompted to either login or create an account. When successful, they are able to make input selections as to what
        #actions they want to take while using the App using the returned User object from Login().

        self.databaseIntegrityCheck()

        currentUser = self.Login()

        while currentUser is None or currentUser is False:
            if currentUser is None:
                print(f'Error logging in; Please try again.')
                currentUser = self.Login()
            elif currentUser is False:
                print(f'Invalid username; Please try again')
                currentUser = self.Login()

        print(f'Welcome {currentUser.firstName}, how can we help you today?')
        self.userOptions()
        

        userInput = input("Please make a selection: ")

        while userInput != "8":
            if userInput == "1":
                currentUser.getAccountBalance()
            elif userInput == "2":
                currentUser.getAllAccountBalance()
            elif userInput == "3":
                currentUser.makeDeposit()
            elif userInput == "4":
                currentUser.makeWithdrawal()
            elif userInput == "5":
                currentUser.getTransactionHistory()
            elif userInput == "6":
                currentUser.addAccount()
            elif userInput == "7":
                currentUser.deleteAccount()
            elif userInput == "8":
                print("Thank you for using our services! Goodbye.")
                con.commit()
                break
            else:
                userInput = input("Invalid input; Please try again: ")
            
            self.userOptions()
            userInput = input("Enter now: ")


PythonBank = Bank()

PythonBank.App()