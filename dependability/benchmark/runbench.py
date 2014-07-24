#!/usr/bin/env python

import benchpattern
import sys
import json

if __name__ == "__main__":

    try:
        repetitions = sys.argv[1]
        slots = sys.argv[2]
        objects = sys.argv[3]
        seed = None
        if len(sys.argv) is 5:
            seed = int(sys.argv[4])
    except:
        print("Parameters: repetitions of the main loop, number of slots for acquirations, number of objects, seed(optional)")
        sys.exit(1)
    (bench, seed) = benchpattern.create_pattern(int(repetitions), int(slots), int(objects), seed)
    print("seed: " + str(seed))
    print("repetitions: " + str(repetitions))
    print("slots: " + str(slots))
    print("objects: " + str(objects))
    print("distance: " + str(benchpattern.calculate_mean_distance(bench)))
    print("acquiration_duration: " + str(benchpattern.calculate_mean_acquiration_duration(bench)))
    print("waiting_duration: " + str(benchpattern.calculate_mean_waiting_duration(bench)))
    print("sizes: " + str(benchpattern.calculate_mean_sizes(bench)))
    print("complete_duration: " + str(benchpattern.calculate_full_duration(bench)))
    print("standard_deviation_of_sizes: " + str(benchpattern.calculate_standard_deviation_of_sizes(bench)))
    print("standard_deviation_of_distances: " + str(benchpattern.calculate_standard_deviation_of_distances(bench)))
    print("standard_deviation_of_acquiration_durations: " + str(benchpattern.calculate_standard_deviation_of_acquiration(bench)))
    print("standard_deviation_of_waiting_durations: " + str(benchpattern.calculate_standard_deviation_of_waiting(bench)))

    bench.generate_bench_app()
