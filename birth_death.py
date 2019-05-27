import numpy as np
import matplotlib.pyplot as plt


BIRTH_RATE = 4.0 
DEATH_RATE = 5.0

NUMBER_OF_BEDS = 10

# recursively solve for state probabilites

denom = [BIRTH_RATE / DEATH_RATE]

for i in range(1, NUMBER_OF_BEDS - 1):
    previous = denom[i-1]
    denom.append(previous * (BIRTH_RATE / DEATH_RATE))

print(denom)

probs = [1.0 / (1 + sum(denom))]

for i in range(1, NUMBER_OF_BEDS):
    previous = probs[i-1]
    probs.append((BIRTH_RATE / DEATH_RATE) * previous)


print(probs)

numbers = [x for x in range(NUMBER_OF_BEDS)]


plt.plot(numbers, probs, '-o')
plt.ylabel("Percentage of time in state")
plt.xlabel("Number of beds filled")
plt.ylim(0, max(probs) + 0.1)
plt.xticks([x for x in range(NUMBER_OF_BEDS)])
plt.show()

