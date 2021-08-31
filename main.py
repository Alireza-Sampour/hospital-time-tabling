from random import randint, choices
from math import ceil

import openpyxl as xl
import time
import os

section_to_name = {}
section_to_shift = {}
preferences = {}
nurse_to_name = {}
nurse_to_section = {}
file_name = "template.xlsx"


# Read data from file_name
def read_data():
    base_path = os.getcwd() + "/"
    file_path = base_path + file_name
    wb = xl.load_workbook(file_path)
    sheet = wb['inputs']

    index1 = 1
    for index, (x1, x2, x3, x4, x5) in enumerate(zip(sheet['A'][1:], sheet['B'][1:], sheet['C'][1:], sheet['D'][1:], sheet['E'][1:]),
                                                 start=1):
        if x2.value not in section_to_name.values():
            section_to_name[index1] = x2.value
            section_to_shift[index1] = x3.value
            index1 += 1
        if x4.value is not None:
            preferences[index] = {}
            preferences[index].setdefault('days', [int(x) for x in str(x4.value).split(',')])
        if x5.value is not None:
            preferences[index].setdefault('shifts', [int(x) for x in str(x5.value).split(',')])
        nurse_to_name[index] = x1.value
        nurse_to_section[index] = index1 - 1


def create_population() -> list:
    pop = []
    for i in range(number_of_population):
        last_n_id = 1
        pop.append([])

        for se in range(1, number_of_sections + 1):
            pop[i].extend(choices(range(last_n_id, section_to_number_of_nurses.get(se) + last_n_id),
                                  k=section_to_shift.get(se) * number_of_work_days))
            last_n_id += section_to_number_of_nurses.get(se)
    return pop


# Read data
read_data()


# Define variables
number_of_work_days = 7
number_of_sections = len(section_to_shift)
number_of_genes = 3 * list(section_to_shift.values()).count(3) * number_of_work_days + 2 * list(
    section_to_shift.values()).count(2) * number_of_work_days
number_of_population = number_of_genes
selection_part = (number_of_genes - 1) // 2 + 20
section_to_number_of_nurses = {key: sum(x == key for x in nurse_to_section.values()) for key in
                               range(1, number_of_sections + 1)}

# Create population
population = create_population()


def save_chromosome_to_file(chromosome: list) -> None:
    base_path = os.getcwd() + "/"
    file_path = base_path + file_name
    wb = xl.load_workbook(file_path)
    del wb['inputs']
    excel_shifts = {0: 'B', 1: 'C', 2: 'D'}

    sections = chunk_chromosome(chromosome)
    wb.active = wb['Section 1']
    for idx, sec in enumerate(sections, start=1):
        target = wb.copy_worksheet(wb[section_to_name.get(1)]) if idx != 1 else wb['Section 1']
        target.title = section_to_name.get(idx)
        target['A1'] = section_to_name.get(idx)

        for i in range(1, number_of_work_days + 1):
            sub_sec = chunk_it(sec, number_of_work_days)

            if section_to_shift.get(idx) == 2:
                target.delete_cols(4)
            for j in range(section_to_shift.get(idx)):
                target[f'{excel_shifts.get(j)}{i + 1}'] = nurse_to_name.get(sub_sec[i - 1][j])

    wb.save(base_path + "output.xlsx")
    return None


def chunk_it(seq: list, num: int) -> list:
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def chunk_chromosome(seq: list) -> list:
    out = []
    last = 0

    for i in range(1, number_of_sections + 1):
        out.append(seq[last:last + section_to_shift.get(i) * number_of_work_days])
        last += section_to_shift.get(i) * number_of_work_days

    return out


def fitness(x: list) -> float:
    score = 0
    sections = chunk_chromosome(x)
    if not set(range(1, len(nurse_to_section) + 1)).issubset(x):  # Is all nurses in chromosome?
        return 999

    for idx, sec in enumerate(sections, start=1):
        for i in range(len(sec)):
            nurse = sec[i]
            if nurse_to_section.get(nurse) != idx:  # Is nurse is in correct section?
                return 999
            if i != len(sec) - 1 and sec[i] == sec[i + 1]:  # Check there is duplicated continuous nurse in section?
                score += 5

        if set(range(max(sec) - section_to_number_of_nurses.get(idx), max(sec)+1)).issuperset(preferences.keys()):  # Check if nurses in section idxth has preferences?
            for t in (set(range(max(sec) - section_to_number_of_nurses.get(idx), max(sec)+1)).intersection(preferences.keys())):
                for d in preferences.get(t).get('days'):  # Check nurse is on a preferred day?
                    if t not in sec[(d-1) * section_to_shift.get(idx):((d-1) * section_to_shift.get(idx)) + section_to_shift.get(idx)]:
                        score += 1
                for s in preferences.get(t).get('shifts'):  # Check nurse is on a preferred shift?
                    if sec[(s-1)::section_to_shift.get(idx)].count(t) < ((len(sec) // section_to_number_of_nurses.get(idx)) // 2) + 1:
                        score += 1

        nurse_count_in_section = [sec.count(nurse) for nurse in set(sec)]
        score += max(nurse_count_in_section) - min(
            nurse_count_in_section)  # Make the attendance of nurses in week equal

    print(f"fitness is: {score}")

    return score


def main() -> None:
    minimum_possible_score = 0
    maximum_possible_score = 0
    max_number_generation = 10_000
    mutation_rate = 0.15
    answer = {'is_find': False, 'generation': -1, 'population': [], 'fitness': 999}

    # Find minimum possible score
    for k in range(1, number_of_sections+1):
        minimum_possible_score += 0 if (section_to_shift.get(k) * number_of_work_days) % section_to_number_of_nurses.get(k) == 0 else 1

    # Find maximum possible score
    maximum_possible_score += minimum_possible_score
    for v in preferences.values():
        for r in v.values():
            maximum_possible_score += len(r)

    for i in range(max_number_generation):
        pop_fitness = {}

        if answer.get('is_find') and i - answer.get('generation') > 300:
            save_chromosome_to_file(answer.get('population'))
            return None

        print(f"Gen {i + 1}")

        # Calculate fitness value
        for j in range(number_of_population):
            pop_fitness[j] = fitness(population[j])

            # Is termination criteria satisfied?
            if list(pop_fitness.values())[-1] == minimum_possible_score:
                save_chromosome_to_file(population[j])
                return None

            elif list(pop_fitness.values())[-1] < maximum_possible_score and list(pop_fitness.values())[-1] < answer.get('fitness'):
                answer['is_find'] = True
                answer['generation'] = i
                answer['population'] = population[j]
                answer['fitness'] = list(pop_fitness.values())[-1]

        # Select
        best_fitness = sorted(pop_fitness, key=pop_fitness.get, reverse=True)[-number_of_population // 2:]

        if i + 1 == max_number_generation:
            save_chromosome_to_file(population[best_fitness[-1]])
            return None

        # Crossover
        childs = []
        for index, (idx1, idx2) in enumerate(zip(best_fitness[0::2], best_fitness[1::2]), start=1):
            childs.append(population[idx1][:selection_part] + population[idx2][selection_part:])
            childs.append(population[idx2][:selection_part] + population[idx1][selection_part:])

        # If number of parents is even number must add last parent separately
        if number_of_population % 2 == 0:
            childs.append(population[best_fitness[-1]][:selection_part] + population[best_fitness[-2]][selection_part:])

        # Mutation
        for _ in range(ceil(mutation_rate * number_of_population)):
            rand_pop_idx1 = randint(0, len(childs) - 1)
            rand_pop_idx2 = randint(0, len(childs) - 1)
            rand_sec_idx = randint(1, number_of_sections)
            tmp = chunk_chromosome(population[0])
            x = 0
            for i in range(rand_sec_idx-1):
                x += len(tmp[i])
            y = x + (section_to_shift.get(rand_sec_idx) * number_of_work_days) - 1
            rand_gene_idx1 = randint(x, y)
            rand_gene_idx2 = randint(x, y)
            childs[rand_pop_idx1][rand_gene_idx1], childs[rand_pop_idx2][rand_gene_idx2] = childs[rand_pop_idx2][
                                                                                               rand_gene_idx2], \
                                                                                           childs[rand_pop_idx1][
                                                                                               rand_gene_idx1]

        # Replace parents with low fitness value with new children's
        not_chosen_parents = list(set(pop_fitness.keys()).difference(best_fitness))
        for p in not_chosen_parents:
            population[p] = childs.pop()


if __name__ == "__main__":
    started = time.time()
    main()
    elapsed = time.time()
    print('Time taken:', elapsed - started)
