import re 

xml_content = open('test10.xml').read()
terms_file = open('terms.txt','w')

row_numbers = re.findall('<row>(.*)</row>', xml_content)
subjects = re.findall('<subj>(.*)</subj>', xml_content)
bodies = re.findall('<body>(.*)</body>', xml_content)

for row_index in range(len(row_numbers)):
    split_subject = re.split('[^0-9a-zA-Z_-]',subjects[row_index])
    split_body = re.split('[^0-9a-zA-Z_-]', bodies[row_index])
    for term in split_subject:
        if len(term)>2:
            terms_file.write('s-' + term.lower() + ':' + row_numbers[row_index] + '\n')
    for body in split_body:
        if len(body)>2:
            terms_file.write('b-' + body.lower() + ':' + row_numbers[row_index] + '\n')


terms_file.close()
    
