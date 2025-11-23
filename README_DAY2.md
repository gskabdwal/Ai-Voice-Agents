# Day 2: Coffee Shop Barista Agent

## Overview
This agent acts as a friendly barista at "Code & Coffee". It takes orders, asks clarifying questions, and visualizes the order in real-time on the frontend.

## Features
- **Persona**: Friendly Barista.
- **State Management**: Tracks Drink, Size, Milk, Extras, Name.
- **Tools**: `update_order` and `submit_order`.
- **Visualization**: Real-time coffee cup rendering on the frontend (Advanced Challenge).
- **Output**: Saves completed orders to `backend/order.json`.

## How to Run

### 1. Backend (Agent)
The agent logic is in `backend/src/agent.py`.

1. Open a terminal.
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Install dependencies (if not already done):
   ```bash
   # If using uv
   uv sync
   # Or using pip with the existing venv
   .\.venv\Scripts\pip install -r requirements.txt # (if requirements.txt exists)
   # Or just rely on existing environment
   ```
4. Run the agent:
   ```bash
   # If using uv
   uv run src/agent.py dev
   # Or using python directly (Windows)
   .\.venv\Scripts\python src/agent.py dev
   ```

### 2. Frontend (Web UI)
The frontend has been updated to include the `OrderVisualization` component.

1. Open a new terminal.
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies (if needed):
   ```bash
   pnpm install
   ```
4. Run the development server:
   ```bash
   pnpm dev
   ```
5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage
1. Click "Start call" on the web page.
2. Speak to the agent (e.g., "I'd like a latte").
3. The agent will ask for missing details (Size, Milk, Name).
4. Watch the coffee cup visualization update in real-time!
5. Once confirmed, the agent will save the order to `backend/order.json`.

## Verification
- Check `backend/order.json` after finishing an order to see the summary.
- Record your video as per the challenge instructions!
