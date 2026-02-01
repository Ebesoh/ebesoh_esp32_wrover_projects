# gps_sentence_diversity_test.py
#Goal: Ensure real GPS parsing, not repeated junk.
def test_sentence_diversity(nmea_lines):
    print("TEST: NMEA sentence diversity")

    types = set()

    for line in nmea_lines:
        if line.startswith("$"):
            types.add(line[1:6])

    print("Sentence types:", types)
    return len(types) >= 2
