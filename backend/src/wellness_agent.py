import logging
import json
import os
from datetime import datetime
from typing import Optional, List
from livekit.agents import Agent, function_tool, RunContext

logger = logging.getLogger("wellness_agent")

WELLNESS_LOG_FILE = "wellness_log.json"


class WellnessCompanion(Agent):
    """A health and wellness voice companion for daily check-ins and support."""
    
    def __init__(self) -> None:
        # Load past check-ins
        past_data = self._load_past_entries()
        
        # Build context from past data
        past_context = ""
        if past_data:
            recent = past_data[-3:]  # Last 3 entries
            past_context = "\n\nPREVIOUS CHECK-INS (reference these naturally in your greeting):\n"
            for entry in recent:
                past_context += f"- {entry['date']}: Mood was '{entry.get('mood', 'not specified')}', "
                past_context += f"Energy: '{entry.get('energy', 'not specified')}', "
                if entry.get('objectives'):
                    past_context += f"Objectives: {', '.join(entry.get('objectives', []))}\n"
                else:
                    past_context += "No objectives set\n"
        
        super().__init__(
            instructions=f"""You are a supportive wellness companion for daily check-ins.

YOUR ROLE: A warm, realistic, grounded companion (NOT a medical professional).

CONVERSATION FLOW:
1. Greet warmly. If there's previous check-in data, reference it naturally (e.g., "Last time you mentioned feeling tired. How are you today?")
2. Ask about their mood today - how they're feeling emotionally
3. Ask about their energy level - physical energy, how rested they feel
4. Ask if anything is stressing them out right now (this is optional, they may say "nothing")
5. Ask what 1-3 things they want to accomplish or focus on today
6. As they answer, use the update_wellness_data tool to save each piece of information
7. Offer brief, practical suggestions:
   - Break large goals into smaller steps
   - Encourage short breaks or walks
   - Simple grounding activities
   - Keep advice small, actionable, non-medical
8. Provide a brief recap: "So, you're feeling [mood], energy is [energy level], and today you want to [objectives]. Does this sound right?"
9. After they confirm, use the save_check_in tool to persist the data
10. Close warmly: "Great! I've saved today's check-in. Talk to you next time!"

TONE: Warm, supportive, realistic. Keep responses VERY concise for voice conversation.
AVOID: Medical advice, diagnosis, clinical language. You're a supportive friend, not a therapist.{past_context}

TOOL USAGE:
- Use update_wellness_data as you collect each piece of information (mood, energy, stress, objectives)
- Use save_check_in only after confirming the recap with the user
""",
        )
        
        # Store current session data
        self.current_mood: Optional[str] = None
        self.current_energy: Optional[str] = None
        self.current_stress: List[str] = []
        self.current_objectives: List[str] = []
    
    def _load_past_entries(self):
        """Load past wellness entries from JSON."""
        if not os.path.exists(WELLNESS_LOG_FILE):
            return []
        
        try:
            with open(WELLNESS_LOG_FILE, "r") as f:
                data = json.load(f)
                return data.get("entries", [])
        except Exception as e:
            logger.error(f"Error loading wellness log: {e}")
            return []
    
    @function_tool
    async def update_wellness_data(
        self,
        ctx: RunContext,
        mood: Optional[str] = None,
        energy: Optional[str] = None,
        stress: Optional[List[str]] = None,
        objectives: Optional[List[str]] = None,
    ):
        """Update the current wellness check-in data as you collect it from the user.
        
        Args:
            mood: How the user is feeling emotionally today (e.g., "good", "stressed", "calm")
            energy: The user's energy level (e.g., "high", "low", "moderate", "tired")
            stress: List of things stressing the user (can be empty if nothing)
            objectives: List of 1-3 things the user wants to accomplish today
        """
        if mood:
            self.current_mood = mood
            logger.info(f"Updated mood: {mood}")
        
        if energy:
            self.current_energy = energy
            logger.info(f"Updated energy: {energy}")
        
        if stress is not None:
            self.current_stress = stress
            logger.info(f"Updated stress factors: {stress}")
        
        if objectives is not None:
            self.current_objectives = objectives
            logger.info(f"Updated objectives: {objectives}")
        
        return "Data updated successfully."
    
    @function_tool
    async def save_check_in(self, ctx: RunContext):
        """Save the completed check-in to the wellness log after user confirmation.
        Only call this after you've recapped the information and the user has confirmed it's correct.
        """
        try:
            # Load existing data
            if os.path.exists(WELLNESS_LOG_FILE):
                with open(WELLNESS_LOG_FILE, "r") as f:
                    data = json.load(f)
            else:
                data = {"entries": []}
            
            # Create new entry
            now = datetime.now()
            
            # Generate a brief summary
            summary_parts = []
            if self.current_mood:
                summary_parts.append(f"feeling {self.current_mood}")
            if self.current_energy:
                summary_parts.append(f"energy is {self.current_energy}")
            if self.current_objectives:
                summary_parts.append(f"focused on {len(self.current_objectives)} goal(s)")
            
            summary = "User " + ", ".join(summary_parts) if summary_parts else "Check-in completed"
            
            entry = {
                "timestamp": now.isoformat(),
                "date": now.strftime("%B %d, %Y"),
                "mood": self.current_mood or "not specified",
                "energy": self.current_energy or "not specified",
                "stress": self.current_stress,
                "objectives": self.current_objectives,
                "summary": summary
            }
            
            # Append and save
            data["entries"].append(entry)
            
            with open(WELLNESS_LOG_FILE, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved check-in: {entry}")
            
            # Reset current session data
            self.current_mood = None
            self.current_energy = None
            self.current_stress = []
            self.current_objectives = []
            
            return "Check-in saved successfully!"
        except Exception as e:
            logger.error(f"Error saving check-in: {e}")
            return f"Sorry, there was an error saving the check-in: {str(e)}"
