import pickle

with open("rmi_sobrante_a", "rb") as file:
    rmi_sobrante_a = pickle.load(file)


with open("rmi_sobrante_b", "rb") as file:
    rmi_sobrante_b = pickle.load(file)


with open("desperdicios_a", "rb") as file:
    desperdicios_a = pickle.load(file)


with open("desperdicios_b", "rb") as file:
    desperdicios_b = pickle.load(file)

# i = 0
# for x in rmi_sobrante_a:
#     color = x[0]
#     print(color, rmi_sobrante_a[i][1], rmi_sobrante_b[i][1])
#     i += 1

# i = 0
# for x in desperdicios_a:
#     color, size = x[0], x[1]
#     print(color, size, desperdicios_a[i][2], desperdicios_b[i][2])
#     i+=1
