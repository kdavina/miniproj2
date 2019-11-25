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
    output_mode = 'brief'
    final_rows = []
    while True:
        query = input("Enter a query. Press q to exit. ").lower() + ' '
        if query == 'q ':
            break

        # detect mode
        o_output = re.search('output[=](full|brief)\s+', query)
        if o_output:
            output_mode = o_output.group()
            query = query.replace(output_mode,"")
            output_mode.replace(" ","")
            output_mode = output_mode[7:]

        # get all the term queries
        correct_term_queries = re.findall('(?:subj|body)\s*:\s*[0-9a-zA-Z_-]+%?\s+', query)
        for t_query in correct_term_queries:
            query = query.replace(t_query, "")
        correct_term_queries = remove_whitespace(correct_term_queries)
        print("term queries", correct_term_queries)

        # get all the date queries
        correct_date_queries = re.findall('date\s*[<>:][=]?\s*\d\d\d\d[/]\d\d[/]\d\d\s+', query)
        for d_query in correct_date_queries:
            query = query.replace(d_query, "")
        correct_date_queries = remove_whitespace(correct_date_queries)
        print("date queries", correct_date_queries)

        # get all the email address queries
        correct_email_address_queries = re.findall('(?:from|to|cc|bcc)\s*:\s*[0-9a-zA-Z-_.]+@[0-9a-zA-Z-_.]+\s+', query)
        for ad_query in correct_email_address_queries:
            query = query.replace(ad_query, "")
        correct_email_address_queries = remove_whitespace(correct_email_address_queries)
        print("email address queries", correct_email_address_queries)

        # get all single term queries
        single_term_queries = re.findall('[0-9a-zA-Z_-]+%?\s+', query)
        for s_t_query in single_term_queries:
            query = query.replace(s_t_query, "")
        single_term_queries = remove_whitespace(single_term_queries)
        correct_term_queries.extend(single_term_queries)
        print("single term queries", single_term_queries)
       
        query = query.replace(" ","")

        if len(query) > 0:
             print("query", query)
             print("Syntax Error")
             continue

        # ------------- WRITE ALL YOUR FUNCTIONS HERE ---------------
        term_rows = termQuery(correct_term_queries)
        if term_rows:
            final_rows.append(term_rows)
        
        #partial_matches = partial_match(partial_term)


        email_rows = email_query(correct_email_address_queries)
        if email_rows:
            final_rows.append(email_rows)

        date_rows = dates_query(correct_date_queries)
        if date_rows:
            final_rows.append(date_rows)
        
        #this is the intersection part, you may get a combination where they all return nothing
        if len(final_rows) == 0:
            print('No results with those conditions')
            continue
        else:
            while len(final_rows) > 1:
                final_rows[0] = list(set(final_rows[0]) & set(final_rows[1]))
                del final_rows[1]
            
            final_results(final_rows[0], output_mode)


def final_results(rows, mode):
    for terms in rows:
        result = re_curs.set(terms.encode("utf-8"))
        if mode == 'brief':
            output = re.search('<subj>(.*)</subj>', result[1].decode("utf-8"))
            subject = output.group(1)
            subject = replace_char(subject)
            if subject == '':
                subject = 'No subject found'
            print('\nRow: '+terms+'\nSubject: '+subject)

        else:
            print('\nRow: '+terms)
            result[1] = replace_char(result[1].decode("utf-8"))
            print(result[1])

    print('\n')

def remove_whitespace(replace_list):
    for list_index in range(len(replace_list)):
        replace_list[list_index] = replace_list[list_index].replace(" ","")
    return replace_list


def termQuery(term_queries):
    #term_queries = ['subj:gas', 'body:the', 'subj:clos%', 'body:west%', 'fro%', 'closing']
    #print("term_queries:", term_queries)
    term_list = []
    results = []
    for i in term_queries:
        if ":" in i:
            terms = i.split(":")
            #print(terms)
            if terms[0] == "subj":
                if "%" == terms[1][-1]:
                    partial_term = "s-" + terms[1][:-1]
                    p1 = partial_match(partial_term)
                    if p1 and not results:
                        results += p1
                    else:
                        results = list(set(results) & set(p1))
                    terms = []
                else:
                    terms[0] = "s-" + terms[1]
                    del terms[1]
                    #print(terms)
            elif terms[0] == "body":
                if "%" == terms[1][-1]:
                    partial_term = "b-" + terms[1][:-1]
                    p2 = partial_match(partial_term)
                    if p2 and not results:
                        results += p2
                    else:
                        results = list(set(results) & set(p2))
                    terms = []
                else:
                    terms[0] = "b-" + terms[1]
                    del terms[1]
                    #print(terms)
            # else:
            #     #this else statement will never run since term_queries has already been checked for input validity
            #     print("Invalid entry")
        elif "%" in i:
            partial_term = "b-" + i[:-1]
            p3 = partial_match(partial_term)
            if p3 and not results:
                results += p3
            else:
                results = list(set(results) & set(p3))
            partial_term = "s-" + i[:-1]
            p4 = partial_match(partial_term)
            if p4 and not results:
                results += p4
            else:
                results = list(set(results) & set(p4))
                print("results table:", results)
            terms = []
        else:
            terms = [("b-"+i), ("s-"+i)]
            #terms[0] = "s-" + i
            #terms[1] = "b-" + i
            #print(terms)
        
        for j in terms:
            term_list.append(j)

    print("only including partials:", results)
    
    print("\n", "List of all exact terms:", term_list)

    for key in term_list:
        index = te_curs.set(key.encode("utf-8"))
        #print("index val:", index)
        if index != None:
            recID = (index[1].decode("utf-8"))
            if not results:
                results.append(recID)
            else:
                results = list(set(results) & set(recID))
            print("after including 1st result", results)
        dup = te_curs.next_dup()
        while(dup!=None):
            duplicates = (dup[1].decode("utf-8"))
            #print(duplicates)
            dup = te_curs.next_dup()
            #dup = te_curs.next_dup()
            #print(dup[0].decode("utf-8"))
            print("before including duplicates:", results)
        
           # if not results:
            results.append(duplicates)
            #else:
               # results = list(set(results) & set(duplicates))
            print("after including duplicates:", results)    

    print("\n", "Printing partial match results first, then exact match results:", "\n", results, "\n\n")    
    return results


def partial_match(partial_term):
    #print("\n\n", "This is the partial term parsed into partial match func:", partial_term)
    results_partial = []
    
    index = te_curs.set_range((partial_term.encode("utf-8")))
    #index = te_database.get((partial_term[0].encode("utf-8")))
    #print("Results of curs.set_range:", index)
    while index:
        #print("Try to match part of index key to partial term using:", index[0][:len(partial_term)].decode("utf-8"), "\n")
        if index[0][:len(partial_term)].decode("utf-8") == partial_term:
            results_partial.append(index[1].decode("utf-8"))
            print("Partial matches:", partial_term)
            index = te_curs.next()
        else:
            break
    
    print("Print record IDs for partial matches:", results_partial, "\n\n") 
    return results_partial

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

def replace_char(to_replace):
        to_replace = to_replace.replace('&#10','\n')         
        to_replace = to_replace.replace('&lt','<')
        to_replace = to_replace.replace('&gt','>')
        to_replace = to_replace.replace('&amp','&')
        to_replace = to_replace.replace('&apos','\'')
        to_replace = to_replace.replace('&quot','"')
        return to_replace
    

main()
