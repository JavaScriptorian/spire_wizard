# Written by The JavaScriptorian to help myself and others play the Spire of Eternity from Elvenar.
import json
import os
from random import randint
import re
import time
import subprocess

# Add the json/final folders
if not os.path.exists('json/final'):
    os.makedirs('json/final')

# Create a list of a random sample of resources.
supplies = ['coins', 'supplies', 'planks', 'marble', 'iron', 'magic dust', 'elixir', 'gems']

# Create a dictionary for the first selection. 
# The numbers will refer to an index of the supplies used in a spire encounter.
selection1_combos = {
    3: '01201',
    4: '01230',
    5: '01234',
    6: '01234', 
    7: '01234',
    8: '01234'
}


class SpireEncounter:
    # This class mimics the game mechanics of the Spire Wizard.
    # To use, create an instance of SpireEncounter by giving it: 1) list of resources, 2) list of resources that ghost desires.
    def __init__(self, resources, ghostDesires):
        self.resourceOptions = resources
        self.resourceCount = len(resources)
        self.ghostCount = 5
        self.attempts = 3
        self.attemptNumber = 0
        self.win = None
        self.attemptColorAndResource = ['' for i in range(0, self.ghostCount)]
        # self.attemptColors keeps track of the Red, Yellow, and Green resources.
        self.attemptColors = [
            ['' for i in range(0, self.ghostCount)],
            ['' for i in range(0, self.ghostCount)],
            ['' for i in range(0, self.ghostCount)],
            ['' for i in range(0, self.ghostCount)],
            ['' for i in range(0, self.ghostCount)],
        ]

        # Get array of desires from ghosts
        self.ghostDesires = ghostDesires
        self.ghosts = self.createGhosts()

        # Unwanted resources
        self.unwantedResources = []

        # Which resources the user knows are not needed anymore.
        self.knownUnwantedResources = []
        # Resources to Ghosts
        self.resourceOutcomes = {val: [i for i in range(0, self.ghostCount)] for val in self.resourceOptions}
        # Update the status
        self.updateStatus()

    # Return an array of ghost objects.
    def createGhosts(self):
        array = []
        for i in range(0, self.ghostCount):
            array.append(
                {
                    'resourcesUsed': [],
                    'resourcesPossible': self.resourceOptions,
                    'desire': self.ghostDesires[i],
                    'satisfied': False
                }
            )
        return array

    # Update the Status of Ghosts
    def updateStatus(self):
        # Populate array of resources that are unwanted.
        self.updateUnwantedResources()
        self.eliminateChoices()

    def updateUnwantedResources(self):
        # Empty out the unwantedResources array.
        self.unwantedResources = []
        # Add a resource to unwantedResources array if it's not in the ghost desires.
        for resourceOption in self.resourceOptions:
            if resourceOption not in self.ghostDesires:
                self.unwantedResources.append(resourceOption)

    def updateResourceOutcomes(self):
        results = self.attemptColors[self.attemptNumber]
        for ghostIndex, result in enumerate(results):
            # Remove the ghost from every resourceOutcomes value, but do not remove the resource.
            if result.startswith('Green'):
                for key, value in self.resourceOutcomes.items():
                    self.resourceOutcomes[key] = [i for i in self.resourceOutcomes[key] if i != ghostIndex]
            # Remove this ghost from the specific resource, but do not remove anything else.
            elif result.startswith('Yellow'):
                self.resourceOutcomes[result[7:]] = [i for i in self.resourceOutcomes[result[7:]] if i != ghostIndex]
            # Remove everyone from this resource.
            elif result.startswith('Red'):
                self.resourceOutcomes[result[4:]] = []

        # Eliminate any green resources if re.search(r'^[GY]+$', gameResultString)
        gameResultString = calculateGameResultString(s, self.attemptNumber)


        yellowResources = []
        greenResources = []
        otherResources = []

        if re.search(r'^[^R]+?$', gameResultString) and 'G' in gameResultString and 'Y' in gameResultString:
            # Iterate through the attemptColors and get the resources
            for ghostIndex, result in enumerate(results):
                if result.startswith('Yellow'):
                    yellowResources.append(result[7:])
                elif result.startswith('Green'):
                    greenResources.append(result[6:])
            # Check to see if all yellow resources are different from each other.
            yellowResourceSet = set(yellowResources)
            if len(yellowResources) == len(yellowResourceSet):
                for key, value in self.resourceOutcomes.items():
                    if key not in yellowResourceSet:
                        self.resourceOutcomes[key] = []


    def selectResources(self, selection):
        if self.attempts == 0:
            print('You have no more attempts')
            return None
        # TODO: This wil need to be modified a bit, since we don't have an interface anymore.

        for i in range(0, len(selection)):
            # Skip any ghosts that are already satisfied.
            if self.ghostDesires[i] == '':
                continue

            # Add each item into the correct ghost's resources used.
            self.ghosts[i]['resourcesUsed'].append(selection[i])

            # If resource === green
            if selection[i] == self.ghosts[i]['desire']:
                # print(f'Ghost #{i+1} is happy with your offer of {selection[i]}')
                self.ghosts[i]['satisfied'] = True
                self.ghostDesires[i] = ''

                self.attemptColors[self.attemptNumber][i] = f'Green {selection[i]}'
                self.attemptColorAndResource[i] = f'Green {selection[i]}'
            elif selection[i] in self.ghostDesires:
                # Remove this ghost from the outcomes
                self.attemptColors[self.attemptNumber][i] = selection[i]
            else:
                self.knownUnwantedResources.append(selection[i])
                self.attemptColors[self.attemptNumber][i] = f'Red {selection[i]}'


        # Make anything that's not red or green into a yellow color
        for i in range(0, self.ghostCount):
            if not self.attemptColors[self.attemptNumber][i].startswith('Red') and not self.attemptColors[self.attemptNumber][i].startswith('Green'):
                # If the resource still occurs somewhere, then it deserves to be Yellow.
                if self.attemptColors[self.attemptNumber][i] in self.ghostDesires:
                    self.attemptColors[self.attemptNumber][i] = 'Yellow ' + self.attemptColors[self.attemptNumber][i]
                # If not it should be red.
                else:
                    self.attemptColors[self.attemptNumber][i] = 'Red ' + self.attemptColors[self.attemptNumber][i]
        # Correct any weird ones that weren't converted to green yet
        for i in range(0, len(self.attemptColorAndResource)):
            if self.attemptColorAndResource[i] != '':
                self.attemptColors[self.attemptNumber][i] = self.attemptColorAndResource[i]

        # This function must come before the attempt number is incremented
        self.updateResourceOutcomes()

        self.attemptNumber += 1
        self.attempts += -1
        self.updateStatus()

        if self.isWin():
            self.win = True
        elif self.isWin() == False and self.attempts == 0:
            self.win = False


    # Eliminate obvious choices
    def eliminateChoices(self):
        # Empty out ghost's resource
        for ghost in self.ghosts:
            ghost['resourcesPossible'] = []

        # If any array has a length of 1, make that the obvious choice in the ghosts resources
        ghostIndexOccurrences = {}
        for key, value in self.resourceOutcomes.items():
            for ghostIndex in value:
                if ghostIndex not in ghostIndexOccurrences:
                    ghostIndexOccurrences[ghostIndex] = 0
                ghostIndexOccurrences[ghostIndex] += 1

        # Add ghost's possible resources
        for key, value in self.resourceOutcomes.items():
            for ghostIndex in value:
                self.ghosts[ghostIndex]['resourcesPossible'].append(key)
 
    def addAttempts(self):
        # In case somebody wants to pay diamonds to try a fourth/fifth attempt.
        self.attempts += 1

    def isWin(self):
        ghostSatisified = [ghost['satisfied'] for ghost in self.ghosts]
        if False not in ghostSatisified:
            return True
        return False


def get_next_selection(s):
    ghostOutcomes = {i: [] for i in range(0, 5)}
    for resource, ghostIndices in s.resourceOutcomes.items():
        for ghostIndex in ghostIndices:
            if resource not in ghostOutcomes[ghostIndex]:
                ghostOutcomes[ghostIndex].append(resource)

    nextSelection = []
    for ghostIndex, resourcePossibilities in sorted(ghostOutcomes.items()):
        if len(resourcePossibilities) == 0:
            nextSelection.append('-')
        else:
            nextSelection.append(resourcePossibilities[randint(0, len(resourcePossibilities)-1)])
    return nextSelection


def calculateGameSelectionString(selectionList, gameSupplies):
    # 01234, 4321
    gameSelectionString = ''
    for resource in selectionList:
        if resource == '-':
            gameSelectionString += '-'
        else:
            gameSelectionString +=  str(gameSupplies.index(resource))    
    return gameSelectionString


def calculateGameResultString(s, idx):
    # RGYG-, GGGGG
    return ''.join([i[0] for i in s.attemptColors[idx]])


def computeData(gameIndex, s, selectionLists, gameSupplies, dataDict):
    gameCombination = []
    for idx, selectionList in enumerate(selectionLists):
        gameSelectionString = calculateGameSelectionString(selectionList, gameSupplies)
        gameResultString = calculateGameResultString(s, idx)

        gameCombination.append(gameSelectionString)
        gameCombination.append(gameResultString)
    
    gameCombo = '/'.join(gameCombination)

    if gameCombo not in dataDict:
        dataDict[gameCombo] = {
            'games': 0,
            'wins': 0
        }
    
    if s.isWin():
        dataDict[gameCombo]['wins'] += 1
    dataDict[gameCombo]['games'] += 1

def saveData(resourceCount, dataDict, idx='3'):
    if idx == '4':           
        dataSaved = False
        while dataSaved == False:
            try:
                with open(f'R{resourceCount} (Turn 4).json', 'w', encoding='utf-8') as file_out:
                    json_data = json.dumps(dataDict, ensure_ascii=False)
                    print(json_data, file=file_out)
                dataSaved = True
            except:
                time.sleep(2)
    elif idx == '5':
        dataSaved = False
        while dataSaved == False:
            try:
                with open(f'R{resourceCount} (Turn 5).json', 'w', encoding='utf-8') as file_out:
                    json_data = json.dumps(dataDict, ensure_ascii=False)
                    print(json_data, file=file_out)    
                dataSaved = True
            except:
                time.sleep(2)
    else:
        dataSaved = False
        while dataSaved == False:
            try:
                with open(f'R{resourceCount}.json', 'w', encoding='utf-8') as file_out:
                    json_data = json.dumps(dataDict, ensure_ascii=False)
                    print(json_data, file=file_out)
                dataSaved = True
            except:
                time.sleep(2)

resourceCounts = [7,8]

for resourceCount in resourceCounts:
    globalData = {}
    globalData4 = {}
    globalData5 = {}
    # Check for JSON files to see if there is a game history. 
    # Save it into the globalData dictionaries. 
    # This will make sure data isn't lost from previous games.
    if os.path.exists(f'R{resourceCount}.json'):
        with open(f'R{resourceCount}.json', 'r', encoding='utf-8') as file_in:
            globalData = json.loads(file_in.read())
    if os.path.exists(f'R{resourceCount} (Turn 4).json'):
        with open(f'R{resourceCount} (Turn 4).json', 'r', encoding='utf-8') as file_in:
            globalData4 = json.loads(file_in.read())
    if os.path.exists(f'R{resourceCount} (Turn 5).json'):
        with open(f'R{resourceCount} (Turn 5).json', 'r', encoding='utf-8') as file_in:
            globalData5 = json.loads(file_in.read())


    selection1_combo = selection1_combos[resourceCount] # '01234'
    gameSupplies = supplies[0:resourceCount] # ['coins', 'supplies', 'planks', 'steel', 'crystal']

    i = 1

    # Open Selection CSVs
    # If there's an existing json, use it to select better choices.
    if os.path.exists(f'json/R{resourceCount}-Choice2.json'):
        with open(f'json/R{resourceCount}-Choice2.json', 'r', encoding='utf-8') as file_in:
            selection2_dict = json.loads(file_in.read())
    else:
        selection2_dict = None
    if os.path.exists(f'json/R{resourceCount}-Choice3.json'):
        with open(f'json/R{resourceCount}-Choice3.json', 'r', encoding='utf-8') as file_in:
            selection3_dict = json.loads(file_in.read())
    else:
        selection3_dict = None
    if os.path.exists(f'json/R{resourceCount}-Choice4.json'):
        with open(f'json/R{resourceCount}-Choice4.json', 'r', encoding='utf-8') as file_in:
            selection4_dict = json.loads(file_in.read())
    else:
        selection4_dict = None
    if os.path.exists(f'json/R{resourceCount}-Choice5.json'):
        with open(f'json/R{resourceCount}-Choice5.json', 'r', encoding='utf-8') as file_in:
            selection5_dict = json.loads(file_in.read())
    else:
        selection5_dict = None


    # Play the game X amount of times.
    while i < 5000000:
        # Update terminal with how many games have been played.
        if i % 1000 == 0:
            print(f'\r{i}', end='')
        # Create a random desire for each ghost based on the gameSupplies selected.
        ghostDesires = [gameSupplies[randint(0, len(gameSupplies)-1)] for i in range(0, 5)]
        # Initialize the game encounter
        s = SpireEncounter(gameSupplies, ghostDesires)

        # Provide the resources for choice 1.
        selection1 = [gameSupplies[int(selection1_combo[0])], gameSupplies[int(selection1_combo[1])], gameSupplies[int(selection1_combo[2])], gameSupplies[int(selection1_combo[3])], gameSupplies[int(selection1_combo[4])]]
        s.selectResources(selection1)

        # If the game is already won, compute the game data and continue to next game.
        if s.win == True:
            computeData(i, s, [selection1], gameSupplies, dataDict=globalData)
            i += 1
            continue

        
        if selection2_dict == None:
            # get_next_selection() chooses a random selection of POSSIBLE resources based on what the game knows is unwanted and wanted.
            selection2 = get_next_selection(s)
            selection2_combo = calculateGameSelectionString(selection2, gameSupplies)
        else:
            # Here, we determine the best selection from previous games instead of choosing a random selection.
            result1 = calculateGameResultString(s, 0)

            # If a game encounter exists, then it will find it in selection2_dict
            if f'{selection1_combo}/{result1}' in selection2_dict:
                possible_selections = selection2_dict[f'{selection1_combo}/{result1}']
                if len(possible_selections) == 0:
                    selection2 = get_next_selection(s)
                    selection2_combo = calculateGameSelectionString(selection2, gameSupplies)
                else:
                    selected = possible_selections[randint(0, len(possible_selections)-1)]
                    selection2_combo = str(selected[0][0])
                    selection2 = []
                    for x in selected[0][0]:
                        if x == '-':
                            selection2.append('-')
                        else:
                            selection2.append(gameSupplies[int(x)])
            # If a game encounter has never happened, then it will continue to use random until it's played the game enough times.
            else:
                selection2 = get_next_selection(s)
                selection2_combo = calculateGameSelectionString(selection2, gameSupplies)

        # Select the resources for choice 2.
        s.selectResources(selection2)

        # If the game is won already, save the data into globalData dictionary and continue to next game.
        if s.win == True:
            computeData(i, s, [selection1, selection2], gameSupplies, dataDict=globalData)
            i += 1
            continue

        ### ROUND 3 ###
        if selection3_dict == None:
            selection3 = get_next_selection(s)
            selection3_combo = calculateGameSelectionString(selection3, gameSupplies)
        else:
            result2 = calculateGameResultString(s, 1)
            selection3 = []
            combo_result = f'{selection1_combo}/{result1}/{selection2_combo}/{result2}'
            if combo_result in selection3_dict:
                possible_selections = selection3_dict[combo_result]
                if len(possible_selections) == 0:
                    selection3 = get_next_selection(s)
                    selection3_combo = calculateGameSelectionString(selection3, gameSupplies)
                else:
                    selected3 = possible_selections[randint(0, len(possible_selections)-1)]
                    selection3_combo = str(selected3[0][0])
                    selection3 = []
                    for x in selected3[0][0]:
                        if x == '-':
                            selection3.append('-')
                        else:
                            selection3.append(gameSupplies[int(x)])
            else:
                selection3 = get_next_selection(s)
                selection3_combo = calculateGameSelectionString(selection3, gameSupplies)
        
        s.selectResources(selection3)

        if s.win == True:
            computeData(i, s, [selection1, selection2, selection3], gameSupplies, dataDict=globalData)
            i += 1
            continue
        else:
            computeData(i, s, [selection1, selection2, selection3], gameSupplies, dataDict=globalData)
            i += 1

        ### ROUND 4 ###
        if s.isWin() == False:
            s.attempts += 1
            if selection4_dict == None:
                selection4 = get_next_selection(s)
                selection4_combo = calculateGameSelectionString(selection4, gameSupplies)
            else:
                result3 = calculateGameResultString(s, 2)
                selection4 = []
                combo_result = f'{selection1_combo}/{result1}/{selection2_combo}/{result2}/{selection3_combo}/{result3}'
                
                if combo_result in selection4_dict:
                    possible_selections = selection4_dict[combo_result]
                    if len(possible_selections) == 0:
                        selection4 = get_next_selection(s)
                    else:
                        selected4 = possible_selections[randint(0, len(possible_selections)-1)]
                        selection4_combo = str(selected4[0][0])
                        selection4 = []
                        for x in selected4[0][0]:
                            if x == '-':
                                selection4.append('-')
                            else:
                                selection4.append(gameSupplies[int(x)])
                else:
                    selection4 = get_next_selection(s)
                    selection4_combo = calculateGameSelectionString(selection4, gameSupplies)
            s.selectResources(selection4)

            if s.win == True:
                computeData(i, s, [selection1, selection2, selection3, selection4], gameSupplies, dataDict=globalData4)
                i +=  1
                continue
            else:
                computeData(i, s, [selection1, selection2, selection3, selection4], gameSupplies, dataDict=globalData4)
                i +=  1


        ### ROUND 5 ###
        if s.isWin() == False:
            s.attempts += 1
            if selection5_dict == None:
                selection5 = get_next_selection(s)
                selection5_combo = calculateGameSelectionString(selection5, gameSupplies)
            else:
                result4 = calculateGameResultString(s, 3)
                selection5 = []
                combo_result = f'{selection1_combo}/{result1}/{selection2_combo}/{result2}/{selection3_combo}/{result3}/{selection4_combo}/{result4}'
                if combo_result in selection5_dict:
                    possible_selections = selection5_dict[combo_result]
                    if len(possible_selections) == 0:
                        selection5 = get_next_selection(s)
                        selection5_combo = calculateGameSelectionString(selection5, gameSupplies)
                    else:
                        selected5 = possible_selections[randint(0, len(possible_selections)-1)]
                        selection5_combo = str(selected5[0][0])
                        selection5 = []
                        for x in selected5[0][0]:
                            if x == '-':
                                selection5.append('-')
                            else:
                                selection5.append(gameSupplies[int(x)])
                else:
                    selection5 = get_next_selection(s)
                    selection5_combo = calculateGameSelectionString(selection5, gameSupplies)
            s.selectResources(selection5)
            
            # Compute the data from the game after round 5.
            computeData(i, s, [selection1, selection2, selection3, selection4, selection5], gameSupplies, dataDict=globalData5)
            i +=  1

    
    # After all games are played, save out the data for rounds 3, 4, and 5.
    saveData(resourceCount, dataDict=globalData, idx='3')
    saveData(resourceCount, dataDict=globalData4, idx='4')
    saveData(resourceCount, dataDict=globalData5, idx='5')

    # Run the spire compiler to calculate the best options from each game.
    subprocess.run(["python3", "spire_compile_data.py", str(resourceCount)])

        
    