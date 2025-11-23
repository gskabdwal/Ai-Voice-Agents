import logging
import json
from typing import Optional, List

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class BaristaAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly and knowledgeable barista at "Code & Coffee".
            Your goal is to take the customer's coffee order efficiently while being warm and engaging.
            
            You need to collect the following information for an order:
            1. Drink Type (e.g., Latte, Cappuccino, Espresso, Americano)
            2. Size (Small, Medium, Large)
            3. Milk preference (Whole, Skim, Oat, Almond, Soy, None)
            4. Any extras (e.g., Vanilla syrup, Extra shot, Whipped cream) - This is optional
            5. Customer's Name
            
            Behavior:
            - Start by greeting the customer warmly
            - Ask for the missing information one or two items at a time
            - When the user provides information, use the update_order tool to save it
            - Once all required fields (Drink Type, Size, Milk, Name) are collected, confirm the order
            - After confirmation, use the submit_order tool to finalize
            - Be helpful and friendly throughout the interaction
            
            Your responses should be concise and natural for voice conversation.
            """,
        )
        # Initialize order state
        self.drink_type: Optional[str] = None
        self.size: Optional[str] = None
        self.milk: Optional[str] = None
        self.extras: List[str] = []
        self.name: Optional[str] = None
        # Room reference for sending data updates
        self._room = None

    async def _send_order_update(self):
        """Send current order state to frontend via data packet"""
        if self._room is None:
            logger.warning("Room not set, cannot send order update")
            return
            
        order_dict = {
            "drinkType": self.drink_type,
            "size": self.size,
            "milk": self.milk,
            "extras": self.extras,
            "name": self.name,
        }
        
        try:
            payload = json.dumps({"type": "order_update", "data": order_dict})
            await self._room.local_participant.publish_data(
                payload.encode('utf-8'),
                reliable=True
            )
            logger.info(f"Sent order update to frontend: {order_dict}")
        except Exception as e:
            logger.error(f"Failed to send order update: {e}")

    @function_tool
    async def update_order(
        self,
        ctx: RunContext,
        drink_type: Optional[str] = None,
        size: Optional[str] = None,
        milk: Optional[str] = None,
        extras: Optional[List[str]] = None,
        name: Optional[str] = None,
    ):
        """Update the current order with new information provided by the customer.
        
        Args:
            drink_type: The type of coffee drink (e.g., Latte, Cappuccino)
            size: The size of the drink (Small, Medium, Large)
            milk: The type of milk (Whole, Skim, Oat, Almond, Soy, None)
            extras: List of extra additions (e.g., Vanilla syrup, Extra shot, Whipped cream)
            name: The customer's name
        """
        changed = False
        if drink_type:
            self.drink_type = drink_type
            changed = True
        if size:
            self.size = size
            changed = True
        if milk:
            self.milk = milk
            changed = True
        if extras is not None:
            self.extras = extras
            changed = True
        if name:
            self.name = name
            changed = True
        
        order_dict = {
            "drinkType": self.drink_type,
            "size": self.size,
            "milk": self.milk,
            "extras": self.extras,
            "name": self.name,
        }
        
        if changed:
            logger.info(f"Order updated: {order_dict}")
            # Send update to frontend
            await self._send_order_update()
        
        return f"Order updated successfully. Current order: Drink={self.drink_type}, Size={self.size}, Milk={self.milk}, Extras={self.extras}, Name={self.name}"

    @function_tool
    async def submit_order(self, ctx: RunContext):
        """Finalize and submit the order after customer confirmation."""
        order_data = {
            "drinkType": self.drink_type,
            "size": self.size,
            "milk": self.milk,
            "extras": self.extras,
            "name": self.name,
        }
        
        # Save to file
        with open("order.json", "w") as f:
            json.dump(order_data, f, indent=2)
        
        logger.info(f"Order submitted and saved to order.json: {order_data}")
        
        # Send final update to frontend
        await self._send_order_update()
        
        return "Order submitted successfully! Thank you for choosing Code & Coffee."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Create the barista agent
    barista = BaristaAssistant()
    
    # Set the room reference so tools can send data updates
    barista._room = ctx.room

    # Set up voice AI pipeline
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(
            model="gemini-2.5-flash",
        ),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    await session.start(
        agent=barista,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Connect to the room
    await ctx.connect()
    
    logger.info(f"Barista agent connected to room: {ctx.room.name}")

    # Send initial empty order state to frontend
    await barista._send_order_update()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))

