# Welcome to Shang Dynasty: Spirit Messenger!

![](https://tokei.rs/b1/github/leoliu012/Shang-Dynasty-Spirit-Messenger)
## Description: 
**Shang Dynasty: Spirit Messenger** is a side-scrolling adventure that immerses you in Bronze-Age China 
as a sacred courier. Navigate randomized mountains, lakes, and cliffs by choosing between a nimble bird, 
sturdy turtle, or swift deer—each with unique strengths and spirit costs. Along the way, collect 
fragmented oracle words in the sky and on the ground to reconstruct and deliver a divine message 
to the heavens.
## Run Instructions:

### Prerequisites
Windows 10+

macOS 10.13+

Python 3.6-3.11

## Project Installation

### Project Setup
Clone the repository:
```commandline
git clone https://github.com/leoliu012/Shang-Dynasty-Spirit-Messenger
```

```commandline
cd Shang-Dynasty-Spirit-Messenger
```

### Setup Virtual Environment
Setting up a virtual environment is recommended
```commandline
python -m venv venv
```
Then activate the virtual environment:
#### On Windows:
```commandline
venv\Scripts\activate
```
#### On MacOS/Linux:
```commandline
source venv/bin/activate
```

### Required Libraries
cmu-graphics package and Pillow are two required libraries for this project.

Under the directory of this project, run:
```commandline
pip install -r requirements.txt
```
Or:
```commandline
pip install cmu_graphics Pillow
```

### Running the game
To run the game, run:
```commandline
cd ./src
```
Then:
```commandline
python main.py
```