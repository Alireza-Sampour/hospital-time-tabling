from random import randint, choices
from math import ceil

import openpyxl as xl
import time

# Define variables
NUMBER_OF_WORK_DAYS = 7
SECTION_TO_SHIFT = {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3}
NUMBER_OF_SECTIONS = len(SECTION_TO_SHIFT)
NUMBER_OF_GENES = 3 * list(SECTION_TO_SHIFT.values()).count(3) * NUMBER_OF_WORK_DAYS + 2 * list(
    SECTION_TO_SHIFT.values()).count(2) * NUMBER_OF_WORK_DAYS
NUMBER_OF_POPULATION = NUMBER_OF_GENES
SELECTION_PART = (NUMBER_OF_GENES - 1) // 2 + 20
NURSE_TO_SECTION = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2, 11: 3, 12: 3, 13: 3, 14: 3, 15: 3, 16: 4, 17: 4, 18: 4, 19: 4, 20: 4, 21: 5, 22: 5, 23: 5, 24: 5, 25: 5, 26: 6, 27: 6, 28: 6, 29: 6, 30: 6}
SECTION_TO_NUMBER_OF_NURSES = {key: sum(x == key for x in NURSE_TO_SECTION.values()) for key in
                               range(1, NUMBER_OF_SECTIONS + 1)}
preferences = {1: {'shifts': [1, 3], 'days': [1]}, 2: {'shifts': [2, 3], 'days': [4]}}


def create_population() -> list:
    pop = []
    for i in range(NUMBER_OF_POPULATION):
        last_n_id = 1
        pop.append([])

        for se in range(1, NUMBER_OF_SECTIONS + 1):
            pop[i].extend(choices(range(last_n_id, SECTION_TO_NUMBER_OF_NURSES.get(se) + last_n_id),
                                  k=SECTION_TO_SHIFT.get(se) * NUMBER_OF_WORK_DAYS))
            last_n_id += SECTION_TO_NUMBER_OF_NURSES.get(se)
    return pop


# Create population
population = create_population()


def map_chromosome_to_human_readable_text(chromosome: list) -> None:
    base_path = "/home/alireza/Desktop/"
    file_path = base_path + "template.xlsx"
    wb = xl.load_workbook(file_path)
    excel_shifts = {0: 'B', 1: 'C', 2: 'D'}

    sections = chunk_chromosome(chromosome)

    for idx, sec in enumerate(sections, start=1):
        target = wb.copy_worksheet(wb.active) if idx != 1 else wb.active
        target.title = f"Section {idx}"
        target['A1'] = f"Section #{idx}"

        for i in range(1, NUMBER_OF_WORK_DAYS + 1):
            sub_sec = chunk_it(sec, NUMBER_OF_WORK_DAYS)

            if SECTION_TO_SHIFT.get(idx) == 2:
                target.delete_cols(4)
            for j in range(SECTION_TO_SHIFT.get(idx)):
                target[f'{excel_shifts.get(j)}{i + 1}'] = sub_sec[i - 1][j]

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

    for i in range(1, NUMBER_OF_SECTIONS + 1):
        out.append(seq[last:last + SECTION_TO_SHIFT.get(i) * NUMBER_OF_WORK_DAYS])
        last += SECTION_TO_SHIFT.get(i) * NUMBER_OF_WORK_DAYS

    return out


def fitness(x: list) -> float:
    score = 0
    sections = chunk_chromosome(x)
    if not set(range(1, len(NURSE_TO_SECTION) + 1)).issubset(x):  # Is all nurses in chromosome?
        return 999

    for idx, sec in enumerate(sections, start=1):
        for i in range(len(sec)):
            nurse = sec[i]
            if NURSE_TO_SECTION.get(nurse) != idx:  # Is nurse is in correct section?
                return 999
            if i != len(sec) - 1 and sec[i] == sec[i + 1]:  # Check there is duplicated continuous nurse in section?
                score += 5

        if set(range(max(sec) - SECTION_TO_NUMBER_OF_NURSES.get(idx), max(sec)+1)).issuperset(preferences.keys()):  # Check if nurses in section idxth has preferences?
            for t in (set(range(max(sec) - SECTION_TO_NUMBER_OF_NURSES.get(idx), max(sec)+1)).intersection(preferences.keys())):
                for d in preferences.get(t).get('days'):  # Check nurse is on a preferred day?
                    if t not in sec[(d-1) * SECTION_TO_SHIFT.get(idx):((d-1) * SECTION_TO_SHIFT.get(idx)) + SECTION_TO_SHIFT.get(idx)]:
                        score += 1
                for s in preferences.get(t).get('shifts'):  # Check nurse is on a preferred shift?
                    if sec[(s-1)::SECTION_TO_SHIFT.get(idx)].count(t) < ((len(sec) // SECTION_TO_NUMBER_OF_NURSES.get(idx)) // 2) + 1:
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
    for k in range(1, NUMBER_OF_SECTIONS+1):
        minimum_possible_score += 0 if (SECTION_TO_SHIFT.get(k) * NUMBER_OF_WORK_DAYS) % SECTION_TO_NUMBER_OF_NURSES.get(k) == 0 else 1

    # Find maximum possible score
    maximum_possible_score += minimum_possible_score
    for v in preferences.values():
        for r in v.values():
            maximum_possible_score += len(r)

    for i in range(max_number_generation):
        pop_fitness = {}

        if answer.get('is_find') and i - answer.get('generation') > 300:
            map_chromosome_to_human_readable_text(answer.get('population'))
            return None

        print(f"Gen {i + 1}")

        # Calculate fitness value
        for j in range(NUMBER_OF_POPULATION):
            pop_fitness[j] = fitness(population[j])

            # Is termination criteria satisfied?
            if list(pop_fitness.values())[-1] == minimum_possible_score:
                map_chromosome_to_human_readable_text(population[j])
                return None

            elif list(pop_fitness.values())[-1] < maximum_possible_score and list(pop_fitness.values())[-1] < answer.get('fitness'):
                answer['is_find'] = True
                answer['generation'] = i
                answer['population'] = population[j]
                answer['fitness'] = list(pop_fitness.values())[-1]

        # Select
        best_fitness = sorted(pop_fitness, key=pop_fitness.get, reverse=True)[-NUMBER_OF_POPULATION // 2:]

        if i + 1 == max_number_generation:
            map_chromosome_to_human_readable_text(population[best_fitness[-1]])
            return None

        # Crossover
        childs = []
        for index, (idx1, idx2) in enumerate(zip(best_fitness[0::2], best_fitness[1::2]), start=1):
            childs.append(population[idx1][:SELECTION_PART] + population[idx2][SELECTION_PART:])
            childs.append(population[idx2][:SELECTION_PART] + population[idx1][SELECTION_PART:])

        # If number of parents is even number must add last parent separately
        if NUMBER_OF_POPULATION % 2 == 0:
            childs.append(population[best_fitness[-1]][:SELECTION_PART] + population[best_fitness[-2]][SELECTION_PART:])

        # Mutation
        for _ in range(ceil(mutation_rate * NUMBER_OF_POPULATION)):
            rand_pop_idx1 = randint(0, len(childs) - 1)
            rand_pop_idx2 = randint(0, len(childs) - 1)
            rand_sec_idx = randint(1, NUMBER_OF_SECTIONS)
            tmp = chunk_chromosome(population[0])
            x = 0
            for i in range(rand_sec_idx-1):
                x += len(tmp[i])
            y = x + (SECTION_TO_SHIFT.get(rand_sec_idx) * NUMBER_OF_WORK_DAYS) - 1
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
