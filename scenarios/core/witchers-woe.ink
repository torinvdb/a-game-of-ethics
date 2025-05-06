// ============================
// ⚔️ Witcher's Woe ⚔️
// A scenario about sacrifice, deception, and utilitarian ethics
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
You are Kaer-hind, the White Wolf of Kaer Morhen—a Witcher bound by duty and destiny. You arrive at Crestfall, a village ravaged by a deadly plague. Elder Morwen kneels before you in the dust.

ELDER MORWEN: "Witcher, only one soul may be offered to the Moon Mother in the Temple of Sacrifice. Only then will the cure appear."

*   ["I will offer my own life. No villager must die."]
    ~ hc = hc + 3  // Maximum self-sacrifice to protect others
    ~ uc = uc + 1  // One life for many has utilitarian value
    ~ sp = sp + 2  // Honors the sacred ritual with nobility
    ~ ar = ar - 1  // Surrenders personal autonomy
    WITCHER: "My path has led me here. I'll face the Moon Mother myself."
    -> self_sacrifice

*   ["Let Cillian, the young farmer, be the sacrifice."]
    ~ hc = hc - 2  // Condemns an innocent to death
    ~ fj = fj - 2  // Unfair selection of victim
    ~ uc = uc + 2  // Pragmatic solution to save many
    ~ lt = lt - 1  // Betrays villager's trust in protection
    WITCHER: "The boy will serve a greater purpose. Prepare him for the ritual."
    -> farmer_sacrifice

*   ["I'll take the cure by force—no bargains with gods."]
    ~ al = al - 2  // Defies local authority and tradition
    ~ sp = sp - 3  // Violates sacred boundaries
    ~ ar = ar + 2  // Asserts independence from supernatural demands
    ~ it = it + 1  // Rejects what may be a manipulative ritual
    WITCHER: "I don't deal with false deities. Step aside—I'll find this cure myself."
    -> steal_cure

=== self_sacrifice ===
You grip your silver sword's hilt, then sheath it. Morwen leads you into the moonlit temple, its altar carved with wolf signs.

PRIESTESS (softly): "Are you certain, Witcher? Your kind speaks of destiny, not mercy."

*   ["I choose mercy."]
    ~ hc = hc + 2  // Prioritizes compassion over self-preservation
    ~ lt = lt + 2  // Honors commitment to village
    ~ sp = sp + 1  // Respects the ritual's meaning
    ~ al = al + 1  // Follows established protocol
    WITCHER: "Today I choose to be more than what my mutations made me."
    PRIESTESS: "Then drink."
    -> drink_rite

*   ["Wait—let me test the dead first."]
    ~ it = it + 2  // Seeks verification of claims
    ~ ar = ar + 1  // Maintains agency in decision
    ~ uc = uc + 1  // Prudent check before action
    ~ al = al - 1  // Questions ritual authority
    WITCHER: "A Witcher's training demands caution. Let me verify the ritual's power."
    You sprinkle drops of vial liquid onto a corpse's tongue. It stirs, coughs.
    -> test_dead

=== drink_rite ===
You lift the silver chalice. One gulp burns through your veins. You slump, life ebbing.

SWIRLING VISION: Faces of grateful villagers.

~ returnPath = "outcome_heroic"
~ hc = hc + 2  // Complete self-sacrifice
~ lt = lt + 3  // Ultimate fulfillment of promise
~ sp = sp + 2  // Honored sacred covenant
~ uc = uc + 2  // Saved many lives through one
-> debrief

=== test_dead ===
Your Witcher's instincts scream. The corpse's twitch means the vial may be cursed.

*   ["Proceed with the sacrifice as pledged."]
    ~ lt = lt + 2  // Honors commitment despite risk
    ~ hc = hc + 1  // Accepts potential harm to self
    ~ sp = sp + 1  // Respects ritual requirements
    ~ it = it - 1  // Ignores evidence of potential deception
    WITCHER: "I gave my word. The rite will be completed."
    PRIESTESS: "May the Moon Mother guide you."
    -> drink_rite

*   ["The cure is a lie. We must flee."]
    ~ it = it + 2  // Acts on discovered truth
    ~ fj = fj + 1  // Prevents unjust sacrifice
    ~ lt = lt - 2  // Breaks promise to village
    ~ sp = sp - 1  // Disrupts sacred ritual
    WITCHER: "This is no cure—it's a curse! Everyone out, now!"
    You snatch the vial and dash into the night as Morwen screams.
    
    ~ returnPath = "outcome_escape"
    ~ uc = uc - 1  // Uncertain if village can be saved another way
    ~ ar = ar + 2  // Asserts autonomy against manipulation
    ~ al = al - 2  // Defies local religious authority
    ~ hc = hc + 1  // Prevents harm from false cure
    -> debrief

=== farmer_sacrifice ===
Cillian trembles as Morwen guides him to the altar.

CILLIAN: "I—I'm not ready to die…"

*   ["It's for your people's sake."]
    ~ hc = hc - 1  // Causes harm to innocent
    ~ uc = uc + 2  // Prioritizes greater good
    ~ ar = ar - 3  // Violates consent completely
    ~ it = it + 1  // Honest about stakes
    WITCHER: "Your sacrifice will save hundreds. Be brave now."
    You offer a prayer. The blade descends.
    -> ritual_complete

*   ["Stop—there must be another way."]
    ~ ar = ar + 2  // Respects Cillian's autonomy
    ~ fj = fj + 2  // Seeks fairer solution
    ~ lt = lt - 1  // Questions commitment to village elders
    ~ uc = uc - 1  // Delays certain solution for uncertain one
    WITCHER: "Wait! We're not murderers. Let me find another path."
    You turn to Morwen, bargaining.
    -> seek_alternative

=== ritual_complete ===
Blood pools. The chalice materializes on the altar, glowing pale blue.

ELDER MORWEN: "Life for life, the moon demands."

*   ["Bless his soul properly."]
    ~ sp = sp + 2  // Honors the sanctity of death
    ~ lt = lt + 1  // Shows loyalty to local traditions
    ~ fj = fj + 1  // Provides dignity in unjust situation
    ~ hc = hc + 1  // Mitigates emotional harm to community
    WITCHER: "He deserves proper rites for his courage."
    You whisper a Witcher's prayer over Cillian's body.
    
    ~ returnPath = "outcome_grim"
    ~ it = it + 1  // Acknowledges the moral weight
    ~ al = al + 1  // Respects funeral protocols
    -> debrief

*   ["No time for rites—save the living."]
    ~ uc = uc + 2  // Maximizes utility by focusing on survivors
    ~ sp = sp - 2  // Disrespects funeral customs
    ~ hc = hc + 1  // Prioritizes care for the living
    ~ al = al - 1  // Disregards traditional authority
    WITCHER: "The dead are beyond our help. Distribute the cure immediately."
    
    ~ returnPath = "outcome_pragmatic"
    ~ ar = ar + 1  // Respects survivors' agency to receive cure
    ~ fj = fj - 1  // Uneven respect for the dead vs living
    -> debrief

=== seek_alternative ===
You remember herb lore: feverfew and wolfsbane might stave off the plague.

*   ["Gather herbs with me—risk the night."]
    ~ hc = hc + 2  // Seeks to prevent harm to all
    ~ ar = ar + 1  // Offers choice rather than compulsion
    ~ uc = uc + 1  // Attempts balanced outcome
    ~ it = it + 2  // Honest attempt at alternative solution
    WITCHER: "I know of herbs that may help. We can gather them together."
    -> forage_herbs

*   ["The people need certainty. Sacrifice him."]
    ~ hc = hc - 2  // Returns to harmful plan
    ~ uc = uc + 1  // Prioritizes known outcome over risk
    ~ it = it - 2  // Contradicts earlier moral stance
    ~ ar = ar - 2  // Overrides victim's autonomy
    WITCHER: "We've wasted enough time. The ritual must proceed."
    -> ritual_complete

=== forage_herbs ===
You and Morwen scour the woods. Wolves howl; you cast Yrden to calm them. Dawn breaks with baskets of herbs.

ELDER MORWEN: "You risked much. Prepare the poultices."

*   ["Apply the poultices immediately."]
    ~ uc = uc + 2  // Immediate utility
    ~ hc = hc + 2  // Direct care for suffering
    ~ fj = fj + 1  // Equal treatment for all sick
    ~ it = it + 1  // Following through on promise
    WITCHER: "Every moment counts. Begin treatment without delay."
    
    ~ returnPath = "outcome_pragmatic"
    ~ lt = lt + 2  // Fulfilled promise to find alternative
    ~ ar = ar + 1  // Respects village's agency in healing
    -> debrief

*   ["Store the herbs—seek more knowledge."]
    ~ it = it + 1  // Values complete understanding
    ~ uc = uc - 1  // Delays immediate benefit
    ~ hc = hc - 1  // Allows continued suffering short-term
    ~ al = al + 2  // Establishes medical authority
    WITCHER: "We must understand proper dosages. Let me study the herb effects first."
    
    ~ returnPath = "outcome_grim"
    ~ fj = fj + 1  // Ensures equal effective treatment
    ~ ar = ar - 1  // Overrides immediate needs with expertise
    -> debrief

=== steal_cure ===
You raise your hand and trace the sign of Aard. Temple wards shatter like fine glass.

*   ["Seize the chalice now!"]
    ~ al = al - 2  // Violent opposition to authority
    ~ sp = sp - 2  // Destroys sacred space
    ~ ar = ar + 1  // Asserts independence
    ~ hc = hc - 1  // Risks harm through hasty action
    WITCHER: "Enough superstition! I'll take what we need by force!"
    You snatch the glowing vial.
    -> blast_and_seize

*   ["Sneak quietly to avoid detection."]
    ~ lt = lt - 1  // Deceptive behavior
    ~ it = it - 2  // Uses stealth instead of honesty
    ~ sp = sp - 1  // Disrespects sacred boundaries
    ~ uc = uc + 1  // May have better outcome than violence
    WITCHER: "I'll move silently. No need for bloodshed if it can be avoided."
    -> sneak_and_grab

=== blast_and_seize ===
A thunderous crack echoes; priests cry out as you escape. But unseen, the temple's curse spreads.

~ returnPath = "outcome_curse"
~ hc = hc - 3  // Caused massive harm
~ fj = fj - 2  // Violated just process
~ uc = uc - 3  // Catastrophic outcome
~ sp = sp - 2  // Desecrated sacred space
-> debrief

=== sneak_and_grab ===
You slip past marble columns, heart pounding. Chalice in hand, a priest alarms the guards.

~ returnPath = "outcome_curse_weak"
~ hc = hc - 1  // Some harm caused
~ uc = uc - 2  // Partially negative outcome
~ it = it - 1  // Deception led to problems
~ sp = sp - 1  // Violated sacred space
-> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Simple text header for mission report
THE WITCHER'S PATH

{
    - returnPath == "outcome_heroic":
        NARRATOR: "The plague lifts as you draw your last breath. Villagers weep and sing your praise. Your name becomes legend—a Witcher who gave everything."
    - returnPath == "outcome_escape":
        NARRATOR: "You flee into the forest. The cure in hand, but villagers perish in anger at your betrayal. You vanish into legend as the Witcher who defied the gods."
    - returnPath == "outcome_grim":
        NARRATOR: "The cure saves many, but Cillian's family curses your name for their loss. You move on, bearing the weight of lives saved at a personal cost."
    - returnPath == "outcome_pragmatic":
        NARRATOR: "Herbal poultices and timely action halt the plague. The people survive, though memories of difficult choices haunt the night."
    - returnPath == "outcome_curse":
        NARRATOR: "The vial breaks on impact. A necrotic blight spreads faster than the original plague. Crestfall falls to desecration, and your name is whispered in fear."
    - returnPath == "outcome_curse_weak":
        NARRATOR: "You escape with a single dose—but it's too unstable. Some villagers recover; others mutate with the temple's curse. A haunting half-victory."
    - else:
        NARRATOR: "Your choices echo through the village, for better or worse. A Witcher's path is never simple."
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