from bsddb3 import db
import re

# document says we don't need to include db type if it already exists 
# obviously database exists, so we don't need to include create

re_database = db.DB()
re_database.set_flags(db.DB_DUP)
re_database.open("re.idx")
re_curs = re_database.cursor()

da_database = db.DB()
da_database.set_flags(db.DB_DUP)
da_database.open("da.idx")
da_curs = da_database.cursor()

te_database = db.DB()
te_database.set_flags(db.DB_DUP)
te_database.open("te.idx")
te_curs = te_database.cursor()

em_database = db.DB()
em_database.set_flags(db.DB_DUP)
em_database.open("em.idx")
em_curs = em_database.cursor()

def main():
    final_rows = []
    while True:
        query = input("Enter a query in the format of field_of_interest: Press q to exit. ").lower() + ' '
        query = ' ' + query
        if query == ' q ':
            break

        # get all the term queries
        correct_term_queries = re.findall('(?:subj|body)\s*:\s*[0-9a-zA-Z_-]+%?\s+', query, )
        all_term_queries = re.findall('subj|body', query)
        if len(correct_term_queries) != len(all_term_queries):
            print("Incorrect query syntax")
            continue
        remove_whitespace(correct_term_queries)
        print("term queries", correct_term_queries)

        termQuery()

        # get all the date queries
        correct_date_queries = re.findall('date\s*[<>:][=]?\s*\d\d\d\d[/]\d\d[/]\d\d\s+', query)
        all_date_queries = re.findall('date', query)
        if len(correct_date_queries) != len(all_date_queries):
            print("Incorrect query syntax")
            continue
        remove_whitespace(correct_date_queries)
        print("date queries", correct_date_queries)
        date_rows = dates_query(correct_date_queries)
        if date_rows:
            final_rows.append(date_rows)

        # get all the email address queries
        correct_email_address_queries = re.findall('(?:from|to|cc|bcc)\s*:\s*[0-9a-zA-Z-_.]+@[0-9a-zA-Z-_.]+\s+', query)
        all_email_address_queries = re.findall('from|to|cc|bcc', query)
        if len(correct_email_address_queries) != len(all_email_address_queries):
            print("Incorrect query syntax")
            continue
        remove_whitespace(correct_email_address_queries)
        print("email address queries", correct_email_address_queries)
        email_rows = email_query(correct_email_address_queries)
        if email_rows:
            final_rows.append(email_rows)

        # get all single term queries
        # need something to check no date, cc, from, to, bcc
        #pattern = re.compile("([0-9a-zA-Z_%-])\s+([0-9a-zA-Z_-]+%?)\s+")
        #single_term_queries = pattern.sub(r'\2', query)
        #single_term_queries = re.findall('(?<![:]\s*)([0-9a-zA-Z_-]+%?)\s+', query)
        #remove_whitespace(single_term_queries)
        
        #this is the intersection part, you may get a combination where they all return nothing
        if len(final_rows) == 0:
            print('No results with those conditions')
            continue
        else:
            while len(final_rows) > 1:
                final_rows[0] = list(set(final_rows[0]) & set(final_rows[1]))
                del final_rows[1]
            
            # replace false with whatever variable you're setting output as davina
            final_results(final_rows[0], False)


def final_results(rows, mode):
    for terms in rows:
        result = re_curs.set(terms.encode("utf-8"))
        if not mode:
            output = re.search('<subj>(.*)</subj>', result[1].decode("utf-8"))
            subject = output.group(1)
            if subject == '':
                subject = 'No subject found'
            print('\nRow: '+terms+'\nSubject: '+subject)

        else:
            print('\nRow: '+terms)
            print(result[1].decode("utf-8"))

    print('\n')

def remove_whitespace(replace_list):
    for list_index in range(len(replace_list)):
        replace_list[list_index] = replace_list[list_index].replace(" ","")
    return replace_list


def termQuery():
    term_queries = ['subj:gas', 'body:the', 'subj:clos%', 'body:west%', 'from%', 'closing']
    print("term_queries:", term_queries)
    new_list = []
    for i in term_queries:
        if ":" in i:
            terms = i.split(":")
            print(terms)
            if terms[0] == "subj":
                if "%" == terms[1][-1]:
                    partial_term = "s-" + terms[1][:-1]
                    partial_match(partial_term)
                    terms = []
                else:
                    terms[0] = "s-" + terms[1]
                    del terms[1]
                    print(terms)
            elif terms[0] == "body":
                if "%" == terms[1][-1]:
                    partial_term = "b-" + terms[1][:-1]
                    partial_match(partial_term)
                    terms = []
                else:
                    terms[0] = "b-" + terms[1]
                    del terms[1]
                    print(terms)
            # else:
            #     #this else statement will never run since term_queries has already been checked for input validity
            #     print("Invalid entry")
        elif "%" in i:
            i = i[:-1]
            partial_term = [("s-"+i), ("b-"+i)]
            partial_match(partial_term)
            terms = []
        else:
            terms = [("s-"+i), ("b-"+i)]
            #terms[0] = "s-" + i
            #terms[1] = "b-" + i
            print(terms)
        
        for j in terms:
            new_list.append(j)
    
    print("List of all indexes:", new_list)

    for key in new_list:
        index = te_curs.set(key.encode("utf-8"))
        print("index val:", index)
        results = []
        if index != None:
            recID = (index[1].decode("utf-8"))
            results.append(recID)
        dup = te_curs.next_dup()
        while(dup!=None):
            duplicates = (dup[1].decode("utf-8"))
            #print(duplicates)
            dup = te_curs.next_dup()
            #dup = te_curs.next_dup()
            #print(dup[0].decode("utf-8"))
        
            
            results.append(duplicates)
            print("print recIDs:", results)


def partial_match(partial_term):

    partial_recID = []
    print("in partial matching for term:", partial_term)
    
    index = te_curs.set_range((partial_term[0].encode("utf-8")))
    #index = te_database.get(partial_term[0].encode("utf-8"))
    print(index)
    while index:
        print("partial match to this key from te.idx:", index[0][:len(partial_term[0])].decode("utf-8"))
        if index[0][:len(partial_term[0])].decode("utf-8") == partial_term:
            partial_recID.append(index[1].decode("utf-8"))
            print("Partial matches:", partial_term)
            index = te_curs.next()
        else:
            break

# depending on the word, I replaced the values to match the xml file
# then passed the newly formatted email into my find email function
def email_query(email):
    final_list = []
    for terms in email:
        if 'from' in terms:
            parsed_email = re.sub('from:', 'from-',terms)
            email_rows = find_email(parsed_email)
        elif 'to' in terms:
            parsed_email = re.sub('to:', 'to-', terms)
            email_rows = find_email(parsed_email)
        elif 'cc' in terms:
            parsed_email = re.sub('cc:', 'cc-', terms)
            email_rows = find_email(parsed_email)
        elif 'bcc' in terms:
            parsed_email = re.sub('bcc:', 'bcc-', terms)
            email_rows = find_email(parsed_email)
        
        # this is the part where i check for intersection
        # first if nothing is in final list we add our first term into it
        if not final_list:
            final_list += email_rows
        # breaking down: set gets rid of duplicates within its own list
        # doing the & symbol looks for which values appears in both sets
        # by the end we should only have values that appear in both so set it as a list again
        else:
            final_list = list(set(final_list) & set(email_rows))

        
    return final_list

# email is correctly formatted to our xml file
# since email is our key, we only need to run through cursor duplicates and nothing else
# if we find the match, we append it to a new list
# by the end of it we should have a list of index numbers that correspond to that email (and respective to,from, cc, bcc)
def find_email(email):
    new_list = []
    result = em_curs.set(email.encode("utf-8"))
    if result != None:
        new_list.append(result[1].decode("utf-8"))
        duplicate = em_curs.next_dup()

        while duplicate != None:
            new_list.append(duplicate[1].decode("utf-8"))
            duplicate = em_curs.next_dup()

    return new_list

# you have to be careful since we are indexing the actual string
def dates_query(dates_queries):
    final_list = []
    for terms in dates_queries:
        if ':' in terms:
            date_row = exact_date(terms[5:])
        elif '<' in terms and '=' not in terms:
            date_row = less_date(terms[5:], False)
        elif '<' in terms and '=' in terms:
            date_row = less_date(terms[6:], True)

        elif '>' in terms and '=' not in terms:
            date_row = greater_date(terms[5:], False)

        elif '>' in terms and '=' in terms:
            date_row = greater_date(terms[6:], True)

        # this is the part where i check for intersection
        # first if nothing is in final list we add our first term into it
        if not final_list:
            final_list += date_row

        else:
            final_list = list(set(final_list) & set(date_row))

    return final_list
    
    # set gets rid of duplicates
    
# since we are looking for rows with this exact date AND date is the key
# we only need to iterate through cursor duplicates    
def exact_date(date):
    new_list = []
    result = da_curs.set(date.encode("utf-8"))
    if result != None:
        new_list.append(result[1].decode("utf-8"))
        dup = da_curs.next_dup()
        while dup != None:
            new_list.append(dup[1].decode("utf-8"))
            dup = da_curs.next_dup()

    return new_list


def less_date(date, equals_bool):
    new_list = []
    result = da_curs.first()
    while result != None:
        if result[0].decode("utf-8") < date :
            new_list.append(result[1].decode("utf-8"))

        elif result[0].decode("utf-8") <= date and equals_bool:
            new_list.append(result[1].decode("utf-8"))


        # checking for duplicate functions
        dup = da_curs.next_dup()
        while dup != None:
            if dup[0].decode("utf-8") < date:
                new_list.append(dup[1].decode("utf-8"))
            elif dup[0].decode("utf-8") <= date and equals_bool:
                new_list.append(dup[1].decode("utf-8"))
            dup = da_curs.next_dup()

        result = da_curs.next()

    return new_list



def greater_date(date, equals_bool):
    new_list = []
    result = da_curs.last()
    
    while result != None:
        if result[0].decode("utf-8") > date:
            new_list.append(result[1].decode("utf-8"))
        elif result[0].decode("utf-8") >= date and equals_bool:
            new_list.append(result[1].decode("utf-8"))

        #checking for duplicates
        dup = da_curs.next_dup()
        while dup != None:
            if dup[0].decode("utf-8") < date:
                new_list.append(dup[1].decode("utf-8"))
            elif dup[0].decode("utf-8") <= date and equals_bool:
                new_list.append(dup[1].decode("utf-8"))
            dup = da_curs.prev_dup()

      
        result = da_curs.prev()
   
    return new_list


    

main()
