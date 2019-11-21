import re 

xml_content = open('test10.xml').read()
terms_file = open('terms.txt','w') # creating the terms file

row_numbers = re.findall('<row>(.*)</row>', xml_content)
for row in row_numbers:
    print(row)
    subject_terms = re.findall('<subj>(.*)</subj>',xml_content)
