import random
def modified(a):
    b = a.copy()
    b[1] = 10
    return b
rnd = [1,2,3,5,4,5]

rnd1 = modified(rnd)

print(rnd,rnd1)
#print(random.choice(rnd))

print(rnd.index(max(rnd)))
