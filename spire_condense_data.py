import json
from tqdm import tqdm as prog

# Condenses the json files down to the best options for the Spire Wizard website.
def condense_data(resource_count, choice_index):
    with open(f'json/R{resource_count}-Choice{choice_index}.json', 'r', encoding='utf-8') as file_in:
        data = json.loads(file_in.read())
    
    selection_dict = {}

    for combo, options in data.items():
        if 'GGGGG' in combo:
            continue
        best_option = options[0][0]
        best_combo = best_option[0]
        best_combo_probability = best_option[1]
        selection_dict[combo] = {
            'next_combo': best_combo,
            'prob': str(int(best_combo_probability * 100)) + '%'
        }
    return selection_dict

def filter_dict(dict1, dict2):
    dict1_keys_combined = sorted([key + '/' + value['next_combo'] for key, value in dict1.items()])
    dict2_keys = sorted([key for key, value in dict2.items()])
    dict2_keys_condensed = [key[0:-6] for key in dict2_keys]
    for idx, key in enumerate(dict2_keys_condensed):
        if key not in dict1_keys_combined:
            del dict2[dict2_keys[idx]]

resources = [3,4,5,6]
for resource in resources:
    print(f'RESOURCE: {resource}\n\n\n')
    selection2_dict = condense_data(resource, 2)

    with open(f'json/final/R{resource}-C2.json', 'w', encoding='utf-8') as file_out:
        print(json.dumps(selection2_dict, ensure_ascii=False), file=file_out)

    selection3_dict = condense_data(resource, 3)
    filter_dict(selection2_dict, selection3_dict)
    
    with open(f'json/final/R{resource}-C3.json', 'w', encoding='utf-8') as file_out:
        print(json.dumps(selection3_dict, ensure_ascii=False), file=file_out)

    if resource > 3:
        selection4_dict = condense_data(resource, 4)
        filter_dict(selection3_dict, selection4_dict)
        condensed_keys = [key[0:-6] for key, value in selection3_dict.items()]
        for key, value in prog(selection4_dict.items()):
            condensed_key = key[0:-12]
            next_selection = selection3_dict[condensed_key]['next_combo']

        with open(f'json/final/R{resource}-C4.json', 'w', encoding='utf-8') as file_out:
            print(json.dumps(selection4_dict, ensure_ascii=False), file=file_out)

    if resource > 4:
        selection5_dict = condense_data(resource, 5)
        filter_dict(selection4_dict, selection5_dict)
        condensed_keys = [key[0:-6] for key, value in selection4_dict.items()]
        for key, value in prog(selection5_dict.items()):
            condensed_key = key[0:-12]
            next_selection = selection4_dict[condensed_key]['next_combo']

        with open(f'json/final/R{resource}-C5.json', 'w', encoding='utf-8') as file_out:
            print(json.dumps(selection5_dict, ensure_ascii=False), file=file_out)
