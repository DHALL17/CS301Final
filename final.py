def satsifyConditions( d , conditions ):
    # If there are no conditions always returns TRUE(1)
    if conditions == ['']:
        return 1
    # Checks if the conditions are met for the tuple returns False if not met
    for cond in conditions:
        found = 0
        for attribute in d:
            if attribute[0] == cond[0]:
                found = 1
                if cond[1] == ">":
                    if attribute[1] <= cond[2]:
                        return 0
                elif cond[1] == "<":
                    if attribute[1] >= cond[2]:
                        return 0
                elif cond[1] == "=":
                    if attribute[1] != cond[2]:
                        return 0
                elif cond[1] == ">=":
                    if attribute[1] < cond[2]:
                        return 0
                elif cond[1] == "<=":
                    if attribute[1] > cond[2]:
                        return 0
                elif cond[1] == "<>":
                    if attribute[1] == cond[2]:
                        return 0
                else:
                    print("Some kind of conditional problem in SatisfyConditions")
        # Checks to see if the attribute for condition was found
        if found == 0:
            return 0
    return 1

def query( db , params , output ):
    conditions = params[0].split(',')
    # Splits conditions into ['attrbiute' , 'operation', val]
    for i, cond in enumerate(conditions):
        operator = ""
        for letter in cond:
            char = letter.lower()
            if (char <= '9' and char >= '0') == 1:
                conditions[i] = conditions[i].split(operator)
                conditions[i].insert(1, operator)
                conditions[i][2] = int(conditions[i][2])
                break
            if (char >= 'a' and char <= 'z') == 0:
                operator += char
    # Separates the parameters into a list of fields
    fields = params[1].split(',')
    # Prints the tuples satisfying the conditions
    for d in db:
        if satsifyConditions( d , conditions ) == 1:
            # Handles the case of 0 fields
            if fields == ['']:
                out = ""
                for i, attribute in enumerate(d):
                    if attribute[0] != "DocID":
                        out += attribute[0] + ':' + str(attribute[1]) + ' '
                print(out[:len(out) - 1], file=output)
            # Handles the case of n fields
            else:
                for i, field in enumerate(fields):
                    found = 0
                    for attribute in d:
                        if attribute[0] == field:
                            found = 1
                            if i != len(fields) - 1:
                                print(attribute[0] + ":" + str(attribute[1]), end=' ', file=output)
                            else:
                                print(attribute[0] + ":" + str(attribute[1]), file=output)
                    if found == 0:
                        if i != len(fields) - 1:
                            print(field + ":NA", end='', file=output)
                        else:
                            print(field + ":NA", file=output)
    print(file=output)

def count( db , params ):
    _type = int(params[1])
    field = params[0]
    count = 0
    # Counts the total occurences
    if _type == 0:
        for d in db:
            for attribute in d:
                if attribute[0] == params[0]:
                    count += 1
        return count
    # Counts the unique occurences
    else:
        _list = []
        for d in db:
            for attribute in d:
                if attribute[0] == params[0]:
                    if attribute[1] not in _list:
                        _list.append(attribute[1])
                        count += 1
        return count

def duplicate_id( db , _id ):
    for d in db:
        for attribute in d:
            if attribute[0] == "DocID":
                if _id == attribute[1]:
                    return 1
    return 0

def insert( db , params , maxId , output ):
    found = 0
    # Separates the string into attributes
    params = params.split(' ')
    # Searches attribute list for DocID to check for duplicates
    for attr in params:
        if attr[:5] == "DocID":
            if duplicate_id( db , int(attr[6:]) ) == 1:
                print("Duplicate DocID error!" + '\n', file=output)
                return
            found = 1
            break
    
    # Sets a new attribute of DocID if it wasn't found in the search
    docId = ""
    if found == 0:
        maxId[0] = maxId[0] + 1
        docId = "DocID:" + str(maxId[0])
        # Separates the attribute type from value for docId
        docId = docId.split(':', 1)
        docId[1] = int(docId[1])
    
    # Separates the attribute type from value for list of params
    for i, attr in enumerate(params):
        attr = attr.split(':', 1)
        attr[1] = int(attr[1])
        params[i] = attr
        i += 1

    if len(docId) > 0:
        params.insert(0, docId)
    db.append(params)

    # Prints the insert back as confirmation
    for i, atr in enumerate(params):
        print(atr[0] + ":" + str(atr[1]), end='', file=output)
        if( i != len(params) - 1):
            print(" " , end='', file=output)
    print('\n', file=output)

    return

def validateSyntax( line ):
    if len(line) > 13:
        # Creates a sub-string of the query used to determine which it is
        query = line[:13]
        if query == "final.count([":
            # Grabs everything to the right of the condition above
            line = line[13:]
            # Checks that the field and uniqueness are separated correctly
            if line.find("],[") > 0:
                line = line.split("],[", 1)
                # Confirms that the condition consists of only alpha and numeric values
                if line[0].isalnum() == 1:
                    # Checks that the query is closed correctly
                    if line[1].find("])") > 0:
                        line = line[1].split("])", 1)
                        # Looks for the case that something other than a new line
                        # is after the enclosing parenthesis
                        if line[1] != '':
                            if line[1] != '\n':
                                return False
                        # Validates the uniqueness is a boolean value
                        if line[0] == '0' or line[0] == '1':
                            return True
        elif query == "final.insert(":
            # Grabs everything to the right of the condition above
            line = line[13:]
            # Checks for enclosing parenthesis
            if line.find(')') > 0:
                line = line.split(')', 1)
                # Checks that either nothing or \n exists after
                # enclosing parenthesis
                if line[1] != '':
                    if line[1] != '\n':
                        return False
                # Separates query into ['field:1', 'field2:2']
                line = line[0].split(' ')
                # Separates the fields from values and checks for the correct types
                for i, val in enumerate(line):
                    val = val.split(':', 1)
                    if val[0].isalnum() == 0 or val[1].isdigit() == 0:
                        return False
                return True
        elif query == "final.query([":
            # Grabs everything to the right of the condition above
            line = line[13:]
            if line == "],[])" or line == "],[]\n":
                return True
            # Checks that the query is closed correctly
            if line.find("])") > 0:
                line = line.split("])", 1)
                # Looks for the case that something other than a new line
                # or nothing is after the enclosing parenthesis
                if line[1] != '\n':
                    if line[1] != '':
                        return False
                line = line[0]
                # Checks that the operations and fields are separated correctly
                if line.find("],[", 1) >= 0:
                    line = line.split("],[", 1)
                    for i, item in enumerate(line):
                        line[i] = item.split(',')
                    for condition in line[0]:
                        operator = ""
                        if condition == '':
                            return False
                        for i, letter in enumerate(condition):
                            if letter.isalnum() == 0:
                                operator = letter
                                cond = []
                                # Handles cases where the the operator is one character
                                if operator == ">":
                                    cond = condition.split(">", 1)
                                elif operator == "<":
                                    cond = condition.split("<", 1)
                                elif operator == "=":
                                    cond = condition.split("=", 1)
                                else:
                                    return False
                                # Handles cases where the operator is two characters
                                if len(condition) > i + 1:
                                    if condition[i + 1].isdigit() == False:
                                        operator += condition[i+1]
                                        if operator == "<>":
                                            cond = condition.split("<>", 1)
                                        elif operator == ">=":
                                            cond = condition.split(">=", 1)
                                        elif operator == "<=":
                                            cond = condition.split("<=", 1)
                                        else:
                                            return False
                                
                                print(line)
                                print(str(condition.split(operator, 1)) + '\n')
    return False



#             elif query == "query([":
#                 line = line[13:].split("])", 1)
#                 if len(line) > 1:
#                     line = line[0]
#                     line = line.split("],[", 1)
#                     if len(line) > 1:
#                         conditions = line[0].split(',')
#                         fields = line[1].split(',')
#                         if fields != ['']:
#                             for field in fields:
#                                 if field.isalpha() == False:
#                                     return 0
#                         if conditions != ['']:
#                             for cond in conditions:
#                                 for i, letter in enumerate(cond):
#                                     if letter.isalpha() == False:
#                                         operator = letter
#                                         condition = []
#                                         # Handles cases where the the operator is one character
#                                         if operator == ">":
#                                             condition = cond.split(">", 1)
#                                         elif operator == "<":
#                                             condition = cond.split("<", 1)
#                                         elif operator == "=":
#                                             condition = cond.split("=", 1)
#                                         # Handles cases where the operator is two characters
#                                         if len(cond) > i + 1:
#                                             if cond[i + 1].isdigit() == False:
#                                                 operator += cond[i+1]

#                                             if operator == "<>":
#                                                 condition = cond.split("<>", 1)
#                                             elif operator == ">=":
#                                                 condition = cond.split(">=", 1)
#                                             elif operator == "<=":
#                                                 condition = cond.split("<=", 1)
#                                             else:
#                                                 return 0
#                                         else:
#                                             return 0
#                                         # Validates that the right hand side of the condition is only digits
#                                         if condition[1].isnumeric() == False:
#                                             return 0
#                                         else:
#                                             return 1



db = []
maxId = [0]
output = open("results.txt", "w+")
# Builds the inital database from Data.txt file
with open("data.txt", 'r') as fp:
    for line in fp:
        new = []
        found = 0
        for word in line.split():
            attribute = word.split(':')
            # Casts attribute value to an integer value
            attribute[1] = int(attribute[1])
            # Sets the maxId
            if attribute[0] == "DocID":
                found = 1
                if attribute[1] > maxId[0]:
                    maxId[0] = attribute[1]
            new.append(attribute)
        db.append(new)
        if found == 0:
            maxId[0] += 1
            db[len(db) - 1].insert(0, ["DocID", maxId])
# Searches the Query file for different Queries and calls the appropriate function
with open("queries.txt", 'r') as fp:
    for line in fp:
        print('>' + line, end='', file=output)
        # Makes sure the string has a length to store final
        if len(line) < 5:
            print(file=output)
        # Checks query for final
        elif line[:5] != "final":
            print(file=output)
        # Checks all other validation
        elif validateSyntax( line ) == True:
            # Grabs everything to the left of the first paranthesis
            operation = line.split('(')[0]
            # Grabs the operation type from the query
            operation = operation.split('.')[1]
            # Grabs everything to the right of the first parenthesis
            params = line.split('(')[1]
            # Removes the ) from the end of the string
            # EOF doesn't have \n conditions are for consistent output
            if params[len(params) - 1] != '\n':
                params = params[:(len(params) - 1)]
                print(file=output)
            else:
                params = params[:(len(params) - 2)]
            # Handles the different queries
            if operation == "query":
                params = params.split('],[', 1)
                params[0] = params[0][1:]
                params[1] = params[1][:len(params[1]) - 1]
                query( db , params , output )
            elif operation == "count":
                params = params.split(',', 1)
                params[0] = params[0][1:len(params[0]) - 1]
                params[1] = params[1][1:len(params[1]) - 1]
                print(str(count( db , params )) + '\n', file=output)
            elif operation == "insert":
                insert( db , params , maxId , output )
            else:
                print("query semantic error!", file=output)
        else:
            if line[len(line) - 1] != '\n':
                print(file=output)
            print("validate query semantic error!\n", file=output)
