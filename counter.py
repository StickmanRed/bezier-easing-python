"""
https://github.com/gre/bezier-easing
BezierEasing - use bezier curve for transition easing function
by Gaëtan Renaudeau 2014 - 2015 – MIT License

i just put it into python, so i get no credit
"""

# These values are NOT established by empiricism with tests, because JavaScript
# runs differently than Python.

NEWTON_ITERATIONS = 4
NEWTON_MIN_SLOPE = 0.001
SUBDIVISION_PRECISION = 0.0000001
SUBDIVISION_MAX_ITERATIONS = 10

kSplineTableSize = 11
kSampleStepSize = 1.0 / (kSplineTableSize - 1.0)

def A(aA1, aA2): return 1.0 - 3.0 * aA2 + 3.0 * aA1
def B(aA1, aA2): return 3.0 * aA2 - 6.0 * aA1
def C(aA1)     : return 3.0 * aA1

def calcBezier(aT, aA1, aA2): # I don't understand the naming scheme here.
    return ((A(aA1, aA2) * aT + B(aA1, aA2)) * aT + C(aA1)) * aT

# It's really easy to copy these types of functions because JS and Python
# use the same operators
def getSlope(aT, aA1, aA2):
    return 3.0 * A(aA1, aA2) * aT * aT + 2.0 * B(aA1, aA2) * aT + C(aA1)

def binarySubdivide(aX, aA, aB, mX1, mX2):
    currentX = 0
    currentT = 0
    i = 0

    # Patch for JavaScript do-while
    condition = (Math.abs(currentX) > SUBDIVISION_PRECISION and ++i < SUBDIVISION_MAX_ITERATIONS)
    while condition:
        currentT = aA + (aB - aA) / 2.0
        currentX = calcBezier(currentT, mX1, mX2) - aX
        if currentX > 0.0:
            aB = currentT
        else:
            aA = currentT

        condition = (Math.abs(currentX) > SUBDIVISION_PRECISION and ++i < SUBDIVISION_MAX_ITERATIONS)
    return currentT

def newtonRaphsonIterate(aX, aGuessT, mX1, mX2):
    for i in range(NEWTON_ITERATIONS):
        currentSlope = getSlope(aGuessT, mX1, mX2)
        if currentSlope == 0.0:
            return aGuessT
        currentX = calcBezier(aGuessT, mX1, mX2) - aX
        aGuessT -= currentX / currentSlope
    return aGuessT
     
def linear(x):
    return x # Straightforward, isn't it?

def bezier(mX1, mY1, mX2, mY2):
    if not ((0 < mX1 < 1) and (0 < mX2 < 1)):
        raise ValueError('Wrong number.')
    
    if (mX1 == mY1) and (mX2 == mY2):
        return linear
    
    sampleValues = []
    for i in range(kSplineTableSize):
        # "IndexError: list assignment index out of range". Bleugh.
        sampleValues.append(calcBezier(i * kSampleStepSize, mX1, mX2))
    
    def getTForX(aX):
        intervalStart = 0.0
        currentSample = 1
        lastSample = kSplineTableSize - 1

        while (currentSample != lastSample) and (sampleValues[currentSample] <= aX):
            intervalStart += kSampleStepSize
            currentSample += 1
        currentSample -= 1

        dist = (aX - sampleValues[currentSample]) / (sampleValues[currentSample + 1] - sampleValues[currentSample])
        guessForT = intervalStart + dist * kSampleStepSize

        initialSlope = getSlope(guessForT, mX1, mX2)
        if initialSlope >= NEWTON_MIN_SLOPE:
            return newtonRaphsonIterate(aX, guessForT, mX1, mX2)
        elif initialSlope == 0.0:
            return guessForT
        else:
            return binarySubdivide(aX, intervalStart, intervalStart + kSampleStepSize, mX1, mX2)
    
    def BezierEasing(x):
        if (x == 0) or (x == 1): return x
        return calcBezier(getTForX(x), mY1, mY2)
    return BezierEasing

# I'm done. :)
