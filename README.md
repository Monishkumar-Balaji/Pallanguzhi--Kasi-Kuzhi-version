# Pallanguzhi Game

A modern, traditional variant of the classic South Indian board game **Pallanguzhi**, built using Python and the `arcade` library. 

This digital version faithfully recreates the authentic physical experience, featuring a 2x7 board layout, strategic sowing and capturing mechanics, multi-round progression, and a computer opponent (AI) to challenge your skills.

## Features

*   **Traditional Board Layout:** 2x7 pits with a central **Kasi Kuzhi** (storage well) in each row (column 3).
*   **Configurable Start:** Choose your starting seed count (from 2 to 6 counters per pit) directly from the home screen.
*   **Authentic Rule Set:**
    *   **Sowing & Continuation:** Sowing seeds one by one; if your last seed lands in a non-empty pit, you pick up those seeds and continue.
    *   **Capturing:** If the last seed drops into an empty pit, you capture the seeds from the adjacent pit and the opposite pit.
    *   **Pasu (4-counter) Collection:** Whenever a pit accumulates exactly 4 counters, the active player collects them immediately.
    *   **End of Round & Multi-Round Mechanics:** Unreserved Kasi seeds carry forward, and players only collect from their reserved Kasis.
*   **AI Opponent:** Play against the computer if you don't have a second player.
*   **Gameplay Controls:** Instantly terminate the current game and return to the main menu using the `ESC` key.

## Installation & Setup

### Prerequisites
*   Python 3.8+ 
*   `arcade` library

### Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Monishkumar-Balaji/Pallanguzhi--Kasi-Kuzhi-version.git
    cd Pallanguzhi--Kasi-Kuzhi-version
    ```

2.  **Create a virtual environment (Optional but recommended):**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Play

To launch the game, run the main script from your terminal:

```bash
python main.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Download

👉 [Download Latest Version] https://github.com/Monishkumar-Balaji/Pallanguzhi--Kasi-Kuzhi-version/releases/download/v2.0/Pallanguzhi-Setup.exe

[Download from SourceForge] https://sourceforge.net/projects/pallanguzhi-game/

