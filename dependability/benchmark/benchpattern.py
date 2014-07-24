
import benchfile
import random
import os
import math

def create_pattern(repetitions, slots, objects, seed = None):
    if seed is None:
        seed = os.urandom(4).__hash__()
    random.seed(seed)
    acquirationRange = random.randint(2, 2**14)
    waitRange = random.randint(2, 2**14)
    bench = benchfile.Benchfile(repetitions)
    CheckedObjects = []
    for i in range(objects):
        CheckedObjects.append(benchfile.CheckedObject("co" + str(i), random.randint(4, 2**15)))
    for i in range(slots):
        bench.add(benchfile.Acquiration(CheckedObjects[random.randint(0, len(CheckedObjects) - 1)], random.randint(1, random.randint(2, acquirationRange) * 2)))
        bench.add(benchfile.BusyWaiting(random.randint(1, random.randint(2, waitRange) * 2)))
    return (bench, seed)

def calculate_mean_distance(bench):
    co = []
    for s in bench.sequence:
        if isinstance(s, benchfile.Acquiration) and not s.checkedObject in co:
            co.append(s.checkedObject)

    distance = 0
    acquirations = 0
    mean_distance = 0
    for c in co:
        for s in bench.sequence:
            if (isinstance(s, benchfile.Acquiration) and s.checkedObject is c):
                acquirations += 1
            else:
                distance = distance + s.dur()
        mean_distance += distance / acquirations
    return mean_distance / len(co)

def calculate_mean_acquiration_duration(bench):
    acquirations = 0
    duration = 0
    for s in bench.sequence:
        if isinstance(s, benchfile.Acquiration):
            acquirations += 1
            duration += s.dur()
    return duration / acquirations

def calculate_mean_waiting_duration(bench):
    waitings = 0
    duration = 0
    for s in bench.sequence:
        if isinstance(s, benchfile.BusyWaiting):
            duration += s.dur()
            waitings += 1
    return duration / waitings

def calculate_full_duration(bench):
    duration = 0
    for s in bench.sequence:
        duration += s.dur()
    return duration

def calculate_mean_sizes(bench):
    size = 0
    objects = 0

    co = []
    for s in bench.sequence:
        if isinstance(s, benchfile.Acquiration) and not s.checkedObject in co:
            co.append(s.checkedObject)
            size += s.checkedObject.size
            objects += 1
    return size / objects

def calculate_standard_deviation_of_sizes(bench):
    mean = calculate_mean_sizes(bench)
    variance = 0.0
    objects = 0

    co = []
    for s in bench.sequence:
        if isinstance(s, benchfile.Acquiration) and not s.checkedObject in co:
            co.append(s.checkedObject)
            variance += (s.checkedObject.size - mean) * (s.checkedObject.size - mean)
            objects += 1
    return math.sqrt(variance / objects)

def calculate_standard_deviation_of_distances(bench):
    mean = calculate_mean_distance(bench)
    co = []
    for s in bench.sequence:
        if isinstance(s, benchfile.Acquiration) and not s.checkedObject in co:
            co.append(s.checkedObject)

    distance = 0
    acquirations = 0
    variance = 0
    for c in co:
        for s in bench.sequence:
            if (isinstance(s, benchfile.Acquiration) and s.checkedObject is c):
                acquirations += 1
            else:
                distance = distance + s.dur()
        variance += ((distance / acquirations) - mean)**2
    return math.sqrt(variance)

def calculate_standard_deviation_of_acquiration(bench):
    mean = calculate_mean_acquiration_duration(bench)
    variance = 0
    for s in bench.sequence:
        if isinstance(s, benchfile.Acquiration):
            variance += (s.dur() - mean)**2
    return math.sqrt(variance)

def calculate_standard_deviation_of_waiting(bench):
    mean = calculate_mean_waiting_duration(bench)
    variance = 0
    for s in bench.sequence:
        if isinstance(s, benchfile.BusyWaiting):
            variance += (s.dur() - mean)**2
    return math.sqrt(variance)
