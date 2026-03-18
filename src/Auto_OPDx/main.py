import sys
import numpy as np
import pandas as pd
import cv2
import traceback
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, 
                             QSpinBox, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt
from OPDx_read.reader import DektakLoad
from .global_plane import generate_global_plane
from .mask import refine_background_mask
from .filter import filter_components
from .reorder import reorder_components
from .calculate_heights import calculate_heights

class ProfilometryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Profilometry Heights GUI')
        self.resize(550, 450)
        
        layout = QVBoxLayout()
        
        # 1. OPDx File Selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("OPDx File:")
        self.file_input = QLineEdit()
        self.file_btn = QPushButton("Browse")
        self.file_btn.clicked.connect(self.browse_opdx)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.file_btn)
        layout.addLayout(file_layout)
        
        # 2. Grid Layout Specification
        grid_layout = QHBoxLayout()
        self.rows_label = QLabel("Grid Rows:")
        self.rows_input = QSpinBox()
        self.rows_input.setMinimum(1)
        self.rows_input.setValue(1)
        
        self.cols_label = QLabel("Grid Columns:")
        self.cols_input = QSpinBox()
        self.cols_input.setMinimum(1)
        self.cols_input.setValue(1)
        
        grid_layout.addWidget(self.rows_label)
        grid_layout.addWidget(self.rows_input)
        grid_layout.addWidget(self.cols_label)
        grid_layout.addWidget(self.cols_input)
        layout.addLayout(grid_layout)
        
        # 3. Output CSV Selection
        csv_layout = QHBoxLayout()
        self.csv_label = QLabel("Output CSV:")
        self.csv_input = QLineEdit()
        self.csv_btn = QPushButton("Browse")
        self.csv_btn.clicked.connect(self.browse_csv)
        csv_layout.addWidget(self.csv_label)
        csv_layout.addWidget(self.csv_input)
        csv_layout.addWidget(self.csv_btn)
        layout.addLayout(csv_layout)
        
        # 4. Run Button
        self.run_btn = QPushButton("Process Data")
        self.run_btn.setStyleSheet("font-weight: bold; padding: 10px;")
        self.run_btn.clicked.connect(self.process_data)
        layout.addWidget(self.run_btn)
        
        # 5. Log Output Area
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
        self.setLayout(layout)

    def log(self, message):
        """Helper to print messages to the GUI text box."""
        self.log_output.append(message)
        # Force the text edit to scroll to the bottom
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
        QApplication.processEvents()
        
    def browse_opdx(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select OPDx File", "", "OPDx Files (*.OPDx *.opdx);;All Files (*)")
        if filename:
            self.file_input.setText(filename)
            
    def browse_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Output CSV", "sample_heights.csv", "CSV Files (*.csv);;All Files (*)")
        if filename:
            self.csv_input.setText(filename)
            
    def process_data(self):
        opdx_file = self.file_input.text()
        csv_file = self.csv_input.text()
        rows = self.rows_input.value()
        cols = self.cols_input.value()

        if not opdx_file or not csv_file:
            QMessageBox.warning(self, "Input Error", "Please specify both the input OPDx and output CSV file paths.")
            return

        self.log(f"Loading data from {opdx_file}...")

        try:
            # Load Data
            loader = DektakLoad(opdx_file)
            x, y, z = loader.get_data_2D()


            self.log(f"Data loaded successfully. Matrix shape: {z.shape}")
            self.log(f"Applying Grid Layout: {rows} rows by {cols} cols...")

            num_samples = rows * cols
            x_mesh, y_mesh = np.meshgrid(x, y)

            global_plane, intercept, coeff  = generate_global_plane(z, x_mesh, y_mesh, group_size=10)
            background_mask = refine_background_mask(z, x_mesh, y_mesh, intercept, coeff)

            # Prepare mask for OpenCV connectedComponentsWithStats
            connectivity = 4
            output_mask_cv = (~background_mask).astype(np.uint8) * 255

            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(output_mask_cv, connectivity, cv2.CV_32S)

            self.log(f"OpenCV found {num_labels} raw components.")

            new_num_labels, filtered_labels, filtered_stats, filtered_centroids = filter_components(num_labels, labels, stats, centroids)

            self.log(f"After filtering, {new_num_labels} components remain.")

            final_labels, final_stats, final_centroids = reorder_components(num_labels, stats, centroids, rows, cols)

            self.log(f"Final count for height calculation: {len(final_stats)}")

            height_results = calculate_heights(z, x_mesh, y_mesh, final_stats, final_centroids, background_mask, intercept, coeff, num_samples)

            # Create DataFrame and Export
            df_heights = pd.DataFrame(height_results)
            df_heights.to_csv(csv_file, index=False)

            self.log(f"Calculation complete. Results successfully saved to {csv_file}")

        except Exception as e:
            traceback.print_exc()
            self.log(f"Error at: {traceback.format_exc().splitlines()[-2]}")
            self.log(f"Message: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = ProfilometryApp()
    window.show()
    sys.exit(app.exec_())
