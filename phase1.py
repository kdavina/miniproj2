import re 

xml_content = open('test10.xml').read()
terms_file = open('terms.txt','w')
emails_file = open('emails.txt', 'w')
dates_file = open('dates.txt', 'w')
recs_file = open('recs.txt','w')

# parse the row number, subject, body, emails, dates, and records into different lists
row_numbers = re.findall('<row>(.*)</row>', xml_content)
subjects = re.findall('<subj>(.*)</subj>', xml_content)
bodies = re.findall('<body>(.*)</body>', xml_content)
from_emails = re.findall('<from>(.*)</from>', xml_content)
to_emails = re.findall('<to>(.*)</to>', xml_content)
cc_emails = re.findall('<cc>(.*)</cc>', xml_content)
bcc_emails = re.findall('<bcc>(.*)</bcc>', xml_content)

for row_index in range(len(row_numbers)):
    # generate terms.txt
    split_subject = re.split('[^0-9a-zA-Z_-]',subjects[row_index])
    split_body = re.split('[^0-9a-zA-Z_-]', bodies[row_index])
    for term in split_subject:
        if len(term)>2:
            terms_file.write('s-' + term.lower() + ':' + row_numbers[row_index] + '\n')
    for body in split_body:
        if len(body)>2:
            terms_file.write('b-' + body.lower() + ':' + row_numbers[row_index] + '\n')
    
    # generate emails.txt
    if len(from_emails[row_index])>0:
        emails_file.write('from-' + from_emails[row_index] + ':' + row_numbers[row_index] + '\n')
    
    if len(to_emails[row_index])>0:
        emails_file.write('to-'+ to_emails[row_index] + ':' + row_numbers[row_index] + '\n')

    if len(cc_emails[row_index])>0:
         emails_file.write('cc-'+ cc_emails[row_index] + ':' + row_numbers[row_index] + '\n')
        
    if len(bcc_emails[row_index])>0:
        emails_file.write('bcc-'+ bcc_emails[row_index] + ':' + row_numbers[row_index] + '\n')

terms_file.close()
emails_file.close()
dates_file.close()
recs_file.close()

    
