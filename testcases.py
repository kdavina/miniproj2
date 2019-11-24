from phase3 import main

# A list of test cases we can run everytime we've completed a certain part of our project to test that the output is working

#--- TEST SUBJ AND BODY ---
# # Test case 1:
# subj:term
# e.g. for query 1 subj: gas, emails with row number 5 has gas in their subject 
# I'm still unclear about what output we're supposed to get, I asked on eclass forums and hopefully I'll hear back soon,
# but just for example let's assume we only need the rows numbers back
# we haven't made this function yet, let's assume it exists lol
# result = findsubj(gas)
# assert(result == 5) 
# more elegant way of writing it: assert(findsubj(gas) == 5)

# Test case 1.5:
# subj:     term 

# Test case 2:
# subj: term body: term

# Test case 2.5:
# subj:  term body:     term

# Test case 3:
# subj: term subj: term body: term

# Test case 4:
# subj:term body:term subj:term 

# Test case 5:
# subj: term body:term subj:term body:term

#--- TEST INDIVIDUAL TERMS AND THEIR COMBINATION WITH SUBJ AND/OR BODY ---
# Test case 6:
# term 

# Test case 7:
# term subj:term 

# Test case 8:
# term subj:term term

# Test case 9:
# term subj:term term body:term 

# Test case 10:
# term subj:term

# Test case 11:
# term subj:term term%

# Test case 12:
# term subj:term term% body:term 

# Test case 13:
# term subj:term term% body:term%

# Test case 14:
# subj: term% body:term

#--- TEST EMAILS ---
# Test case 15:
# from: email

# Test case 16:
# from: email%

# Test case 17:
# to:email

# Test case 18:
# to:email%

# Test case 19:
# from: email from:email 

# Test case 20:
# from: email% from: email

# Test case 21:
# to: email from:email

# Test case 22:
# to: email% from:email 

# Test case 23:
# bcc:email

# Test case 24:
# bcc:email%

# Test case 25:
# cc:email

# Test case 26:
# cc:email%

# Test case 27:
# bcc:email cc:email

# Test case 28:
# bcc:email to:email from:email 

#--- TEST DATES ---
# Test case 29:
# date:DATE/FORMAT/LOL

# Test case 29.5:
# date:   DATE/FORMAT/LOL

# Test case 30:
# date>DATE/FORMAT/LOL

# Test case 31:
# date >   DATE/FORMAT/LOL

# Test case 31:
# date<DATE/FORMAT/LOL

# Test case 32:
# date <    DATE/FORMAT/LOL

# Test case 33:
# date>=DATE/FORMAL/LOL

# Test case 44:
# date   >=  DATE/FORMAL/LOL

# Test case 45:
# date<=DATE/FORMAL/LOL

# Test case 46:
# date   <= DATE/FORMAL/LOL

# --- TEST MANY THINGS PUT TOGETHER ---
# Test case 47:
# to:email term% subj:  term date <= DATE/FORMAT/LOL body:term body:term     bcc:email     subj:term term%



