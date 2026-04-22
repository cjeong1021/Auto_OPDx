import sys
import os
import numpy as np
import pandas as pd
import cv2
import traceback
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, 
                             QSpinBox, QTextEdit, QMessageBox, QListWidget, QListWidgetItem,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from OPDx_read.reader import DektakLoad
from Auto_OPDx.global_plane import generate_global_plane
from Auto_OPDx.mask import refine_background_mask
from Auto_OPDx.filter import filter_components
from Auto_OPDx.reorder import reorder_components
from Auto_OPDx.calculate_heights import calculate_heights

class ProfilometryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Profilometry Heights GUI')
        self.resize(900, 850)
        
        main_layout = QHBoxLayout()
        layout = QVBoxLayout()
        
        # 1. OPDx File Selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("OPDx Files:")
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
        self.rows_input.setValue(8)
        
        self.cols_label = QLabel("Grid Columns:")
        self.cols_input = QSpinBox()
        self.cols_input.setMinimum(1)
        self.cols_input.setValue(8)
        
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
        
        main_layout.addLayout(layout, stretch=1)

        # Right side visualization
        viz_main_layout = QVBoxLayout()
        
        self.preview_list = QListWidget()
        self.preview_list.setViewMode(QListWidget.IconMode)
        self.preview_list.setIconSize(QSize(100, 100))
        self.preview_list.setResizeMode(QListWidget.Adjust)
        self.preview_list.setFixedHeight(150)
        self.preview_list.itemClicked.connect(self.display_selected_visualization)
        viz_main_layout.addWidget(self.preview_list)
        
        self.viz_container = QWidget()
        self.viz_container_layout = QVBoxLayout(self.viz_container)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.viz_container_layout.addWidget(self.canvas)
        viz_main_layout.addWidget(self.viz_container, stretch=1)
        
        main_layout.addLayout(viz_main_layout, stretch=2)
        
        self.setLayout(main_layout)

    def log(self, message):
        """Helper to print messages to the GUI text box."""
        self.log_output.append(message)
        # Force the text edit to scroll to the bottom
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
        QApplication.processEvents()
        
    def browse_opdx(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select OPDx Files", "", "OPDx Files (*.OPDx *.opdx);;All Files (*)")
        if filenames:
            self.file_input.setText(";".join(filenames))
            self.update_visualizations(filenames)
            
    def update_visualizations(self, filenames):
        self.preview_list.clear()
        self.figure.clear()
        self.canvas.draw()
        self.cached_scans = {}
        QApplication.processEvents()
        
        for idx, opdx_file in enumerate(filenames):
            try:
                loader = DektakLoad(opdx_file)
                x, y, z = loader.get_data_2D()
                self.cached_scans[opdx_file] = (x, y, z)
                
                import matplotlib.cm as cm
                # Normalize and colorize for thumbnail using matplotlib viridis colormap
                z_norm_plt = (z - z.min()) / (z.max() - z.min() + 1e-8)
                z_color_rgba = cm.viridis(z_norm_plt)
                z_color_rgb = (z_color_rgba[:, :, :3] * 255).astype(np.uint8)
                z_color_rgb = np.ascontiguousarray(np.flipud(z_color_rgb))
                
                h, w, ch = z_color_rgb.shape
                bytes_per_line = ch * w
                qimg = QImage(z_color_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                
                icon_pixmap = pixmap.scaled(100, 100, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                icon = QIcon(icon_pixmap)
                
                item = QListWidgetItem(icon, os.path.basename(opdx_file))
                item.setData(Qt.UserRole, opdx_file)
                self.preview_list.addItem(item)
                
                if idx == 0:
                    self.preview_list.setCurrentItem(item)
                    self.display_selected_visualization(item)
                    
            except Exception as e:
                self.log(f"Error previewing {opdx_file}: {e}")
                
        if not filenames:
            self.figure.clear()
            self.canvas.draw()

    def display_selected_visualization(self, item):
        opdx_file = item.data(Qt.UserRole)
        if opdx_file in getattr(self, 'cached_scans', {}):
            x, y, z = self.cached_scans[opdx_file]
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            im = ax.imshow(z, cmap='viridis', origin='lower', extent=[x.min(), x.max(), y.min(), y.max()], aspect='equal')
            self.figure.colorbar(im, ax=ax, label='Height')
            ax.set_title(os.path.basename(opdx_file))
            ax.set_xlabel('X (μm)')
            ax.set_ylabel('Y (μm)')
            self.canvas.draw()
            
    def browse_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Output CSV", "sample_heights.csv", "CSV Files (*.csv);;All Files (*)")
        if filename:
            self.csv_input.setText(filename)
            
    def process_data(self):
        opdx_files_text = self.file_input.text()
        csv_file = self.csv_input.text()
        rows = self.rows_input.value()
        cols = self.cols_input.value()

        if not opdx_files_text or not csv_file:
            QMessageBox.warning(self, "Input Error", "Please specify both the input OPDx files and output CSV file paths.")
            return

        opdx_files = [f.strip() for f in opdx_files_text.split(";") if f.strip()]
        all_results = []

        for idx, opdx_file in enumerate(opdx_files):
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

                # Append file info and results
                filename = os.path.basename(opdx_file)
                all_results.append((filename, height_results))

            except Exception as e:
                traceback.print_exc()
                self.log(f"Error processing {opdx_file} at: {traceback.format_exc().splitlines()[-2]}")
                self.log(f"Message: {str(e)}")
                continue

        if all_results:
            import csv
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                
                if all_results and all_results[0][1]:
                    columns = list(all_results[0][1][0].keys())
                else:
                    columns = ['component_id', 'centroid_x', 'centroid_y', 'top', 'bottom', 'difference']

                for file_idx, (filename, file_results) in enumerate(all_results):
                    # Write the filename
                    writer.writerow([f"{filename}"])
                    # Write the data column headers
                    writer.writerow(columns)

                    for i, res in enumerate(file_results):
                        row = [res.get(col, '') for col in columns]
                        writer.writerow(row)
                        
                        # Add a blank line every 16 points
                        if (i + 1) % 16 == 0 and (i + 1) != len(file_results):
                            writer.writerow([])
                            
                    # Add a blank line before the next file's header
                    if file_idx < len(all_results) - 1:
                        writer.writerow([])

            self.log(f"Calculation complete. Results successfully saved to {csv_file}")
        else:
            self.log("No results were generated. Check for errors.")

def main():
    app = QApplication(sys.argv)
    window = ProfilometryApp()
    window.show()
    sys.exit(app.exec_())
