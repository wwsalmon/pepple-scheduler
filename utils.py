import numpy as np
import pandas as pd
from tabulate import tabulate
import copy
from score import *

# Format the interaction matrix properly
def prep_data(df):
	# Need to change this part if data source is different
	train_data = df.iloc[:69, :68]
	train_data.columns = uniquify(train_data.iloc[:, 0])
	train_data.index = uniquify(train_data.iloc[:, 0])
	train_data = train_data.iloc[1:, 1:]
	train_data.replace(['P', 'p'], 1, inplace=True)
	train_data.replace(['V'], 0, inplace=True)
	train_data.replace(['N'], 0, inplace=True)
	return train_data

# Eliminating duplicated column names
def uniquify(df_columns):
    seen = []
    for item in df_columns:
        fudge = 0
        newitem = item

        while newitem in seen:
            fudge += 1
            newitem = "{}_{}".format(item, fudge)

        seen.append(newitem)
    return list(seen)

# Format the auxiliary data properly
def prep_aux(aux):
    aux.columns = uniquify(aux.iloc[0, :])
    aux.index = uniquify(aux.iloc[:, 0])
    aux = aux.iloc[1:, 1:]
    return aux

# calucalte the maximum for initial assignment (prioritize Tues/Wednes/Thurs)
def compute_max_seat_daily(MAX_SEAT, aux):
    max_seat_daily = [MAX_SEAT] * 5

    total_seats = sum(aux.loc[:, 'NUM_DAY'])

    # Not enough seats already, so need to expand seat limit for now, and then eliminate later
    if sum(max_seat_daily) < total_seats:
        return [round(total_seats/5) + 2] * 5

    # Seats are pretty tight, just going to leave it like this for now
    if sum(max_seat_daily) < total_seats + 10:
        return max_seat_daily

    # Seats are not tight, so we can priortize Tues/Wed/Thur
    while sum(max_seat_daily) >= total_seats + 10:
        max_seat_daily[0] -= 1
        max_seat_daily[4] -= 1

    max_seat_daily[0] -= 2
    max_seat_daily[4] -= 2
    return max_seat_daily

# elimante people if the assigned seats of each day exceeds maximum
def set_maximum(maximum, groups, people_groups, train_data, aux):
    for key in groups.keys():
        while len(groups[key]) > maximum:
            eliminate_person(groups[key], people_groups, train_data, key, aux, key)

# find the person that has the least amount of interactions and eliminate
def eliminate_person(group, people_groups, train_data, key, aux, group_num):
    min = float('inf')
    candidate = ""
    for i in group:
        sum_temp = 0
        for j in group:
            if i != j:
                sum_temp += int(train_data.loc[str(i), str(j)])
        if len(people_groups[i]) != 1 and sum_temp < min and aux.loc[str(i), str(group_num) + '_MUST'] != 1:
            min = sum_temp
            candidate = i
    if candidate != "":
        group.remove(candidate)
        people_groups[candidate].remove(key)
    print(candidate + " is removed.")

# check if each day is at least filled to 90% capacity
def properly_filled(groups, max_seat_daily, threshold=0.25):
    for i in range(5):
        if len(groups[i+1]) < (max_seat_daily[i] * threshold):
            return False
    return True

def show_result(groups, train_data):
    result, score_original = interpret_result(groups, train_data)
    print(result, score_original)
    groups_temp = copy.deepcopy(groups)
    for key in groups_temp.keys():
        while len(groups_temp[key]) < 45:
            groups_temp[key].append(" ")
    table = [groups_temp[1], groups_temp[2], groups_temp[3], groups_temp[4], groups_temp[5]]
    print(tabulate(listTranspose(table)))

# Transposing list for displaying purposes
def listTranspose(x):
    """ Interpret list of lists as a matrix and transpose """
    tups = zip(*x)
    return [list(t) for t in tups]

def interpret_result(groups, train_data):
    score, score_sum = all_score(train_data, groups)
    total_opportunities = [0, 0, 0, 0, 0]

    for i in range(5):
        for person in groups[i+1]:
            total_opportunities[i] += np.sum(np.nan_to_num(np.array(train_data.loc[str(person)].tolist())))
    group_rate = np.array(score) / np.array(total_opportunities)
    print(total_opportunities)

    # numpy_data = np.nan_to_num(train_data.to_numpy())
    # total_all_opportunities = np.sum(numpy_data)
    # count_dic = {}

    # total_all_opportunities_matrix = pd.DataFrame(train_data.to_dict(), columns=train_data.columns, index=train_data.index)
    # for col in total_all_opportunities_matrix:
    #     total_all_opportunities_matrix[col].values[:] = 0
    # for k in range(5):
    #     people = groups[k+1]
    #     for i in people:
    #         for j in people:
    #             if i != j and total_all_opportunities_matrix.loc[str(i), str(j)] == 0:
    #                 total_all_opportunities_matrix.loc[str(i), str(j)] += float(train_data.loc[str(i), str(j)])
    # numpy_data_mat = total_all_opportunities_matrix.to_numpy()
    # count_dic[1] = np.count_nonzero(numpy_data_mat == 1) / np.count_nonzero(numpy_data == 1)
    # if np.count_nonzero(numpy_data == 0.5) != 0:
    #     count_dic[0.5] = np.count_nonzero(numpy_data_mat == 0.5) / np.count_nonzero(numpy_data == 0.5)
    # else:
    #     count_dic[0.5] = 0

    # return group_rate, np.sum(total_all_opportunities_matrix.to_numpy()) / total_all_opportunities, count_dic, score_original
    return group_rate, score