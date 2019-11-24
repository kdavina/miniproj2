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
        query = input("Enter a query in the format of field_of_interest: Press q to exit. ")
        query1 = 'subj:gas'
        if query == 'q':
            break

        # get all the term queries
        # OUR PARSER IN PROGRESS, CURRENTLY SELECTS ANYTHING FROM THE GROUP AND ONLY PRINTS THAT
        term_queries = re.findall('subj\s*:\s*[0-9a-zA-Z_-]+|body\s*:\s*[0-9a-zA-Z_-]+', query)
        print("term queries:", term_queries)

        # get all the date queries
        date_queries = re.findall('date\s*<\s*\d\d\d\d[/]\d\d[/]\d\d|date\s*>\s*\d\d\d\d[/]\d\d[/]\d\d|date\s*<=\s*\d\d\d\d[/]\d\d[/]\d\d|date\s*>=\s*\d\d\d\d[/]\d\d[/]\d\d|date\s*:\s*\d\d\d\d[/]\d\d[/]\d\d', query)
        print("date queries", date_queries)

        # get all the email address queries
        email_address_queries = re.findall('from\s*:\s*[0-9a-zA-Z-_.]+@[0-9a-zA-Z-_.]+|to\s*:\s*[0-9a-zA-Z-_.]+@[0-9a-zA-Z-_.]+|cc\s*:\s*[0-9a-zA-Z-_.]+@[0-9a-zA-Z-_.]+|bcc\s*:\s*[0-9a-zA-Z-_.]+@[0-9a-zA-Z-_.]+', query)
        print("email address queries", email_address_queries)

        # get all single term queries
        # need something to check no date, cc, from, to, bcc, term at the beginning
        single_term_queries = re.findall('\Bsubj[0-9a-zA-Z_-]+%?', query)
        print("single term queries", single_term_queries)


main()
