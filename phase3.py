from bsddb3 import db
import re

# document says we don't need to include db type if it already exists 
# obviously database exists, so we don't need to include create
def main():
    re_database = db.DB()
    re_database.open("re.idx")
    re_curs = re_database.cursor()
    print(re_curs.first())

    da_database = db.DB()
    da_database.open("da.idx")
    da_curs = da_database.cursor()
    print(da_curs.first())

    te_database = db.DB()
    te_database.open("te.idx")
    te_curs = te_database.cursor()
    print(te_curs.first())

    em_database = db.DB()
    em_database.open("em.idx")
    em_curs = em_database.cursor()
    print(em_curs.first())

    while True:
        query = input("Enter a query in the format of field_of_interest: Press q to exit. ").lower() + ' '
        if query == 'q ':
            break

        # get all the term queries
        term_queries = re.findall('(?:subj|body)\s*:\s*[0-9a-zA-Z_-]+%?\s+', query, )
        remove_whitespace(term_queries)
        print("term queries:", term_queries)

        # get all the date queries
        date_queries = re.findall('date\s*[<>:][=]?\s*\d\d\d\d[/]\d\d[/]\d\d\s+', query)
        remove_whitespace(date_queries)
        print("date queries", date_queries)

        # get all the email address queries
        email_address_queries = re.findall('(?:from|to|cc|bcc)\s*:\s*[0-9a-zA-Z-_.]+@[0-9a-zA-Z-_.]+\s+', query)
        remove_whitespace(email_address_queries)
        print("email address queries", email_address_queries)

        # get all single term queries
        # need something to check no date, cc, from, to, bcc
        single_term_queries = re.findall('(?:!subj)[0-9a-zA-Z_-]+%?\s+', query)
        remove_whitespace(single_term_queries)
        print("single term queries", single_term_queries)

def remove_whitespace(replace_list):
    for list_index in range(len(replace_list)):
        replace_list[list_index] = replace_list[list_index].replace(" ","")
    return replace_list


main()
