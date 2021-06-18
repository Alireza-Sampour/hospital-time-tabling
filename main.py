from random import randint
from itertools import groupby
from math import floor

# define variables
n_pop = 50
MAX_N_GEN = 10000
best_answers = 0.3
mutation_rate = 0.1
alpha = 0.5
number_of_sections = 3
number_of_shifts = 3
number_of_nurses = 9
number_of_work_days = 7
nurses = [1, 2, 3, 4, 5, 6, 7, 8, 9]
number_of_genes = number_of_shifts * number_of_work_days
days = {1: "Saturday", 2: "Sunday", 3: "Monday", 4: "Tuesday", 5: "Wednesday", 6: "Thursday", 7: "Friday"}
nurses_associated_with_sections = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3}
sections_nurses = {key: sum(x == key for x in nurses_associated_with_sections.values()) for key in range(1, number_of_sections + 1)}
population = [[randint(1, number_of_nurses) for _ in range(number_of_sections * number_of_genes)] for _ in range(n_pop)]


def map_chromosome_to_human_readable_text(chromosome: list) -> None:
    sections = chunk_it(chromosome, number_of_sections)
    for idx, sec in enumerate(sections, start=1):
        print(f"---------------section {idx}--------------------")
        for i in range(1, number_of_work_days+1):
            sub_sec = chunk_it(sec, number_of_work_days)
            print(f"{days.get(i)}: ", end="")
            for j in range(number_of_shifts):
                print(f"{sub_sec[i-1][j]}", end=" ")
            print()


def chunk_it(seq: list, num: int) -> list:
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def fitness(x: list) -> float:
    score = 0
    sections = chunk_it(x, number_of_sections)
    if not set(nurses).issubset(x):  # is all nurses in chromosome?
        score += len(set(nurses).difference(x))
    for idx, sec in enumerate(sections, start=1):
        for i in range(len(sec)):
            nurse = sec[i]
            if nurses_associated_with_sections.get(nurse) != idx:  # is nurse is in correct section?
                score += 5
            if i != len(sec)-1 and sec[i] == sec[i+1]:  # check there is duplicated continuous nurse in section?
                score += 5
    print(f"fitness is: {score}")
    return score


def check_constraints(x: list) -> int:
    good_parents_idx = []
    best_index = -1
    for index, parent in enumerate(x):
        flag = False
        if set(nurses).issubset(parent):  # all nurses is in chromosome?
            if len([k for k, g in groupby(parent) if sum(1 for _ in g) > 1]) == 0:  # check there is duplicated continuous nurse in parent?
                sections = chunk_it(parent, number_of_sections)
                last_nurse_id = 1
                for idx, sec in enumerate(sections, start=1):
                    if len(set(sec).difference(list(range(last_nurse_id, sections_nurses.get(idx) + last_nurse_id)))) == 0:  # check all nurses in section {idx} is correct nurses that should be in this section?
                        flag = True
                    else:
                        flag = False
                        break
                    last_nurse_id += sections_nurses.get(idx)
                if flag:
                    good_parents_idx.append(index)

    if len(good_parents_idx) > 1:
        good_parent_fitness = 99999
        for index in good_parents_idx:
            tmp = fitness(x[index])
            if tmp < good_parent_fitness:
                good_parent_fitness = tmp
                best_index = index
    elif len(good_parents_idx) == 1:
        best_index = good_parents_idx[0]
    return best_index


for i in range(MAX_N_GEN):
    print(f"Gen {i+1}")
    if (ans := check_constraints(population)) != -1:
        map_chromosome_to_human_readable_text(population[ans])
        exit(0)
    pop_fitness = {}
    for j in range(n_pop):
        pop_fitness[j] = fitness(population[j])

    # select
    best_fitness = sorted(pop_fitness, key=pop_fitness.get, reverse=True)[-n_pop//2:]

    childs = []
    for idx1, idx2 in zip(best_fitness[0::2], best_fitness[1::2]):
        childs.append(population[idx1][:(len(population[idx1]) - 1) // 2 + 10])
        childs.append(population[idx2][:(len(population[idx2]) - 1) // 2 + 10])
        t = [floor(alpha * (population[idx1][i] + population[idx2][i])) for i in range((len(population[idx1]) - 1) // 2 + 10, len(population[idx1]))]
        childs[len(childs) - 2] += t
        childs[len(childs) - 1] += t

    # last parent add
    if n_pop % 2 == 0:
        childs.append(population[best_fitness[-1]][:(len(population[best_fitness[-1]]) - 1) // 2 + 10])
        t = [floor(alpha * (population[best_fitness[-1]][i] + population[best_fitness[0]][i])) for i in range((len(population[best_fitness[-1]]) - 1) // 2 + 10, len(population[best_fitness[-1]]))]
        childs[len(childs) - 1] += t

    not_chosen_parents = list(set(pop_fitness.keys()).difference(best_fitness))
    for p in not_chosen_parents:
        population[p] = childs.pop()


    # mutation
    rand_pop_idx1 = randint(0, n_pop - 1)
    rand_pop_idx2 = randint(0, n_pop - 1)
    rand_gene_idx1 = randint(0, (number_of_genes*number_of_sections) - 1)
    rand_gene_idx2 = randint(0, (number_of_genes*number_of_sections) - 1)
    population[rand_pop_idx1][rand_gene_idx1], population[rand_pop_idx2][rand_gene_idx2] = population[rand_pop_idx2][rand_gene_idx2], population[rand_pop_idx1][rand_gene_idx1]

mx = 0
ind = 0
for j in range(n_pop):
    x = fitness(population[j])
    if x > mx:
        mx = x
        ind = j

print(f"final population is:")
map_chromosome_to_human_readable_text(population[ind])