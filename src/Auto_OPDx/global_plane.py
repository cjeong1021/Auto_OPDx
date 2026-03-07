import numpy as np


def generate_global_plane(z, x_mesh, y_mesh, group_size):

    # Group by 10 lines
    num_rows = z.shape[0]
    group_size = 10

    # Number of groups
    num_groups = int(np.ceil(num_rows / group_size))

    # List to hold threshold for each group
    group_background_thresholds = []

    # Loop through the z array in steps of group_size:
    for i in range(num_groups):
        # Select group from z
        start_row = i * group_size
        end_row = min((i + 1) * group_size, num_rows)
        current_group_data = z[start_row:end_row, :]

        combined_heights = current_group_data.flatten()

        # Calculate threshold
        percentile_value = np.percentile(combined_heights, 45)
        group_background_thresholds.append(percentile_value)

    group_background_masks_rows = []

    # Apply threshold to each row
    for row_idx in range(num_rows):
        group_index = row_idx // group_size

        # Get the corresponding group threshold
        threshold = group_background_thresholds[group_index]

        # Get the current row data from z
        row_data = z[row_idx, :]

        # Create a boolean mask: True if pixel height <= threshold
        row_mask = row_data <= threshold
        group_background_masks_rows.append(row_mask)

    # Convert the list of row masks into a single numpy boolean array
    group_background_mask = np.array(group_background_masks_rows)
    x_background = x_mesh[group_background_mask]
    y_background = y_mesh[group_background_mask]
    z_actual_background = z[group_background_mask]

    A_background = np.c_[x_background, y_background, np.ones(x_background.shape[0])]

    # 2. Perform a least squares fit
    coeffs_background, _, _, _ = np.linalg.lstsq(A_background, z_actual_background, rcond=None)

    # Store the coefficients and intercept
    reg_coef_background = coeffs_background[:2]
    reg_intercept_background = coeffs_background[2]

    # Calculate Z values from estimated coefficients
    z_predicted_background_new_plane = reg_intercept_background + reg_coef_background[0] * x_background + reg_coef_background[1] * y_background

    return z_predicted_background_new_plane, reg_intercept_background, reg_coef_background

