# spire_wizard
The Python code behind the Spire Wizard for Elvenar tool: https://javascriptorian.com/spire-wizard

People have asked to see the code behind the Spire Wizard, so here it is: 3 Python scripts explained in order of use:

1. spire_train.py
This script is where the game mechanics are recreated for the Spire of Eternity. This script will play the game several times and output the game states. The data is condensed so that it only outputs the selected choices of resources by index, (e.g. 01234) and the color coding for ghosts is condensed to RYG (red, yellow, green).

2. spire_compile_data.py
This script is run at the end of spire_train.py. It simply condenses all the data generated from spire_train.py and outputs the best 20 (if available) choices. The next time spire_train.py is run, it will pick one of these 20 choices instead of randomly choosing any possible combination.

3. spire_condense_data.py
This script is run after millions of games have been played for each resource count. I generally run the script only about 500,000 times for resources 3, 4, and 5 since they are much more simple. Resources 6, 7, and 8 need millions of tries based on the way this script is set up. In hindsight, I would have made the spire training data more simple and cleaner, but I slapped this together fast so I could spend more time doing other coding projects.
