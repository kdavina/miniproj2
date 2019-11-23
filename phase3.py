from bsddb3 import db


re_database = db.DB()

#document says we don't need to include db type if it already exists 
# obviously database exists, so we don't need to include create
re_database = db.DB()
re_database.open("re.idx")
re_curs = re_database.cursor()
print(re_curs.first())

da_database = db.DB()
da_database.open("da.idx")
da_curs = da_database.cursor()
print(da_curs.first())