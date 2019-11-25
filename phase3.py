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
        for t_query in correct_term_queries:
            query = query.replace(t_query, "")
        correct_term_queries = remove_whitespace(correct_term_queries)
        
        # get all the date queries
        correct_date_queries = re.findall('date\s*[<>:][=]?\s*\d\d\d\d[/]\d\d[/]\d\d\s+', query)
        for d_query in correct_date_queries:
            query = query.replace(d_query, "")
        correct_date_queries = remove_whitespace(correct_date_queries)

        # get all the email address queries
        correct_email_address_queries = re.findall('(?:from|to|cc|bcc)\s*:\s*[0-9a-zA-Z-_]+[.]?[0-9a-zA-Z-_]+[@][0-9a-zA-Z-_]+[.]?[0-9a-zA-Z-_]+\s+', query)
        for ad_query in correct_email_address_queries:
            query = query.replace(ad_query, "")
        correct_email_address_queries = remove_whitespace(correct_email_address_queries)

        # get all single term queries
        single_term_queries = re.findall('[0-9a-zA-Z_-]+%?\s+', query)
        for s_t_query in single_term_queries:
            query = query.replace(s_t_query, "")
        single_term_queries = remove_whitespace(single_term_queries)
        correct_term_queries.extend(single_term_queries)

        # remove whitespaces
        query = query.replace(" ","")

        # check that there is nothing left after removing queries with correct grammar
        if len(query) > 0:
             print("Syntax Error")
             continue

        # ------------- WRITE ALL YOUR FUNCTIONS HERE ---------------
        term_rows = termQuery(correct_term_queries)
        if len(correct_term_queries) != 0 and len(term_rows) > 0:
            final_rows.append(term_rows)
        elif len(correct_term_queries) != 0 and len(term_rows) == 0:
            print("No results with those conditions")
            continue
    
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
            if  mode == 'brief':
                output = re.search('<subj>(.*)</subj>', result[1].decode("utf-8"))
                subject = output.group(1)
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


# the termQuery function takes in inputs that contain keywords "subj" or "body"
# it also takes in single-term query inputs
def termQuery(term_queries):
    term_list = []
    results = []
    pm = []
    # iterate through list of inputted term_queries and process them based on format
    # there are 5 different possibility for format:
    # body:___, subj:___, body:___%, subj:___%, ____%, ____
    for i in term_queries:
        if ":" in i:
            terms = i.split(":")
            if terms[0] == "subj":
                # checks for partial match in subject
                if "%" == terms[1][-1]:
                    partial_term = "s-" + terms[1][:-1]
                    # retrieve partial matches from partial_match function
                    # intersect with results list if both are not empty
                    p1 = partial_match(partial_term)
                    if p1:
                        if not results:
                            results.extend(p1)
                        else:
                            results = list(set(results) & set(p1))
                    terms = []
                # checks for exact match in subject
                else:
                    terms[0] = "s-" + terms[1]
                    del terms[1]


            elif terms[0] == "body":
                # checks for partial match in body
                if "%" == terms[1][-1]:
                    partial_term = "b-" + terms[1][:-1]
                    # retrieve partial matches from partial_match function
                    # intersect with results list if both are not empty
                    p2 = partial_match(partial_term)
                    if p2:
                        if not results:
                            results.extend(p2)
                        else:
                            results = list(set(results) & set(p2))
                    terms = []
                # checks for exact match in body
                else:
                    terms[0] = "b-" + terms[1]
                    del terms[1]


        # checks for partial match of single term
        elif "%" in i:
            # checks for partial match in body first
            # if both p3 and results not empty, adds to pm list
            partial_term = "b-" + i[:-1]
            p3 = partial_match(partial_term)
            if p3:
                if not results:
                    results.extend(p3)
                    pm.extend(p3)
                else:
                    pm.extend(p3)
            # then checks for partial match in subject
            partial_term = "s-" + i[:-1]
            p4 = partial_match(partial_term)
            if p4:
                if not results:
                    results.extend(p4)
                # check to see if p4 has any records not in p3, and if it does, adds record to p4
                elif p4 not in pm:
                    pm.extend(p4)
                    # intersect pm list and results list to find common records in both
                    results = list(set(results) & set(pm))
                else:
                    results = list(set(results) & set(pm))
            terms = []


        # checks for exact match of single term
        else:
            terms = [("b-"+i), ("s-"+i)]
        
        # all exact terms to be searched on index file are added to term_list
        for j in terms:
            term_list.append(j)
            

    duplicates = []
    # iterates through term_list and searches for index-key matches with any of the elements in term_list
    for key in term_list:
        index = te_curs.set(key.encode("utf-8"))
        # if there is a match, decode the index value (record ID) for the given key and add to duplicates list
        if index != None:
            recID = (index[1].decode("utf-8"))
            duplicates.append(recID)
            # next check for duplicates of record (same key, different record ID)
            dup = te_curs.next_dup()
            # if there are duplicates, decode index value (record ID) and add to duplicates table
            while(dup!=None):
                dup_index = (dup[1].decode("utf-8"))
                if dup_index not in duplicates:
                    duplicates.append(dup_index)
                dup = te_curs.next_dup()

            # if results list is empty, simply add the duplicates list to results
            # else, intersect the results list and the duplicates list to find intersecting record IDs
            if not results:
                results.extend(duplicates)
            else:
                results = list(set(results) & set(duplicates))
    return results


# partial_match function only runs if the last character in the input query is the wild card character "%"
# it takes in as input the partial_term that was formulated within the termQuery function
def partial_match(partial_term):
    results_partial = []
    # partial matches are found using the cursor.set_range function which is a part of the imported db library
    index = te_curs.set_range((partial_term.encode("utf-8")))
    while index:
        # this checks to see if the first n characters of the index key match the partial_term
        # where n is the length of the partial term
        if index[0][:len(partial_term)].decode("utf-8") == partial_term:
            pt_match = (index[1].decode("utf-8"))
            # if there is a match and index value is not in results_partial list, add it
            if pt_match not in results_partial:
                results_partial.append(pt_match)
            index = te_curs.next()
        else:
            break
    
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


main()
