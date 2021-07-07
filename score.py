import numpy as np

# calculate scores achieved by a single group
def calculate_single_group_score(data, groups, group):
    score = 0
    people = groups[group]
    for i in people:
        for j in people:
            if i != j:
                score += int(data.loc[str(i), str(j)])
    return score

# calculate scores achieved by all groups, and the total score
def all_score(data, groups):
    scores = []
    for i in groups.keys():
        scores.append(calculate_single_group_score(data, groups, i))
    return scores, sum(scores)

# calculate the potential score that can be achieved in each group
def get_potential_score(train_data, groups):
    total_opportunities = [0, 0, 0, 0, 0]

    for i in range(5):
        for person in groups[i + 1]:
            total_opportunities[i] += np.sum(np.nan_to_num(np.array(train_data.loc[str(person)].tolist())))
    return total_opportunities

# calculate the regularized scores which encourages equal proportion of interactions achieved
def regularized_score(list1, total_opportunities, lambd):
    sum = np.sum(np.array(list1))
    sum_t = np.sum(total_opportunities)
    best_list = []
    for i in range(5):
        best_list.append(sum * (total_opportunities[i] / sum_t))
    penalty = np.sum(np.abs(list1 - np.array(best_list)))

    return np.sum(list1) - lambd * penalty