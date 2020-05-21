import numpy as np
from copy import deepcopy
from .config import datadir


def normalize_dictionary(d):
    """
    Normalize the dictionary ``d``.

    Args:
        d (dict): A dictionary with numerical values.

    Returns:
        A normalized dictionary.
    """
    total = np.sum([d[i] for i in d], dtype=float)
    if total == 0.0:
        return d
    new_dictonary = {}
    for i in d:
        new_dictonary[i] = float(d[i])/total
    return new_dictonary


def norm_age_group(age_dictionary, age_min, age_max):
    """
    Create a normalized dictionary for the range ``age_min`` to ``age_max``, inclusive.

    Args:
        age_dictionary (dict) : A dictionary with numerical values.
        age_min (int)         : The minimum value of the range for the dictionary.
        age_max (int)         : The maximum value of the range for the dictionary.

    Returns:
        A normalized dictionary for keys in the range ``age_min`` to ``age_max``, inclusive.
    """
    dictionary = {}
    for a in range(age_min, age_max+1):
        dictionary[a] = age_dictionary[a]
    return normalize_dictionary(dictionary)


# Functions related to age distributions

def get_age_by_brackets_dictionary(age_brackets):
    """
    Create a dictionary mapping age to the age bracket it falls in.

    Args:
        age_brackets (dict): A dictionary mapping age bracket keys to age bracket range.

    Returns:
        A dictionary of age bracket by age.
    """
    age_by_brackets_dictionary = {}
    for b in age_brackets:
        for a in age_brackets[b]:
            age_by_brackets_dictionary[a] = b
    return age_by_brackets_dictionary


def get_aggregate_ages(ages, age_by_brackets_dictionary):
    """
    Create a dictionary of the count of ages by age brackets.

    Args:
        ages (dict)                       : A dictionary of age count by single year.
        age_by_brackets_dictionary (dict) : A dictionary mapping age to the age bracket range it falls within.
    Returns:
        A dictionary of aggregated age count for specified age brackets.
    """
    bracket_keys = set(age_by_brackets_dictionary.values())
    aggregate_ages = dict.fromkeys(bracket_keys, 0)
    for a in ages:
        b = age_by_brackets_dictionary[a]
        aggregate_ages[b] += ages[a]
    return aggregate_ages


def get_aggregate_age_dictionary_conversion(larger_aggregate_ages, larger_age_brackets, smaller_age_brackets, age_by_brackets_dictionary_larger, age_by_brackets_dictionary_smaller):
    """
    Convert the aggregate age count in ``larger_aggregate_ages`` from a larger number of age brackets to a smaller number of age brackets.

    Args:
        larger_aggregate_ages (dict)              : A dictionary of aggregated age count.
        larger_age_brackets (dict)                : A dictionary of age brackets.
        smaller_age_brackets (dict)               : A dictionary of fewer age brackets.
        age_by_brackets_dictionary_larger (dict)  : A dictionary mapping age to the larger number of age brackets.
        age_by_brackets_dictionary_smaller (dict) : A dictionary mapping age to the smaller number of age brackets.

    Returns:
        A dictionary of the aggregated age count for the smaller number of age brackets.

    """
    if len(larger_age_brackets) < len(smaller_age_brackets): raise NotImplementedError('Cannot reduce aggregate ages any further.')
    smaller_aggregate_ages = dict.fromkeys(smaller_age_brackets.keys(), 0)
    for lb in larger_age_brackets:
        a = larger_age_brackets[lb][0]
        sb = age_by_brackets_dictionary_smaller[a]
        smaller_aggregate_ages[sb] += larger_aggregate_ages[lb]
    return smaller_aggregate_ages


# Functions related to contact matrices

def get_aggregate_matrix(M, age_by_brackets_dictionary):
    """
    Aggregate a symmetric matrix to fewer age brackets. Do not use for homogeneous mixing matrix.

    Args:
        M (np.ndarray)                    : A symmetric age contact matrix.
        age_by_brackets_dictionary (dict) : A dictionary mapping age to the age bracket range it falls within.

    Returns:
        A symmetric contact matrix (``np.ndarray``) aggregated to age brackets.
   """
    N = len(M)
    num_agebrackets = len(set(age_by_brackets_dictionary.values()))
    M_agg = np.zeros((num_agebrackets, num_agebrackets))
    for i in range(N):
        bi = age_by_brackets_dictionary[i]
        for j in range(N):
            bj = age_by_brackets_dictionary[j]
            M_agg[bi][bj] += M[i][j]
    return M_agg


def get_asymmetric_matrix(symmetric_matrix, aggregate_ages):
    """
    Get the contact matrix for the average individual in each age bracket.

    Args:
        symmetric_matrix (np.ndarray) : A symmetric age contact matrix.
        aggregate_ages (dict)         : A dictionary mapping single year ages to age brackets.

    Returns:
        A contact matrix (``np.ndarray``) whose elements ``M_ij`` describe the contact frequency for the average individual in age bracket ``i`` with all possible contacts in age bracket ``j``.
    """
    M = deepcopy(symmetric_matrix)
    for a in aggregate_ages:
        M[a, :] = M[a, :]/float(aggregate_ages[a])

    return M


def get_symmetric_community_matrix(ages):
    """
    Get a symmetric homogeneous matrix.

    Args:
        ages (dict): A dictionary with the count of each single year age.
    Returns:
        A symmetric homogeneous matrix for age count in ages.
    """
    N = len(ages)
    M = np.ones((N, N))
    for a in range(N):
        M[a, :] = M[a, :] * ages[a]
        M[:, a] = M[:, a] * ages[a]
    for a in range(N):
        M[a, a] -= ages[a]
    M = M/(np.sum([ages[a] for a in ages], dtype=float) - 1)
    return M


def combine_matrices(matrix_dictionary, weights_dictionary, num_agebrackets):
    """
    Combine different contact matrices into a single contact matrix.

    Args:
        matrix_dictionary (dict)     : A dictionary of different contact matrices by setting.
        weights_dictionary (dict)    : A dictionary of weights for each setting.
        num_agebrackets (int)        : The number of age brackets for the different matrices.

    Returns:
        A contact matrix (``np.ndarray``) that is a linear combination of setting specific matrices given weights for each setting.
    """
    M = np.zeros((num_agebrackets, num_agebrackets))
    for setting_code in weights_dictionary:
        M += matrix_dictionary[setting_code] * weights_dictionary[setting_code]
    return M


def get_ids_by_age_dictionary(age_by_id_dictionary):
    """
    Get lists of IDs that map to each age.

    Args:
        age_by_id_dictionary (dict): A dictionary with the age of each individual by their ID.

    Returns:
        A dictionary listing IDs for each age from a dictionary that maps ID to age.
    """
    max_val = max([v for v in age_by_id_dictionary.values()])
    ids_by_age_dictionary = dict.fromkeys(np.arange(max_val+1))
    for i in ids_by_age_dictionary:
        ids_by_age_dictionary[i] = []
    for i in age_by_id_dictionary:
        ids_by_age_dictionary[age_by_id_dictionary[i]].append(i)
    return ids_by_age_dictionary


def get_uids_by_age_dictionary(popdict):
    """
    Get lists of UIDs that map to each age.

    Args:
        popdict (sc.dict): A dictionary mapping an individual's ID to a dictionary with their age and other attributes.
    Returns:
        A dictionary listing UIDs for each age.
    """
    uids_by_age_dictionary = {}
    for uid in popdict:
        uids_by_age_dictionary.setdefault(popdict[uid]['age'], [])
        uids_by_age_dictionary[popdict[uid]['age']].append(uid)
    return uids_by_age_dictionary
