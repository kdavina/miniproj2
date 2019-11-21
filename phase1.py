import re 

xml_content = open('test10.xml').read()
terms_file = open('terms.txt','w') # creating the terms file

row_numbers = re.findall('<row>(.*)</row>', xml_content)

# reading xml content and outputting into a file
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

#creating date file 
date_file = open('dates.txt', "w+")
dates = re.findall('<date>(.*)</date>', xml_content)

for index in range(len(row_numbers)): 
    date_file.write(dates[index]+':'+row_numbers[index]+'\n')
    
#creating rec file
recs_file = open("recs.txt", 'w+')

#need the i in order to keep track of indexing for row numbers
i = 0
with open(filename, "r") as inputfile:
    for line in inputfile:
        result = re.search('<mail>(.*)</mail>', line)
        if result != None:
            recs_file.write(row_numbers[i] +':'+result.group(0)+'\n')
            i += 1 
    
