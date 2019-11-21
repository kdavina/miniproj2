import re 

terms_file = open('terms.txt','w')
emails_file = open('emails.txt', 'w')
dates_file = open('dates.txt', 'w')
recs_file = open('recs.txt','w')

def main():
    filename = 'test1000.xml'
    xml_content = open(filename).read()

    # parse the row number, subject, body, emails, dates, and records into different lists
    row_numbers = re.findall('<row>(.*)</row>', xml_content)
    subjects = re.findall('<subj>(.*)</subj>', xml_content)
    bodies = re.findall('<body>(.*)</body>', xml_content)
    from_emails = re.findall('<from>(.*)</from>', xml_content)
    to_emails = re.findall('<to>(.*)</to>', xml_content)
    cc_emails = re.findall('<cc>(.*)</cc>', xml_content)
    bcc_emails = re.findall('<bcc>(.*)</bcc>', xml_content)

    for row_index in range(len(row_numbers)):

        create_term_file(subjects, bodies, row_index, row_numbers, terms_file)

        # generate emails.txt
        if len(from_emails[row_index])>0:
            sep_f_emails = from_emails[row_index].split(',')
            for f_email in sep_f_emails:
                emails_file.write('from-' + f_email + ':' + row_numbers[row_index] + '\n')
        
        if len(to_emails[row_index])>0:
            sep_to_emails = to_emails[row_index].split(',')
            for to_email in sep_to_emails:
                emails_file.write('to-'+ to_email + ':' + row_numbers[row_index] + '\n')

        if len(cc_emails[row_index])>0:
            sep_cc_emails = cc_emails[row_index].split(',')
            for cc_email in sep_cc_emails:
                emails_file.write('cc-'+ cc_email + ':' + row_numbers[row_index] + '\n')
        
        if len(bcc_emails[row_index])>0:
            sep_bcc_emails = bcc_emails[row_index].split(',')
            for bcc_email in sep_bcc_emails:
                emails_file.write('bcc-'+ bcc_email + ':' + row_numbers[row_index] + '\n')

    #creating date file 
    date_file(filename,row_numbers)

    #creating rec file
    record_file(filename, row_numbers)

    terms_file.close()
    emails_file.close()
    dates_file.close()
    recs_file.close()

def replace_char(to_replace):
        to_replace = to_replace.replace('&#10','!') # #10 is actually a newline, replace with ! so it doesn't appear after future split 
        to_replace = to_replace.replace('&lt','<')
        to_replace = to_replace.replace('&gt','>')
        to_replace = to_replace.replace('&amp','&')
        to_replace = to_replace.replace('&apos','\'')
        to_replace = to_replace.replace('&quot','"')
        return to_replace

def create_term_file(subjects, bodies, row_index, row_numbers, terms_file):
        # generate terms.txt
        subjects[row_index] = replace_char(subjects[row_index])
        bodies[row_index] = replace_char(bodies[row_index])
        split_subject = re.split('[^0-9a-zA-Z_-]',subjects[row_index])
        split_body = re.split('[^0-9a-zA-Z_-]', bodies[row_index])
        for term in split_subject:
            if len(term)>2:
                terms_file.write('s-' + term.lower() + ':' + row_numbers[row_index] + '\n')
        for body in split_body:
            if len(body)>2:
                terms_file.write('b-' + body.lower() + ':' + row_numbers[row_index] + '\n')
        

def date_file(filename, row_numbers):
    i = 0
    with open(filename, "r") as inputfile:
        for line in inputfile:
            result = re.search('<date>(.*)</date>', line)
            if result != None:
                dates_file.write(result.group(1)+':'+row_numbers[i]+'\n')
                i += 1  

def record_file(filename, row_numbers):
    i= 0 
    with open(filename, "r") as inputfile:
        for line in inputfile:
            result = re.search('<mail>(.*)</mail>', line)
            if result != None:
                recs_file.write(row_numbers[i] +':'+result.group(0)+'\n')
                i += 1 
main()