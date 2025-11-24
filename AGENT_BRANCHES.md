# Agent Branch Guide

This project has multiple voice agents implemented in separate git branches. You can easily switch between them.

## Available Branches

### 🍵 `day-2-barista-agent` - Coffee Shop Barista
A friendly barista that takes coffee orders at "Code & Coffee"

**Features:**
- Takes coffee orders via voice
- Collects: drink type, size, milk preference, extras, customer name
- Saves orders to `order.json`
- Sends real-time updates to frontend

**To use:**
```powershell
git checkout day-2-barista-agent
cd backend
.venv\Scripts\python.exe src\agent.py dev
```

---

### 🧘 `day-3-wellness-agent` - Health & Wellness Companion
A supportive wellness companion for daily check-ins

**Features:**
- Daily mood and energy check-ins
- Collects stress factors and daily objectives
- Persists to `wellness_log.json`
- References past check-ins for continuity
- Supportive, non-medical advice

**To use:**
```powershell
git checkout day-3-wellness-agent
cd backend
.venv\Scripts\python.exe src\agent.py dev
```

---

## Quick Switch Guide

### Switch to Barista Agent
```powershell
# Make sure you're in the project root
cd c:\CS\Development\ten-days-of-voice-agents-2025

# Switch to barista branch
git checkout day-2-barista-agent

# Restart the backend (if running)
# Kill current agent with Ctrl+C, then:
cd backend
.venv\Scripts\python.exe src\agent.py dev
```

### Switch to Wellness Agent
```powershell
# Make sure you're in the project root
cd c:\CS\Development\ten-days-of-voice-agents-2025

# Switch to wellness branch
git checkout day-3-wellness-agent

# Restart the backend (if running)
# Kill current agent with Ctrl+C, then:
cd backend
.venv\Scripts\python.exe src\agent.py dev
```

---

## Current Branch Structure

```
main
├── day-2-barista-agent (Coffee Shop Barista)
└── day-3-wellness-agent (Wellness Companion)
```

---

## Important Notes

> [!IMPORTANT]
> **Always restart the backend agent after switching branches!**
> 
> The agent code is loaded when you start `src/agent.py dev`, so switching branches won't take effect until you restart.

> [!TIP]
> **Frontend stays the same**
> 
> The frontend at `c:\CS\Development\ten-days-of-voice-agents-2025\frontend` doesn't need to be restarted when switching agents. Just keep it running with `pnpm dev`.

> [!NOTE]
> **Data files are branch-specific**
> 
> - Barista agent uses: `backend/order.json`
> - Wellness agent uses: `backend/wellness_log.json`
> 
> These files are preserved when you switch branches.

---

## Troubleshooting

### "Already on 'branch-name'"
This is fine! Just restart the backend agent.

### Agent not responding after branch switch?
1. Make sure you killed the previous agent process (Ctrl+C)
2. Restart with `.venv\Scripts\python.exe src\agent.py dev`
3. Check the terminal for any errors

### Which branch am I on?
```powershell
git branch
```
The current branch will have an asterisk (*) next to it.

---

## Future Agents

As you complete more days, you can create more branches:
- `day-4-agent-name`
- `day-5-agent-name`
- etc.

This keeps all your implementations organized and accessible!
