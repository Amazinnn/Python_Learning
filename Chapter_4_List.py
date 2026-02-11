# Chapter 4 List

animals = ['dog','cat','bird']
for animal in animals :
    print(f"{animal.title()}s could be great pets!")
print("Any of these animals would make a great pet!")

a_1 = [num for num in range(1,21)]
print(a_1)

a_2 = [num for num in range (1,1_001)]
print(min(a_2),max(a_2))
# print(a_2)

a_3 = [num for num in range(3,31,3)]
print(a_3)

a_4 = [num**3 for num in range (1,11)]
print(a_4)

players = ['charles','martina','michael','florence','eli']
print(players[-2:])
print(players[-2:-1])
print(players[-1:1])
print(players[-1:0])
print(players[::2])

list1=[2]
list2=[2,]
tuple1=(2)
tuple2=(2,)
print(list1)
print(list2)
print(tuple1)
print(tuple2)
list1 = list2
tuple1 = tuple2
print(list1)
print(tuple1)






