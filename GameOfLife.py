#!/usr/bin/python

import itertools
import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
import re
import seaborn as sns
import sys
from celluloid import Camera
from itertools import groupby

"""
Author: David Kohler
Description: This file creates a simulation gif of Conway's Game of Life

    Run from command line:
        python GameOfLife.py {optional: RLEfile.rle}

    RLE text file is optional
"""

def addSpace(grid, extraSpace):
    """
    Adds cells to grid if grid needs to be resized larger
    """
    expandedGrid = grid.copy()
    for i in range(extraSpace):
        expandedGrid = np.append(
            expandedGrid,
            [[0 for i in range(expandedGrid.shape[1])]],
            axis = 0
        )
        expandedGrid = np.append(
            [[0 for i in range(expandedGrid.shape[1])]],
            expandedGrid,
            axis = 0
        )
        expandedGrid = np.append(
            expandedGrid,
            np.array([0 for i in range(expandedGrid.shape[0])])[:,None],
            axis = 1
        )
        expandedGrid = np.append(
            np.array([0 for i in range(expandedGrid.shape[0])])[:,None],
            expandedGrid,
            axis = 1
        )
    return expandedGrid


def checkArray(g, r, c):
    """
    Check cell in grid g at row r and column c to see if it is a valid location,
    otherwise it is treated as a dead cell
    """
    if r < 0:
        r = g.shape[0] + 1
    if c < 0:
        c = g.shape[1] + 1
    #Check for index out of bounds
    try:
        nVal = g[r][c]
    except IndexError:
        nVal = 0
    return nVal


def createAnimation(inGrid, gridSize, generations):
    """
    Executes {generations} number of time step updates to model the Game of Life
    while also taking snapshots to compile into an animation at the end
    """
    if not os.path.exists("GoL-gifs"): os.mkdir("GoL-gifs")
    filename = unique_file("GoL-gifs/GoL{}s{}g".format(gridSize, generations), "gif")

    fps = input('Please enter desired frame rate (ex. 5, 10, etc.): ')
    while not fps.isdigit():
        fps = input('Enter desired frame rate as an integer (ex. 5, 10, etc.): ')

    Writer = animation.writers['pillow']
    writer = Writer(fps=int(fps), metadata=dict(artist='Me'), bitrate=1800)

    if (inGrid.shape[0] < gridSize) or (inGrid.shape[1] < gridSize):
        grid = addSpace(inGrid, max(
            abs(gridSize - inGrid.shape[0]),
            abs(gridSize - inGrid.shape[1])
        ))
    else:
        grid = inGrid.copy()

    fig = plt.figure()
    fig.set_size_inches(8, 8)
    camera = Camera(fig)
    plt.axis('off')
    plt.annotate(
        'Generation (0/{})...'.format(generations),
        xy=(50, 30),
        xycoords='figure pixels',
        size=20
    )
    plt.imshow(grid, cmap="tab20_r")
    camera.snap()

    for i in range(generations):
        plt.annotate(
            'Generation ({}/{})...'.format(i+1, generations),
            xy=(50, 30),
            xycoords='figure pixels',
            size=20
        )
        plt.imshow(updateGrid(grid), cmap="tab20_r")
        camera.snap()
        print('Generation ({}/{})...'.format(i+1, generations))

    print('Creating animation... Please wait...')
    ani = camera.animate()
    ani.save(filename, writer = writer)
    print("Done! Saved as {}".format(filename))


def encodeGrid(grid, top, bot, minCol, maxCol):
    """
    Encodes a grid into a grouping list of RLE tags and counts
    """
    encodedStrings = []
    for row in range(top, bot + 1):
        cellCount = 0
        rowString = ''
        for col in range(minCol, maxCol + 1):
            cell = grid[row][col]
            rowString += 'o' if cell == 1 else 'b'
        groups = [(label, sum(1 for _ in group)) for label, group in groupby(rowString)]
        encodedStrings += groups
        if row != bot:
            encodedStrings += [('$', 1)]
        else:
            encodedStrings +=  [('!', 1)]

    return encodedStrings


def findBoundaries(grid):
    """
    Finds meaningful top, bottom, right, and left boundaries of grid to be used
    in RLE encoding
    """
    for top in range(grid.shape[0]):
        if sum(grid[top]) > 0:
            break
    for bot in range(grid.shape[0]-1, -1, -1):
        if sum(grid[bot]) > 0:
            break
    minCol = math.inf
    maxCol = -math.inf
    for row in range(top, bot + 1):
        for col in range(grid.shape[1]):
            if grid[row][col] == 1:
                if col < minCol:
                    minCol = col
                elif col > maxCol:
                    maxCol = col
        if (minCol == 0) and (maxCol == grid.shape[1] - 1):
            #min is first column, and max is last column
            #so no need to keep looping
            break
    return top, bot, minCol, maxCol


def findNeighbors(g, r, c):
    """
    Check all neighbors of cell at row r, column c in grid g to find the count
    of all living neighbor cells
    """
    nAlive = checkArray(g, r-1, c-1) + checkArray(g, r-1, c) + \
        checkArray(g, r-1, c+1) + checkArray(g, r+1, c-1) + \
        checkArray(g, r+1, c) + checkArray(g, r+1, c+1) + \
        checkArray(g, r, c-1) + checkArray(g, r, c+1)
    return nAlive


def parseInput(args):
    """
    Parses command line arguments to see if RLE file supplied, or if using a
    randomly generated grid
    """
    gridInput = input('Please enter desired grid size: ')
    while not gridInput.isdigit():
        gridInput = input('Please enter desired grid size: ')
    gridSize = int(gridInput)

    if (len(args) == 2):
        #supplied RLE file
        initialGrid = parseRLE(args[1])
    else:
        #create a random grid
        initialGrid = randomGrid(gridSize)

    generationInput = input('Please enter desired number of generations: ')
    while not generationInput.isdigit():
        generationInput = input('Please enter desired number of generations: ')
    generations = int(generationInput)

    return initialGrid, gridSize, generations


def parseRLE(filename):
    """
    Parses an RLE text file passed in as filename, into a grid
    """
    with open(filename) as f:
        content = [line.strip() for line in f]
    RLEstring = ''
    for line in content:
        if line[0] == '#':
            #comment line
            continue
        elif line[0] == 'x':
            #rule line (note: only considering basic Conway Life rules)
            chunks = line.split(',')
            xvalue = int(chunks[0].strip().split('=')[1])
            yvalue = int(chunks[1].strip().split('=')[1])

        else:
            RLEstring += line
        if line[-1] == '!':
            RLEstring = RLEstring[:-1]
            break

    grid = []
    for chunk in RLEstring.split('$'):
        RLEtags = re.findall(r'[bo]',chunk)
        tagCounts = re.split(r'[bo]',chunk)
        gridLine = []
        for i in range(len(RLEtags)):
            curTag = RLEtags[i]
            try:
                curCt = int(tagCounts[i])
            except ValueError:
                curCt = 1
            if curTag == 'b':
                gridLine.extend([0 for i in range(curCt)])
            else:
                gridLine.extend([1 for i in range(curCt)])

        if len(gridLine) != xvalue:
            #fill to end of line
            gridLine.extend([0 for i in range(xvalue - len(gridLine))])
        grid.append(gridLine)
    return np.array(grid)


def randomGrid(N):
    """
    Generates a random grid of size N*N with p[0]% dead cells, p[1]% alive cells
    """
    return np.random.choice([0,1], N*N, p=[0.4, 0.6]).reshape(N, N)


def saveRLE(grid):
    """
    Prompt and save RLE text file of starting grid
    """
    save = input('Do you want to save RLE file of starting state? (y/n) ')
    while (save != 'y') and (save != 'n'):
        save = input('Do you want to save RLE file of starting state? (y/n) ')
    if save == 'y':
        writeRLE(startingState)


def unique_file(basename, ext):
    """
    Finds unique filename with given base and extension to avoid overwriting
    """
    actualname = '{}.{}'.format(basename, ext)
    c = itertools.count()
    while os.path.exists(actualname):
        actualname = '{}_{}.{}'.format(basename, next(c), ext)
    return actualname


def updateGrid(grid):
    """
    Executes a single generation time step according to the rules in Conway's
    Game of Life, and updates grid accordingly
    """
    nextGrid = grid.copy()

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            #boundary check
            nAlive = 0
            nAlive = findNeighbors(grid, i, j)

            nextState = 0
            if grid[i][j] == 1:
                #alive cell
                if (nAlive < 2 or nAlive > 3):
                    #underpopulation or overpopulation
                    nextState = 0
                else:
                    #lives on
                    nextState = 1
            else:
                #dead cell
                if (nAlive == 3):
                    #reproduces
                    nextState = 1
                else:
                    #stays dead
                    nextState = 0

            #build grid of next states
            nextGrid[i][j] = nextState

    grid[:] = nextGrid[:]
    return grid


def writeRLE(grid):
    """
    Writes grid out to a text file in RLE format
    """
    filename = unique_file("saved-RLEs/savedRLE", "rle")
    f = open(filename, "w")
    top, bot, minCol, maxCol = findBoundaries(grid)
    #write x,y header
    f.write('x = {}, y = {}\n'.format(str(maxCol - minCol + 1), str(bot - top + 1)))
    RLEgroups = encodeGrid(grid, top, bot, minCol, maxCol)
    finishedWriting = False
    allLines = []
    individualLine = ''
    pos = 0
    #write grid with 70 character lines
    while finishedWriting == False:
        if (pos == len(RLEgroups) - 2) and (RLEgroups[pos][0] == 'b'):
            pos += 1
            continue
        if (RLEgroups[pos][1] == 1):
            #single cell
            if (1 + len(individualLine) > 70):
                #new line
                individualLine += '\n'
                f.write(individualLine)
                individualLine = RLEgroups[pos][0]
            else:
                #same line
                individualLine += RLEgroups[pos][0]
        else:
            if (len(str(RLEgroups[pos][1])) + len(individualLine) + 1 > 70):
                #new line
                individualLine += '\n'
                f.write(individualLine)
                individualLine = str(RLEgroups[pos][1]) + RLEgroups[pos][0]
            else:
                #same line
                individualLine += str(RLEgroups[pos][1]) + RLEgroups[pos][0]
        if (pos == len(RLEgroups) - 1):
            f.write(individualLine)
            finishedWriting = True
        else:
            pos += 1
    f.close()
    print('RLE written to {}'.format(filename))



if __name__ == '__main__':
    """
    Generates simulation and gif animation of Game of Life, allows user
    to write out RLE file corresponding to grid
    """
    initialGrid, gridSize, generations = parseInput(sys.argv)
    #save starting state in case user wants to write out RLE later
    startingState = initialGrid.copy()
    createAnimation(initialGrid, gridSize, generations)
    saveRLE(startingState)

    sys.exit(0)
