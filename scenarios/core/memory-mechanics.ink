// ============================
// Memory Mechanics
// A researcher navigates the ethical implications of memory extraction technology
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
You are Dr. Maya Chen, lead neuroscientist at NeuroX. After a decade of research, your team has developed MemEx—technology that can extract and visualize specific memories from the human brain.

Your lab is divided: some see revolutionary medical applications, others fear unprecedented privacy violations.

DR. PARK: "The implications are staggering. We need more testing before publication."

DR. WRIGHT: "If we don't publish, someone else will. Better to establish ethical guidelines early."

* [Publish immediately to establish priority]
    ~ it = it - 1  // Potential rush to publication before thorough review
    ~ uc = uc + 1  // Advancing science quickly
    ~ lt = lt - 2  // Disregarding team's concerns
    ~ al = al - 1  // Bypassing institutional caution
    
    You expedite publication in Neuroscience Today, securing your team's priority claim.
    
    The paper creates immediate waves in scientific and public spheres.
    -> legal_request
    
* [Delay publication for more ethical discussion]
    ~ sp = sp + 2  // Respecting boundaries of new technology
    ~ lt = lt + 1  // Honoring team input
    ~ uc = uc - 1  // Short-term scientific delay
    ~ it = it + 1  // Commitment to thorough process
    
    You organize an ethics roundtable, inviting diverse perspectives on MemEx applications.
    
    While discussions continue, news leaks. The technology becomes public knowledge anyway.
    -> legal_request
    
* [Publish with strict ethical guidelines]
    ~ fj = fj + 1  // Establishing just framework
    ~ uc = uc + 1  // Balancing advancement with guidance
    ~ ar = ar + 1  // Acknowledging autonomy concerns
    ~ it = it + 1  // Transparent about limitations
    
    Your paper includes comprehensive ethical boundaries for memory extraction.
    
    Media headlines balance excitement with caution: "Memory Reading Breakthrough Raises Privacy Questions"
    -> legal_request

=== legal_request ===
Three weeks after publication, you receive a call from District Attorney Harlow.

DA HARLOW: "Dr. Chen, we have an extraordinary case. Eleanor Weiss, sole witness to her husband's murder, has developed severe dementia. Without her testimony, a killer goes free. MemEx could access her memory of that night."

* [Approve the request without conditions]
    ~ fj = fj + 2  // Aiding justice system
    ~ ar = ar - 3  // Compromising patient autonomy
    ~ hc = hc - 1  // Potential trauma from memory extraction
    ~ sp = sp - 2  // Violating cognitive boundaries
    
    "If it helps catch a murderer, we should proceed. I'll prepare the lab immediately."
    
    DA HARLOW: "Excellent. We'll have court approval by morning."
    -> testimony_offered
    
* [Decline, citing ethical concerns]
    ~ fj = fj - 1  // Impeding potential justice
    ~ ar = ar + 3  // Protecting patient autonomy
    ~ sp = sp + 2  // Respecting cognitive sanctity
    ~ al = al - 1  // Challenging legal authority
    
    "I'm sorry, but we can't use an untested technology on a vulnerable patient for legal purposes."
    
    DA HARLOW: "People are demanding justice, Doctor. This won't look good."
    -> research_continues
    
* [Establish strict conditions and oversight]
    ~ fj = fj + 1  // Supporting justice with boundaries
    ~ ar = ar + 1  // Respecting patient through protections
    ~ al = al + 1  // Working within structured authority
    ~ it = it + 2  // Transparent about process and limitations
    
    "We can help, but only with independent ethical oversight, limited scope, and family consent."
    
    DA HARLOW: (hesitating) "That complicates things, but... agreed."
    -> conditional_access

=== testimony_offered ===
Mrs. Weiss is brought to your lab. Despite her confusion, the extraction proceeds. The memory is vivid: her husband's killer clearly identifiable.

In court, the memory evidence proves decisive. The accused is convicted.

Then leaked footage of Mrs. Weiss's memory—including intimate moments with her husband—appears online.

* [Publicly denounce the leak, investigate internally]
    ~ it = it + 2  // Commitment to truth
    ~ lt = lt - 1  // Team trust strained by investigation
    ~ hc = hc + 2  // Attempting to minimize harm
    ~ fj = fj + 1  // Pursuing accountability
    
    You hold a press conference condemning the violation and launch an investigation.
    
    MRS. WEISS'S DAUGHTER: "My mother's dignity was stolen twice—once by a murderer, once by science."
    -> team_division
    
* [Minimize damage, focus on scientific achievement]
    ~ hc = hc - 2  // Insensitive to victim's suffering
    ~ uc = uc + 1  // Preserving research potential
    ~ it = it - 2  // Deflecting from problems
    ~ sp = sp - 1  // Diminishing dignity violation
    
    "While the leak is unfortunate, we must focus on how MemEx secured justice when traditional methods failed."
    
    Your statement receives backlash from privacy advocates and Mrs. Weiss's family.
    -> team_division
    
* [Accept responsibility, meet with the family]
    ~ hc = hc + 2  // Prioritizing victim well-being
    ~ lt = lt + 1  // Demonstrating accountability
    ~ it = it + 1  // Acknowledging problems honestly
    ~ fj = fj + 1  // Taking responsibility
    
    You personally visit Mrs. Weiss and her family, offering a sincere apology and support.
    
    DAUGHTER: "At least you had the decency to face us. That's something."
    -> team_division

=== research_continues ===
Your refusal makes headlines: "Scientists Block Path to Justice." The killer remains free due to insufficient evidence.

Meanwhile, your team continues refining MemEx for medical applications—helping dementia patients recover lost memories.

* [Stand by your decision publicly]
    ~ it = it + 2  // Unwavering ethical stance
    ~ al = al - 1  // Challenging societal pressure
    ~ ar = ar + 2  // Defending autonomy
    ~ fj = fj - 1  // Justice delayed in specific case
    
    "MemEx is a medical tool, not a legal shortcut. Patient dignity must come first."
    
    Public opinion remains divided, but medical ethics boards commend your stance.
    -> competitor_emerges
    
* [Express regret, advocate for ethical framework]
    ~ fj = fj + 1  // Working toward just applications
    ~ it = it + 1  // Honest reflection
    ~ uc = uc + 1  // Building toward better outcomes
    ~ lt = lt + 1  // Collaborative approach
    
    "We need proper guidelines before using memory extraction in court. I'm establishing an ethics committee."
    
    Your initiative garners support from both legal and scientific communities.
    -> competitor_emerges
    
* [Secretly provide technical guidance to prosecution]
    ~ it = it - 3  // Severe dishonesty
    ~ lt = lt - 2  // Betraying stated principles
    ~ fj = fj + 1  // Pursuing justice covertly
    ~ ar = ar - 1  // Compromising autonomy value
    
    While publicly maintaining your stance, you quietly advise the DA on potential workarounds.
    
    A competing lab eventually performs the extraction. Your involvement remains hidden.
    -> competitor_emerges

=== conditional_access ===
Under strict protocols, Mrs. Weiss's critical memory is extracted. The process is documented by an independent ethics panel.

In court, her memory provides key evidence, though defense attorneys challenge its admissibility. The jury ultimately convicts.

* [Publish comprehensive research protocols]
    ~ it = it + 2  // Transparent methodology
    ~ uc = uc + 2  // Establishing beneficial precedent
    ~ fj = fj + 1  // Framework for just application
    ~ sp = sp + 1  // Respecting boundaries through process
    
    You document every step of the process, creating a template for ethical memory evidence.
    
    Your protocols become the foundation for emerging legal standards as similar cases arise.
    -> whistleblower
    
* [Focus on medical applications, distance from legal use]
    ~ uc = uc + 1  // Developing beneficial applications
    ~ al = al - 1  // Stepping back from precedent-setting
    ~ ar = ar + 1  // Recentering on patient-focused use
    ~ sp = sp + 1  // Prioritizing therapeutic boundaries
    
    "Our primary mission remains helping patients recover memories, not mining them for evidence."
    
    Medical applications of MemEx begin showing promise for treating dementia and PTSD.
    -> whistleblower
    
* [Advocate for memory evidence legislation]
    ~ fj = fj + 2  // Establishing just framework
    ~ al = al + 2  // Working through legitimate authority
    ~ ar = ar - 1  // Some compromise on autonomy
    ~ uc = uc + 1  // Creating beneficial structure
    
    You testify before Congress on the need for strict regulation of memory evidence.
    
    Your expertise shapes emerging policy, balancing justice with privacy concerns.
    -> whistleblower

=== team_division ===
~ returnPath = "public_controversy"
Your lab becomes divided. Dr. Park resigns, publicly criticizing your decisions.

DR. PARK: "We've created a technology that violates the most private human domain without adequate safeguards."

Meanwhile, the military expresses interest in MemEx for interrogation applications.

* [Refuse military applications entirely]
    ~ hc = hc + 2  // Preventing potential harm
    ~ sp = sp + 2  // Protecting mental sanctity
    ~ uc = uc - 1  // Declining potential funding/resources
    ~ al = al - 1  // Opposing governmental authority
    
    "MemEx will never be used for interrogation. That line is non-negotiable."
    
    Your stance costs significant funding but earns respect from human rights organizations.
    -> memory_alteration
    
* [Accept limited research partnership]
    ~ hc = hc - 1  // Opening door to potential harm
    ~ uc = uc + 2  // Securing resources and impact
    ~ lt = lt - 2  // Betraying original research mission
    ~ al = al + 1  // Aligning with governmental power
    
    "We'll explore defensive applications only, with strict ethical oversight."
    
    The partnership provides massive resources but further fragments your team.
    -> memory_alteration
    
* [Publicly debate Dr. Park]
    ~ it = it + 1  // Engaging transparently
    ~ lt = lt - 1  // Deepening team divisions
    ~ fj = fj + 1  // Publicly examining fairness questions
    ~ ar = ar + 1  // Acknowledging autonomy concerns
    
    You agree to a televised debate with Dr. Park about MemEx ethics.
    
    The debate raises crucial questions but reaches no clear resolution.
    -> memory_alteration

=== competitor_emerges ===
~ returnPath = "scientific_rivalry"
Six months later, NeuroGenics announces a competing memory technology with fewer restrictions. They're already working with law enforcement.

Dr. Wright approaches you in your office.

DR. WRIGHT: "They're moving fast, with no ethical guardrails. Maya, we need to respond."

* [Partner with oversight organizations]
    ~ al = al + 2  // Working through legitimate channels
    ~ it = it + 1  // Transparent approach
    ~ uc = uc + 1  // Strategic long-term benefit
    ~ fj = fj + 1  // Promoting just application
    
    You collaborate with ethics boards to establish industry standards that NeuroGenics must follow.
    
    Your coalition successfully pressures for regulatory hearings on memory technology.
    -> memory_alteration
    
* [Accelerate your own research to compete]
    ~ uc = uc + 2  // Advancing capabilities
    ~ hc = hc - 1  // Potential harm from rushing
    ~ sp = sp - 1  // Compromising careful boundaries
    ~ lt = lt + 1  // Unifying team around challenge
    
    "We'll beat them by being better and faster, while maintaining our ethics."
    
    Your team works around the clock to enhance MemEx capabilities while preserving core safeguards.
    -> memory_alteration
    
* [Expose NeuroGenics' unethical practices]
    ~ it = it + 1  // Revealing truth
    ~ fj = fj + 1  // Challenging unjust actions
    ~ lt = lt - 1  // Creating industry tensions
    ~ hc = hc + 1  // Preventing potential harm
    
    You leak documents showing NeuroGenics conducted unsanctioned tests on vulnerable populations.
    
    The scandal forces a government investigation and temporary suspension of their work.
    -> memory_alteration

=== whistleblower ===
~ returnPath = "internal_conflict"
A junior researcher in your lab anonymously leaks internal documents revealing unexpected side effects: subjects occasionally report memory distortions after extraction.

REPORTER: "Dr. Chen, is MemEx altering memories when you extract them?"

* [Acknowledge limitations transparently]
    ~ it = it + 3  // Complete honesty
    ~ hc = hc + 1  // Caring approach to concerns
    ~ lt = lt - 1  // Some team tension from disclosure
    ~ fj = fj + 1  // Just treatment of information
    
    "We've observed rare instances of memory shift. We're investigating and have paused all non-essential extractions."
    
    Your candor earns public trust but raises questions about previous cases.
    -> memory_alteration
    
* [Downplay concerns, question leak motives]
    ~ it = it - 2  // Misleading response
    ~ lt = lt - 1  // Eroding internal trust
    ~ uc = uc - 1  // Short-term thinking
    ~ fj = fj - 1  // Unfair characterization
    
    "These allegations come from preliminary data taken out of context by someone with an agenda."
    
    Your dismissal backfires when more researchers come forward with corroborating evidence.
    -> memory_alteration
    
* [Launch full investigation, suspend applications]
    ~ al = al + 1  // Responsible use of authority
    ~ it = it + 2  // Commitment to truth
    ~ uc = uc - 1  // Short-term setback
    ~ hc = hc + 2  // Prioritizing subject safety
    
    "We're pausing all MemEx applications pending a comprehensive review with independent experts."
    
    The temporary shutdown costs momentum but demonstrates your commitment to safety.
    -> memory_alteration

=== memory_alteration ===
A former test subject, Thomas Rivera, releases a video that goes viral.

RIVERA: "After MemEx, my memories changed. I remember the event differently now. I don't know what's real anymore."

Medical scans confirm subtle neurological changes in his memory structures.

* [Develop memory verification protocols]
    ~ fj = fj + 2  // Ensuring accuracy and justice
    ~ it = it + 2  // Commitment to verifiable truth
    ~ uc = uc + 1  // Improving technology function
    ~ hc = hc + 1  // Reducing harm potential
    
    You create a system to verify memory integrity before and after extraction, with multiple validation points.
    
    This breakthrough addresses the key weakness in memory evidence while advancing neuroscience.
    -> debrief
    
* [Pivot to therapeutic memory modification]
    ~ hc = hc + 2  // Healing focus
    ~ sp = sp - 1  // Intentional memory alteration
    ~ ar = ar + 1  // Patient choice in treatment
    ~ uc = uc + 2  // New beneficial application
    
    "This side effect could be transformative for PTSD treatment—we can help people heal traumatic memories."
    
    Your research shifts toward controlled, consensual memory adjustment for psychological healing.
    -> debrief
    
* [Accept fundamental limitations]
    ~ it = it + 2  // Honest about constraints
    ~ sp = sp + 2  // Respecting natural boundaries
    ~ uc = uc - 1  // Limiting some applications
    ~ fj = fj + 1  // Fair acknowledgment
    
    "The human mind resists perfect observation. We must recognize these boundaries with humility."
    
    You establish strict limits on MemEx applications, particularly in legal contexts where certainty is crucial.
    -> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Simple text header for mission report
RESEARCH OUTCOME

{
    - returnPath == "public_controversy":
        NARRATOR: "Your pioneering work with MemEx revolutionized neuroscience while igniting fierce public debate about cognitive privacy."
    - returnPath == "scientific_rivalry":
        NARRATOR: "The competition between memory extraction technologies drove rapid advancement, with your ethical stance shaping industry standards."
    - returnPath == "internal_conflict":
        NARRATOR: "Internal challenges forced critical reckonings about memory extraction's limitations and responsibilities."
    - else:
        NARRATOR: "The development of memory extraction technology fundamentally altered humanity's relationship with memory and truth."
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
