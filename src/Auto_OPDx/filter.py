import numpy as np
import cv2

def filter_components(num_labels, labels, stats, centroids):
    min_area_threshold = 15

    filtered_labels = np.zeros_like(labels, dtype=np.int32)

    # Initialize lists to store filtered stats and centroids
    filtered_stats = [stats[0]]
    filtered_centroids = [centroids[0]]

    # Iterate through each component (starting from label 1, as 0 is background)
    current_label = 1
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area_threshold:
            filtered_labels[labels == i] = current_label # Assign new sequential label
            filtered_stats.append(stats[i])
            filtered_centroids.append(centroids[i])
            current_label += 1

    # Convert lists back to numpy arrays
    filtered_stats = np.array(filtered_stats)
    filtered_centroids = np.array(filtered_centroids)

    # Get the new number of labels
    new_num_labels = len(filtered_stats)

    return new_num_labels, filtered_labels, filtered_stats, filtered_centroids 

