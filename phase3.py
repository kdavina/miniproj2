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

        # get all the date queries
        correct_date_queries = re.findall('date\s*[<>:][=]?\s*\d\d\d\d[/]\d\d[/]\d\d\s+', query)
        all_date_queries = re.findall('date', query)
        if len(correct_date_queries) != len(all_date_queries):
            print("Incorrect query syntax")
            continue
        remove_whitespace(correct_date_queries)
        print("date queries", correct_date_queries)
        date_rows = dates_query(correct_date_queries)

        # get all the email address queries
        correct_email_address_queries = re.findall('(?:from|to|cc|bcc)\s*:\s*[0-9a-zA-Z-_.]+@[0-9a-zA-Z-_.]+\s+', query)
        all_email_address_queries = re.findall('from|to|cc|bcc', query)
        if len(correct_email_address_queries) != len(all_email_address_queries):
            print("Incorrect query syntax")
            continue
        remove_whitespace(correct_email_address_queries)
        print("email address queries", correct_email_address_queries)

        # get all single term queries
        # need something to check no date, cc, from, to, bcc
        #pattern = re.compile("([0-9a-zA-Z_%-])\s+([0-9a-zA-Z_-]+%?)\s+")
        #single_term_queries = pattern.sub(r'\2', query)
        single_term_queries = re.findall('(?<![:]\s*)([0-9a-zA-Z_-]+%?)\s+', query)
        remove_whitespace(single_term_queries)
        print("single term queries", single_term_queries)

def remove_whitespace(replace_list):
    for list_index in range(len(replace_list)):
        replace_list[list_index] = replace_list[list_index].replace(" ","")
    return replace_list

# you have to be careful since we are indexing the actual string
def dates_query(dates_queries):
    final_list = []
    for terms in dates_queries:
        if ':' in terms:
            date_row = exact_date(terms[5:15])
        elif '<' in terms and '=' not in terms:
            date_row = less_date(terms[5:15], False)
        elif '<' in terms and '=' in terms:
            date_row = less_date(terms[6:16], True)

        elif '>' in terms and '=' not in terms:
            date_row = greater_date(terms[5:15], False)

        elif '>' in terms and '=' in terms:
            date_row = greater_date(terms[6:16], True)

        if not final_list:
            final_list += date_row
        else:
            final_list = list(set(final_list) & set(date_row))

    for index in final_list:
        print(index)
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
