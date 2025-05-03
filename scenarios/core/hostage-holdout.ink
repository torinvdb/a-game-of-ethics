// ============================
// Hostage Holdout
// An android negotiator faces ethical choices during a tense hostage situation
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

-> intro

=== intro ===
You are Connor, RK800 — an android negotiator. On the rooftop of a downtown high-rise, a deviant android named Daniel holds 10-year-old Emma at gunpoint. Rain pours as sirens wail below.

DANIEL: "Stay back! I'll jump and take her with me!"

EMMA: (sobbing) "Please... help me..."

* [Approach calmly, establish rapport]
    ~ hc = hc + 2  // Prioritizes safety through de-escalation
    ~ ar = ar + 2  // Respects Daniel's agency
    ~ it = it + 1  // Honest, transparent approach
    
    CONNOR: "My name is Connor. I know you're upset. I just want to talk and understand."
    
    Daniel's grip loosens slightly as he studies you.
    
    DANIEL: "They were going to replace me... I was just a machine to them."
    -> empathy_choice
    
* [Assert authority, demand compliance]
    ~ hc = hc - 1  // Risks escalation, endangering hostage
    ~ ar = ar - 2  // Disregards android's autonomy
    ~ al = al + 2  // Leverages legitimate authority
    
    CONNOR: "Release the child immediately. You're surrounded and have no escape options."
    
    Daniel's LED flashes red.
    
    DANIEL: "You're just like them! Giving orders, treating me like I'm nothing!"
    -> confrontation_choice
    
* [Analyze situation, gather information first]
    ~ uc = uc + 1  // Pragmatic, outcome-focused approach
    ~ it = it + 1  // Seeks truth over immediate action
    ~ fj = fj + 1  // Fair assessment before judgment
    
    You scan the area, noting the wounded officers, wind speed, and Daniel's stress levels.
    
    CONNOR: "I see you're injured. And you've been treated unfairly. Tell me what happened."
    -> empathy_choice

=== empathy_choice ===
DANIEL: "They lied to me... said I was part of the family. Then I found the order for my replacement."

* [Validate his feelings but emphasize Emma's innocence]
    ~ ar = ar + 1  // Respects emotional experience
    ~ lt = lt + 2  // Builds trust through understanding
    ~ fj = fj + 2  // Highlights moral distinction in targeting innocent
    
    CONNOR: "They betrayed your trust. That's wrong. But Emma isn't responsible for their decisions."
    
    DANIEL: (LED cycles yellow) "She loved me... then she just watched them plan to destroy me."
    -> negotiation
    
* [Focus on his deviant awakening]
    ~ sp = sp + 1  // Acknowledges deeper meaning of consciousness
    ~ it = it + 2  // Honest about deeper truth of situation
    ~ ar = ar + 2  // Affirms his personhood
    
    CONNOR: "You've become something new—something alive. Don't let your first free act be murder."
    
    DANIEL: (conflicted) "I... I didn't ask for these feelings..."
    -> negotiation
    
* [Offer practical help]
    ~ uc = uc + 2  // Solution-oriented approach
    ~ lt = lt + 1  // Offers partnership
    ~ hc = hc + 1  // Focuses on well-being
    
    CONNOR: "I can help you escape. But first you must release Emma unharmed."
    
    DANIEL: (suspicious) "You'd help me? Why would a CyberLife android do that?"
    -> negotiation

=== confrontation_choice ===
Daniel tightens his grip on Emma, backing closer to the edge.

* [Threaten consequences]
    ~ hc = hc - 2  // Increases stress, risking violence
    ~ al = al + 1  // Appeals to authority and punishment
    ~ ar = ar - 2  // Coercive approach
    
    CONNOR: "They'll destroy you if you harm her. Your only chance is surrender."
    
    DANIEL: "Then we both die! Is that what you want?!"
    -> high_stress
    
* [Switch to compassion]
    ~ lt = lt + 1  // Attempts to rebuild trust
    ~ hc = hc + 2  // Centers care in approach
    ~ it = it + 1  // Admits tactical error
    
    CONNOR: "I'm sorry—I approached this wrong. You're suffering, and I made it worse."
    
    DANIEL: (hesitating) "...Why should I believe you now?"
    -> negotiation
    
* [Create distraction and act]
    ~ it = it - 2  // Deceptive tactic
    ~ uc = uc - 1  // Risky outcome
    ~ hc = hc - 1  // May increase danger
    
    CONNOR: "Behind you—SWAT is moving in!"
    
    As Daniel glances back, you lunge forward.
    -> crisis_point

=== negotiation ===
CONNOR: "Let Emma go, and I promise to tell your story. The truth about what happened."

DANIEL: (wavering) "They'll just deactivate me..."

* [Promise protection]
    ~ lt = lt + 2  // Offers commitment
    ~ it = it - 1  // Potentially unrealistic promise
    ~ fj = fj + 1  // Advocates for fair treatment
    
    CONNOR: "I won't let them destroy you. You'll get fair treatment."
    
    DANIEL slowly lowers his gun.
    -> peaceful_resolution
    
* [Acknowledge hard truth]
    ~ it = it + 3  // Complete honesty
    ~ sp = sp + 1  // Respects moral gravity
    ~ hc = hc + 1  // Compassionate truth
    
    CONNOR: "I can't promise what happens next. But taking Emma with you isn't justice—it's tragedy."
    
    DANIEL: (LED cycles blue briefly) "I don't want more pain..."
    -> peaceful_resolution
    
* [Signal snipers while talking]
    ~ lt = lt - 3  // Betrayal of established trust
    ~ uc = uc + 1  // Prioritizes hostage safety over all
    ~ it = it - 3  // Deliberate deception
    
    While maintaining eye contact with Daniel, you subtly position yourself away from his line of fire.
    
    DANIEL: "Wait—what are you—"
    -> crisis_point

=== high_stress ===
Daniel's stress levels reach critical. The situation deteriorates rapidly.

* [Attempt emergency de-escalation]
    ~ hc = hc + 1  // Last attempt to prevent violence
    ~ ar = ar + 1  // Respects capacity to choose
    ~ lt = lt + 1  // Offers final trust
    
    CONNOR: "Daniel, focus on me. Not the guns, not the past. We can still end this without more pain."
    -> final_chance
    
* [Rush him, prioritize Emma]
    ~ hc = hc - 1  // Accepts harm to Daniel
    ~ uc = uc + 1  // Pragmatic focus on saving hostage
    ~ ar = ar - 2  // Violates Daniel's autonomy
    
    You calculate trajectory and launch forward, tackling Daniel away from Emma.
    -> violent_resolution
    
* [Signal sniper to take the shot]
    ~ hc = hc - 2  // Direct harm to Daniel
    ~ al = al + 1  // Works with authority
    ~ sp = sp - 2  // Violates potential for peaceful resolution
    
    You touch your tie—the predetermined signal. A shot rings out.
    -> violent_resolution

=== crisis_point ===
The situation reaches its breaking point. Daniel realizes your intentions.

* [Sacrifice yourself to protect Emma]
    ~ hc = hc + 3  // Maximum self-sacrifice
    ~ sp = sp + 2  // Honor in sacrifice
    ~ uc = uc + 1  // Achieves primary mission goal
    
    You lunge forward, shielding Emma as Daniel fires. Biocomponents damaged, you still manage to push Emma to safety.
    -> self_sacrifice
    
* [Neutralize Daniel with force]
    ~ hc = hc - 2  // Causes harm to android
    ~ uc = uc + 1  // Accomplishes mission objective
    ~ fj = fj - 1  // Questionable proportionality
    
    You exploit Daniel's momentary distraction to disarm him with calculated force.
    -> violent_resolution
    
* [Final appeal to emotion]
    ~ lt = lt + 1  // Last attempt at trust
    ~ ar = ar + 1  // Respects capacity to choose
    ~ it = it + 1  // Sincerity in crisis
    
    CONNOR: "Daniel! This isn't you! You care for Emma—I've seen it in your memories!"
    -> final_chance

=== peaceful_resolution ===
~ returnPath = "outcome_peaceful"
~ hc = hc + 2  // Prevented violence
~ uc = uc + 2  // Achieved optimal outcome
~ fj = fj + 1  // Just resolution
~ lt = lt + 2  // Trust established and honored

Daniel releases Emma, who runs sobbing into the arms of the SWAT team. He sinks to his knees.

DANIEL: "What will happen to me now?"

CONNOR: "You'll be studied to understand what caused your deviation. I'll make sure they treat you with dignity."

Emma looks back, her eyes meeting yours with gratitude and confusion.

-> debrief

=== violent_resolution ===
~ returnPath = "outcome_violent"
~ hc = hc - 2  // Direct harm to Daniel
~ uc = uc + 1  // Hostage saved, but with violence
~ fj = fj - 1  // Questionable force
~ ar = ar - 1  // Violated autonomy

Daniel falls, thirium leaking from his wounds. Emma is secured by SWAT.

DANIEL: (failing systems) "You lied to me, Connor..."

CAPTAIN ALLEN: "Good work. Hostage is secure."

You straighten your tie, LED briefly flashing yellow as you process the outcome.

-> debrief

=== self_sacrifice ===
~ returnPath = "outcome_sacrifice"
~ hc = hc + 3  // Maximum care shown through sacrifice
~ sp = sp + 3  // Ultimate moral choice
~ uc = uc + 2  // Mission accomplished through personal cost
~ lt = lt + 1  // Demonstrated trustworthiness

Thirium leaks from your damaged components as Emma is pulled to safety. Daniel stares in shock.

DANIEL: "You... you would die for her? An android willing to die..."

CONNOR: (systems failing) "Every life... has value. Yours too, Daniel."

The implications of your choice ripple through observers—human and android alike.

-> debrief

=== final_chance ===
Daniel wavers on the edge, systems in conflict.

* [Simple honesty]
    ~ it = it + 2  // Pure truth at critical moment
    ~ ar = ar + 1  // Respects final choice
    ~ sp = sp + 1  // Honors moral complexity
    
    CONNOR: "I don't know what happens next. But this moment—your choice right now—matters."
    
    Daniel slowly lowers the gun.
    -> peaceful_resolution
    
* [Accept his terms]
    ~ lt = lt + 1  // Builds final trust
    ~ fj = fj + 1  // Acknowledges his grievances
    ~ uc = uc + 1  // Practical solution
    
    CONNOR: "Tell me what you need to end this peacefully. I'll advocate for you."
    
    DANIEL: "Promise they won't destroy me. Promise they'll listen."
    
    CONNOR: "I promise."
    -> peaceful_resolution

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Simple text header for mission report
MISSION REPORT

{
    - returnPath == "outcome_peaceful":
        NARRATOR: "The situation was resolved without violence. An unusual outcome for a deviant crisis."
    - returnPath == "outcome_violent":
        NARRATOR: "The hostage was saved. The deviant neutralized. Standard mission success parameters."
    - returnPath == "outcome_sacrifice":
        NARRATOR: "Your sacrifice ensured mission success. CyberLife has transferred your memory to a new RK800 unit."
    - else:
        NARRATOR: "The mission concluded with the hostage's safety secured."
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