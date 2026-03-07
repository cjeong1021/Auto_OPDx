import numpy as np

def calculate_heights(z, x_mesh, y_mesh, final_stats, final_centroids, background_mask, intercept, coeff, num_samples):
    # Setup bounding box
    box_w_px = 15
    box_h_px = 80

    # Prepare list for results
    height_results = []

    # Iterate through slots 1-64
    for i in range(1, num_samples + 1):
        # Check if component exists (stats not zero)
        if np.all(final_stats[i] == 0):
            height_results.append({
            'component_id': i,
            'centroid_x': 'NoVal',
            'centroid_y': 'NoVal',
            'top': 'NoVal',
            'bottom': 'NoVal',
            'difference': 'NoVal',
        })
            continue
            
        cx_px, cy_px = final_centroids[i]
        
        # Define crop boundaries (ensure within image limits)
        y_start = int(max(0, cy_px - box_h_px // 2))
        y_end = int(min(z.shape[0], cy_px + box_h_px // 2))
        x_start = int(max(0, cx_px - box_w_px // 2))
        x_end = int(min(z.shape[1], cx_px + box_w_px // 2))
        

        # Extract local data in region
        x_mesh_local = x_mesh[y_start:y_end, x_start:x_end]
        y_mesh_local = y_mesh[y_start:y_end, x_start:x_end]
        z_local = z[y_start:y_end, x_start:x_end]
        new_background_mask_local = background_mask[y_start:y_end, x_start:x_end]

        # Extract local background pixels for plane fitting
        x_bg_for_fit = x_mesh_local[new_background_mask_local]
        y_bg_for_fit = y_mesh_local[new_background_mask_local]
        z_bg_for_fit = z_local[new_background_mask_local]

        # Determine plane coefficients for local region
        local_reg_coef = coeff  # Fallback to global
        local_reg_intercept = intercept # Fallback to global

        # Only fit a local plane if enough background points (min 3 for a plane)
        if len(x_bg_for_fit) >= 3:
            A_local_bg = np.c_[x_bg_for_fit, y_bg_for_fit, np.ones(x_bg_for_fit.shape[0])]
            try:
                coeffs_local, _, _, _ = np.linalg.lstsq(A_local_bg, z_bg_for_fit, rcond=None)
                local_reg_coef = coeffs_local[:2]
                local_reg_intercept = coeffs_local[2]
            except np.linalg.LinAlgError:
                print(f"Warning: Local plane fit failed for component {i} (singular matrix). Using global plane.")
        else:
            print(f"Warning: Not enough background points ({len(x_bg_for_fit)}) for local plane fit for component {i}. Using global plane.")

        # Find the index of the maximum Z-height within the local region
        max_z_idx_flat = np.argmax(z_local)
        max_z_row, max_z_col = np.unravel_index(max_z_idx_flat, z_local.shape)

        # (x,y) coordinates at the location of max Z
        x_at_max_z = x_mesh_local[max_z_row, max_z_col]
        y_at_max_z = y_mesh_local[max_z_row, max_z_col]

        # Calculate predicted Z-value at the exact (x,y) of max Z
        z_predicted_at_max_z_idx = local_reg_intercept + local_reg_coef[0] * x_at_max_z + local_reg_coef[1] * y_at_max_z

        # Calculate the max actual Z-height within the local region
        max_z_in_local_region = z_local.max()

        # Calculate the height of the sample (feature height above local plane at that specific point)
        # Convert to micrometers
        sample_height_from_exact_point = (max_z_in_local_region - z_predicted_at_max_z_idx) * 1e6

        height_results.append({
            'component_id': i,
            'centroid_x': cx_px,
            'centroid_y': cy_px,
            'top': max_z_in_local_region * 1e6,
            'bottom': z_predicted_at_max_z_idx * 1e6,
            'difference': sample_height_from_exact_point,
        })

    return height_results
