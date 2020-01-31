# Game-Of-Life

Python program for simulating Conway's Game of Life made by David Kohler and designed for Python 3.6. Generates gif for user based on passed in parameters. User can choose to start the simulation using a random grid of size specified by the user, or can start the simulation using an RLE (Run Length Encoded) formatted file (with .rle file extension) with a specified minimum grid size. Once the grid has been generated or parsed from file, the program asks the user for the number of generations to run and the frame rate to use to generate the gif. Program will then generate the simulation and save a gif in a "GoL-gifs" folder. The program will then ask the user if they want to save an RLE file translating the grid it has just simulated, saving a .rle file in a "saved-RLEs" folder. Designed for use from the terminal.

## Installation

1. Copy the repository
2. Make sure you have Python version 3.6 or later
3. Make sure you have up to date versions of the following libraries: `matplotlib`, `numpy`, `seaborn`, `celluloid`

## Usage

From terminal, two options for usage.

To use a random starting grid: `python GameOfLife.py`

To use a starting specified RLE file: `python GameOfLife.py <path to RLE file.rle>`

## Example

First, below is an example of a gif created by running the program using a specified RLE file for the Gosper Glider Gun:

![Gosper Glider Gun](GoL-gifs/GoL80s300g.gif)

Second, below is an example of a gif created using a random grid of size 40 with 200 generations:

![Random Starting Grid](GoL-gifs/GoL40s200g.gif)

## Authors

David Kohler

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
