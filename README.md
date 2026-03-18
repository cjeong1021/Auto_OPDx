# Auto_OPDx

**Auto_OPDx** is a Python-based tool designed for the automated processing and analysis of profilometry data (OPDx files). It provides both a graphical user interface (GUI) for interactive data visualization and a Jupyter Notebook interface for flexible, document-based analysis.

## Features

* **OPDx Parsing:** Native support for loading and extracting surface data from OPDx files.
* **Interactive Visualization:** Integrated Matplotlib plotting within a Qt-based GUI to inspect surface profiles instantly.
* **Automated Export:** Seamlessly transition from raw data to structured CSV files for downstream analysis.

---

## Installation

### Prerequisites
* **Python 3.10+**
* It is highly recommended to use [uv](https://github.com/astral-sh/uv) for the fastest and most reliable dependency management.
* Or you can use pip.

### Installing with pip
1.  **Clone the repository and navigate into it:**
    ```
    git clone https://github.com/cjeong1021/Auto_OPDx.git

    cd Auto_OPDx
    ```
2.  **Create and activate a virtual environment:**
    ```
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install:**
    ```
    pip install -e .
    ```

### Installing with `uv`
[uv](https://github.com/astral-sh/uv) handles virtual environments and dependencies automatically based on the `pyproject.toml` file. 

1.  **Clone the repository and navigate into it:**
    ```
    git clone https://github.com/cjeong1021/Auto_OPDx.git

    cd Auto_OPDx
    ```
2.  **Sync dependencies:**
    This command creates a virtual environment and installs all necessary packages in one step.
    ```
    uv sync
    ```

## Usage

### Running the GUI
Run the application in your virtual environment:
```
auto-opdx
```

### Running Jupyter Notebook
An interactive Jupyter Notebook is also provided for better visualization. You can run the Jupyter Notebook in the virtual environment:

1.  Launching Server
```bash
jupyter lab 
```
This will open a web browser where you can open `profilometryheights_notebook.ipynb`. Ensure all OPDx files are in the same directory and complete the initial prompt asking for the file name and grid rows/cols.
