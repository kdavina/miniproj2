#run chmod +x commands.sh at first
#run ./commands.sh
sort -un -o recs.txt recs.txt  
perl break.pl< recs.txt > new_recs.txt
db_load -T -c dupsort=1 -f new_recs.txt -t hash re.idx

sort -u -o dates.txt dates.txt
perl break.pl < dates.txt > new_dates.txt
db_load -T -c dupsort=1 -f new_dates.txt -t btree da.idx

sort -u -o terms.txt terms.txt
perl break.pl < terms.txt > new_terms.txt
db_load -T -c dupsort=1 -f new_terms.txt -t btree te.idx

sort -u -o emails.txt emails.txt
perl break.pl < emails.txt > new_emails.txt
db_load -T -c dupsort=1 -f new_emails.txt -t btree em.idx

