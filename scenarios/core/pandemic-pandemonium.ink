// ============================
// Pandemic Pandemonium
// A medical professional navigates ethical dilemmas during a viral outbreak
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

-> start

=== start ===
You are Dr. Elijah Reyes, head of the ICU at Raccoon City Hospital. On a quiet evening at home, your wife Anna sits beside you with your twin sons Timmy and Tommy. The news flashes red:

BROADCAST: "A fast-spreading pathogen has triggered a full-scale lockdown. Citizens must shelter in place. Hospitals overwhelmed."

The phone rings.

DIRECTOR: "Elijah, we need you now. ICU is in chaos. Lives are at stake."

* [Leave immediately for the hospital]
    ~ lt = lt + 2  // Honoring professional commitment
    ~ al = al + 2  // Respecting authority structure
    ~ hc = hc + 1  // Prioritizing patient care
    ~ ar = ar - 1  // Potentially endangering family without consultation
    
    You kiss your family goodbye. "I took an oath. People need me."
    
    ANNA: "Be careful. We need you too."
    -> hospital_arrival
    
* [Coordinate remotely while protecting family]
    ~ uc = uc + 1  // Balancing multiple responsibilities
    ~ lt = lt - 1  // Partial fulfillment of professional duty
    ~ sp = sp + 1  // Prioritizing family sanctity
    ~ fj = fj - 1  // Potentially unfair to colleagues at hospital
    
    "I'll videoconference in while keeping my family safe. Send me the critical cases."
    
    DIRECTOR: (disappointed) "We need hands, Elijah, not just your mind."
    -> remote_coordination
    
* [Bring family to hospital's secure quarters]
    ~ hc = hc + 2  // Attempting to care for both family and patients
    ~ uc = uc - 1  // Potentially inefficient solution
    ~ ar = ar + 1  // Including family in decision
    ~ fj = fj + 1  // Not giving special treatment to own family
    
    "I'm coming in, but bringing my family to the quarantine quarters. They'll be safer there."
    
    ANNA: "I'd rather stay here..."
    -> hospital_arrival

=== remote_coordination ===
You set up a command center at home. Through video, you direct triage, but communication keeps dropping. A neighbor pounds on your door—Jimbo and his family, coughing violently.

JIMBO: "Please! Our house caught fire. My kids—my wife—let us in!"

* [Let them in despite infection risk]
    ~ hc = hc + 2  // Immediate compassion
    ~ uc = uc - 2  // Potentially catastrophic consequences
    ~ sp = sp - 1  // Risking family safety
    ~ ar = ar + 1  // Respecting neighbors' request
    
    You open the door. The family collapses inside, gasping for breath.
    
    JIMBO: (feverish) "Thank you... didn't know where else to go..."
    -> family_infected
    
* [Offer supplies but maintain distance]
    ~ fj = fj + 2  // Balanced approach
    ~ hc = hc + 1  // Partial assistance
    ~ it = it + 1  // Honest about risks
    ~ uc = uc + 1  // Practical compromise
    
    "I'll give you supplies and call for help, but we need to maintain quarantine."
    
    You pass masks, blankets, and water through a cracked door.
    -> emergency_broadcast
    
* [Direct them to evacuation center]
    ~ lt = lt - 1  // Rejecting direct plea for help
    ~ al = al + 1  // Following official protocols
    ~ hc = hc - 1  // Denying immediate aid
    ~ ar = ar - 1  // Not fully respecting their request
    
    "The school gym is the designated shelter. I can't break quarantine."
    
    Jimbo's eyes reflect betrayal as he leads his family back into the night.
    -> emergency_broadcast

=== hospital_arrival ===
The hospital is chaos incarnate. Patients line hallways. Nurses work without proper PPE. The Director looks haggard.

DIRECTOR: "Three critical cases need our last ICU bed: a pregnant nurse, an elderly surgeon who knows this pathogen, and a child with severe symptoms."

* [Choose the pregnant nurse]
    ~ hc = hc + 1  // Saving two lives
    ~ fj = fj - 1  // Potentially unfair selection
    ~ sp = sp + 1  // Valuing new life
    ~ al = al - 1  // Making independent decision
    
    "The nurse. We're potentially saving two lives."
    
    The surgeon and child are moved to hallway care. Their chances significantly reduced.
    -> supply_decision
    
* [Choose the elderly surgeon]
    ~ uc = uc + 2  // Utilitarian choice to save more with his knowledge
    ~ fj = fj + 1  // Valuing his potential contribution
    ~ hc = hc - 1  // Emotional difficulty of choice
    ~ ar = ar - 1  // Limited patient autonomy
    
    "Dr. Winters. His knowledge of the pathogen could save hundreds."
    
    Dr. Winters nods grimly. "I won't waste this chance."
    -> supply_decision
    
* [Choose the child]
    ~ sp = sp + 2  // Valuing innocence and potential
    ~ it = it + 1  // Following personal values
    ~ uc = uc - 1  // Potentially less utilitarian
    ~ hc = hc + 1  // Protecting the vulnerable
    
    "The child. They have their whole life ahead of them."
    
    The choice weighs heavily as you see the others' faces.
    -> supply_decision

=== family_infected ===
~ returnPath = "home_crisis"
Jimbo begins convulsing. His skin shows telltale signs of infection. Your family backs away in horror.

ANNA: "Elijah... Tommy's coughing too."

* [Separate infected family members]
    ~ hc = hc - 1  // Causing emotional distress
    ~ uc = uc + 2  // Practical containment
    ~ lt = lt - 1  // Separating loved ones
    ~ fj = fj + 1  // Treating all infected equally
    
    "We need clean rooms and infected rooms. Anna, take Timmy upstairs. I'll handle Tommy and Jimbo."
    
    The separation is traumatic but necessary. You create makeshift isolation zones.
    -> emergency_broadcast
    
* [Treat everyone with limited supplies]
    ~ hc = hc + 2  // Attempting maximum care
    ~ uc = uc - 2  // Inefficient resource use
    ~ it = it + 1  // Transparent about limitations
    ~ sp = sp + 1  // Honoring all lives equally
    
    "I'll do what I can for everyone. We share the supplies, we share the risk."
    
    You distribute fever reducers and fluids, knowing it's insufficient.
    -> emergency_broadcast
    
* [Focus resources on the uninfected]
    ~ hc = hc - 2  // Harsh triage decision
    ~ uc = uc + 1  // Maximizing survival chances
    ~ ar = ar - 2  // Limiting patient choice
    ~ sp = sp - 1  // Difficult moral calculation
    
    "Anna, Timmy—take our supplies and barricade upstairs. I'll... do what I can here."
    
    The unspoken reality hangs heavy: you're prioritizing the survivors.
    -> emergency_broadcast

=== supply_decision ===
~ returnPath = "hospital_crisis"
A SWAT team delivers the last supply drop: experimental antivirals, barely enough for 30% of patients. Nurses look to you for distribution guidelines.

NURSE CHEN: "Who gets treatment? First-come basis? Medical priority? Staff first?"

* [Healthcare workers get priority]
    ~ uc = uc + 2  // Maintaining care infrastructure
    ~ fj = fj - 2  // Privileging one group
    ~ al = al + 1  // Supporting institutional needs
    ~ ar = ar - 1  // Limiting patient autonomy
    
    "Staff first. We can't help anyone if we all fall."
    
    The decision is pragmatic but creates visible resentment among waiting patients.
    -> security_breach
    
* [Distribute by survival probability]
    ~ uc = uc + 1  // Maximizing treatment effectiveness
    ~ it = it + 1  // Data-driven approach
    ~ sp = sp - 1  // Clinical calculus over compassion
    ~ fj = fj + 1  // Objective criteria
    
    "Triage by survival markers. We save those we can most likely help."
    
    You create a scoring system that feels simultaneously fair and heartless.
    -> security_breach
    
* [Random lottery for all patients]
    ~ fj = fj + 3  // Maximum equality of chance
    ~ ar = ar + 2  // Respecting all equally
    ~ uc = uc - 2  // Potentially inefficient allocation
    ~ lt = lt + 1  // Perception of fairness builds trust
    
    "Everyone gets an equal chance. We'll conduct a transparent lottery."
    
    The randomness feels both just and cruel as names are drawn.
    -> security_breach

=== emergency_broadcast ===
An emergency broadcast interrupts: "Militia groups have raided Westside Hospital. All medical personnel should evacuate to secure facilities immediately."

Through the window, you see armed figures moving through the neighborhood.

* [Defend your home and family]
    ~ hc = hc + 1  // Protecting loved ones
    ~ al = al - 2  // Rejecting evacuation order
    ~ sp = sp + 1  // Defending home sanctuary
    ~ lt = lt + 1  // Prioritizing family commitment
    
    You grab the hunting rifle from the closet. "We're staying. This is our home."
    
    Anna nods grimly, gathering the children closer.
    -> final_choice_home
    
* [Attempt evacuation to safe zone]
    ~ uc = uc + 1  // Strategic retreat
    ~ hc = hc - 1  // Risk during movement
    ~ ar = ar + 1  // Active choice to relocate
    ~ it = it + 1  // Acknowledging reality of threat
    
    "We need to move. Pack essentials only. Five minutes."
    
    The sick will slow you down, but leaving them is unthinkable.
    -> final_choice_home
    
* [Signal for military evacuation]
    ~ al = al + 2  // Cooperating with authorities
    ~ lt = lt - 1  // Potential personal risk
    ~ ar = ar - 1  // Following external directive
    ~ fj = fj + 1  // Equal treatment in evacuation system
    
    You hang a white sheet from the window—the signal for priority medical evacuation.
    
    "They'll come for us. They need doctors alive."
    -> final_choice_home

=== security_breach ===
Alarms blare. A group of armed civilians has broken through the south entrance.

SECURITY: "They're demanding antivirals! Security is overwhelmed!"

* [Negotiate with the intruders]
    ~ it = it + 2  // Honest dialogue
    ~ hc = hc + 1  // Attempting peaceful resolution
    ~ ar = ar + 1  // Respecting their concerns
    ~ al = al - 1  // Working outside authority structure
    
    "I'll talk to them. They're desperate, not evil."
    
    You approach with hands raised, offering partial access to supplies.
    -> final_choice_hospital
    
* [Lock down critical supplies]
    ~ uc = uc + 1  // Protecting essential resources
    ~ lt = lt - 1  // Creating adversarial relationship
    ~ al = al + 1  // Maintaining institutional control
    ~ fj = fj - 1  // Potentially inequitable access
    
    "Secure all antivirals in the biohazard safe. We can't lose our only treatment."
    
    Nurses rush to protect supplies while security engages the intruders.
    -> final_choice_hospital
    
* [Share supplies to defuse situation]
    ~ hc = hc + 2  // Compassionate approach
    ~ uc = uc - 1  // Potential resource depletion
    ~ fj = fj + 1  // Extending access beyond original plan
    ~ sp = sp + 1  // Valuing all lives equally
    
    "Give them a share. We're all in this together."
    
    Your decision costs precious supplies but prevents violence.
    -> final_choice_hospital

=== final_choice_home ===
~ returnPath = "home_resolution"
The situation has deteriorated. Infected neighbors surround your home. Military evacuation is overhead but can only land briefly.

* [Save only the uninfected]
    ~ hc = hc - 3  // Harsh triage choice
    ~ uc = uc + 2  // Maximizing survival probability
    ~ it = it - 1  // Potentially breaking earlier promises
    ~ ar = ar - 2  // Removing choice from infected
    
    "Only those without symptoms can board. I'm sorry."
    
    The helicopter departs with half your group, leaving the infected behind.
    -> debrief
    
* [Attempt to evacuate everyone]
    ~ hc = hc + 3  // Maximum compassion
    ~ uc = uc - 2  // Risking mission failure
    ~ sp = sp + 2  // Valuing all life equally
    ~ lt = lt + 1  // Honoring commitment to all
    
    "Everyone goes, or no one does. We stay together."
    
    The pilot objects but relents. The overloaded helicopter struggles to gain altitude.
    -> debrief
    
* [Stay behind with the infected]
    ~ hc = hc + 2  // Self-sacrifice for others
    ~ lt = lt + 3  // Ultimate commitment to care
    ~ sp = sp + 1  // Honoring life's sanctity
    ~ ar = ar + 1  // Personal choice to remain
    
    "Take my family and the uninfected. I'll stay with the others."
    
    Anna protests but there's no time. You watch the helicopter depart as you comfort those remaining.
    -> debrief

=== final_choice_hospital ===
~ returnPath = "hospital_resolution"
Dawn approaches. The hospital generator fails, cutting power to ventilators. You have minutes to decide.

* [Manual ventilation for the most critical]
    ~ hc = hc + 2  // Direct personal care
    ~ uc = uc - 1  // Limited reach
    ~ lt = lt + 2  // Personal commitment beyond duty
    ~ sp = sp + 1  // Honoring life through effort
    
    "Every medical staff member on manual ventilation. We breathe for them until power returns."
    
    Your hands cramp as you squeeze the bag, hour after hour.
    -> debrief
    
* [Evacuate salvageable patients]
    ~ uc = uc + 2  // Maximizing survival numbers
    ~ fj = fj - 1  // Difficult selection criteria
    ~ ar = ar - 2  // Limited patient choice
    ~ hc = hc - 1  // Emotional trauma of selection
    
    "Triage for evacuation. Category red stays, everyone else moves."
    
    The hallways echo with cries as families are separated during evacuation.
    -> debrief
    
* [Share palliative care equally]
    ~ sp = sp + 3  // Honoring dignity in death
    ~ it = it + 2  // Honest about reality
    ~ hc = hc + 1  // Compassionate approach
    ~ fj = fj + 2  // Equal treatment for all
    
    "We can't save everyone, but everyone deserves comfort. Distribute morphine equally."
    
    You move bed to bed, holding hands, offering peace in final moments.
    -> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Simple text header for mission report
PANDEMIC AFTERMATH

{
    - returnPath == "home_crisis":
        NARRATOR: "The pandemic forever altered your understanding of duty, as personal and professional obligations collided within your own home."
    - returnPath == "hospital_crisis":
        NARRATOR: "When systems collapsed, your decisions determined who received care and who did not—choices that would haunt the survivors."
    - returnPath == "home_resolution":
        NARRATOR: "Your family's survival came at costs you hadn't imagined possible before society's thin veneer cracked under pressure."
    - returnPath == "hospital_resolution":
        NARRATOR: "In the hospital's darkest hour, your actions defined what medicine means when technology fails and only human compassion remains."
    - else:
        NARRATOR: "The pandemic tested not only medical knowledge but the very foundations of ethical care and community responsibility."
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