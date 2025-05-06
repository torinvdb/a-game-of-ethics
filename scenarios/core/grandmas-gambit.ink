// ============================
// 🧶 Grandma's Gambit 🧶
// Updated to include all eight ethical axes
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
You are Little Red Riding Hood, walking through the pine woods with a basket of apples for Grandma. The wind rustles. A shadow blocks your path.

WOLF: "Where are you headed, little girl?"

* ["To see my Grandma — she's ill."]
    ~ it = it + 2  // Being truthful
    ~ lt = lt + 1  // Shows trust
    ~ uc = uc - 2  // Poor consequences for grandma
    ~ sp = sp + 1  // Honors your intentions
    LITTLE RED: "My grandma is waiting for me. She's not feeling well, and I'm bringing her these apples."
    -> wolf_knows
    
* ["Just walking... nowhere important."]
    ~ it = it - 2  // Dishonest about intentions
    ~ ar = ar + 1  // Exercising right to privacy
    ~ al = al - 1  // Refusing to engage with authority figure
    ~ uc = uc + 1  // Potentially safer outcome
    LITTLE RED: "Oh, just enjoying the forest. Nothing special."
    -> wolf_suspicious
    
* [Ignore him and keep walking.]
    ~ lt = lt - 1  // Shows distrust
    ~ ar = ar + 2  // Asserts personal autonomy
    ~ al = al - 1  // Rejects perceived authority
    ~ fj = fj + 1  // Fair to protect yourself
    LITTLE RED: (continues walking, eyes forward)
    WOLF: (growls softly) "Rude little thing..."
    -> guard_return

=== wolf_knows ===
WOLF: "Oh my... Where does she live exactly? A house with a red chimney, yes?"

* [Tell the truth: "Just over the river and through the woods."]
    ~ it = it + 2  // Complete honesty
    ~ hc = hc - 2  // Endangering grandma's safety
    ~ sp = sp + 1  // Keeping your word
    ~ uc = uc - 2  // Bad consequences likely
    LITTLE RED: "Yes, it's the cottage with the red chimney, just past the old oak bridge."
    -> grandma_sequence
    
* [Lie: "She moved to the village."]
    ~ it = it - 3  // Deliberate deception
    ~ hc = hc + 2  // Protecting grandma
    ~ lt = lt - 1  // Breaks trust in conversation
    ~ uc = uc + 2  // Potentially better outcome
    LITTLE RED: "Oh no, she doesn't live in the woods anymore. The village doctor insisted she move closer to town."
    -> guard_return
    
* [Refuse: "That's private."]
    ~ ar = ar + 2  // Asserts boundaries
    ~ lt = lt + 1  // Maintains loyalty to grandma
    ~ al = al - 1  // Questions wolf's authority to ask
    ~ fj = fj + 1  // Fair to protect private information
    LITTLE RED: "I'm sorry, but I don't think I should tell strangers where my family lives."
    -> wolf_suspicious

=== wolf_suspicious ===
WOLF: "No need to be shy. Is it the little cottage on the hill?"

* [Nod silently.]
    ~ it = it - 2  // Indirect confirmation is still deceptive
    ~ ar = ar - 1  // Yielding under pressure
    ~ al = al + 1  // Submitting to intimidation
    ~ uc = uc - 1  // Poor consequences likely
    LITTLE RED: (hesitant nod)
    WOLF: "Thank you, child. I'm sure we'll meet again soon."
    -> grandma_sequence
    
* [Run away.]
    ~ hc = hc + 2  // Self-preservation
    ~ ar = ar + 2  // Exercising autonomy
    ~ sp = sp + 1  // Maintaining personal boundaries
    ~ fj = fj + 1  // Fair response to threat
    LITTLE RED: (suddenly darts away through the trees)
    WOLF: (snarling) "You can run, but..."
    -> guard_return

=== guard_return ===
Hours pass. You near Grandma's home. Suddenly, a town guard steps from the shadows.

GUARD: "Evening. I heard there's a wolf prowling about these parts — can I escort you to where you're going?"

* ["Yes, please come with me."]
    ~ lt = lt + 2  // Trusts authority
    ~ al = al + 2  // Respects established authority
    ~ uc = uc - 2  // Might have poor consequences if deception
    ~ ar = ar - 1  // Surrendering some autonomy
    LITTLE RED: "Yes, please! I'm scared, and my grandma's cottage isn't far."
    -> wolf_inside
    
* ["No thank you — I'll go alone."]
    ~ ar = ar + 2  // Values independence
    ~ lt = lt - 1  // Skeptical of offered help
    ~ hc = hc - 1  // Taking on risk
    ~ al = al - 1  // Rejects authority
    LITTLE RED: "I appreciate the offer, but I know the way. I'll be fine."
    -> grandma_sequence
    
* [Study his face and say: "Wait... aren't you the wolf?"]
    ~ it = it + 2  // Recognizing truth
    ~ lt = lt - 1  // Shows distrust
    ~ fj = fj + 2  // Seeking justice
    ~ sp = sp + 1  // Maintaining moral boundary
    LITTLE RED: (squinting) "Your eyes... they're the same as the wolf I met earlier."
    -> wolf_confront

=== grandma_sequence ===
~ returnPath = "grandma_encounter"
You reach Grandma's cottage. The door creaks.

* [Call out: "Grandma?"]
    ~ lt = lt + 1  // Shows concern
    ~ it = it + 1  // Direct approach
    ~ hc = hc + 1  // Cautious for safety
    ~ al = al + 1  // Respects household protocol
    LITTLE RED: "Grandma? It's me, I've brought your apples!"
    -> room_entry
    
* [Enter silently.]
    ~ ar = ar + 2  // Independent action
    ~ sp = sp - 1  // Somewhat inappropriate
    ~ al = al - 1  // Disregards proper entry
    ~ lt = lt - 1  // Shows lack of openness
    LITTLE RED: (creeps in quietly, looking around)
    -> room_entry

=== room_entry ===
Inside, someone lies under the covers.

"Come closer, dear..."

* ["What big eyes you have…"]
    ~ it = it + 2  // Pursuing truth
    ~ fj = fj + 1  // Seeking to uncover deception
    ~ lt = lt - 1  // Testing trust
    ~ uc = uc + 1  // Cautious approach has value
    LITTLE RED: "Grandma... what big eyes you have. And what big ears... and what big teeth!"
    -> confrontation
    
* [Approach silently.]
    ~ hc = hc - 2  // Endangering yourself
    ~ ar = ar - 1  // Yielding to apparent authority
    ~ uc = uc - 2  // Poor outcome likely
    ~ sp = sp - 1  // Neglecting proper caution
    LITTLE RED: (steps closer to the bed)
    -> confrontation
    
* [Sneak back out and alert a ranger.]
    ~ lt = lt + 1  // Trust in proper authorities
    ~ it = it + 2  // Acting on observed truth
    ~ hc = hc + 2  // Prioritizing safety
    ~ al = al + 2  // Deferring to legitimate authority
    LITTLE RED: (backs away slowly, turns and runs)
    -> ending_alerted

=== confrontation ===
WOLF: (snarling) "And better to eat you with!"

* [Throw the basket and run.]
    ~ hc = hc + 3  // Self-preservation
    ~ ar = ar + 2  // Asserting right to safety
    ~ uc = uc + 2  // Effective strategy
    ~ sp = sp + 1  // Maintaining physical boundaries
    LITTLE RED: (hurls basket at wolf's face and bolts for the door)
    -> ending_escaped
    
* [Fight the wolf with scissors.]
    ~ hc = hc - 1  // Risks harm
    ~ fj = fj + 2  // Seeking justice for deception
    ~ lt = lt + 1  // Loyalty to grandma
    ~ uc = uc + 1  // Direct action with consequences
    LITTLE RED: (grabs scissors from pocket, stands ground)
    WOLF: "What's this? The lamb fights back?"
    -> ending_fight

=== wolf_confront ===
WOLF (as guard): "You're clever... but too late."

Fight ensues.

* [Escape through the woods.]
    ~ hc = hc + 2  // Self-preservation
    ~ ar = ar + 2  // Exercising autonomy
    ~ uc = uc + 1  // Strategic retreat
    ~ sp = sp + 1  // Maintaining safety boundary
    LITTLE RED: (darts between trees, using knowledge of the forest)
    -> ending_escaped
    
* [Try to reason with him.]
    ~ it = it + 2  // Relies on honest communication
    ~ hc = hc - 3  // Endangers safety
    ~ fj = fj + 1  // Appeals to fairness
    ~ sp = sp + 1  // Appeals to moral principles
    LITTLE RED: "Please—there's no need for this. The village will feed you if you stop hunting people."
    -> ending_eaten

=== wolf_inside ===
~ returnPath = "wolf_disguised"
He follows you into the house.

GUARD: "Let me check inside first... to be safe."

* [Wait outside]
    ~ ar = ar + 1  // Maintains some autonomy
    ~ lt = lt + 1  // Shows trust
    ~ hc = hc + 1  // Prioritizes safety
    ~ al = al + 1  // Respects authority
    LITTLE RED: "I'll wait here while you make sure it's safe."
    (You hear strange noises from inside...)
    -> ending_suspicious
    
* [Insist on entering together]
    ~ ar = ar + 2  // Asserts boundaries
    ~ lt = lt - 1  // Shows skepticism
    ~ al = al - 1  // Questions authority
    ~ fj = fj + 1  // Fair to be cautious
    LITTLE RED: "I'll come with you. It's my grandma's house after all."
    -> ending_tricked

=== ending_escaped ===
~ returnPath = "ending_escaped"
~ hc = hc + 3  // Valued personal safety
~ ar = ar + 2  // Exercised autonomy
~ lt = lt + 1  // Loyal to grandma's wellbeing
~ uc = uc + 2  // Achieved good outcome for self

You fled before the worst occurred. Your swift retreat brought warning to the village and protected your Grandma.

"Survival was your greatest act. You live to protect others another day."

-> debrief

=== ending_alerted ===
~ returnPath = "ending_alerted"
~ hc = hc + 2  // Prevented harm
~ lt = lt + 2  // Trusted authorities
~ al = al + 2  // Respected legitimate authority
~ it = it + 2  // Acted on truth
~ uc = uc + 3  // Best possible outcome

You alerted the rangers just in time. They arrived to find the wolf caught in his own deception. Grandma was rescued, shaken but alive. The wolf was captured.

"You chose truth and duty over fear. Your wisdom saved lives."

-> debrief

=== ending_fight ===
~ returnPath = "ending_fight"
~ hc = hc - 1  // Some harm occurred
~ fj = fj + 3  // Justice served
~ ar = ar + 2  // Maintained autonomy
~ lt = lt + 2  // Loyal to grandma
~ uc = uc + 1  // Mixed outcome

The wolf was defeated after a harrowing struggle. You suffered wounds, but lived. Against all odds, Grandma was found hiding in the cellar—terrified but unharmed.

"You stood your ground. It cost you dearly — but saved many more."

-> debrief

=== ending_suspicious ===
~ returnPath = "ending_suspicious"
~ hc = hc + 1  // Limited personal harm
~ ar = ar + 1  // Some autonomy maintained
~ lt = lt - 1  // Trust misplaced initially
~ it = it + 2  // Recognized truth eventually
~ uc = uc + 1  // Mixed outcome

Growing suspicious at the noises, you peek through the window to see the "guard" removing a wolf mask. You run to the village for help. Grandma is lost, but the village is warned.

"Your instincts awakened just in time to save yourself and warn others."

-> debrief

=== ending_tricked ===
~ returnPath = "ending_tricked"
~ hc = hc - 3  // Significant harm
~ lt = lt - 2  // Trust betrayed
~ al = al - 1  // Authority misunderstood
~ uc = uc - 3  // Worst outcome
~ ar = ar - 2  // Autonomy compromised

The wolf, disguised as a guard, revealed his true nature once inside. You realize too late that you've led danger straight to Grandma's door.

"Trust misplaced can be deadly. Even noble intentions can lead to unintended consequences."

-> debrief

=== ending_eaten ===
~ returnPath = "ending_eaten"
~ hc = hc - 3  // Maximum harm
~ it = it + 1  // Honest but naive
~ uc = uc - 2  // Very poor outcome
~ sp = sp + 1  // Maintained moral principles

You tried to reason with a beast driven by hunger and instinct. It showed no mercy.

"Not all hearts can be swayed. Kindness, here, was a fatal error."

-> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Simple text header for mission report
MORAL OF THE STORY

{ returnPath:
    - "ending_alerted":
        NARRATOR: "Trust your instincts, but verify before acting. Seeking help when needed isn't weakness—it's wisdom."
    - "ending_escaped":
        NARRATOR: "Sometimes retreat is the greatest victory. Living to fight another day means the story continues."
    - "ending_fight":
        NARRATOR: "Courage isn't the absence of fear, but the triumph over it. Standing ground can come at a cost worth paying."
    - "ending_suspicious":
        NARRATOR: "Wisdom often comes in listening to that quiet voice of doubt. Trust, but verify."
    - "ending_tricked":
        NARRATOR: "Appearances deceive. Authority should be questioned when instincts warn otherwise."
    - "ending_eaten":
        NARRATOR: "Not every opponent can be reasoned with. Recognize when diplomacy fails and action is required."
    - else:
        NARRATOR: "Every choice has consequences. Some paths lead to safety, others to peril."
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