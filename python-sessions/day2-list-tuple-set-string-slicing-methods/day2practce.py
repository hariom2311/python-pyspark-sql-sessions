# list methods
# list slicing
# string methods
# string slicing
# set methods 
# set slicing
# tuple methods 
# tuple slicing

# list data type

# students = ['Ajay', ['python', 'SQL', 'Pyspark'], 87, 23, True, None]

# # properties of list
# # it is mutable
# students[0]= 'Ajay Devgan'

# # it can have duplicate values
# duplicate_values = [8, 8]

# #indexing and slicing
# # indexing 
# name = students[0]

# # slicing
# name_and_subject = students[0:2]

# nums = [10, 20, 30, 40, 50, 60, 70, 80]

# print(nums)


# print(nums[0:3]) # ouput from index 0, 1 and 2

# print(nums[3:])

# print(nums[::-1]) # i want to go from start to end

# print(nums[6:2:-1])


# print(nums[-5:-1])

# list methods
a = [1, 2, 3]
print(a)

# len() method
print(len(a))

# append() method
# b = 4
# a.append(b)
# print(a)

# b = [4, 5]
# a.append(b)
# print(a)

# [1, 2, 3, 4, 5]

# extend() methods
# a.extend(b)
# print(a)

# b = [4, 5, [6, 7]]

# a.extend(b) # if you use append [1, 2, 3, [4, 5, [6, 6]]]
# print(a)

# print(a)

# # insert() method

# # a.insert(1, 1.5)
# # print(a)

# # remove() method
# a = [1, 2, 3, 2]
# print(a)
# a.remove(2)
# print(a)


# # pop() method
# a = [1, 2, 3, 2]
# # popped_value = a.pop()
# # print(popped_value)
# # print(a.pop())
# # print(a)

# # a.pop(1)
# # print(a)


# # index() method
# print(a.index(2)) # exmple if I have [1, 3, 3, 5] and I want to get the index for value 3

# # count() method
# print(a.count(3))

# copy() method
a = [1, 2, 3]
# b = a
# b[0] = 10
# print(a, b)

# b = a.copy()
# b[0] = 10
# print(a, b)

# sort() method
a = [5, 2, 8, 3]
a.sort(reverse=False)
print(a)
# a.sort()
# print(a)


# sorted()
# b = sorted(a)
# print(a, b)

# string methods
# string

# what is mutable and immutable
# mutable means if you want to change the values inside any sequiential data types so you can do
# immutable- you can not do this

name = "Python"
# name[0] = "p"
# print(name)

print(name[:2:2])



name = "DataEngineering"

print(name[-5:])

print(name[10:2:-2])


# String methods

# strip method
# name = " Hariom "
# print(name)
# strip_name = name.strip()
# print(name)
# print(strip_name)


# split method
# course_names = "python, sql, pyspark"

# course_list = course_names.split(",")
# print(course_list)


# join method
course_list = ["python", "SQL", "Pyspark"]
course_details = ", ".join(course_list)
print(course_details)


# replace method
var1 = "abcabc" 
replaced_value = var1.replace('a', 'X')
print(replaced_value)

# find method
print(var1.find("P"))


# index method

# print(var1.index('P'))

# lower, upper, capitalize
print(var1.lower())

print(var1.upper())

print(var1.startswith('a'))

file_name = 'students.csv'

print(file_name.endswith('.json'))


phone = "38383838"

print(phone.isdigit())


alpha_num = "LDLE9393*"
print(alpha_num.isalnum())


# Tuple
# Tuple is immutable
# hold duplicate values
# slicing and indexing works here
# Indexing also works in tuple

tuple1 = (3, 4, "BD", )

tuple2 = ("String")

tuple3 = (5,)
print(type(tuple1), type(tuple2), type(tuple3))


numbers = (10, 20, 30, 40, 50, 60, 20)
print(numbers)


print(numbers[:34])


# tuple methods

#count method
print(numbers.count(20))

# index method
print(numbers.index(20))

student = ("Arjun", "Python", 39)

name, course, age = student
print(name, course, age)


# set
# it is mutable
# it does not hold duplicate values
# it is unordered
# slicing will not work
# indexing will not work

a = {1, 2, 4, 6, 7, 4, 6}
print(a)

a.add(8)
print(a)

a.remove(8)
print(a)


