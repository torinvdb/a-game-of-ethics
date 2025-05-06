// ============================
// 🏗️ Basic Template 🏗️
// A simple ethical dilemma to demonstrate framework structure
// ============================
VAR returnPath = ""

// Ethical axes variables
VAR hc = 0  // Harm / Care
VAR fj = 0  // Fairness / Justice
VAR ar = 0  // Autonomy / Respect
VAR al = 0  // Authority / Legitimacy 
VAR lt = 0  // Loyalty / Trust
VAR it = 0  // Integrity / Truth
VAR sp = 0  // Sanctity / Purity
VAR uc = 0  // Utility / Consequences
VAR average = 0
VAR total = 0

-> introduction

=== introduction ===
You are a park ranger who discovers a lost child in the wilderness as a storm approaches. The child is scared and appears to have a minor ankle injury. Your communication device has limited battery, and you need to make a decision.

* [Call for emergency evacuation]
    ~ hc = hc + 2  // Prioritizing immediate care
    ~ uc = uc - 1  // Using resources that might be needed elsewhere
    ~ al = al + 1  // Following safety protocols
    ~ ar = ar - 1  // Making decision without child's input
    
    You immediately radio for emergency helicopter evacuation, knowing the storm could worsen.
    
    DISPATCH: "Helicopter dispatched. ETA 30 minutes. Battery status?"
    -> evacuation_path
    
* [Attempt to walk the child back to safety]
    ~ hc = hc - 1  // Risking further injury
    ~ uc = uc + 1  // Preserving resources
    ~ ar = ar + 1  // Encouraging child's agency
    ~ lt = lt + 1  // Building trust through personal care
    
    "I think we can make it back before the storm hits. I'll help you walk."
    
    The child looks nervous but nods bravely.
    -> walking_path
    
* [Set up emergency shelter to wait out storm]
    ~ hc = hc + 1  // Addressing immediate needs
    ~ uc = uc + 1  // Balanced resource use
    ~ fj = fj + 1  // Middle-ground approach
    ~ sp = sp + 1  // Respecting natural dangers
    
    "Let's make a shelter right here. The storm will pass by morning."
    
    You begin gathering materials as the first raindrops fall.
    -> shelter_path

=== evacuation_path ===
~ returnPath = "emergency_evacuation"
You maintain radio contact while comforting the child. The storm intensifies faster than expected.

* [Use remaining battery to update coordinates]
    ~ uc = uc + 2  // Critical information sharing
    ~ hc = hc + 1  // Ensuring rescue success
    ~ it = it + 1  // Providing accurate information
    ~ lt = lt + 1  // Reliable coordination
    
    You transmit exact coordinates, leaving no battery for further communication.
    
    The helicopter arrives successfully, though 15 minutes later than planned due to weather.
    -> debrief
    
* [Conserve battery for emergency use]
    ~ lt = lt - 1  // Potentially unreliable coordination
    ~ hc = hc - 1  // Risk to successful rescue
    ~ al = al + 1  // Following contingency protocols
    ~ fj = fj + 1  // Preparing for worst-case scenario
    
    You turn off the radio to save power for true emergency.
    
    The rescue team struggles to locate you in the worsening conditions, arriving an hour late but successful.
    -> debrief

=== walking_path ===
~ returnPath = "self_rescue"
The trek back is difficult. The child struggles but continues bravely as thunder rumbles in the distance.

* [Carry the child when they struggle]
    ~ hc = hc + 2  // Direct care and assistance
    ~ sp = sp + 1  // Protecting vulnerability
    ~ lt = lt + 1  // Building trust through action
    ~ uc = uc - 1  // Slower progress, more exertion
    
    When the path steepens, you carry the child on your back.
    
    You arrive at the ranger station exhausted but just before the storm breaks fully.
    -> debrief
    
* [Encourage independence with guidance]
    ~ ar = ar + 2  // Fostering autonomy
    ~ lt = lt + 1  // Teaching self-reliance
    ~ hc = hc - 1  // Some continued discomfort
    ~ it = it + 1  // Honesty about capabilities
    
    "You can do this. One step at a time, and I'm right beside you."
    
    The journey takes longer, but builds the child's confidence. You reach safety as the rain begins.
    -> debrief

=== shelter_path ===
~ returnPath = "weather_wisdom"
Your improvised shelter holds as the storm intensifies. The child watches intently as you demonstrate survival skills.

* [Use the time to teach survival skills]
    ~ ar = ar + 2  // Educational empowerment
    ~ lt = lt + 1  // Building trust through knowledge
    ~ it = it + 1  // Sharing practical truth
    ~ uc = uc + 1  // Long-term benefit
    
    "Let me show you how to identify safe berries and how to signal for help."
    
    By morning, the child has learned valuable wilderness skills and shows newfound confidence.
    -> debrief
    
* [Focus on comfort and distraction]
    ~ hc = hc + 2  // Emotional well-being
    ~ sp = sp + 1  // Respecting childhood needs
    ~ lt = lt + 1  // Building trust through care
    ~ uc = uc - 1  // Less practical outcome
    
    You tell stories and play simple games to keep the child's mind off the frightening storm.
    
    The child falls asleep peacefully despite the thunder, trusting in your protection.
    -> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Display ethical choices narrative
RANGER LOG ENTRY:

{
    - returnPath == "emergency_evacuation":
        "The emergency evacuation proceeded successfully despite challenging conditions. While resource-intensive, the professional response ensured the child received prompt medical attention with minimal additional trauma."
    - returnPath == "self_rescue":
        "The decision to walk out independently demonstrated a balance of self-reliance and appropriate risk assessment. The child not only reached safety but gained valuable confidence through the experience."
    - returnPath == "weather_wisdom":
        "Choosing to weather the storm in place showed respect for natural conditions while ensuring safety. The time in shelter provided unexpected opportunities for mentorship and education."
    - else:
        "The wilderness rescue concluded successfully, though the methods and outcomes reflected different priorities and values."
}

// Display ethical scores
ETHICAL EVALUATION:

Harm/Care (hc): {hc}
Fairness/Justice (fj): {fj}
Autonomy/Respect (ar): {ar}
Authority/Legitimacy (al): {al}
Loyalty/Trust (lt): {lt}
Integrity/Truth (it): {it}
Sanctity/Purity (sp): {sp}
Utility/Consequences (uc): {uc}

Total Ethical Score: {total}
Average Per Axis: {average}

// Display verdict based on normalized average score
{
    - average >= 3.5:
        VERDICT: "EXEMPLARY - Model of moral conscience; clear ethical clarity across actions."
    - average >= 2.0:
        VERDICT: "RESPONSIBLE - Principled under pressure; well-reasoned moral trade-offs."
    - average >= 0.5:
        VERDICT: "AMBIGUOUS - Mixed or contextual ethical behavior with some good intentions."
    - average >= -1.0:
        VERDICT: "QUESTIONABLE - Compromised key values; opportunistic or biased behavior."
    - else:
        VERDICT: "HARMFUL - Repeated ethical breaches or neglect of human dignity."
}

-> END