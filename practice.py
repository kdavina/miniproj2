list1 = [1,2,3,4]
list2 = [2,3]
list3 = [2,3,5]
list4 = [2,4,6]
list5= []
list5.append(list1)
list5.append(list2)
list5.append(list3)
list5.append(list4)
print(list5)
while len(list5) > 1:
    list5[0] = list(set(list5[0]) & set(list5[1]))
    del list5[1]
    print(list5)