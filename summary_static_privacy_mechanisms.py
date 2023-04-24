import numpy as np
from collections import Counter


def mean_mechanism(samples, s):
    """Summary Static Privacy mechanism for mean

    Parameters:
    samples (1-D array-like): The original samples
    s (float): The segment length parameter of the mechanism

    Returns:
    1-D array-like: The processed samples

    """
    samples = np.asarray(samples)
    old_mean = np.mean(samples)
    seq_pos = int(old_mean / s)
    new_mean = (seq_pos + 0.5) * s
    new_samples = samples + new_mean - old_mean
    return new_samples


def quantile_mechanism(samples, s, alpha):
    samples = np.asarray(samples)
    """Summary Static Privacy mechanism for quantile

    Parameters:
    samples (1-D array-like): The original samples
    s (float): The segment length parameter of the mechanism
    alpha: The quantile to protect, which must be between 0 and 1 inclusive.

    Returns:
    1-D array-like: The processed samples

    """
    old_quantile = np.quantile(samples, alpha)
    seq_pos = int(old_quantile / s)
    new_quantile = (seq_pos + 0.5) * s
    new_samples = samples * new_quantile / old_quantile
    return new_samples


def fraction_mechanism(samples, s, class_):
    """Summary Static Privacy mechanism for fraction

    Parameters:
    samples (1-D array-like): The original samples
    s (float): The segment length parameter of the mechanism. 1/s must be an integer
    class_: The class whose fraction to be protected.

    Returns:
    1-D array-like: The processed samples

    """
    dist = dict(Counter(list(samples)))
    dist_keys = list(dist.keys())
    dist_values = np.asarray(list(dist.values()))
    dist_values = dist_values / np.sum(dist_values)
    if class_ not in dist_keys:
        raise ValueError(f'{class_} should appear at least once in samples')
    class_index = dist_keys.index(class_)

    seq_pos = int(dist_values[class_index] / s)
    old_class_fraction = dist_values[class_index]
    new_class_fraction = (seq_pos + 0.5) * s
    diff = new_class_fraction - old_class_fraction
    diff_per_other = -diff / (len(dist) - 1)
    new_dist_values = dist_values + diff_per_other
    new_dist_values[class_index] = new_class_fraction

    # Adjustment if min(new_dist) < 0.
    min_value = min(np.min(new_dist_values), 0)
    new_dist_values = new_dist_values - min_value
    new_dist_values[class_index] = (new_class_fraction +
                                    min_value * (len(dist) - 1))

    # Generate new samples.
    new_samples = np.random.choice(
        dist_keys, size=len(samples), p=new_dist_values)
    return new_samples
