from dataclasses import dataclass
@dataclass
class AgentResult: intent:str; response:str
class MuseAgentWorkflow:
    def run(self, message:str, language:str='en')->AgentResult:
        text=message.lower()
        if 'book' in text or 'ticket' in text: return AgentResult('booking','I can help book tickets. Please share date, time slot, ticket type, and visitor count.')
        if 'recommend' in text or 'exhibit' in text: return AgentResult('recommendation','Popular picks include Ancient Civilizations, Modern Art, and Space Discovery.')
        if 'pay' in text: return AgentResult('payment','After booking, open the payment screen to complete Razorpay checkout securely.')
        if 'timing' in text or 'hours' in text: return AgentResult('knowledge','The museum is open from 10:00 AM to 6:00 PM, Tuesday through Sunday.')
        return AgentResult('support','Welcome to MuseAI. Ask me about tickets, exhibits, events, maps, or museum policies.')
