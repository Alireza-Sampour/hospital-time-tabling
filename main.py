from random import randint, choices
from math import floor, ceil

# Define variables
NUMBER_OF_SECTIONS = 3
NUMBER_OF_WORK_DAYS = 7
SECTION_TO_SHIFT = {1: 3, 2: 3, 3: 3}
NUMBER_OF_GENES = 3 * list(SECTION_TO_SHIFT.values()).count(3) * NUMBER_OF_WORK_DAYS + 2 * list(
    SECTION_TO_SHIFT.values()).count(2) * NUMBER_OF_WORK_DAYS
NUMBER_OF_POPULATION = NUMBER_OF_GENES
SELECTION_PART = (NUMBER_OF_GENES - 1) // 2 + 20
NURSES = [1, 2, 3, 4, 5, 6, 7, 8, 9]
NURSE_TO_SECTION = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3}
SECTION_TO_NUMBER_OF_NURSES = {key: sum(x == key for x in NURSE_TO_SECTION.values()) for key in
                               range(1, NUMBER_OF_SECTIONS + 1)}


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
    sections = chunk_chromosome(chromosome)
    days = {1: "Saturday", 2: "Sunday", 3: "Monday", 4: "Tuesday", 5: "Wednesday", 6: "Thursday", 7: "Friday"}
    for idx, sec in enumerate(sections, start=1):
        print(f"---------------section {idx}--------------------")
        for i in range(1, NUMBER_OF_WORK_DAYS + 1):
            sub_sec = chunk_it(sec, NUMBER_OF_WORK_DAYS)
            print(f"{days.get(i)}: ", end="")
            for j in range(SECTION_TO_SHIFT.get(idx)):
                print(f"{sub_sec[i - 1][j]}", end=" ")
            print()
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
    if not set(NURSES).issubset(x):  # Is all nurses in chromosome?
        return 999

    for idx, sec in enumerate(sections, start=1):
        for i in range(len(sec)):
            nurse = sec[i]
            if NURSE_TO_SECTION.get(nurse) != idx:  # Is nurse is in correct section?
                return 999
            if i != len(sec) - 1 and sec[i] == sec[i + 1]:  # Check there is duplicated continuous nurse in section?
                score += 5

        nurse_count_in_section = [sec.count(nurse) for nurse in set(sec)]
        score += max(nurse_count_in_section) - min(
            nurse_count_in_section)  # Make the attendance of nurses in week equal

    print(f"fitness is: {score}")

    return score


def main():
    alpha = 0.5
    minimum_possible_score = 0
    max_number_generation = 10_000
    mutation_rate = 0.01

    # Find minimum possible fitness value
    for i in range(1, NUMBER_OF_SECTIONS + 1):
        minimum_possible_score += (SECTION_TO_SHIFT.get(i) * NUMBER_OF_WORK_DAYS) % SECTION_TO_NUMBER_OF_NURSES.get(i)

    # print(minimum_possible_score)
    # exit(0)
    for i in range(max_number_generation):
        pop_fitness = {}

        print(f"Gen {i + 1}")

        # Calculate fitness value
        for j in range(NUMBER_OF_POPULATION):
            pop_fitness[j] = fitness(population[j])
            if list(pop_fitness.values())[-1] == minimum_possible_score:  # Is termination criteria satisfied?
                map_chromosome_to_human_readable_text(population[j])
                exit(0)

        # Select
        best_fitness = sorted(pop_fitness, key=pop_fitness.get, reverse=True)[-NUMBER_OF_POPULATION // 2:]

        if i + 1 == max_number_generation:
            print(f"final population is with fitness {pop_fitness.get(best_fitness[-1])}:")
            map_chromosome_to_human_readable_text(population[best_fitness[-1]])

        # Crossover
        childs = []
        for index, (idx1, idx2) in enumerate(zip(best_fitness[0::2], best_fitness[1::2]), start=1):
            if index % 2 == 0:
                childs.append(population[idx1][:SELECTION_PART])
                childs.append(population[idx2][:SELECTION_PART])
                t = [floor(alpha * (population[idx1][i] + population[idx2][i])) for i in
                     range(SELECTION_PART, NUMBER_OF_GENES)]
                childs[len(childs) - 2] += t
                childs[len(childs) - 1] += t
            else:
                y = NUMBER_OF_GENES - SELECTION_PART
                childs.append(population[idx1][y:])
                childs.append(population[idx2][y:])
                t = [floor(alpha * (population[idx1][i] + population[idx2][i])) for i in range(0, y)]
                childs[len(childs) - 2] += t
                childs[len(childs) - 1] += t

        # If number of parents is even number must add last parent separately
        if NUMBER_OF_POPULATION % 2 == 0:
            childs.append(population[best_fitness[-1]][:SELECTION_PART])
            t = [floor(alpha * (population[best_fitness[-1]][i] + population[best_fitness[0]][i])) for i in
                 range(SELECTION_PART, NUMBER_OF_GENES)]
            childs[len(childs) - 1] += t

        # Mutation
        for _ in range(ceil(mutation_rate * NUMBER_OF_POPULATION)):
            rand_pop_idx1 = randint(0, len(childs) - 1)
            rand_pop_idx2 = randint(0, len(childs) - 1)
            rand_gene_idx1 = randint(0, NUMBER_OF_GENES - 1)
            rand_gene_idx2 = randint(0, NUMBER_OF_GENES - 1)
            childs[rand_pop_idx1][rand_gene_idx1], childs[rand_pop_idx2][rand_gene_idx2] = childs[rand_pop_idx2][
                                                                                               rand_gene_idx2], \
                                                                                           childs[rand_pop_idx1][
                                                                                               rand_gene_idx1]

        # Replace parents with low fitness value with new children's
        not_chosen_parents = list(set(pop_fitness.keys()).difference(best_fitness))
        for p in not_chosen_parents:
            population[p] = childs.pop()


if __name__ == "__main__":
    main()
