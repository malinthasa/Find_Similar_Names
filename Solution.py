import sys
import re
from Levenshtein import distance
import pandas as pd
import logging
import numpy as np

logging.basicConfig(level=logging.ERROR)

# Regular expression for processing the original names
RGX_EXTRACT_TEXT_IN_BRACKETS = r"[\(\[].*?[\)\]]"
RGX_IDENTIFY_BRACKETS = r"[\()]"

# Column name of the dog names column in the data file
DOG_COLUMN_NAME = "HUNDENAME"


def _split_names_from_original_names(original_name):
    """
    This function separate the text inside the round brackets as a different name
    ex: "Abby (Abbygail)" is separated as ["Abby", "Abbygail"]
    :param original_name: the original text extracted from the data file as the name
    :return: list of possible names of the given dog
    """
    found_names = []
    # Find all texts in the brackets inside an original name
    in_bracket_names = re.findall(RGX_EXTRACT_TEXT_IN_BRACKETS, original_name)

    # Text after removing the content inside the brackets
    found_names.append(re.sub(RGX_EXTRACT_TEXT_IN_BRACKETS, "", original_name))

    # appending the name/s inside the round brackets
    found_names = found_names + [re.sub(RGX_IDENTIFY_BRACKETS, "", z) for z in in_bracket_names]

    # return the separated names as a list
    return found_names


def main(argv):
    try:
        # Handling number of commandline arguments
        if len(argv) != 3:
            raise Exception

        # reading the source csv file into a dataframe
        df = pd.read_csv(argv[0], delimiter=',')

        # get the unique dog names into a list
        unique_names = list(df[DOG_COLUMN_NAME].unique())

        # Note: According to the observations, some names may contain alternative/ owner information inside
        # the round brackets
        # I made an assumption of such alternative and owner information embedded in the original names
        # (inside brackets) and split the original name text into multiple name to minimize the error for such scenarios

        # Splitting the original name text into multiple names in where there are round brackets
        filtered_names = [_split_names_from_original_names(x) for x in unique_names if x == x and x != ""]

        # Flatten the list of lists into a single list
        filtered_names = list(set([item for sublist in filtered_names for item in sublist]))

        # Here I use the https://github.com/polm/levenshtein python library to calculate Levenshtein distance between
        # two strings.

        # calculate the levenshtein distance between each name in the given dog names list and the given reference name
        levenshtein_distances = np.array([distance(name, argv[1]) for name in filtered_names])

        # Indexes of the names for which the levenshtein distance match with the given distance value
        score_matches = np.where(levenshtein_distances == float(argv[2]))[0]

        # identified names for the given score
        matched_names = [filtered_names[x] for x in score_matches]
        print(",".join(matched_names))

    except FileNotFoundError:
        logging.error("Could not find a valid file in the provided path")
    # TODO Use exact exception type rather than generic exception
    except Exception:
        logging.error("Invalid inputs. Please provide the data file name, Reference name and the Levenshtein score")
    return


if __name__ == "__main__":
    main(sys.argv[1:])
