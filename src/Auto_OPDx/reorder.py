import numpy as np
from scipy.optimize import linear_sum_assignment
import cv2

def reorder_components(num_labels, stats, centroids, rows, cols):
    min_area = 15
    valid_comp_indices = [i for i in range(1, num_labels) if stats[i, cv2.CC_STAT_AREA] >= min_area]
    comp_centroids_raw = centroids[valid_comp_indices]
    comp_stats_raw = stats[valid_comp_indices]

    print(f"Total components detected for mapping: {len(comp_centroids_raw)}")

    # 2. Define 8x8 Grid centers based on the bounds of these detections
    unique_x = np.linspace(comp_centroids_raw[:, 0].min(), comp_centroids_raw[:, 0].max(), 8)
    unique_y = np.linspace(comp_centroids_raw[:, 1].min(), comp_centroids_raw[:, 1].max(), 8)

    # 3. Create theoretical slots in quadrant order (BL, TL, BR, TR)
    # Quadrant ranges: 0-3 and 4-7
    quadrant_ranges = [
        ((0, 4), (0, 4)), # Bottom-Left
        ((0, 4), (4, 8)), # Top-Left
        ((4, 8), (0, 4)), # Bottom-Right
        ((4, 8), (4, 8))  # Top-Right
    ]

    theoretical_slots = []
    for col_range, row_range in quadrant_ranges:
        # Within quadrant: Sequential on each row (L-R), Bottom to Top
        for r in range(row_range[0], row_range[1]):
            for c in range(col_range[0], col_range[1]):
                theoretical_slots.append((unique_x[c], unique_y[r]))
    theoretical_slots = np.array(theoretical_slots)

    # 4. Global 1-to-1 Mapping
    dist_matrix = np.zeros((len(comp_centroids_raw), len(theoretical_slots)))
    for i in range(len(comp_centroids_raw)):
        for j in range(len(theoretical_slots)):
            dist_matrix[i, j] = np.linalg.norm(comp_centroids_raw[i] - theoretical_slots[j])

    det_indices, slot_indices = linear_sum_assignment(dist_matrix)

    slot_to_det_map = {slot_idx + 1: det_idx for det_idx, slot_idx in zip(det_indices, slot_indices)}

    # 5. Build final 65-element arrays
    final_centroids = np.zeros((65, 2))
    final_stats = np.zeros((65, 5), dtype=int)
    final_centroids[0] = centroids[0]
    final_stats[0] = stats[0]


    for slot_id in range(1, rows * cols + 1):
        if slot_id in slot_to_det_map:
            d_idx = slot_to_det_map[slot_id]
            final_centroids[slot_id] = comp_centroids_raw[d_idx]
            final_stats[slot_id] = comp_stats_raw[d_idx]
        else:
            final_centroids[slot_id] = theoretical_slots[slot_id - 1]
            final_stats[slot_id] = 0

    return final_centroids, final_stats, final_centroids
