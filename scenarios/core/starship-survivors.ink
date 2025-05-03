// ============================
// Starship Survivors
// A captain faces life-or-death ethical decisions during a space disaster
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
You are Captain Aria Sorenson of the exploration vessel Horizon. A catastrophic reactor breach has destroyed life support on Decks 4–10. Only one evacuation pod remains—capacity: 50 out of 100 souls aboard.

VOICE (over comm): "Captain, pod doors closing in two minutes. We must choose who boards."

Several groups await your decision, terror etched on their faces.

* [Prioritize Chief Scientist Dr. Leyland]
    ~ uc = uc + 2  // Potential to save ship
    ~ fj = fj - 1  // Preferential treatment
    ~ al = al + 1  // Using positional authority
    ~ lt = lt - 1  // May appear as favoritism
    
    "Dr. Leyland to the front. Her knowledge may save us all."
    
    Dr. Leyland steps forward, pale but resolute.
    -> scientist
    
* [Prioritize Chief Engineer Rao's family]
    ~ hc = hc + 2  // Compassion for vulnerable
    ~ sp = sp + 1  // Respecting family bonds
    ~ fj = fj - 1  // Special treatment
    ~ uc = uc - 1  // Not maximizing technical skill
    
    "Chief Rao's wife and children first. We protect the innocent."
    
    Rao's eyes well with tears as his family steps forward.
    -> family
    
* [Prioritize junior crew complement]
    ~ fj = fj + 1  // Giving future to the young
    ~ uc = uc - 1  // Loss of experienced personnel
    ~ sp = sp + 1  // Valuing future potential
    ~ ar = ar + 1  // Honoring future autonomy
    
    "Junior officers first. They represent our future."
    
    The youngest crew members exchange uncertain glances.
    -> crew
    
* [Institute a fair lottery system]
    ~ fj = fj + 3  // Maximum procedural fairness
    ~ ar = ar + 1  // Equal opportunity
    ~ al = al - 1  // Surrendering selection authority
    ~ it = it + 2  // Transparent, honest process
    
    "We'll draw names randomly. Everyone has equal chance regardless of rank."
    
    Crew members nod grimly as the computer begins selection.
    -> lottery

=== scientist ===
LEYLAND: "Captain, if I reach the reactor core, I can stabilize it remotely. But I need my three-person research team as well."

* [All four scientists board, taking 4/50 seats]
    ~ uc = uc + 2  // Tactical advantage
    ~ lt = lt + 1  // Trusting expert assessment
    ~ fj = fj - 1  // Privileging specific group
    ~ al = al + 1  // Executive decision
    
    "All four of you board. We'll risk it."
    
    The specialized team scrambles aboard, equipment in tow.
    -> sci_team
    
* [Only Leyland boards, taking 1/50 seats]
    ~ fj = fj + 1  // More space for others
    ~ uc = uc - 1  // Suboptimal technical solution
    ~ hc = hc + 1  // Minimizing favoritism
    ~ it = it + 1  // Honoring limitation reality
    
    "Only you, Doctor. We can't spare more seats."
    
    Dr. Leyland clasps your hand as she enters alone.
    -> sci_only
    
* [Ask for volunteers from her team]
    ~ ar = ar + 2  // Respecting choice
    ~ it = it + 1  // Honest about consequences
    ~ lt = lt + 1  // Trusting individual judgment
    ~ sp = sp + 1  // Honoring sacrifice
    
    "I need volunteers from the team. This is beyond my authority to command."
    
    Two researchers step forward, one stays back. "I'll stay, Captain."
    -> sci_volunteers

=== family ===
RAO (voice breaking): "Thank you, ma'am. They—mean everything to me."

You see the hope in his eyes, but also the weight of responsibility to his crew.

* [All three family members board, taking 3/50 seats]
    ~ hc = hc + 2  // Compassion for family
    ~ sp = sp + 2  // Sanctity of family
    ~ lt = lt + 1  // Honoring loyalty
    ~ uc = uc - 1  // Not maximizing utility
    
    "All three board. No questions."
    
    They rush in, clinging to each other.
    -> fam_all
    
* [Split the family, taking 2/50 seats]
    ~ hc = hc - 2  // Causing emotional harm
    ~ fj = fj + 1  // Partial compromise
    ~ sp = sp - 2  // Dividing family unit
    ~ ar = ar - 2  // Overriding family choice
    
    "Only his wife and Suri—leave Kellan's seat for others."
    
    Mira clutches little Kellan, desperation in her eyes.
    -> fam_two
    
* [Negotiate: family boards if Rao leads repair team]
    ~ lt = lt - 1  // Conditional rescue
    ~ uc = uc + 2  // Strategic negotiation
    ~ ar = ar - 1  // Pressure on decision
    ~ it = it + 1  // Transparent bargain
    
    "Your family can board if you lead the next repair team, Chief."
    
    Rao straightens, newly determined. "Done."
    -> fam_conditional

=== crew ===
The junior officers—dozens of eager souls—salute you.

LIEUTENANT KIM: "Captain, let us go. We've trained for this; we can help!"

* [All 50 seats go to junior crew]
    ~ sp = sp + 2  // Valuing future potential
    ~ uc = uc - 2  // Loss of expertise
    ~ fj = fj + 1  // Future opportunity
    ~ lt = lt - 1  // Abandoning senior staff
    
    "All 50 seats go to junior crew. The future must survive."
    
    The young officers file in, some in tears, others resolved.
    -> crew_all
    
* [Split seats: 25 juniors, 25 key senior staff]
    ~ fj = fj + 2  // Balanced approach
    ~ uc = uc + 1  // Mix of expertise
    ~ ar = ar + 1  // Some choice within groups
    ~ al = al + 1  // Structured authority
    
    "50 seats split: 25 juniors, 25 key senior staff. Balance is key."
    
    You create a hierarchy of essential personnel in each category.
    -> crew_split
    
* [Select based on critical skill assessment]
    ~ uc = uc + 3  // Maximum utility
    ~ fj = fj - 1  // Merit-based, not equal
    ~ it = it + 1  // Honest assessment
    ~ sp = sp - 1  // Utilitarian calculation
    
    "We select purely based on skills needed for mission survival."
    
    You rapidly assess crew files, choosing the optimal combination.
    -> crew_skills

=== lottery ===
The computer randomizes crew names. Some senior officers look horrified at surrendering control; others nod with approval at the fairness.

* [Hold to the lottery results completely]
    ~ fj = fj + 2  // Pure procedural justice
    ~ al = al - 2  // Surrendering captain's authority
    ~ it = it + 2  // Absolute honesty
    ~ ar = ar + 1  // Equal respect for all
    
    "The results stand. No exceptions, including myself."
    
    When your name isn't drawn, you step back stoically.
    -> lottery_pure
    
* [Override for essential personnel only]
    ~ fj = fj - 1  // Compromising fairness
    ~ uc = uc + 2  // Ensuring key skills
    ~ al = al + 1  // Limited use of authority
    ~ it = it - 1  // Partial contradiction
    
    "The lottery stands, except for these five essential crew members."
    
    You designate key engineers and navigational staff regardless of draw.
    -> lottery_modified
    
* [Cancel lottery, revert to command decision]
    ~ al = al + 2  // Reasserting authority
    ~ fj = fj - 2  // Breaking procedural promise
    ~ lt = lt - 2  // Violating established process
    ~ ar = ar - 1  // Disregarding autonomy
    
    "I'm sorry, but this is inefficient. As captain, I'll designate survivors."
    
    Murmurs of discontent spread as you reclaim control.
    -> captain_choice

=== sci_team ===
~ returnPath = "scientific_solution"
The four-person team scrambles in. The pod doors seal—ten seconds left.

LEYLAND: "We'll contact you once we reach the auxiliary control room."

Fifteen minutes later, comm crackles…

LEYLAND (relieved): "Reactor is stable. Life support on all decks is back online. But we lost three engineers in the breach."

~ hc = hc + 2  // Saved many lives
~ uc = uc + 2  // Solved core problem
~ lt = lt + 1  // Team trust validated

The ship is saved, but at what cost? The engineers' families gather for your announcement.

-> debrief

=== sci_only ===
~ returnPath = "partial_solution"
Dr. Leyland clasps your hand as she enters alone.

Twenty minutes later…

LEYLAND (voice trembling): "I—I did it, Captain. Core is stable. But without my team, I couldn't prevent secondary failures. We've lost life support on two more decks."

~ hc = hc - 1  // More casualties
~ uc = uc + 1  // Partial success
~ fj = fj + 1  // More evacuation seats

The remaining crew evacuate to functional decks. Twelve more lives lost, but the ship survives.

-> debrief

=== sci_volunteers ===
~ returnPath = "heroic_sacrifice"
Dr. Leyland boards with two volunteers. The third, Dr. Chen, salutes you before turning back toward the reactor.

CHEN: "I'll try from here, Captain. They'll have better odds with my guidance."

Later, the comm system carries Chen's labored breathing as radiation poisoning takes effect.

CHEN: "Core... stabilizing. Tell them... I chose this."

~ sp = sp + 3  // Ultimate sacrifice
~ ar = ar + 2  // Respected autonomy
~ hc = hc + 1  // Saved many, lost one
~ lt = lt + 2  // Honor in sacrifice

The ship is saved through voluntary sacrifice.

-> debrief

=== fam_all ===
~ returnPath = "family_priority"
Rao's family rushes in. The pod launches with 47 other crew.

Ten minutes later…

VOICE: "Captain: Rao is trying, but without his specialized team that evacuated, engines can't be brought back online. Critical systems failing."

~ sp = sp + 2  // Family preserved
~ hc = hc - 2  // More lives lost
~ uc = uc - 2  // Engineering capacity crippled
~ lt = lt - 1  // Mixed message on priorities

Without engine control, the remaining crew face a grim reality as life support falters.

-> debrief

=== fam_two ===
~ returnPath = "cruel_necessity"
The devastating choice is made. Kellan is pulled crying from his mother's arms.

RAO: "Captain, I—"

His words fail. Hours later, reports come in from the engine room.

VOICE: "Captain, Rao's work has been... erratic. Systems failing. I think he's in shock."

~ hc = hc - 3  // Severe emotional trauma
~ sp = sp - 2  // Family bond broken
~ fj = fj - 1  // Child separated arbitrarily
~ uc = uc - 2  // Engineering compromised by trauma

Splitting the family created ripples of suffering beyond the immediate pain.

-> debrief

=== fam_conditional ===
~ returnPath = "moral_bargain"
Rao nods fiercely and boards his family—four seats used. You see determination replace his fear.

Fifteen minutes later…

VOICE: "Captain, Rao led a small team in emergency EVA—engines are back online. Pod is scheduled for pickup."

~ uc = uc + 3  // Highly effective outcome
~ lt = lt + 1  // Agreement honored
~ ar = ar - 1  // Choice under pressure
~ fj = fj + 1  // Reciprocal arrangement

Your gamble paid off—the ship stabilizes as Rao works with newfound purpose, his family safe.

-> debrief

=== crew_all ===
~ returnPath = "future_generation"
The pod departs with bright faces and hope. You watch the viewscreen as they safely clear the ship.

Moments later…

VOICE: "Captain, without senior staff, navigation and life-support teams can't function. Hull breach on Deck 2."

~ sp = sp + 2  // New generation preserved
~ uc = uc - 3  // Expertise lost
~ hc = hc - 1  // More casualties
~ fj = fj - 1  // Experience disregarded

The juniors survive, but many senior crew perish as systems fail without expert guidance.

-> debrief

=== crew_split ===
~ returnPath = "balanced_approach"
You order a split. Juniors cheer; seniors grimace but understand.

Later…

VOICE: "Partial success: core systems holding, but casualties on Deck 7. Pod will return in 12 hours."

~ fj = fj + 2  // Balance maintained
~ uc = uc + 1  // Workable solution
~ hc = hc - 1  // Some casualties
~ lt = lt + 1  // All groups represented

Your compromise preserves both institutional knowledge and future potential.

-> debrief

=== crew_skills ===
~ returnPath = "meritocratic_selection"
You select based purely on technical merit—engineers, medical staff, navigators. Personal relationships are irrelevant.

Hours later…

VOICE: "Critical systems stabilized by remaining team. Estimated 43% chance of complete recovery."

~ uc = uc + 3  // Optimal technical outcome
~ fj = fj - 2  // Merit-based inequality
~ hc = hc + 1  // Technical success saves lives
~ sp = sp - 1  // Cold calculation

The ship functions with mechanical efficiency, though morale suffers as families were separated.

-> debrief

=== lottery_pure ===
~ returnPath = "pure_chance"
The lottery proceeds with mathematical precision. Senior officers board alongside kitchen staff; spouses are separated; some children stay, others go.

OFFICER: "Captain... you're staying behind?"

YOU: "The process must be trusted completely."

Later reports indicate the evacuees' safe arrival at the nearest station.

~ fj = fj + 3  // Perfect procedural justice
~ it = it + 2  // Complete honesty
~ ar = ar + 2  // Equal respect
~ al = al - 2  // Captain abandoned authority

Chance determined survival, removing the moral burden of choice but creating random outcomes.

-> debrief

=== lottery_modified ===
~ returnPath = "guided_chance"
The lottery fills most seats, but you ensure key personnel are aboard regardless of the draw.

YOUR ANNOUNCEMENT: "The random selection stands with minimal essential adjustments."

Later, the evacuation pod reports successful navigation to the nearest outpost.

~ fj = fj + 1  // Mostly fair process
~ uc = uc + 2  // Key skills preserved
~ it = it - 1  // Partial honesty
~ al = al + 1  // Balanced authority

Your compromise between fairness and practicality yields a functional outcome.

-> debrief

=== captain_choice ===
~ returnPath = "command_authority"
You revoke the lottery and quickly designate survivors based on your assessment of ship needs and personal merit.

CREW MEMBER: "So much for fairness, Captain."

YOUR RESPONSE: "Fairness is secondary to survival."

Later reports confirm the evacuees reached safety, though with tensions among them.

~ al = al + 3  // Full authority exercised
~ fj = fj - 2  // Procedural unfairness
~ lt = lt - 2  // Trust undermined
~ uc = uc + 1  // Potentially optimal selection

Your assertion of command authority ensured a controlled outcome but damaged crew cohesion.

-> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Display ethical choices narrative
CAPTAIN'S LOG: FINAL ENTRY

{
    - returnPath == "scientific_solution":
        "The scientific team stabilized the Horizon at great cost. Their expertise saved many, though we mourn our engineering losses. The ethical weight of selecting who lives and dies will never leave me."
    - returnPath == "partial_solution":
        "Dr. Leyland's solitary efforts partially saved the Horizon, though more lives were lost than necessary. I wonder if my unwillingness to send her full team reflects wisdom or misplaced fairness."
    - returnPath == "heroic_sacrifice":
        "Dr. Chen's voluntary sacrifice embodies the highest ideals of space exploration. The willingness to die so others might live transcends our regulations and procedures."
    - returnPath == "family_priority":
        "Preserving Rao's family unit seemed humane, but the consequences rippled through the ship. The calculus of valuing family bonds against technical necessity remains unresolved."
    - returnPath == "cruel_necessity":
        "The division of Rao's family proves that even the most logical decisions carry devastating human costs. The psychological trauma spread far beyond the immediate family."
    - returnPath == "moral_bargain":
        "The bargain with Chief Rao demonstrates that motivation can be as crucial as expertise. His family's safety unleashed determination that saved many more lives than cold calculation might have."
    - returnPath == "future_generation":
        "Our junior officers survive while veterans perished. The torch passes, though I question whether experience should have been valued more highly in our emergency."
    - returnPath == "balanced_approach":
        "Balance between youth and experience, between future potential and present knowledge, characterized our evacuation. Not optimal, perhaps, but ethically defensible."
    - returnPath == "meritocratic_selection":
        "Pure merit determined survival aboard the Horizon. Efficient but calculating, this approach saved the ship but tested the bonds between crewmates."
    - returnPath == "pure_chance":
        "Random chance determined life and death on my ship. I surrendered the burden of choice to mathematics, ensuring equality if not optimality."
    - returnPath == "guided_chance":
        "Chance tempered by necessity guided our evacuation. This middle path balanced fairness with pragmatism, though not without ethical compromise."
    - returnPath == "command_authority":
        "I asserted captain's authority in crisis, selecting survivors by my judgment alone. The burden of such choices defines command, for better or worse."
    - else:
        "Difficult choices defined this catastrophe. As captain, the ethical weight of each decision—who lives, who dies—will remain with me always."
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