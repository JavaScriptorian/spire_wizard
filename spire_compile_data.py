import json
import re
import os
import sys

resourceCount = sys.argv[1]
with open(f'R{resourceCount}.json', 'r', encoding='utf-8') as file_in:
    data = json.loads(file_in.read())


def get_turn_count(key):
    slash_count = key.count('/')
    if slash_count == 9:
        return 5
    elif slash_count == 7:
        return 4
    elif slash_count == 5:
        return 3
    elif slash_count == 3:
        return 2
    elif slash_count == 1:
        return 1

def get_general_probability(game_list):
    games = 0
    wins = 0
    for game in game_list:
        for key, value in game.items():
            games += value['games']
            wins += value['wins']
            if games != wins:
                ibrk = 0
        
    return round(round(wins/games, 2)*100)

def get_best_choice(current_combination, game_list, turn_num, choice_index):
    best_choices = {}
    for game in game_list:
        # Add all wins and games done with this combination.
        for key, value in game.items():
            if get_turn_count(key) < turn_num:
                continue

            combination = key.split('/')[choice_index]
            # Check to make sure this combination is in the best_choices dict
            if combination not in best_choices:
                best_choices[combination] = {'wins': 0, 'games': 0}
            best_choices[combination]['wins'] += value['wins']
            best_choices[combination]['games'] += value['games']
    # Determine the probability of each
    best_probability = {}
    for key, value in best_choices.items():
        best_probability[key] = round(value['wins'] / value['games'], 2)
    sorted_choices  = sorted(best_probability.items(), key=lambda kv: kv[1], reverse=True)
    if len(sorted_choices) > 0:
        return [sorted_choices[0:20]]
    return []


round2_dict = {}
round3_dict = {}

for key, value in data.items():
    # Determine how many turns it took to win.
    turns = get_turn_count(key)

    split_key = key.split('/')

    # Get all games with round1_result at beginning
    round1_result = '/'.join(split_key[0:2])
    if round1_result not in round2_dict:
        round2_dict[round1_result] = []
    round2_dict[round1_result].append({key: value})

    round2_result = '/'.join(split_key[0:4])
    if round2_result not in round3_dict:
        round3_dict[round2_result] = []
    round3_dict[round2_result].append({key: value})


best_choices_round_2 = {}
for key, value in round2_dict.items():
    # Determine a person's odds of winning just based on all games played.
    probability = get_general_probability(value)
    best_choices = get_best_choice(key, value, turn_num=2, choice_index=2)
    best_choices_round_2[key] = best_choices

with open(f'json/R{resourceCount}-Choice2.json', 'w', encoding='utf-8') as file_out:
    json_data = json.dumps(best_choices_round_2)
    print(json_data, file=file_out)

best_choices_round_3 = {}
for key, value in round3_dict.items():
    # Determine a person's odds of winning just based on all games played.
    probability = get_general_probability(value)
    best_choices = get_best_choice(key, value, turn_num=3, choice_index=4)
    best_choices_round_3[key] = best_choices
    
with open(f'json/R{resourceCount}-Choice3.json', 'w', encoding='utf-8') as file_out:
    json_data = json.dumps(best_choices_round_3)
    print(json_data, file=file_out)




############################# FOR ROUND 4
if os.path.exists(f'R{resourceCount} (Turn 4).json'):
    with open(f'R{resourceCount} (Turn 4).json', 'r', encoding='utf-8') as file_in:
        data4 = json.loads(file_in.read())

    round4_dict = {}
    for key, value in data4.items():
        # Determine how many turns it took to win.
        turns = get_turn_count(key)

        split_key = key.split('/')

        # Get all games with round1_result at beginning
        round3_result = '/'.join(split_key[0:6])
        if round3_result not in round4_dict:
            round4_dict[round3_result] = []
        round4_dict[round3_result].append({key: value})


best_choices_round_4 = {}
for key, value in round4_dict.items():
    # Determine a person's odds of winning just based on all games played.
    probability = get_general_probability(value)
    best_choices = get_best_choice(key, value, turn_num=4, choice_index=6)
    best_choices_round_4[key] = best_choices

with open(f'json/R{resourceCount}-Choice4.json', 'w', encoding='utf-8') as file_out:
    json_data = json.dumps(best_choices_round_4)
    print(json_data, file=file_out)


############################# FOR ROUND 5
if os.path.exists(f'R{resourceCount} (Turn 5).json'):
    with open(f'R{resourceCount} (Turn 5).json', 'r', encoding='utf-8') as file_in:
        data5 = json.loads(file_in.read())

    round5_dict = {}
    for key, value in data5.items():
        # Determine how many turns it took to win.
        turns = get_turn_count(key)

        split_key = key.split('/')

        # Get all games with round1_result at beginning
        round4_result = '/'.join(split_key[0:8])
        if round4_result not in round5_dict:
            round5_dict[round4_result] = []
        round5_dict[round4_result].append({key: value})


    best_choices_round_5 = {}
    for key, value in round5_dict.items():
        # Determine a person's odds of winning just based on all games played.
        probability = get_general_probability(value)
        best_choices = get_best_choice(key, value, turn_num=5, choice_index=8)
        best_choices_round_5[key] = best_choices

    with open(f'json/R{resourceCount}-Choice5.json', 'w', encoding='utf-8') as file_out:
        json_data = json.dumps(best_choices_round_5)
        print(json_data, file=file_out)