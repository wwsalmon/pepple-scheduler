import pandas as pd
import copy
import random
import matplotlib.pyplot as plt
from score import *
from utils import *

MAX_SEAT = 10
# This determines how strong regularization is
LAMBDA = .2


# random inital assignment obeying all rules
def initial_assignment(data, aux, max_seat_daily):
    people = data.columns.tolist()
    # maximum length is maximum group, slice at the front
    assignment_list = [1, 2, 3, 4, 5]
    # keys are groups, values are people
    groups = {1: [], 2: [], 3: [], 4: [], 5: []}
    # keys are people, values are groups
    people_groups = {}

    for person in people:
        people_groups[person] = []
        assignment_list_person = copy.deepcopy(assignment_list)
        num_day = aux.loc[person, 'NUM_DAY']
        for i in range(5):

            if aux.loc[person, 'OFF_' + str(i + 1)] == 1:
                assignment_list_person.remove(i + 1)
            if aux.loc[person, 'MUST_' + str(i + 1)] == 1:
                assignment_list_person.remove(i + 1)
                num_day -= 1
                groups[i + 1].append(person)
                people_groups[person].extend([i + 1])
                if num_day == 0:
                    break

        random.shuffle(assignment_list_person)
        if (len(assignment_list_person) < num_day):
            print("Not enough valid days to assign to" + str(person))
            people_groups[person].extend(assignment_list_person)
        else:
            people_groups[person].extend(assignment_list_person[:num_day])
        for group in assignment_list_person[:num_day]:
            groups[group].append(person)
        # if a group is full, it is not available anymore
        for i in assignment_list:
            if len(groups[i]) == max_seat_daily[i - 1]:
                assignment_list.remove(i)

    print(len(groups[1]), len(groups[2]), len(groups[3]), len(groups[4]), len(groups[5]))

    return groups, people_groups


def stochastic_clustering(data, iterations, aux, max_seat_daily):
    while True:
        groups, people_groups = initial_assignment(data, aux, max_seat_daily)
        # repeated initial assignment to guide evenness
        if properly_filled(groups, max_seat_daily):
            break
    print(interpret_result(groups, data))

    skipped = 0
    for _ in range(iterations):
        group_list = [1, 2, 3, 4, 5]
        # choose a random group and person
        while True:
            group = random.choice(group_list)
            person = random.choice(groups[group])

            if len(people_groups[person]) != 5:
                break

        # choose a swap group and person
        for k in people_groups[person]:
            group_list.remove(k)
        swap_group = random.choice(group_list)

        if aux.loc[person, 'OFF_' + str(swap_group)] == 1 or aux.loc[person, 'MUST_' + str(group)] == 1:
            skipped += 1
            continue

        loop_count = 1

        while True:
            swap_person = random.choice(groups[swap_group])
            loop_count += 1
            if loop_count > 100000:
                print(swap_person, people_groups, group)
                raise ValueError("Infinite loop")
            # avoid 2 identical names in one day
            if group not in people_groups[swap_person]:
                break
        if aux.loc[swap_person, 'OFF_' + str(group)] == 1 or aux.loc[swap_person, 'MUST_' + str(swap_group)] == 1:
            skipped += 1
            continue

        score_original, score_original_sum = all_score(data, groups)
        decide_if_swap(score_original, groups, people_groups, group, person, swap_group, swap_person, data)

        print(score_original, score_original_sum)

    # interpret and display final result
    print(str(skipped) + ' iterations skipped because of incompatibility.')
    show_result(groups, data)

    return groups, people_groups


def decide_if_swap(score_original, groups, people_groups, group, person, swap_group, swap_person, data):
    output = False
    groups_temp = copy.deepcopy(groups)
    groups_temp[group].remove(person)
    groups_temp[swap_group].append(person)
    groups_temp[swap_group].remove(swap_person)
    groups_temp[group].append(swap_person)
    total_opportunities = get_potential_score(data, groups)
    if regularized_score(all_score(data, groups_temp)[0], total_opportunities, LAMBDA) > regularized_score(
            score_original, total_opportunities, LAMBDA):
        output = True
        groups[group].remove(person)
        groups[swap_group].append(person)
        groups[swap_group].remove(swap_person)
        groups[group].append(swap_person)
        people_groups[person].remove(group)
        people_groups[person].append(swap_group)
        people_groups[swap_person].remove(swap_group)
        people_groups[swap_person].append(group)
    return output


def run_algorithm(max_seat, data, aux):
    max_seat_daily = compute_max_seat_daily(max_seat, aux)
    groups, people_groups = stochastic_clustering(data, 100, aux, max_seat_daily)
    set_maximum(max_seat, groups, people_groups, data, aux)
    print(groups, people_groups)


if __name__ == '__main__':
    df = pd.read_excel(r'Fake Data Sherry V2.xlsx', sheet_name='Interaction V or IRL')
    aux = pd.read_excel(r'Fake Data Sherry V2.xlsx', sheet_name='BU and Preference')

    train_data = prep_data(df)
    aux = prep_aux(aux)
    max_seat_daily = compute_max_seat_daily(MAX_SEAT, aux)

    groups, people_groups = stochastic_clustering(train_data, 100, aux, max_seat_daily)

    set_maximum(MAX_SEAT, groups, people_groups, train_data, aux)