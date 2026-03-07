import numpy as np

def refine_background_mask(z, x_mesh, y_mesh, intercept, coeff):
    # Calculate predicted Z-values for the entire data (x_mesh, y_mesh)
    # using the plane coefficients derived from previous background data
    z_predicted_full = intercept + coeff[0] * x_mesh + coeff[1] * y_mesh

    # Calculate difference
    difference_z = np.abs(z - z_predicted_full)

    # Refine background mask where the difference is less than 2µm
    new_background_mask = difference_z < 2e-6

    return new_background_mask

