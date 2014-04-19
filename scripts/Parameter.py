import MySQLdb

class Parameter:
    def __init__(self):
        self.host = "localhost"
        self.user = "web_user"
        self.passwd = "dbwebuserpwd"
        self.db = "laser"
        self.allowedTypes = ['integer', 'string', 'date', 'double', 'bool']

    
    def CheckType(self, p_type):
        """checks whether type is allowed"""
        if(self.allowedTypes.index(p_type)!=None):
            return True
        else:
            return False
            
    # the following functions open a database connection and then close it again
    # therefore, only one connection is opened at a time
            
    def GetParameter(self, p_name):
        """returns the value of the parameter or None; type conversion is applied"""

        db = MySQLdb.connect(self.host, self.user, self.passwd, self.db)
        cur = db.cursor()
        cur.execute("SELECT * FROM parameters WHERE name = %s", (p_name,))
        row = cur.fetchone()
        
        if row == None: # not found
            ret = None
        else:
            if row[2] == "integer":
                ret = int(row[1])
            elif row[2] == "double":
                ret = float(row[1])
            elif row[2] == "date":
                ret = row[1]
                print "date conversion not implemented yet"
            elif row[2] == "bool":
                if row[1] == "1" or row[1] == "true" or row[1] == "TRUE" or row[1] == "True" or row[1] == "wahr" or row[1] == "WAHR":
                    ret = True
                else:
                    ret = False
            else:
                ret = row[1]
        
        cur.close()
        db.close()
        return ret

    
    def CreateParameter(self, p_name, p_value, p_type):
        """if parameter does not exist create new entry, else terminate"""
        
        db = MySQLdb.connect(self.host, self.user, self.passwd, self.db)
        cur = db.cursor()
        cur.execute("SELECT * FROM parameters WHERE name = %s", (p_name,))
        row = cur.fetchone()
        
        if row == None: # not found
            if(self.CheckType(p_type)): # p_type is allowed
                db = MySQLdb.connect(self.host, self.user, self.passwd, self.db)
                cur = db.cursor()
                cur.execute("INSERT INTO parameters VALUES (%s, %s, %s)", (p_name, p_value, p_type))
                db.commit()
            else:
                print "parameter type not supported"
        else:
            print "parameter already in database"
        
        cur.close()
        db.close()
            
    
    def SetParameter(self, p_name, p_value):
        """if parameter exists update"""
        
        db = MySQLdb.connect(self.host, self.user, self.passwd, self.db)
        cur = db.cursor()
        cur.execute("SELECT * FROM parameters WHERE name = %s", (p_name,))
        row = cur.fetchone()
        
        if row == None: # not found
            print "parameter not in database"
        else:
            cur.execute("UPDATE parameters SET parameters.value = %s WHERE name = %s", (p_value, p_name))
            db.commit()
        
        cur.close()
        db.close()
        
        
    def StoreParameter(self, p_name, p_value, p_type):
        """checks whether parameter already exists, then creates or updates"""
        
        db = MySQLdb.connect(self.host, self.user, self.passwd, self.db)
        cur = db.cursor()
        cur.execute("SELECT * FROM parameters WHERE name = %s", (p_name,))
        row = cur.fetchone()
        
        if row == None: # not found
            if(self.CheckType(p_type)): # p_type is allowed
                db = MySQLdb.connect(self.host, self.user, self.passwd, self.db)
                cur = db.cursor()
                cur.execute("INSERT INTO parameters VALUES (%s, %s, %s)", (p_name, p_value, p_type))
                db.commit()
            else:
                print "parameter type not supported"
        else: # parameter already there
            cur.execute("UPDATE parameters SET parameters.value = %s WHERE name = %s", (p_value, p_name))
            db.commit()
        
        cur.close()
        db.close()
            
            
