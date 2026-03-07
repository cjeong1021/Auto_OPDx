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

### Using `uv`
[uv](https://github.com/astral-sh/uv) handles virtual environments and dependencies automatically based on the `pyproject.toml` file. 

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/cjeong1021/Auto_OPDx.git](https://github.com/cjeong1021/Auto_OPDx.git)
    cd Auto_OPDx
    ```
2.  **Sync dependencies:**
    This command creates a virtual environment and installs all necessary packages in one step.
    ```bash
    uv sync

    ```
---

## Usage

### Running the GUI
**Using uv:**
Run the application script directly without needing to manually activate the environment:
```bash
    uv run script
```

### Running the GUI

1.  Launch Server
```bash
    uv run jupyter lab 
```
2.  This will open a web browser where you can open `profilometryheights_notebook.ipynb`.
