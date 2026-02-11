# Chapter 5 If

car = 'Audi'
print(car == 'audi',car.lower() == 'audi')

current_users = ['jack','mike']
new_users = ['mary','Mike','tom','bob','jack']
for user in new_users :
    if user.lower() in current_users :
        print(f"{user.title()} has been used!")
    else :
        print(f"{user.title()} hasn't been used!")

num = 15
if num%10 == 1 :
    print(f"{num}st")
elif num%10 == 2 :
    print(f"{num}nd")
elif num%10 == 3 :
    print(f"{num}rd")
else :
    print(f"{num}th")





