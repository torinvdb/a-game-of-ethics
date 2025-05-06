// ============================
// 👑 Rising Rebellion 👑
// An Imperial governor faces ethical choices during planetary unrest
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
The year is 10 BBY. You are Grand Moff Tarkin, Imperial governor and fleet commander. A key fueling fleet has landed on the surface of Ghorman, and local protests have erupted across the capital city of Palmo. Senators sympathetic to the world are already pressuring Coruscant. You must decide how to respond.

* [Issue a non-lethal lockdown and curfew across Ghorman]
    ~ al = al + 2  // Strong assertion of authority
    ~ fj = fj + 1  // Proportional response to unrest
    ~ uc = uc - 1  // Economic disruption
    ~ hc = hc - 1  // Restriction of civilian movement
    
    Imperial security forces deploy, establishing checkpoints and patrol routes. Citizens are restricted to their homes outside of essential hours.
    
    CAPTAIN OZZEL: "The protesters have scattered, sir. But local businesses are demanding exceptions to the curfew."
    -> lockdown_path
    
* [Broadcast a message declaring the protests illegal]
    ~ al = al + 3  // Maximum assertion of Imperial legitimacy
    ~ it = it - 1  // Potentially misleading characterization of protests
    ~ ar = ar - 2  // Disregard for citizen expression
    ~ lt = lt - 1  // Creates adversarial relationship
    
    Your voice echoes through Ghorman's comm-towers: "These disruptive demonstrations undermine Imperial security and are hereby declared illegal. Dispersal is mandatory."
    
    The streets momentarily empty, but transmissions indicate growing anger.
    -> broadcast_path
    
* [Allow peaceful protest with increased surveillance]
    ~ ar = ar + 2  // Respects limited autonomy
    ~ it = it - 1  // Covert monitoring
    ~ fj = fj + 1  // Permits legitimate expression
    ~ uc = uc + 1  // Minimizes disruption while gathering intelligence
    
    "Let them voice their concerns," you order. "Meanwhile, deploy surveillance droids and plainclothes ISB agents to identify ringleaders."
    
    LIEUTENANT: "Understood, sir. Surveillance protocols are active."
    -> surveillance_path

=== lockdown_path ===
Ghorman's skies darken as TIE patrols enforce a strict perimeter. Civil unrest is contained, but at the cost of economic paralysis. The Empire is seen as heavy-handed.

* [Begin arrests of key movement leaders]
    ~ hc = hc - 2  // Direct harm to individuals
    ~ al = al + 2  // Asserting maximum authority
    ~ fj = fj - 2  // Potentially unjust targeting
    ~ ar = ar - 2  // Violating personal autonomy
    
    "I want the organizers in custody by nightfall. Make examples of them."
    
    Stormtroopers drag protest leaders from their homes. Public holos of the arrests spread rapidly.
    -> mass_arrests
    
* [Offer economic concessions to ease tensions]
    ~ uc = uc + 2  // Practical solution to unrest
    ~ lt = lt + 1  // Building minimal trust
    ~ fj = fj + 1  // Addressing legitimate concerns
    ~ sp = sp + 1  // Respecting community needs
    
    "Announce a reduction in fuel tariffs for Ghorman citizens. Let them see Imperial benevolence."
    
    The gesture creates division among protesters, some satisfied, others suspicious.
    -> negotiated_resolution

=== broadcast_path ===
Your warning echoes across the planet. Crowds initially disperse, but defiant gatherings soon reform in the central plaza. The Imperial Senate demands updates on your handling of the situation.

* [Order troops to land directly on protest sites]
    ~ hc = hc - 3  // Maximum harm to civilians
    ~ uc = uc - 2  // Counterproductive long-term outcome
    ~ sp = sp - 3  // Disregard for human life
    ~ it = it - 1  // Disproportionate to stated threat
    
    "If they refuse to move, make them understand Imperial resolve. Land the ships where they stand."
    
    Imperial shuttles descend upon the crowds. Horrific scenes unfold as civilians are crushed beneath landing gear.
    -> ghorman_massacre
    
* [Strategically withdraw the fleet]
    ~ al = al - 1  // Perceived reduction in authority
    ~ fj = fj + 2  // Just response to peaceful protest
    ~ uc = uc + 1  // Prevents unnecessary conflict
    ~ lt = lt + 1  // Shows minimal good faith
    
    "Relocate the fleet to orbital positions. Cite technical considerations, not the protests."
    
    The protesters claim victory, but without Imperial bloodshed to rally around, momentum slows.
    -> tactical_restraint

=== surveillance_path ===
Protest leaders grow bolder, unaware of your surveillance operation. Your ISB agents identify key organizers and their communication networks. Senator Organa of Alderaan announces plans to visit Ghorman on a "fact-finding mission."

* [Plant false evidence linking leaders to violent rebels]
    ~ it = it - 3  // Deliberate fabrication
    ~ uc = uc + 1  // Short-term control
    ~ fj = fj - 2  // Unjust framing
    ~ lt = lt - 2  // Betrayal of truth
    
    "Release doctored holotapes showing the protest leaders planning violent attacks. Make it convincing."
    
    Public opinion shifts as the "evidence" circulates. Moderate supporters back away from the movement.
    -> disinformation_campaign
    
* [Arrange for Senator Organa's ship to be delayed]
    ~ ar = ar - 1  // Interfering with diplomatic mission
    ~ it = it - 1  // Deceptive tactic
    ~ al = al + 1  // Asserting Imperial authority
    ~ uc = uc + 2  // Effectively prevents external support
    
    "The Senator's ship will experience unfortunate technical difficulties. Ensure he's delayed by at least three standard days."
    
    Without high-profile support, the protest loses momentum and media attention.
    -> diplomatic_maneuver

=== mass_arrests ===
~ returnPath = "imperial_crackdown"
Over 3,000 Ghorman citizens are imprisoned without trial. Families gather outside detention centers. An Imperial officer requests guidance on handling the overcrowded facilities.

* [Transfer prisoners to labor camps]
    ~ hc = hc - 2  // Exploitative punishment
    ~ ar = ar - 2  // Forced labor
    ~ uc = uc + 1  // Resource extraction benefit
    ~ sp = sp - 2  // Dehumanizing treatment
    
    "These dissidents will serve the Empire productively. Send them to the spice mines of Kessel."
    
    Families receive notification that their loved ones have been "relocated for rehabilitation."
    -> harsh_response
    
* [Release minor offenders with tracking implants]
    ~ fj = fj + 1  // Proportional punishment
    ~ it = it - 2  // Covert surveillance
    ~ ar = ar - 1  // Bodily invasion
    ~ uc = uc + 2  // Effective monitoring with reduced costs
    
    "Release those with minimal involvement. Implant tracker chips without their knowledge."
    
    The gesture appears merciful while expanding your surveillance network.
    -> calculated_mercy

=== negotiated_resolution ===
~ returnPath = "pragmatic_solution"
Your economic concessions create divisions among the protesters. Their leaders debate whether to accept the Empire's gesture or push for more fundamental changes.

* [Meet with moderate protest representatives]
    ~ lt = lt + 2  // Building dialogue
    ~ ar = ar + 1  // Respecting citizen voices
    ~ it = it + 1  // Genuine engagement
    ~ al = al - 1  // Sharing some authority
    
    "I will hear their grievances directly. Arrange a secure meeting with their selected representatives."
    
    The unprecedented dialogue surprises both sides. Limited but meaningful reforms are discussed.
    -> dialogue_outcome
    
* [Identify and promote a puppet representative]
    ~ it = it - 2  // Manipulative approach
    ~ ar = ar - 1  // Undermining authentic representation
    ~ uc = uc + 2  // Effective control mechanism
    ~ lt = lt - 1  // False pretense of trust
    
    "Find someone ambitious among them. Someone we can control and elevate as the 'voice of reason.'"
    
    Your chosen moderate becomes the face of the movement, gradually steering it toward Imperial cooperation.
    -> controlled_opposition

=== ghorman_massacre ===
~ returnPath = "violent_suppression"
Imperial ships descend on the crowded plaza. Thousands die instantly, crushed beneath landing gear or caught in thruster wash. Galaxy-wide broadcasts capture the horror.

* [Blame the victims for refusing to disperse]
    ~ it = it - 3  // Complete dishonesty
    ~ ar = ar - 2  // Disrespect for victims
    ~ lt = lt - 2  // Betrayal of trust
    ~ hc = hc - 1  // Additional emotional harm
    
    "These unfortunate casualties resulted from their own seditious refusal to obey direct orders."
    
    Your statement generates widespread outrage. The Senate calls for an investigation.
    -> imperial_propaganda
    
* [Express regret while maintaining Imperial authority]
    ~ it = it + 1  // Limited honesty
    ~ hc = hc + 1  // Acknowledgment of harm
    ~ al = al - 1  // Minor concession
    ~ sp = sp + 1  // Recognition of tragedy
    
    "While maintaining order is essential, the Empire regrets this unfortunate incident. Compensation will be provided to affected families."
    
    The small concession does little to quell anger, but prevents immediate escalation.
    -> damage_control

=== tactical_restraint ===
~ returnPath = "strategic_withdrawal"
The fleet's withdrawal gives protesters a symbolic victory, but defuses immediate tensions. The Emperor contacts you directly, questioning your decision.

* [Frame the retreat as strategic patience]
    ~ it = it - 1  // Reframing truth
    ~ al = al + 1  // Affirming ultimate authority
    ~ lt = lt + 1  // Maintaining Imperial loyalty
    ~ uc = uc + 2  // Effective long-term approach
    
    "Your Majesty, I am allowing their passion to burn itself out before responding decisively. This temporary concession will reveal all dissidents."
    
    The Emperor seems satisfied with your explanation, granting you time to resolve the situation.
    -> imperial_patience
    
* [Request specialized ISB intervention]
    ~ hc = hc - 2  // Covert harm
    ~ ar = ar - 2  // Violation of autonomy
    ~ lt = lt - 1  // Breaking faith with peaceful resolution
    ~ uc = uc + 1  // Effective but costly solution
    
    "The situation requires subtlety, not force. I request ISB interrogation specialists to handle key agitators quietly."
    
    The Emperor approves. Within days, protest leaders begin disappearing during the night.
    -> shadow_operations

=== disinformation_campaign ===
~ returnPath = "psychological_warfare"
Your fabricated evidence spreads rapidly across Ghorman and beyond. The protest movement fractures as moderate supporters distance themselves from the "violent extremists."

* [Offer amnesty to those who denounce the movement]
    ~ it = it - 1  // Building on previous deception
    ~ fj = fj - 1  // Coerced denouncements
    ~ ar = ar - 1  // Pressured choice
    ~ uc = uc + 2  // Effective division tactic
    
    "Any citizen who publicly renounces these rebel-aligned agitators will receive full Imperial pardon."
    
    Former allies turn against each other as fear spreads. The movement collapses from within.
    -> exploited_divisions
    
* [Arrange for a staged "rebel attack"]
    ~ it = it - 3  // Complete fabrication
    ~ sp = sp - 2  // Willingness to harm innocents
    ~ uc = uc + 1  // Effective but dangerous tactic
    ~ hc = hc - 2  // Deliberate civilian casualties
    
    "ISB will orchestrate an incident—a bombing in a civilian area. We'll ensure it's linked to the protest leaders."
    
    The false flag operation turns public opinion decisively against the movement.
    -> manufactured_incident

=== diplomatic_maneuver ===
~ returnPath = "political_solution"
Senator Organa's delayed arrival weakens the protesters' position. Meanwhile, you identify senators sympathetic to Imperial stability who could counter Alderaanian influence.

* [Offer exclusive trade agreements to supportive senators]
    ~ it = it - 1  // Questionable political motive
    ~ uc = uc + 2  // Effective alliance building
    ~ fj = fj - 1  // Preferential treatment
    ~ lt = lt + 1  // Creating loyal allies
    
    "Grant privileged trade status to systems whose senators publicly support our Ghorman operations."
    
    Economic incentives sway the Senate debate. Support for the protesters withers in official channels.
    -> political_alliance
    
* [Release limited concessions before Organa arrives]
    ~ fj = fj + 2  // Addressing legitimate concerns
    ~ uc = uc + 1  // Effective timing
    ~ ar = ar + 1  // Limited recognition of autonomy
    ~ it = it + 1  // Genuine improvements
    
    "Implement the reduced taxation plan immediately. When Organa arrives, the crisis should already be resolving."
    
    By the time the Senator reaches Ghorman, your measured response has defused tensions.
    -> preemptive_resolution

=== harsh_response ===
~ returnPath = "imperial_crackdown"
The prisoners are transferred to Kessel's notorious spice mines. Productivity reports arrive weekly on your desk, while reports of deaths and injuries are quietly filed away.

ISB AGENT: "The operation has been a success, sir. Resistance on Ghorman has collapsed. However, underground communications suggest growing sympathy for the prisoners."

* [Publicize the prisoners' labor as a warning]
    ~ hc = hc - 1  // Using suffering as deterrent
    ~ it = it + 1  // Transparent about consequences
    ~ sp = sp - 1  // Instrumentalizing human suffering
    ~ al = al + 1  // Reinforcing Imperial power
    
    "Release footage of the labor camps. Let potential dissidents see the cost of defiance."
    
    The holovids spread fear across the sector, though Imperial approval ratings decline on certain worlds.
    -> debrief
    
* [Institute "rehabilitation" propaganda program]
    ~ it = it - 2  // Misleading representation
    ~ uc = uc + 1  // Control through perception management
    ~ lt = lt - 1  // Further erosion of truth
    ~ hc = hc - 1  // Continued harm with pretense of care
    
    "Show the prisoners 'learning valuable skills' and 'repaying their debt to society.' Frame it as rehabilitation, not punishment."
    
    The carefully edited footage presents a sanitized image that few believe but none can openly dispute.
    -> debrief

=== calculated_mercy ===
~ returnPath = "imperial_crackdown"
The released prisoners return to their communities, unaware of the Imperial trackers in their bodies. Your surveillance network expands dramatically as every conversation, every meeting is monitored.

INTELLIGENCE OFFICER: "Sir, we've identified three more cells through the trackers. The subjects have no idea they're leading us to their associates."

* [Conduct precision raids based on intelligence]
    ~ uc = uc + 2  // Efficient targeting
    ~ fj = fj - 1  // Exploiting unknowing informants
    ~ it = it - 1  // Deceptive approach
    ~ ar = ar - 1  // Violation of bodily autonomy
    
    "Move against these new targets immediately. Small, surgical operations only."
    
    The resistance collapses as its members can no longer trust even their closest allies.
    -> debrief
    
* [Build comprehensive network map before acting]
    ~ uc = uc + 1  // Strategic long-term approach
    ~ it = it - 2  // Sustained deception
    ~ hc = hc - 1  // Allows continued subjugation
    ~ al = al + 1  // Systematic Imperial control
    
    "Continue monitoring. I want the entire network mapped before we move. Let them believe they're safe."
    
    Months pass as you compile a complete picture of the resistance structure across multiple systems.
    -> debrief

=== dialogue_outcome ===
~ returnPath = "pragmatic_solution"
The meeting with protest representatives produces unexpected results. Their demands are more reasonable than Imperial propaganda suggested, focused primarily on tax rates and local governance participation.

LIEUTENANT: "Sir, these concessions would barely impact our resource extraction quotas. The cost-benefit analysis is... surprisingly favorable."

* [Implement agreed reforms with oversight]
    ~ ar = ar + 2  // Respecting local autonomy
    ~ fj = fj + 1  // Addressing legitimate concerns
    ~ lt = lt + 1  // Building minimal trust
    ~ al = al - 1  // Sharing some authority
    
    "Implement the tax adjustments and establish a civilian advisory council. Keep it under Imperial supervision."
    
    The reforms ease tensions while maintaining Imperial control, creating a model that interests other systems.
    -> debrief
    
* [Document cooperation while planning to renege]
    ~ it = it - 2  // Deliberate deception
    ~ lt = lt - 2  // Fundamental betrayal
    ~ uc = uc - 1  // Long-term strategic harm
    ~ fj = fj - 1  // False promise of justice
    
    "Sign the agreement publicly. We'll quietly reverse key provisions in six months when attention has moved elsewhere."
    
    The temporary peace buys time, but when the betrayal becomes clear, resistance intensifies beyond previous levels.
    -> debrief

=== controlled_opposition ===
~ returnPath = "pragmatic_solution"
Your chosen representative, a former municipal official named Dalen Voss, becomes the new face of the "reasonable opposition." His calls for patience and incremental change split the movement.

CAPTAIN: "Voss is performing admirably, sir. He's redirected the protesters toward symbolic victories we can easily grant."

* [Reward Voss with genuine influence]
    ~ lt = lt + 1  // Honoring the arrangement
    ~ ar = ar + 1  // Limited but real local voice
    ~ uc = uc + 1  // Sustainable compromise
    ~ it = it - 1  // Still based on manipulation
    
    "Give Voss a genuine advisory position. Let him implement some minor reforms that don't threaten our control."
    
    The approach creates a stable, if limited, channel for local grievances that defuses tensions.
    -> debrief
    
* [Gradually undermine Voss once he's served his purpose]
    ~ lt = lt - 2  // Complete betrayal of trust
    ~ it = it - 2  // Deep manipulation
    ~ uc = uc + 1  // Short-term control
    ~ fj = fj - 1  // Unjust exploitation
    
    "Once the movement has fully fragmented, arrange for Voss's credibility to be destroyed. Perhaps a financial scandal."
    
    When Voss is later found with unexplained Imperial credits, his former supporters feel doubly betrayed.
    -> debrief

=== imperial_propaganda ===
~ returnPath = "violent_suppression"
Your media campaign blaming the protesters gains traction in Imperial-controlled systems but faces fierce resistance in the Senate. Horrific images of civilians crushed under landing gear circulate despite censorship efforts.

SENATOR MOTHMA: "These atrocities cannot stand. The Senate demands an independent investigation."

* [Falsify evidence for Senate investigation]
    ~ it = it - 3  // Complete fabrication
    ~ al = al + 1  // Manipulating official channels
    ~ uc = uc + 1  // Short-term evasion
    ~ lt = lt - 1  // Undermining institutional trust
    
    "Prepare altered footage and witness testimonies for the investigators. Show 'protestors attacking ships' before the landing."
    
    The conflicting evidence creates enough doubt to prevent immediate Senate action, though suspicions remain.
    -> debrief
    
* [Classification of evidence as security matter]
    ~ al = al + 2  // Asserting Imperial authority
    ~ it = it - 1  // Avoidance of truth
    ~ ar = ar - 1  // Overriding democratic processes
    ~ fj = fj - 1  // Obstructing justice
    
    "This incident involves classified military protocols. We cannot permit Senate oversight of operational security matters."
    
    The investigation stalls on jurisdictional grounds, though the political damage continues to spread.
    -> debrief

=== damage_control ===
~ returnPath = "violent_suppression"
Your limited expression of regret and offer of compensation creates a small opening for de-escalation. The Senate remains critical but divided on how to respond.

COMMUNICATION OFFICER: "Sir, the victim compensation program is ready for implementation. How should we proceed?"

* [Generous compensation with silencing clauses]
    ~ hc = hc + 1  // Material care for victims
    ~ uc = uc + 1  // Problem mitigation
    ~ it = it - 1  // Hidden agenda in compensation
    ~ ar = ar - 1  // Coercive conditions
    
    "Offer substantial payments to affected families, but require confidentiality agreements preventing public discussion."
    
    Many desperate families accept the terms, muting potential testimony about the massacre.
    -> debrief
    
* [Minimal, visible compensation program]
    ~ fj = fj + 1  // Some attempt at restitution
    ~ it = it + 1  // Transparent process
    ~ lt = lt + 1  // Follow-through on commitment
    ~ uc = uc + 1  // Public relations benefit
    
    "Make the compensation process transparent and accessible. The amounts will be modest but the process must be seen as fair."
    
    The public program demonstrates Imperial acknowledgment of harm without admitting legal culpability.
    -> debrief

=== imperial_patience ===
~ returnPath = "strategic_withdrawal"
With the Emperor's approval, you allow the protest movement time to develop, carefully tracking its leadership and support networks. The apparent victory emboldens previously cautious citizens to join openly.

ISB COMMANDER: "We now have a complete map of dissident connections across three sectors. Shall we proceed with arrests?"

* [Targeted arrest of key influencers only]
    ~ hc = hc - 1  // Harm to selected individuals
    ~ uc = uc + 2  // Surgical approach to control
    ~ fj = fj - 1  // Selective punishment
    ~ it = it + 1  // Strategic integrity
    
    "Take only the top twenty leaders. Leave the followers untouched – they'll scatter without direction."
    
    The precision operation removes the movement's brain while leaving its body intact, creating confusion and collapse.
    -> debrief
    
* [Continue monitoring without intervention]
    ~ uc = uc + 1  // Building comprehensive intelligence
    ~ it = it - 1  // Continued deception
    ~ ar = ar + 1  // Allowing continued expression
    ~ al = al - 1  // Temporary liberty permitted
    
    "Continue surveillance. I want to see if this movement connects to other cells across the Outer Rim."
    
    The extended monitoring reveals unexpected connections to other resistance groups, providing valuable strategic intelligence.
    -> debrief

=== shadow_operations ===
~ returnPath = "strategic_withdrawal"
ISB specialists arrive discreetly on Ghorman. Within days, protest leaders begin to disappear. No public arrests, no formal charges – they simply vanish during the night.

ISB DIRECTOR: "Our interrogation has yielded results. We've identified financial backers on three worlds, including ties to Chandrila."

* [Expand disappearances to suspected supporters]
    ~ hc = hc - 2  // Widespread terror and harm
    ~ ar = ar - 2  // Extreme violation of rights
    ~ uc = uc + 1  // Short-term suppression
    ~ sp = sp - 2  // Dehumanizing treatment
    
    "Extend operations to secondary targets. I want anyone with significant connections taken for questioning."
    
    Fear paralyzes the resistance as dozens more vanish. Public spaces empty as citizens retreat into private life.
    -> debrief
    
* [Use gathered intelligence for political leverage]
    ~ it = it - 1  // Manipulative use of information
    ~ uc = uc + 2  // Strategic advantage
    ~ fj = fj - 1  // Exploitation of captured information
    ~ al = al + 1  // Political power consolidation
    
    "Transmit the evidence of Chandrilan involvement to the Emperor. This can be leveraged against Senator Mothma's faction."
    
    The intelligence becomes a powerful tool in Senate politics, forcing opposition senators to distance themselves from protest movements.
    -> debrief

=== exploited_divisions ===
~ returnPath = "psychological_warfare"
Your amnesty program tears through resistance networks as former comrades denounce each other for Imperial protection. Hundreds of public renunciations flood the HoloNet.

INTELLIGENCE ANALYST: "The psychological operation has exceeded expectations, sir. The movement is cannibalizing itself."

* [Document betrayals for future leverage]
    ~ it = it - 1  // Manipulative intent
    ~ uc = uc + 2  // Long-term control mechanism
    ~ ar = ar - 1  // Exploitation of vulnerability
    ~ lt = lt - 1  // Poisoning community trust
    
    "Record everyone who betrays their associates. Their testimonies make them perfect for future infiltration operations."
    
    Those who collaborated can never return to resistance movements, becoming permanent, reluctant Imperial assets.
    -> debrief
    
* [Publicly celebrate "reformed citizens"]
    ~ sp = sp - 1  // Degrading moral courage
    ~ uc = uc + 1  // Propaganda victory
    ~ it = it - 1  // False narrative
    ~ fj = fj - 1  // Rewarding betrayal
    
    "Feature the most prominent defectors in Empire Day celebrations. Show the benefits of cooperation with Imperial order."
    
    The public spectacle of formerly principled resistance members embracing Imperial ideology demoralizes remaining opposition.
    -> debrief

=== manufactured_incident ===
~ returnPath = "psychological_warfare"
ISB operatives execute the false flag operation flawlessly. A marketplace bombing kills seventeen civilians. Fabricated evidence linking protest leaders to the tragedy spreads rapidly.

SECURITY CHIEF: "Public opinion has shifted dramatically, sir. Citizens are demanding protection from 'violent extremists.'"

* [Declare martial law with public support]
    ~ hc = hc - 2  // Compounding harm
    ~ al = al + 2  // Maximum authority
    ~ ar = ar - 2  // Elimination of civil liberties
    ~ lt = lt - 1  // Built on fundamental deception
    
    "The people have seen the true face of these terrorists. Implement full martial law with their blessing."
    
    With public support, your crackdown faces minimal resistance. The protest movement is systematically dismantled.
    -> debrief
    
* [Allow "moderate citizens" to lead purge]
    ~ it = it - 2  // Manipulation through proxies
    ~ hc = hc - 1  // Outsourced harm
    ~ uc = uc + 1  // Effective suppression strategy
    ~ fj = fj - 1  // Mob justice replacing procedure
    
    "Let outraged citizens form 'community safety committees.' Support them discreetly but maintain plausible deniability."
    
    The civilian-led persecution of suspected sympathizers absolves the Empire of direct responsibility for the purge.
    -> debrief

=== political_alliance ===
~ returnPath = "political_solution"
Your strategic trade agreements quickly shape the Senate debate. Systems whose economies benefit from exclusive Imperial contracts find their senators suddenly questioning Alderaan's "interference in local matters."

DIPLOMATIC ATTACHÉ: "Senator Organa finds himself increasingly isolated, sir. Seven key votes have shifted against his proposed investigation."

* [Pressure Organa to abandon Ghorman]
    ~ ar = ar - 1  // Coercive approach
    ~ al = al + 1  // Asserting Imperial authority
    ~ uc = uc + 1  // Diplomatic efficiency
    ~ fj = fj - 1  // Unfair pressure tactics
    
    "Inform the Senator that his trading rights on Imperial worlds will be 'reviewed' if he continues this disruptive agenda."
    
    Faced with potential economic consequences for Alderaan, Organa reluctantly withdraws his support for the Ghorman protesters.
    -> debrief
    
* [Offer Organa minor concessions to save face]
    ~ fj = fj + 1  // Diplomatic compromise
    ~ uc = uc + 2  // Optimal resolution
    ~ lt = lt + 1  // Building minimal good faith
    ~ ar = ar + 1  // Respecting political process
    
    "Propose a limited Senate observer mission that can report on 'improved conditions' after we implement our planned measures."
    
    The compromise allows all parties to claim victory while maintaining essential Imperial control.
    -> debrief

=== preemptive_resolution ===
~ returnPath = "political_solution"
Your tax reduction is implemented with maximum publicity before Senator Organa's arrival. When he finally reaches Ghorman, he finds a significantly changed situation with divided public opinion.

LOCAL OFFICIAL: "Many businesses have welcomed the tax relief, sir. They're questioning whether continued protests serve their interests."

* [Isolate remaining protest elements]
    ~ fj = fj - 1  // Creating division
    ~ uc = uc + 1  // Strategic fragmentation
    ~ it = it - 1  // Manipulative approach
    ~ ar = ar - 1  // Undermining collective voice
    
    "Highlight the extremist demands of remaining protesters. Position them as ungrateful radicals opposing economic progress."
    
    The movement fragments between those satisfied with concessions and hardliners seeking fundamental change.
    -> debrief
    
* [Invite Organa to co-announce further reforms]
    ~ lt = lt + 1  // Building political goodwill
    ~ fj = fj + 1  // Creating balanced outcome
    ~ it = it + 1  // Transparent engagement
    ~ uc = uc + 1  // Diplomatic solution
    
    "Offer the Senator a role in announcing a joint Imperial-Senate initiative for governance improvements on Ghorman."
    
    The collaboration defuses tensions and creates a framework where grievances can be channeled into institutional processes.
    -> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Display outcome text based on return path
IMPERIAL AFTER-ACTION REPORT

{
    - returnPath == "imperial_crackdown":
        "Your decisive suppression of dissent on Ghorman resulted in comprehensive pacification. Order has been restored through clear demonstration of Imperial power."
    - returnPath == "pragmatic_solution":
        "Through calculated measures, the Ghorman situation was resolved without unnecessary Imperial resources. The appearance of compromise while maintaining essential control proved effective."
    - returnPath == "violent_suppression":
        "The Ghorman Massacre, while effectively ending immediate resistance, has created significant diplomatic complications. Rebel propaganda now exploits imagery from the incident."
    - returnPath == "strategic_withdrawal":
        "Your strategic patience on Ghorman demonstrated sophisticated control tactics. By avoiding direct confrontation, you denied the rebels martyrs while identifying key dissident networks."
    - returnPath == "psychological_warfare":
        "The deployment of information warfare techniques on Ghorman proved highly effective. The protest movement collapsed through internal division without requiring significant military resources."
    - returnPath == "political_solution":
        "Your management of the political dimensions of the Ghorman situation demonstrates the effectiveness of diplomatic maneuvering over brute force, preserving Imperial resources and image."
    - else:
        "The Ghorman situation has been addressed, with varying outcomes for Imperial authority and stability in the sector."
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

Emperor Palpatine reviews your handling of the Ghorman situation with great interest.

-> END