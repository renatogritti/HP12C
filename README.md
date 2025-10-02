# HP-12C Calculator Simulator

This project is a functional recreation of the classic HP-12C financial calculator, using Python and the Pygame library for the graphical interface. The goal is to simulate the behavior of the original calculator, including its Reverse Polish Notation (RPN) logic and its main financial functions.

## Features

*   **Graphical Interface**: Visual layout faithful to the physical HP-12C calculator.
*   **RPN Logic**: Stack-based operation with `ENTER`, `CHS`, `CLx`, `R↓` (Roll Down), and `x<>y` (Swap X and Y) keys.
*   **Arithmetic Operators**: Addition (`+`), Subtraction (`-`), Multiplication (`×`), Division (`÷`).
*   **Mathematical Functions**: Power (`y^x`), Reciprocal (`1/x`), and Square Root (`√x`).
*   **Percentage Functions**: Percent (`%`) and Percent Difference (`Δ%`).
*   **Financial Functions (TVM)**: Full implementation for calculating `n` (periods), `i` (interest), `PV` (present value), `PMT` (payments), and `FV` (future value).
*   **Modifier Keys**: Support for `f` (orange) and `g` (blue) keys to access secondary functions, with visual indicators on the screen.
*   **Statistical Functions**: Basic statistical operations like mean (`x̄`) and standard deviation (`s`).
*   **Date Functions**: Calculate the number of days between dates (`ΔDYS`) and find a future/past date.
*   **Depreciation**: SL (Straight-Line), SOYD (Sum-of-the-Years'-Digits), and DB (Declining Balance) depreciation methods.

## How to Run

Follow the steps below to run the calculator on your computer.

### Prerequisites

*   Python 3.6 or higher installed.
*   Docker (optional, for running in a container).

### 1. Clone the repository

```bash
git clone https://github.com/your-username/HP12C.git
cd HP12C
```

### 2. Install dependencies

Open your terminal or command prompt and run the following command to install the Pygame library:

```bash
pip install -r requirements.txt
```

### 3. Run the Calculator

Navigate to the project directory in your terminal and run the `main.py` file:

```bash
python main.py
```

A window with the HP-12C calculator will appear, and you can start using it by clicking the buttons with the mouse or using the keyboard shortcuts.

## Keyboard Shortcuts

| Key             | Calculator Function |
| --------------- | ------------------- |
| `0-9`           | Digits 0-9          |
| `.`             | Decimal point       |
| `+`, `-`, `*`, `/` | Arithmetic operators|
| `Enter`         | `ENTER`             |
| `Backspace`     | `CLx`               |
| `f`             | `f` key             |
| `g`             | `g` key             |
| `n`             | `n` key             |
| `i`             | `i` key             |


## Docker

You can also run the application inside a Docker container. This requires Docker to be installed on your system.

### Build the Docker image

```bash
docker build -t hp12c-simulator .
```

### Run the Docker container

To run the container, you need to forward the X11 socket to the container.

```bash
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix hp12c-simulator
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.