import matplotlib.pyplot as plt
import numpy as np

r = [1, 2, 3, 4, 5]
labels_a = ["Slabé", "Podpriemerné", "Priemerné", "Nadpriemerné", "Vynikajúce"]
labels_b = ["Nie", "Skôr nie", "Neviem", "Skôr áno", "Áno"]

a = [[0+1, 1+1, 1+1+1, 0+1, 0+1],
     [0, 2+1+1, 0+1, 0+2+1, 0],
     [0, 2, 0+1+1, 0+1+1, 0+1+1],
     [1, 1+1+1, 0, 0+1+1+1+1, 0],
     ]

b = [[0+1, 0+1, 2+1+1+1, 0+1, 0],
     [0, 1+1+1, 1, 0+1+1+1+1, 0],
     [0, 0+1, 1+1+1+1, 1+1, 0+1],
     [1+1, 0+1, 1+1+1, 0, 0+1+1],
     ]

c = [[0+2, 0+1+1, 1+1, 1+1, 0],
     [0+1+1, 0+1+1, 2+1+1, 0, 0],
     [0+1, 0+1+1, 0+1+1, 2+1, 0],
     [0+1+1, 0+1+1+1, 0, 2+1, 0],
     ]


for i in range(len(a)):
    assert np.sum(a[i]) == 8

for i in range(len(b)):
    assert np.sum(b[i]) == 8

for i in range(len(c)):
    assert np.sum(c[i]) == 8

assert len(a) == len(b) and len(b) == len(c)


# otazky z A 1 az 3 + 1 az
# x = np.array(labels_a)
# y = np.array(a[0])
# plt.bar(x, y)
# plt.title("A - Otázka 1.")
# plt.yticks(range(1, np.max(a[0])+1))
# plt.savefig("Name.png")

def plot_graph(data, type):
    for i in range(len(data)-1):
        x = np.array(labels_a)
        y = np.array(data[i])
        plt.bar(x, y)
        plt.title(f"{type} - Otázka č. {i+1}.")
        #plt.yticks(range(1, np.max(data[i]) + 1))
        plt.yticks(range(1, 8+1))
        plt.savefig(f"graf_{type}_otazka_{i+1}.png")
        plt.close()

    i = len(data)-1
    x = np.array(labels_b)
    y = np.array(data[i])
    plt.bar(x, y)
    plt.title(f"{type} - Otázka č. {i + 1}.")
    # plt.yticks(range(1, np.max(data[i]) + 1))
    plt.yticks(range(1, 8 + 1))
    plt.savefig(f"graf_{type}_otazka_{i + 1}.png")
    plt.close()


plot_graph(a, "A")
plot_graph(b, "B")
plot_graph(c, "C")

