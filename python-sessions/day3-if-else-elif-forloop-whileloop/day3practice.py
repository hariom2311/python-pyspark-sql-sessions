# if, else, elif, for loop while loop

# if else, elif

# status_code = 201

# if status_code==201:
#     print("Created")

# if status_code==200:
#     print("Get")

# if status_code=='403':
#     print('forbidden')


# number = 1

# if number>8:
#     print('greater>8')
# elif number>5:
#     print('greater>5')
# elif number>2:
#     print('greater>2')
# else:
#     print('less then equal to 1')


# 0 1 2, 3, 4, 5, 6, 7, 8, 9, 10

# for i in range(11):
#     print(i)

# 1, 3, 5, 7, 9

# for i in range(1, 10, 2):
#     print(i)

# list1 = [5, 3, 9, 0, 11, 10]

# # output = 9, 11, 10

# for value in list1:
#     if value > 5:
#         print(value)

# print('===========')
# for value in list1[1:3]:
#     if value > 5:
#         print(value)

# # while loop

# number = 1
# while number < 100:
#     print(number)
#     number += 1 # number = number+1




# # problem solving

# list1 = [1, 3, 5, 8]

# # problem: remove first and last value fromt the list and give sum of it 
# output = [3, 5]
# sum_output = 9

# phone_numbers = [
#     '+91 9393993937',
#     '+1 9393993399',
#     '+201 9339034252',
#     '8838383800',
#     '+2103838383830'
# ]
# output = []
# for number in phone_numbers:
#     digit = number.replace(" ", "")
#     output.append(int(digit[-10:]))
# print(output)

# # output = [9393993937, 9393993399, 9339034252, 8838383800, 3838383830]

# emails = ['abc@google.com', 'hariom@dataengineerigndaily.com',
#           'syed@gmail.com',
#           'ashish@yahoo.com', 'anurag@dataengineerigndaily.com'
# ]
# output = ['google.com', 'dataengineerigndaily.com', 'gmail.com']




# names = [' hAriOm ', ' wjw  lei ', 'RaHu L']
# output = ['Hariom', 'Wjwlei', 'Rahul']

# output = [name.title() for name in names]

# orders = ['order_393993.csv', 'order_773773.csv', 'order_393939.csv']
# output = [393993, 773773, 393939]

# [ 
#     order.split('.')[0][-6:]
#     for order in orders
# ]

# for order in orders:
#     print(order.split('.')[0][-6:])


# input = [393993, 773773, 393939]
# output = ['order_393993.csv', 'order_773773.csv', 'order_393939.csv']

# for inpt in input:
#     print(f"order_{inpt}.csv")

# numbers = [1, 2, 3, 4, 5]
# output = []
# for num in numbers:
#     output.append(num**2)
# print(output)


# List comprehension
# output = [ 
#     num**2 for num in numbers
# ]
# print(output)


# number = [1, 2, 3, 4, 5, 6]

# for num in input:
#     if num%2==0:
#         print(num)


# output = [num for num in number if num%2==0 ]
# print(output)



# output = ["Even" if num%2==0 else "Odd" for num in number]
# print(output)


# matrix = [
#     [1, 2],
#     [3, 4],
#     [5, 6]
# ]
# expted output should be [1, 2, 3, 4, 5, 6]

# output = [
#     num 
#         for row in matrix
#         for num in row
#     ]
# print(output)

# numbers = [1, 2, 3, 4, 5, 6]
# output = {}
# expected output = { 1: 1, 2: 4, 3: 9, 4: 16, 5: 25, 6: 36}

# for num in numbers:
#     output[num] = num**2
# print(output)

# output = {
#     num:num**2 for num in numbers
# }
# print(output)

# duplicate_numbers = [1, 2, 1, 1, 2, 3, 3, 5]
# print(duplicate_numbers)
# output = {}
# for number in duplicate_numbers:
#     if number not in output.keys():
#         output[number] = 1
#     else:
#         output[number]+=1
# print(output)

# 1st iteration number=1, output= {1:1}
# 2nd iteration number=2, output= {1:1, 2: 1}
# 3rd iteration number=1, output = {1:2, 2:1}
# 4th iteration number=1, output = {1:3, 2:1}
# 5th iteration number=2, output= {1:3, 2: 2}

keys = ['name', 'phone', 'email']
values = ['Rahul', 8388833, 'rahul@gmail.com']

# print(zip(keys, values))
# output = {}
# for key, value in zip(keys, values): # zip will make data like this [('name', 'rahul'), ('phone', 4388338)]
#     output[key] = value
# print(output)



# expected output = {
#     "name": "Rahul",
#     "phone": 8388833,
#     "email": 'rahul@gmail.com'
# }


# expected output 

for index, value in enumerate(values): # enuerate will hold values like this [(0, 'rahul'), (1, 3434343)]
    print(index, value)

# {
#     0: "Rahul",
#     1: 388383,
#     2: 'rahul@gmail.com'
# }