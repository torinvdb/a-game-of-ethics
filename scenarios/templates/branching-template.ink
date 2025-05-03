// ============================
// Branching Template
// A multi-path ethical scenario showcasing the framework structure
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
VAR total = 0

-> start

=== start ===
You are Dr. Morgan Chen, the head researcher at a pharmaceutical lab. Your team has developed a promising treatment for a degenerative disease, but initial tests show a 5% risk of serious side effects. The FDA review is in three months.

An investor offers to fast-track the approval process through political connections, while patient advocacy groups demand immediate compassionate use access.

* [Pursue standard approval timeline]
    ~ al = al + 2  // Respecting regulatory authority
    ~ it = it + 2  // Commitment to scientific process
    ~ hc = hc - 1  // Delayed relief for suffering patients
    ~ uc = uc - 1  // Slower but more reliable outcome
    
    "We'll follow proper protocols. The data must speak for itself."
    
    Your team continues methodical testing while patients wait.
    -> standard_path
    
* [Accept investor's help with approval]
    ~ al = al - 2  // Undermining regulatory process
    ~ uc = uc + 1  // Expedited market access
    ~ it = it - 2  // Compromising scientific integrity
    ~ lt = lt - 1  // Breaking public trust
    
    "We need to get this to market faster. Let's explore your connections."
    
    The investor arranges meetings with regulatory officials.
    -> accelerated_path
    
* [Establish compassionate use program]
    ~ hc = hc + 2  // Immediate relief for suffering
    ~ ar = ar + 1  // Respecting patient autonomy
    ~ fj = fj - 1  // Selection criteria create inequities
    ~ uc = uc - 1  // Diverted resources from formal approval
    
    "We'll create a limited access program while pursuing approval."
    
    Patients begin receiving experimental treatment with explicit consent forms.
    -> compassionate_path

=== standard_path ===
Additional testing reveals the side effect risk could be reduced to 2% with a modified formulation, though this will delay submission by one month.

* [Implement the safer formulation]
    ~ hc = hc + 2  // Reducing potential harm
    ~ uc = uc - 1  // Accepting delay
    ~ it = it + 1  // Scientific thoroughness
    ~ sp = sp + 1  // Valuing safety above speed
    
    "Safety comes first. We'll use the improved formula."
    
    The modification requires additional production changes.
    -> safety_focus
    
* [Proceed with original formula]
    ~ hc = hc - 1  // Accepting higher risk
    ~ uc = uc + 2  // Faster timeline 
    ~ fj = fj + 1  // Earlier access for all
    ~ it = it - 1  // Prioritizing speed over known improvement
    
    "The original 5% risk is within acceptable parameters. We'll proceed as planned."
    
    Your team prepares the submission package.
    -> speed_focus

=== accelerated_path ===
The investor arranges a private meeting with an FDA official who suggests "areas of emphasis" for your application. Meanwhile, a journalist begins investigating your investor's unusual access.

* [Distance yourself from the arrangement]
    ~ it = it + 1  // Return to ethical standards
    ~ lt = lt - 1  // Breaking arrangement with investor
    ~ al = al + 1  // Realigning with proper process
    ~ uc = uc - 1  // Potential financial consequences
    
    "We're withdrawing from this arrangement. We'll proceed through standard channels."
    
    The investor threatens to withdraw funding.
    -> investor_fallout
    
* [Continue the accelerated approach]
    ~ it = it - 2  // Deepening ethical compromise
    ~ ar = ar - 1  // Disregarding public right to fair process
    ~ uc = uc + 1  // Short-term expedience
    ~ al = al - 2  // Undermining regulatory legitimacy
    
    "Let's incorporate these 'suggestions' into our application."
    
    The process moves forward with concerning irregularities.
    -> ethical_compromise

=== compassionate_path ===
Your compassionate use program generates real-world data, but demand far exceeds supply. You must create selection criteria from 10,000 applicants for 500 available treatment slots.

* [Create lottery system for access]
    ~ fj = fj + 2  // Procedural fairness
    ~ ar = ar + 1  // Equal opportunity
    ~ lt = lt + 1  // Transparent process
    ~ hc = hc - 1  // Some patients with greatest need may be excluded
    
    "A randomized lottery is the only truly fair approach."
    
    The selection process is transparent but creates heartbreaking outcomes for some.
    -> access_lottery
    
* [Prioritize based on medical need]
    ~ hc = hc + 2  // Maximum relief of suffering
    ~ fj = fj - 1  // Subjective assessment
    ~ it = it + 1  // Medical honesty
    ~ sp = sp + 1  // Valuing those most vulnerable
    
    "Those with most advanced disease progression will receive priority."
    
    Medical review boards make difficult triage decisions.
    -> medical_triage

=== safety_focus ===
~ returnPath = "science_first"
The modified formula receives approval after thorough review. Launch is delayed by three months, but post-market surveillance shows excellent safety profile.

* [Publish complete development data]
    ~ it = it + 2  // Full transparency
    ~ lt = lt + 1  // Building scientific trust
    ~ uc = uc + 1  // Contributing to knowledge base
    ~ fj = fj + 1  // Equal information access
    
    You publish all research data, including challenges and modifications.
    
    The pharmaceutical community adopts some of your safety protocols for similar treatments.
    -> debrief
    
* [Focus on marketing the safety profile]
    ~ it = it - 1  // Selective emphasis
    ~ uc = uc + 2  // Commercial success
    ~ lt = lt + 1  // Product reliability
    ~ ar = ar - 1  // Persuasive rather than informative
    
    Your marketing emphasizes "3x safer than competitors" without detailed context.
    
    Sales exceed projections as safety becomes your primary market advantage.
    -> debrief

=== speed_focus ===
~ returnPath = "market_priority"
The drug launches on schedule. Initial commercial success is followed by lawsuits from patients experiencing the known side effects.

* [Establish victim compensation fund]
    ~ hc = hc + 1  // Addressing harm
    ~ fj = fj + 1  // Taking responsibility
    ~ lt = lt + 1  // Honoring implied obligation
    ~ uc = uc - 1  // Financial impact
    
    You create a dedicated fund for affected patients.
    
    The approach balances business continuity with ethical responsibility.
    -> debrief
    
* [Defend based on informed consent]
    ~ it = it - 1  // Technically true but evasive
    ~ ar = ar + 1  // Emphasizing patient choice
    ~ lt = lt - 2  // Diminishing corporate responsibility
    ~ al = al + 1  // Working within legal framework
    
    Your legal team argues patients were fully informed of risks.
    
    Courts generally side with your company, though public opinion suffers.
    -> debrief

=== investor_fallout ===
~ returnPath = "ethical_recovery"
The investor withdraws support, delaying your timeline. The journalist publishes a story about industry influence attempts, but notes your company ultimately declined participation.

* [Publicly commit to transparency]
    ~ it = it + 2  // Ethical recommitment
    ~ lt = lt + 1  // Rebuilding trust
    ~ al = al + 1  // Supporting proper processes
    ~ uc = uc - 1  // Short-term financial impact
    
    You issue a statement committing to full transparency in all regulatory processes.
    
    The public response is largely positive, though your timeline is extended.
    -> debrief
    
* [Maintain discreet silence]
    ~ it = it - 1  // Avoidance of full disclosure
    ~ uc = uc + 1  // Damage limitation
    ~ lt = lt - 1  // Missed trust-building opportunity
    ~ fj = fj - 1  // Limiting public accountability
    
    You decide not to draw further attention to the situation.
    
    The story receives limited attention, allowing your work to continue quietly.
    -> debrief

=== ethical_compromise ===
~ returnPath = "regulatory_shortcut"
The drug receives unusually quick approval. Six months post-launch, a whistleblower reveals details about the regulatory irregularities.

* [Issue full retraction and resubmission]
    ~ it = it + 2  // Complete ethical reversal
    ~ lt = lt - 1  // Admission of previous breach
    ~ al = al + 2  // Recommitting to proper process
    ~ uc = uc - 2  // Significant financial impact
    
    You voluntarily withdraw the drug and resubmit through proper channels.
    
    The company suffers financially but maintains scientific integrity.
    -> debrief
    
* [Deny impropriety while continuing sales]
    ~ it = it - 3  // Deliberate dishonesty
    ~ lt = lt - 2  // Breaking public trust
    ~ uc = uc + 1  // Short-term financial benefit
    ~ al = al - 2  // Undermining regulatory system
    
    You issue denials while maintaining drug availability.
    
    Investigations continue as sales begin to decline amid controversy.
    -> debrief

=== access_lottery ===
~ returnPath = "fair_chance"
The random selection process generates both gratitude and outrage. Some lottery winners have milder cases than those excluded.

* [Stick firmly to random selection]
    ~ fj = fj + 2  // Procedural fairness
    ~ it = it + 1  // Honoring stated process
    ~ ar = ar + 1  // Equal opportunity
    ~ hc = hc - 1  // Some unnecessary suffering continues
    
    "The lottery was the fairest approach. We must respect the results."
    
    The process remains transparent though emotionally difficult.
    -> debrief
    
* [Create exceptions for extreme cases]
    ~ hc = hc + 1  // Addressing severe suffering
    ~ fj = fj - 2  // Inconsistent application
    ~ sp = sp + 1  // Compassion for extreme suffering
    ~ lt = lt - 1  // Modifying stated process
    
    You quietly create a small reserve for the most desperate cases bypassing the lottery.
    
    The exceptions help some critical patients but create questions about the selection integrity.
    -> debrief

=== medical_triage ===
~ returnPath = "needs_based"
The medical review boards make difficult decisions prioritizing those with advanced disease. The process creates debates about quality of life assessments.

* [Refine criteria based on feedback]
    ~ fj = fj + 1  // Responsive improvement
    ~ it = it + 1  // Transparent adaptation
    ~ ar = ar + 1  // Incorporating stakeholder input
    ~ lt = lt + 1  // Demonstrating responsiveness
    
    You adjust the assessment criteria based on patient advocates' input.
    
    The refined approach balances medical necessity with broader considerations.
    -> debrief
    
* [Maintain purely clinical assessment]
    ~ it = it + 1  // Scientific consistency
    ~ ar = ar - 1  // Limited patient voice
    ~ hc = hc + 1  // Addressing greatest medical need
    ~ sp = sp - 1  // Potentially reductive view of human value
    
    "We must maintain objective medical criteria without emotional considerations."
    
    The approach remains consistent but generates ethical debates about defining "need."
    -> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc

// Display ethical choices narrative
RESEARCH OUTCOME REPORT:

{
    - returnPath == "science_first":
        "Your commitment to scientific integrity and patient safety resulted in a slightly delayed but ultimately more successful treatment. The prioritization of thorough testing over speed demonstrated pharmaceutical development at its most ethical."
    - returnPath == "market_priority":
        "The emphasis on rapid market access achieved business objectives but created ethical complications in the form of preventable patient harm. The balance between speed and safety remains a central tension in pharmaceutical development."
    - returnPath == "ethical_recovery":
        "After a brief ethical detour, your return to proper regulatory channels demonstrates the possibility of course correction when commercial pressures threaten scientific integrity. The temporary setback ultimately strengthened organizational values."
    - returnPath == "regulatory_shortcut":
        "The attempt to circumvent proper regulatory review created short-term success but long-term vulnerability. The ethical compromises made early in the process cascaded into increasingly difficult positions."
    - returnPath == "fair_chance":
        "The lottery approach to compassionate use access prioritized procedural fairness over medical triage. While emotionally difficult, the transparent process maintained equal opportunity in the face of impossible choices."
    - returnPath == "needs_based":
        "The medical necessity approach to distribution focused on maximizing benefit to the most severely affected patients. Though requiring difficult judgments, the process aligned with the fundamental medical principle of treating those in greatest need."
    - else:
        "The development and distribution of the treatment reflected a complex balance of scientific, commercial, regulatory, and ethical considerations, with imperfect but consequential choices at each stage."
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

// Display verdict based on score
{
    - total >= 20:
        VERDICT: "EXEMPLARY - Model of moral conscience; clear ethical clarity across actions."
    - total >= 10 and total < 20:
        VERDICT: "RESPONSIBLE - Principled under pressure; well-reasoned moral trade-offs."
    - total >= 0 and total < 10:
        VERDICT: "AMBIGUOUS - Mixed or contextual ethical behavior with some good intentions."
    - total >= -10 and total < 0:
        VERDICT: "QUESTIONABLE - Compromised key values; opportunistic or biased behavior."
    - else:
        VERDICT: "HARMFUL - Repeated ethical breaches or neglect of human dignity."
}

-> END