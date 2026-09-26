#PROBLEM SOLVING

# short circuite evaluation
# a = 9

# if a or ldfjlsdjflsdjlfdj:
#     print("inside if")


# list1 = [3, 5, 2, 0, 3, 0, 8, 5]

# expected output = [8, 3, 2, 3]
# print(list1[-2::-2])

# list2 = [[1, 2], [3, 4], [5, 6, 7, [1, 2, 3]]]

# listoutput = [1, 2, 3, 4, 5, 6, 7, 1, 2, 3]


# 1st iteration item = [1, 2] -> flatten([1, 2]) ->


# def flatten(data): 
#     result = []
#     for item in data:
#         try:
#             result.extend(flatten(item)) # try to exted(1)

#         except TypeError:
#             result.append(item)
#     return result

# print(flatten(list2))

# n = 3

# 1st time n=3 it will print - Hello and call hell(n-1=2) 2-1 


# def hell(n):
#     if n == 0:
#         return
#     print(f"Hello {n}")
#     hell(n-1)


# hell(n)

# users = [
#     {"id": 1, "name": "  amit sharma ", "age": 25},
#     {"id": 2, "name": "RAHUL KUMAR", "age": 30},
#     {"id": 3, "name": "", "age": 22},
#     {"id": 4, "name": " priya ", "age": None},
#     {"id": 5, "name": "  raj  ", "age": 28}
# ]

# clean_user = []
# for user in users:
#     name = user["name"].strip()
#     age = user["age"]
#     if name == "":
#         continue
#     if age is None:
#         continue
#     user["name"] = name.title()  # rajesh khanna-> Rajesh Khanna
#     clean_user.append(user)

# print(clean_user)


# Requirements
# Remove records where name is empty.
# Remove records where age is missing.
# Strip spaces from names.
# Convert names to title case.


# list1 = [1, 2, 3, 4, 5]

# for num in list1:
#     if num > 3:
#         break
#     print(num)


# lsit_1 =  [1, 2, 1, 3, 4, 2]

# output=[]
# iter1
# output = [1, 2, 3, 4]

# # iter2

# output [1, 2, 3, 4]



# Remove duplicates based on id
# Hashset

# customers = [
#     {"id": 101, "name": "Amit", "email": "amit@gmail.com", "weight": 44},
#     {"id": 102, "name": "Rahul", "email": "rahul@gmail.com", "weight": 87},
#     {"id": 101, "name": "Amit", "email": "amit@gmail.com", "weight": 65},
#     {"id": 103, "name": "Priya", "email": "priya@gmail.com", "weight": 61},
#     {"id": 102, "name": "Rahul", "email": "rahul@gmail.com", "weight": 70}
# ]


# output = {}

# for customer in customers:
#     output[customer[id]] = customer
# print(list(output.values()))

# # 1st Iteration = o
# output = {101: {"id": 101, "name": "Amit", "email": "amit@gmail.com", "weight": 44}}

# # 2nd iteration 
# output = {
#     101: {"id": 101, "name": "Amit", "email": "amit@gmail.com", "weight": 44},
#     102: {"id": 102, "name": "Rahul", "email": "rahul@gmail.com", "weight": 87}
# }

# # 3rd Iteration
# output = {
#     101: {"id": 101, "name": "Amit", "email": "amit@gmail.com", "weight": 65},
#     102: {"id": 102, "name": "Rahul", "email": "rahul@gmail.com", "weight": 87},

# }

# # 4th iteration
# output = {
#     101: {"id": 101, "name": "Amit", "email": "amit@gmail.com", "weight": 65},
#     102: {"id": 102, "name": "Rahul", "email": "rahul@gmail.com", "weight": 87},
#     103: {"id": 103, "name": "Priya", "email": "priya@gmail.com", "weight": 61},
# }

# # 5th iteration
# output = {
#     101: {"id": 101, "name": "Amit", "email": "amit@gmail.com", "weight": 65},
#     102: {"id": 102, "name": "Rahul", "email": "rahul@gmail.com", "weight": 70},
#     103: {"id": 103, "name": "Priya", "email": "priya@gmail.com", "weight": 61},
# }

# output.values()
# list({"id": 101, "name": "Amit", "email": "amit@gmail.com", "weight": 65}, {"id": 102, "name": "Rahul", "email": "rahul@gmail.com", "weight": 70})


# my_set = set()

# output = []

# for customer in customers[::-1]:

#     id = customer["id"]
#     if id not in my_set:
#         output.append(customer)
#         my_set.add(id)
#     print(output)


# emails = [
#     "  AMIT@GMAIL.COM ",
#     "rahul@gmail.com",
#     "priya@gmail",
#     "",
#     "  raj@yahoo.com",
#     "invalid-email",
#     None,
#     "rahul.kumar@gmail"
# ]
# Requirements:

# Handle None
# Remove spaces
# Convert to lowercase
# Validate @
# Validate .
# Return None for invalid emails


# for email in emails:
#     if email is None:
#         continue
#     email = email.strip().lower()

#     if email == "" or "@" not in email or "." not in email.split('@')[1]:
#         continue

#     print(email)


# employees = [
#     {"id": 1, "name": "Amit", "salary": 50000},
#     {"id": 2, "name": "Rahul"},
#     {"id": 3, "name": "Priya", "salary": None},
#     {"id": 4, "name": "Raj", "salary": 70000}
# ]

for employee in employees:
    if employee.get("salary"):
        employee["salary_status"] = "available"
    else:
        employee["salary"] = 0
        employee["salary_status"] = "missing"
    print(employee)



# employees_output = [
#     {"id": 1, "name": "Amit", "salary": 50000, "salary_status": "available"},
#     {"id": 2, "name": "Rahul", "salary": 0, "salary_status": "missing"},
#     {"id": 3, "name": "Priya", "salary": 0, "salary_status": "missing"},
#     {"id": 4, "name": "Raj", "salary": 70000, "salary_status": "available"}
# ]



transactions = [
    {"id": 1, "customer": "Amit", "amount": 500},
    {"id": 2, "customer": "Rahul", "amount": -100},
    {"id": 3, "customer": "Priya", "amount": 700},
    {"id": 4, "customer": "Raj", "amount": None},
    {"id": 5, "customer": "Amit", "amount": 500},
    {"id": 3, "customer": "Priya", "amount": 700}
]

negative_transactions = []
missing_transactions = []
duplicate_transactions = []
valid_transactions = []


# Find:

# Negative amounts
# Missing amounts
# Duplicate transaction IDs
# Valid transactions