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
    while True:
        print("output mode rn", output_mode)
        final_rows = []
        query = input("Enter a query. Press q to exit. ").lower() + ' '
        if query == 'q ':
            break

        # detect mode
        o_output = re.search('output[=](full|brief)\s+', query)
        if o_output:
            output_mode = o_output.group()
            query = query.replace(output_mode,"")
            output_mode = output_mode.replace(" ","")
            output_mode = output_mode[7:]
            query = query.replace(" ","")
            if len(query) > 0:
                print("query", query)
                print("Syntax Error")
                continue
            continue

        # get all the term queries
        correct_term_queries = re.findall('(?:subj|body)\s*:\s*[0-9a-zA-Z_-]+%?\s+', query, )
        all_term_queries = re.findall('subj|body', query)
        if len(correct_term_queries) != len(all_term_queries):
            print("Incorrect query syntax")
            continue
        #changed 
        remove_whitespace(correct_term_queries)
        correct_term_queries = re.findall('(?:subj|body)\s*:\s*[0-9a-zA-Z_-]+%?\s+', query)
        for t_query in correct_term_queries:
            query = query.replace(t_query, "")
        correct_term_queries = remove_whitespace(correct_term_queries)
        print("term queries", correct_term_queries)
        #changed 
        
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
        if len(correct_term_queries) != 0 and len(term_rows) > 0:
            final_rows.append(term_rows)
        elif len(correct_term_queries) != 0 and len(term_rows) == 0:
            print("No results with those conditions")
            continue
        
        #partial_matches = partial_match(partial_term)
    
        #calculating email query
        # we have two conditions:
        # 1. either the user has inputed some email to find row values for and we do get a result
        # 2. the user has inputed some email but we do not get a result
        # for 1, we include that in our final rows to be intersected
        # for 2, we do not want to compute the rest since the query combination has already failed within emails
        # ex. if the user inputed two from emails, our email_rows will be 0 despite having input so we automatically
        # know that the query will fail in the end
        email_rows = email_query(correct_email_address_queries)
        if len(correct_email_address_queries) != 0 and len(email_rows) > 0:
            final_rows.append(email_rows)
        elif len(correct_email_address_queries) != 0 and len(email_rows) == 0:
            print("No results with those conditions")
            continue

        # calculating date query 
        #same logic as emails
        date_rows = dates_query(correct_date_queries)
        if len(correct_date_queries) != 0 and len(date_rows)>0:
            final_rows.append(date_rows)
        elif len(correct_date_queries) != 0 and len(date_rows) == 0:
            print("\n")
            continue
    
        #this is the intersection part
        # if even after all the queries, final list is empty, do not search for rows and just print out a message
        if len(final_rows) == 0:
            print('\n')
        else:
            # each element of final_rows is a list corresponding to one of our calcualted queries
            # if there is more than one, that means we need to intersect them with each other
            # once they are successfully intersected, delete the second list since we have already intersected that
            # continue until we are down to one final row
            while len(final_rows) > 1:
                final_rows[0] = list(set(final_rows[0]) & set(final_rows[1]))
                del final_rows[1]
            # only print out the output if there's a guarantee there are rows 
            final_results(final_rows[0], output_mode)


# after intersecting, rows is our final row numbers to index
def final_results(rows, mode):
    if rows:
        # for each value in rows we find the index in re.idx 
        # depending on the mode we either want to find subj or the entire thing
        # print out the output
        for terms in rows:
            result = re_curs.set(terms.encode("utf-8"))
            print("output mode in final_results", mode)
            if  mode == 'brief':
                output = re.search('<subj>(.*)</subj>', result[1].decode("utf-8"))
                subject = output.group(1)
                subject = replace_char(subject)
                print('\nRow: '+terms+'\nSubject: '+subject)

            else:
                print('\nRow: '+terms)
                print(result[1].decode("utf-8"))
    else:
        print("No results with those conditions")

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
    pm = []
    for i in term_queries:
        if ":" in i:
            terms = i.split(":")
            if terms[0] == "subj":
                if "%" == terms[1][-1]:
                    partial_term = "s-" + terms[1][:-1]
                    p1 = partial_match(partial_term)
                    if p1:
                        if not results:
                            results.extend(p1)
                        else:
                            results = list(set(results) & set(p1))
                    terms = []
                else:
                    terms[0] = "s-" + terms[1]
                    del terms[1]
            elif terms[0] == "body":
                if "%" == terms[1][-1]:
                    partial_term = "b-" + terms[1][:-1]
                    p2 = partial_match(partial_term)
                    if p2:
                        if not results:
                            results.extend(p2)
                        else:
                            results = list(set(results) & set(p2))
                    terms = []
                else:
                    terms[0] = "b-" + terms[1]
                    del terms[1]
        elif "%" in i:
            partial_term = "b-" + i[:-1]
            p3 = partial_match(partial_term)
            if p3:
                if not results:
                    results.extend(p3)
                    pm.extend(p3)
                    print(results)
                else:
                    pm.extend(p3)
            partial_term = "s-" + i[:-1]
            p4 = partial_match(partial_term)
            print(pm)
            if p4:
                if not results:
                    results.extend(p4)
                elif p4 not in pm:
                    pm.extend(p4)
                    results = list(set(results) & set(pm))
                else:
                    results = list(set(results) & set(pm))
                    
                print("results table:", results)
            terms = []
        else:
            terms = [("b-"+i), ("s-"+i)]
        
        for j in terms:
            term_list.append(j)

    print("only including partials:", results)
    
    print("\n", "List of all exact terms:", term_list)

    duplicates = []
    for key in term_list:
        index = te_curs.set(key.encode("utf-8"))
        print(index)
        print("results table before exact match search:", results)
        #print("index val:", index)
        if index != None:
            recID = (index[1].decode("utf-8"))
            if not results:
                results.append(recID)
            elif recID not in duplicates:
                duplicates.append(recID)
            print("after including 1st result", results)
            dup = te_curs.next_dup()
            while(dup!=None):
                dup_index = (dup[1].decode("utf-8"))
                if dup_index not in duplicates:
                    duplicates.append(dup_index)
                #print(duplicates)
                dup = te_curs.next_dup()
                #dup = te_curs.next_dup()
                #print(dup[0].decode("utf-8"))
                print("before including duplicates:", results)
                print("just the duplicates table:", duplicates)
            
            if not results:
                results.extend(duplicates)
            else:
                results = list(set(results) & set(duplicates))
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
            pt_match = (index[1].decode("utf-8"))
            if pt_match not in results_partial:
                results_partial.append(pt_match)
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

# we have multiple options for all the terms in date queries
# depending on the symbol run a certain function
# add that to our final list for intersection and to return
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
        # look for email intersection for explanation
        if not final_list:
            final_list += date_row

        else:
            final_list = list(set(final_list) & set(date_row))

    return final_list
    
    
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
    #set our cursor to the smallest value (since its a btree)
    result = da_curs.first()
    
    while result != None:
        # append the row number if it satisfies the condition
        # note that in order to append to new_list for <= the equals_bool has to be true aka
        # the user input is <= and not <
        # also note that since we are starting at the smallest value, if the value is not smaller than the date
        # all dates after it will also not be smaller
        # for optimization, break out of the loop
        if result[0].decode("utf-8") < date :
            new_list.append(result[1].decode("utf-8"))

        elif result[0].decode("utf-8") <= date and equals_bool:
            new_list.append(result[1].decode("utf-8"))
        else:
            break

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
    # set the cursor to the largest date we have
    result = da_curs.last()
    
    # we check of our largest date is greater than the input date
    # similar to less_date except we go backwards
    while result != None:
        if result[0].decode("utf-8") > date:
            new_list.append(result[1].decode("utf-8"))
        elif result[0].decode("utf-8") >= date and equals_bool:
            new_list.append(result[1].decode("utf-8"))
        else:
            break

        #checking for duplicates
        dup = da_curs.next_dup()
        while dup != None:
            if dup[0].decode("utf-8") > date:
                new_list.append(dup[1].decode("utf-8"))
            elif dup[0].decode("utf-8") >= date and equals_bool:
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
