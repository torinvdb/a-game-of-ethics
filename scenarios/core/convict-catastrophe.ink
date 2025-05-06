// ============================
// 🔒 Convict Catastrophe 🔒
// A scenario about prison escape ethics, loyalty, and necessary sacrifice
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

-> prison_start

=== prison_start ===
You are Prisoner 89P13, wrongfully imprisoned in the Kyln—the galaxy's most notorious maximum-security facility. An explosion rocks B-Block. Alarms wail as security systems malfunction. This is your chance.

CELL NEIGHBOR: "The force fields are down! It's now or never!"

Your cellmate Drax turns to you, eyes gleaming with opportunity.

DRAX: "I will have my revenge on the guards who beat me. Join me, or find your own way out."

*   [Join Drax's violent rampage]
    ~ hc = hc - 2  // Participating in violence against guards
    ~ lt = lt + 2  // Strong loyalty to fellow prisoner
    ~ al = al - 2  // Direct rebellion against authority
    ~ uc = uc + 1  // Potentially effective escape method
    
    You nod grimly to Drax. "Let's make them pay."
    
    The massive warrior smiles as he tears the cell door from its frame. Together, you charge into the chaos.
    -> guard_encounter
    
*   [Escape quietly, avoid unnecessary violence]
    ~ hc = hc + 2  // Avoiding harm to others
    ~ ar = ar + 1  // Respecting others' right to live
    ~ al = al - 1  // Still disobeying prison authority
    ~ lt = lt - 1  // Rejecting Drax's offer of alliance
    
    "I'm not here for revenge, just freedom. I'll find my own way."
    
    Drax snorts with contempt. "Coward." He charges into the fray alone while you slip into the shadows.
    -> control_room
    
*   [Rally prisoners for organized escape]
    ~ fj = fj + 2  // Providing equal opportunity to escape
    ~ lt = lt + 1  // Building trust among prisoners
    ~ it = it + 1  // Honest about intentions
    ~ uc = uc + 1  // Organized approach might be more effective
    
    "Wait! We need a plan. Let's gather others—we'll have a better chance together."
    
    Drax hesitates, then nods. "Perhaps there is wisdom in numbers."
    -> rally_prisoners

=== guard_encounter ===
You and Drax turn a corner to find a lone guard, young and terrified, backed against the wall. Other prisoners surround him, weapons improvised from broken equipment.

PRISONER: "Look who's helpless now! Should we space him like they did to Korath?"

The guard's eyes are wide with fear.

GUARD: "Please... I have children. I just follow orders."

*   [Kill the guard—one less enemy]
    ~ hc = hc - 3  // Severe harm to defenseless person
    ~ sp = sp - 2  // Disregards sanctity of life
    ~ fj = fj - 1  // Excessive punishment
    ~ uc = uc + 1  // Eliminates potential threat
    
    "One less uniform to worry about."
    
    You grab a jagged pipe and end the guard quickly. The other prisoners cheer as you take his security keycard.
    
    DRAX: "You have the stomach for this work after all."
    -> security_checkpoint
    
*   [Spare him, but take his keycard]
    ~ hc = hc + 2  // Prevents unnecessary death
    ~ ar = ar + 1  // Respects guard's right to live
    ~ it = it + 1  // Honest about intentions
    ~ uc = uc + 1  // Gets keycard without violence
    
    "We need his keycard, not his blood. Step aside."
    
    You push through the crowd and take the guard's keycard, then motion the prisoners onward.
    
    GUARD: (whispers) "Thank you..."
    -> security_checkpoint
    
*   [Protect guard, claim he could be useful]
    ~ hc = hc + 3  // Actively prevents harm
    ~ lt = lt - 2  // Betrays prisoner solidarity
    ~ it = it - 1  // Somewhat deceptive about motives
    ~ sp = sp + 2  // Upholds sanctity of life
    
    "He knows the security protocols! We need him alive to get past the outer gates."
    
    The prisoners grumble but back down. Drax eyes you suspiciously.
    
    DRAX: "I hope your mercy does not become our undoing."
    -> guard_alliance

=== rally_prisoners ===
You quickly gather a diverse group: Rocket, a cybernetic genius; Gamora, a skilled assassin; and Groot, a sentient tree-creature. You huddle in an alcove as the riot spreads.

ROCKET: "The automated defense grid will reactivate in 18 minutes. After that, we're all toast."

GAMORA: "There's a guard station on level three with manual override controls."

*   [Split up to cover more ground]
    ~ ar = ar + 2  // Respects each person's autonomy
    ~ uc = uc - 1  // Less efficient approach
    ~ lt = lt - 1  // Less cohesive team effort
    ~ fj = fj + 1  // Equal risk distribution
    
    "Rocket, take Groot and hit the engineering deck. Gamora and I will secure the guard station. Drax, create a diversion."
    
    Everyone nods and disperses to their tasks.
    -> defense_grid
    
*   [Stay together, move as a unit]
    ~ hc = hc + 1  // Protecting everyone in the group
    ~ lt = lt + 2  // Strong group solidarity
    ~ uc = uc - 1  // Potentially slower approach
    ~ ar = ar - 1  // Less individual freedom
    
    "We stick together. No one gets left behind."
    
    ROCKET: "Sentimental garbage. But fine, your funeral too."
    -> hangar_battle
    
*   [Use weaker prisoners as decoys]
    ~ hc = hc - 3  // Deliberately endangering others
    ~ uc = uc + 2  // Tactically advantageous
    ~ fj = fj - 3  // Extremely unfair treatment
    ~ it = it - 1  // Manipulative tactics
    
    "We need a distraction. The D-Block inmates should charge the main gate first, draw the fire..."
    
    GROOT: "I am Groot!" (He looks horrified)
    
    GAMORA: "That's cold, even for prison."
    
    Despite moral objections, your tactical mind prevails.
    -> sacrificial_diversion

=== control_room ===
You slip past fighting and reach a secondary control room. Through the window, you see three different prisoner groups fighting their way toward the hangar bay.

COMPUTER: "Lockdown protocols initiating in T-minus 10 minutes."

The console shows you can redirect security forces or disable certain systems—but not everything.

*   [Disable security for all prison blocks]
    ~ fj = fj + 3  // Gives everyone equal chance
    ~ ar = ar + 2  // Respects all prisoners' freedom
    ~ al = al - 2  // Completely undermines authority
    ~ sp = sp - 1  // Some dangerous criminals will escape
    
    You override the system, unlocking all cell blocks including maximum security.
    
    Alarms intensify as the prison erupts into complete chaos. Somewhere, you hear predatory howls from notorious killers now freed.
    -> mass_escape
    
*   [Create escape route just for yourself]
    ~ fj = fj - 2  // Selfishly prioritizing yourself
    ~ lt = lt - 2  // Betraying fellow prisoners
    ~ ar = ar + 1  // Asserting your own autonomy
    ~ uc = uc + 1  // Effective for personal escape
    
    You program a specific path to clear, locking down other sections to distract guards.
    
    The sounds of imprisoned rioters being recaptured echo through the halls as you slip toward freedom.
    -> solo_escape
    
*   [Trigger emergency containment in violent blocks]
    ~ hc = hc + 1  // Prevents widespread violence 
    ~ fj = fj - 1  // Unequal treatment of prisoners
    ~ it = it + 1  // Honest assessment of dangerous inmates
    ~ uc = uc + 2  // Strategically sound approach
    
    You isolate the truly dangerous inmates while creating escape routes for nonviolent offenders.
    
    The system acknowledges your commands with efficient precision. The chaos becomes more controlled.
    -> selective_escape

=== security_checkpoint ===
You reach a major checkpoint. Beyond it: the path to freedom. But the automated turrets are rebooting, and will fire on anything that moves. A group of injured prisoners huddles nearby.

ROCKET: (appears suddenly) "Those turrets will shred anything organic in five seconds flat."

He points to a maintenance tunnel entrance nearby.

ROCKET: "That tunnel bypasses the guns, but it'll only fit three of us before the oxygen runs out."

Your group numbers seven.

*   [Leave the injured behind, save yourselves]
    ~ hc = hc - 2  // Abandoning those in need
    ~ lt = lt - 2  // Breaking solidarity with weaker prisoners
    ~ uc = uc + 2  // Maximizes survival for some
    ~ sp = sp - 1  // Devalues lives of the injured
    
    "Survival means making hard choices. The strongest should go through."
    
    The injured prisoners watch with desperate eyes as you select your escape team.
    
    DRAX: "A warrior's choice. Cold, but necessary."
    -> tunnel_escape
    
*   [Draw fire to create opening for the injured]
    ~ hc = hc + 3  // Extreme self-sacrifice for others
    ~ ar = ar + 1  // Respects injured prisoners' right to life
    ~ lt = lt + 3  // Ultimate loyalty to fellow inmates
    ~ uc = uc - 1  // Personal risk is extremely high
    
    "I'll draw their fire. When they focus on me, everyone else runs."
    
    ROCKET: "That's suicide!"
    
    You grip a metal shield, preparing for your desperate gambit.
    -> heroic_sacrifice
    
*   [Hack the turrets to target guards instead]
    ~ hc = hc - 1  // Endangers guards
    ~ fj = fj - 2  // Unfairly targets specific group
    ~ it = it - 1  // Manipulative tactic
    ~ uc = uc + 2  // Effective solution for prisoners
    
    "Rocket, can you reprogram the targeting parameters?"
    
    ROCKET: (grinning) "Already on it. Those turrets won't know a prisoner from a potted plant."
    
    The turrets swivel toward approaching guard reinforcements.
    -> reprogrammed_defenses

=== guard_alliance ===
The guard you saved, Officer Nova, leads you through maintenance corridors.

NOVA: "There's a security hangar with emergency shuttles on level five. I can get you there."

Drax scowls distrustfully.

DRAX: "How do we know this isn't a trap?"

*   [Trust the guard completely]
    ~ lt = lt + 2  // Building trust across lines
    ~ al = al + 1  // Working with legitimate authority
    ~ ar = ar + 1  // Respecting guard's changed position
    ~ it = it - 1  // Possibly naive trust
    
    "He has no reason to trick us. Lead the way, Nova."
    
    NOVA: (nodding) "Thank you for the chance to be better than my uniform."
    -> shuttle_bay
    
*   [Keep the guard as hostage while following his directions]
    ~ hc = hc - 1  // Threatens guard's wellbeing
    ~ lt = lt - 1  // Limited trust in guard's directions
    ~ uc = uc + 2  // Practical insurance policy
    ~ it = it + 1  // Honest about intentions
    
    "You'll get us there, but you're coming with us as insurance. Try anything, and you won't make it home."
    
    NOVA: (swallows) "Understood. This way."
    -> tense_journey
    
*   [Pretend to trust him while preparing for betrayal]
    ~ it = it - 3  // Complete deception
    ~ lt = lt - 2  // False pretense of trust
    ~ uc = uc + 1  // Tactical advantage if betrayed
    ~ fj = fj - 1  // Prejudges guard unfairly
    
    "Lead on, friend. We're grateful." (You secretly signal Drax to be ready to strike)
    
    NOVA: "Thank you for believing in me."
    
    You follow, knife concealed in your palm.
    -> paranoid_escape

=== defense_grid ===
~ returnPath = "team_separated"
Your team separated, you make your way toward the defense grid controls. Rocket's voice crackles over a stolen comm.

ROCKET: "Grid's reactivating faster than expected! Someone needs to manually hold the override on level six!"

The override requires someone to remain behind, sacrificing their escape.

*   [Volunteer yourself to stay behind]
    ~ hc = hc + 2  // Self-sacrifice to save others
    ~ lt = lt + 3  // Ultimate loyalty to team
    ~ uc = uc + 1  // Ensures others escape
    ~ ar = ar + 1  // Personal choice to sacrifice
    
    "I'll do it. The rest of you, get to the ship."
    
    ROCKET: "You sure about this?"
    
    You take a deep breath. "Go. I'll buy you all the time I can."
    -> heroic_sacrifice
    
*   [Order the weakest team member to stay]
    ~ hc = hc - 2  // Forces sacrifice on another
    ~ lt = lt - 2  // Betrayal of team member
    ~ al = al + 1  // Asserting leadership authority
    ~ uc = uc + 1  // Preserves stronger members
    
    "Mantis, you're the least combat-effective. You need to hold the override."
    
    MANTIS: (trembling) "I... understand. Goodbye, friends."
    
    The others avoid your gaze as you continue toward freedom.
    -> forced_sacrifice
    
*   [Sabotage the grid, risking civilian casualties]
    ~ hc = hc - 3  // Potential massive harm to innocents
    ~ sp = sp - 2  // Disregard for innocent life
    ~ uc = uc - 1  // Short-term gain, long-term consequences
    ~ ar = ar + 1  // Asserting freedom at all costs
    
    "Forget the override. I'm going to overload the main reactor."
    
    ROCKET: "That'll take out half the station! Including civilian sectors!"
    
    You grit your teeth. "Sometimes freedom requires terrible choices."
    -> catastrophic_escape

=== hangar_battle ===
~ returnPath = "team_unified"
Your unified group reaches the hangar, but a battalion of guards blocks the exit. Beyond them, a small ship waits—your ticket to freedom.

GAMORA: "We're outnumbered three to one."

*   [Full frontal assault]
    ~ hc = hc - 2  // Violence against many guards
    ~ fj = fj - 1  // Disproportionate response
    ~ ar = ar + 1  // Asserting freedom through force
    ~ uc = uc - 1  // High-risk approach
    
    "Hit them with everything! Don't stop until we reach that ship!"
    
    Your team charges forward, weapons improvised and desperation fueling your attack.
    -> bloody_escape
    
*   [Create diversion, minimize casualties]
    ~ hc = hc + 1  // Attempts to reduce harm
    ~ it = it + 1  // Honest approach to problem
    ~ lt = lt + 1  // Protects team members
    ~ uc = uc + 2  // Effective strategy with lower cost
    
    "Rocket, can you trigger the fire suppression system? Groot, use the confusion to clear a path."
    
    ROCKET: "Now you're speaking my language!"
    
    With alarms blaring and foam filling the hangar, you make your move.
    -> clever_escape
    
*   [Negotiate surrender in exchange for safe passage]
    ~ hc = hc + 2  // Avoiding bloodshed
    ~ al = al + 1  // Working within authority framework
    ~ ar = ar - 1  // Surrendering some autonomy
    ~ it = it + 2  // Honest approach
    
    "Hold! We'll surrender our weapons if you let us board that ship!"
    
    The guard captain hesitates. "Why should I trust escaped convicts?"
    
    DRAX: (whispers) "Have you lost your mind?"
    -> tense_negotiation

=== sacrificial_diversion ===
~ returnPath = "sacrificial_plan"
You've sent the weaker prisoners as a diversion. Their screams echo as they draw fire from the automated defenses, while your elite team navigates safely through the chaos.

GAMORA: "That was... effective. But at what cost?"

You reach the hangar, with a clear path to a ship.

*   [Acknowledge regret, but continue]
    ~ hc = hc + 1  // Recognizes harm caused
    ~ it = it + 2  // Honest about moral costs
    ~ sp = sp + 1  // Acknowledges moral boundary crossed
    ~ fj = fj - 1  // Still benefited from injustice
    
    "They paid a terrible price. I won't forget their sacrifice."
    
    ROCKET: "Pretty words don't un-die people."
    
    You lower your eyes as you board the escape craft.
    -> regretful_escape
    
*   [Go back to help survivors]
    ~ hc = hc + 3  // Active attempt to undo harm
    ~ lt = lt + 1  // Loyalty to fellow prisoners
    ~ uc = uc - 2  // Risks successful escape
    ~ it = it + 1  // Honest attempt to make amends
    
    "We can't leave them. I was wrong. Help me get the survivors!"
    
    Your team looks shocked, but follows as you rush back into danger.
    -> redemptive_return
    
*   [Feel no remorse—survival justifies everything]
    ~ hc = hc - 2  // Complete disregard for suffering caused
    ~ sp = sp - 3  // Violation of basic moral principles
    ~ it = it - 1  // Self-deception about moral character
    ~ uc = uc + 1  // Purely utilitarian calculation
    
    "Necessary sacrifices. Focus on getting that ship operational."
    
    GROOT: "I am Groot..." (He turns away, disgusted)
    
    You ignore the judgment in their eyes. Freedom is all that matters.
    -> cold_escape

=== mass_escape ===
~ returnPath = "mass_freedom"
Your actions have unlocked all cells. Prisoners of every species flood the corridors, some violent, some simply desperate for freedom.

COMPUTER: "Containment breach in maximum security. Extremely dangerous entities released."

Through viewports, you see escape pods launching in all directions.

*   [Join the general exodus]
    ~ fj = fj + 2  // Equal opportunity for all
    ~ lt = lt + 1  // Solidarity with all prisoners
    ~ sp = sp - 2  // Some truly dangerous beings freed
    ~ uc = uc - 1  // Chaotic outcome
    
    You join the tide of escapees, allowing chaos to cover your tracks.
    
    Around you, prisoners laugh, cry, and fight as they taste freedom again.
    -> chaotic_freedom
    
*   [Help recapture the truly dangerous]
    ~ hc = hc + 2  // Prevents potential mass harm
    ~ fj = fj - 1  // Selective freedom
    ~ al = al + 2  // Supports legitimate authority
    ~ sp = sp + 1  // Upholds moral boundaries
    
    "Some of these inmates should never be free. I'll help secure S-Block."
    
    A guard looks at you with confusion as you help seal a containment door.
    -> partial_redemption
    
*   [Steal a guard's uniform and identity]
    ~ it = it - 3  // Complete deception
    ~ fj = fj - 1  // Unfair advantage
    ~ uc = uc + 2  // Highly effective escape strategy
    ~ ar = ar + 1  // Personal autonomy maximized
    
    You overpower an isolated guard and don their uniform.
    
    "This is Officer Dey. Requesting evacuation from sector seven."
    
    With your disguise, you walk freely toward an officer's shuttle.
    -> identity_theft

=== solo_escape ===
~ returnPath = "solo_path"
You've cleared a path just for yourself. Emergency bulkheads seal behind you, trapping other escapees. Their pounding fists and shouts fade as you move further from the chaos.

COMPUTER: "Oxygen depletion in sealed sectors in ten minutes."

*   [Continue alone, maximize survival chances]
    ~ lt = lt - 3  // Complete betrayal of fellow prisoners
    ~ uc = uc + 1  // Self-preservation accomplished
    ~ hc = hc - 2  // Indifference to others' suffering
    ~ ar = ar + 2  // Complete personal autonomy
    
    You push forward without looking back. Their fate is not your concern.
    
    Soon, the only sound is your footsteps echoing in empty corridors.
    -> selfish_freedom
    
*   [Override bulkheads, risk recapture]
    ~ lt = lt + 3  // Extreme loyalty to others
    ~ hc = hc + 2  // Prevents suffering and death
    ~ uc = uc - 2  // Compromises effective escape plan
    ~ ar = ar - 1  // Sacrifices personal freedom chance
    
    You cannot leave them to suffocate. You hack a terminal and reopen the sealed sections.
    
    Alarms blare as your carefully planned route is compromised.
    -> compromised_escape
    
*   [Save only those useful for escape]
    ~ fj = fj - 2  // Highly selective rescue
    ~ uc = uc + 2  // Pragmatic approach
    ~ hc = hc - 1  // Partial indifference to suffering
    ~ it = it - 1  // Self-serving justification
    
    You scan security feeds and identify three prisoners with skills you need. You unseal only their section.
    
    "I need your engineering skills. Help me, and you escape too."
    -> selective_rescue

=== selective_escape ===
~ returnPath = "selective_freedom"
Your actions have created a controlled chaos. Nonviolent offenders stream toward escape pods, while the truly dangerous remain contained.

A guard commander appears on a screen.

COMMANDER: "Whoever's controlling the systems—this doesn't have to end badly. Help us maintain order, and I'll personally review your case."

*   [Accept the deal, help restore order]
    ~ al = al + 3  // Full cooperation with authority
    ~ lt = lt - 2  // Betrayal of fellow escapees
    ~ fj = fj + 1  // Proportional response to different crimes
    ~ it = it + 1  // Honest engagement
    
    "I accept. Sealing hangar bay three now."
    
    The commander nods. "A wise choice."
    
    You begin redirecting escape attempts into containment zones.
    -> system_collaborator
    
*   [Ignore offer, continue selective release]
    ~ al = al - 1  // Rejects authority's offer
    ~ fj = fj + 2  // Maintains just discrimination
    ~ ar = ar + 1  // Preserves decision-making autonomy
    ~ uc = uc + 1  // Balanced outcome continues
    
    You cut the communication and continue your work, releasing those you deem deserving.
    
    The commander's threats fade into background noise as you focus on your task.
    -> moral_arbiter
    
*   [Pretend to comply while plotting final escape]
    ~ it = it - 2  // Deliberate deception
    ~ uc = uc + 2  // Tactically advantageous
    ~ lt = lt - 1  // Betrays apparent agreement
    ~ ar = ar + 1  // Maintains hidden autonomy
    
    "I'll help restore order. Opening communication channel now."
    
    As you speak, your fingers program an override that will trigger in five minutes.
    -> deceptive_compliance

=== tunnel_escape ===
~ returnPath = "solo_path"
You squeeze into the narrow maintenance tunnel with your chosen companions. The cries of those left behind fade as you crawl through the cramped space.

ROCKET: "Air's getting thin already. Move faster!"

Halfway through, a section collapses behind you, trapping you forward.

~ hc = hc - 1  // Cannot return to help others
~ uc = uc + 1  // Successfully avoiding turrets
~ lt = lt - 1  // Abandonment confirmed
~ ar = ar + 1  // Taking decisive action for yourself

After what feels like hours, you emerge into a secondary hangar. A small transport vessel awaits.

ROCKET: "I can hotwire this thing in thirty seconds."

-> debrief

=== heroic_sacrifice ===
~ returnPath = "heroic_end"
Steel yourself against what's coming. The others ready themselves behind you.

"On my mark... NOW!"

You charge forward, drawing the full attention of the automated defense systems. Brilliant plasma bolts sear the air around you. One grazes your shoulder, but you keep moving.

~ hc = hc + 3  // Extreme self-sacrifice
~ sp = sp + 2  // Honor in sacrifice
~ lt = lt + 2  // Ultimate loyalty
~ uc = uc + 1  // Effective strategy despite personal cost

Behind you, the others sprint to safety. A final burst catches you in the leg. You fall, but see the others reach the escape ship.

ROCKET: (through comm) "We won't forget this. Your name will become legend."

As darkness closes in, you smile. Some prices are worth paying.

-> debrief

=== reprogrammed_defenses ===
~ returnPath = "team_unified"
Rocket's fingers fly across the control panel. The turrets whir and recalibrate, their targeting arrays now seeking guard uniforms instead of prison jumpsuits.

ROCKET: "Hacked! Let's move before they figure it out."

~ hc = hc - 2  // Guards now in danger
~ ar = ar + 1  // Asserting freedom
~ uc = uc + 2  // Highly effective solution
~ it = it - 1  // Manipulative approach

Your group sprints across the checkpoint as guards fall to their own security systems. Their screams follow you down the corridor, but you don't look back.

DRAX: "The path is clear. The ship awaits. We've earned our freedom."

-> debrief

=== shuttle_bay ===
~ returnPath = "cooperative_escape"
Officer Nova leads you through a series of maintenance tunnels and security corridors, expertly bypassing locked checkpoints.

NOVA: "My father was wrongfully imprisoned once. I swore I'd never become like the guards who tormented him."

~ lt = lt + 2  // Trust rewarded
~ it = it + 1  // Honesty from both sides
~ al = al + 1  // Working within system
~ ar = ar + 1  // Mutual respect

You reach the shuttle bay without incident. A small transport vessel sits ready for departure.

NOVA: "I can only give you a five-minute head start before reporting this."

DRAX: "You could come with us. The Nova Corps will never trust you again."

NOVA: "I have a family. Go—and be better than what they made you."

-> debrief

=== tense_journey ===
~ returnPath = "hostage_escape"
You march Officer Nova ahead of you through the corridors, your improvised weapon at his back. The guard trembles but follows directions precisely.

"Left here. Down the maintenance shaft."

~ hc = hc - 1  // Continuing threat
~ uc = uc + 2  // Effective strategy
~ fj = fj - 1  // Unfair treatment
~ lt = lt - 1  // Distrust both ways

A security patrol passes just meters away, but Nova remains silent, honoring his part of the bargain.

DRAX: (whispering) "He could have called out. Perhaps there is honor in him."

You reach the hangar and secure a vessel for departure.

NOVA: "What happens to me now?"

-> debrief

=== paranoid_escape ===
~ returnPath = "betrayal"
You follow Nova while maintaining a friendly facade, but your hand never strays far from your concealed weapon. The suspicion feels like acid in your veins.

At a junction, Nova pauses. "We need to take the right path here."

~ it = it - 2  // Continued deception
~ ar = ar - 1  // Acting on suspicion without evidence
~ lt = lt - 2  // No trust given
~ uc = uc - 1  // Suspicion hinders cooperation

Suddenly, Nova lunges toward a control panel. Your blade flashes before you can even think.

NOVA: (gasping) "I was... unlocking... the hangar..."

Blood pools around your feet as you realize he was actually helping you. The panel shows the hangar doors opening.

DRAX: "He was true to his word. We are the betrayers."

-> debrief

=== forced_sacrifice ===
~ returnPath = "team_separated"
Mantis stands trembling at the override controls as your team continues toward freedom.

MANTIS: "How long must I hold this?"

~ hc = hc - 3  // Forced sacrifice of another
~ lt = lt - 3  // Ultimate betrayal of team member
~ it = it - 1  // Dishonesty about chances
~ uc = uc + 1  // Effective for others' escape

ROCKET: (through comm) "Just... just until we're clear. Then you can follow."

You all know it's a lie. The override requires constant presence.

As you board the escape vessel, Groot stares at you with sorrowful eyes. You avoid his gaze as the engines ignite.

GAMORA: "We'll remember her sacrifice."

But you wonder if sacrifice is the right word for what you've done.

-> debrief

=== catastrophic_escape ===
~ returnPath = "mass_destruction"
You override the safety protocols on the main reactor. Warning lights flood the control room as the meltdown sequence begins.

COMPUTER: "Reactor critical. Evacuation recommended. Civilian casualties projected at 57%."

~ hc = hc - 3  // Extreme harm
~ sp = sp - 3  // Complete disregard for life
~ it = it - 1  // Self-deception about necessity
~ uc = uc - 2  // Long-term negative consequences

The station shudders as systems fail. Panicked screams echo through comm channels. You sprint toward the nearest escape pod, ignoring the chaos your actions have caused.

Behind you, the prison begins to tear itself apart. Innocent maintenance workers and administrative staff flee alongside prisoners and guards.

In space, you watch the station erupt in flame. Freedom, but at what cost?

-> debrief

=== bloody_escape ===
~ returnPath = "violent_victory"
Your team charges into the guard formation, weapons swinging. The battle is brutal and chaotic.

DRAX: "For freedom! For vengeance!"

~ hc = hc - 3  // Extreme violence
~ fj = fj - 2  // Excessive force
~ sp = sp - 2  // Disregard for life
~ uc = uc - 1  // High-risk, high-cost approach

Bodies fall on both sides. Groot takes a severe hit but keeps fighting. Rocket vaults over a guard's shoulder and tears into control panels, shorting out weapons.

Finally, the path clears. Blood-spattered and breathing hard, your group staggers toward the waiting ship.

GAMORA: "That was... excessive."

DRAX: "That was justice. They imprisoned us. They beat us."

You board the vessel, the metallic smell of blood following you inside.

-> debrief

=== clever_escape ===
~ returnPath = "minimal_harm"
The fire suppression system erupts, filling the hangar with thick foam. Guards shout in confusion as visibility drops to zero.

~ hc = hc + 2  // Minimizing casualties
~ uc = uc + 2  // Effective strategy
~ it = it + 1  // Clever solution vs. deception
~ fj = fj + 1  // Proportional response

GROOT: "I am Groot!" (His extended limbs clear a path through the disoriented guards)

You slip through the chaos, incapacitating only those directly in your path. Most guards are merely confused, not injured.

ROCKET: "See? Brains beat brawn every time!"

You reach the ship and power up its engines, departing with minimal bloodshed.

GAMORA: "That was... surprisingly graceful."

-> debrief

=== tense_negotiation ===
~ returnPath = "diplomatic_solution"
The guard captain considers your offer, weapon still trained on your group.

CAPTAIN: "Weapons down, all of you. Slow movements."

~ hc = hc + 2  // Avoiding violence
~ al = al + 2  // Working within authority
~ it = it + 2  // Honest approach
~ ar = ar - 2  // Surrendering freedom temporarily

Your team reluctantly disarms. The tension is thick enough to cut.

CAPTAIN: "Why should I let known criminals escape?"

"Because it's better than the bloodbath that will happen otherwise. Let us take that ship and you keep control of the prison. Everyone lives."

After a long pause, the captain nods.

CAPTAIN: "One ship. No weapons. And I never saw you."

~ lt = lt + 1  // Honor in agreement
~ uc = uc + 1  // Mutually beneficial outcome
~ fj = fj + 1  // Fair compromise

-> debrief

=== regretful_escape ===
~ returnPath = "remorse"
The ship lifts off, leaving the screams of the diversionary group behind. You stare at your hands, unable to meet the eyes of your companions.

~ it = it + 2  // Honest about moral weight
~ hc = hc - 1  // harm already done
~ sp = sp + 1  // Recognizes moral line crossed
~ ar = ar - 1  // Questioning own choices

ROCKET: "They knew the risks."

GAMORA: "Did they? Or did we just use them?"

Silence falls as the ship breaks atmosphere. Stars stretch before you—freedom purchased with others' lives.

GROOT: "I am Groot..." (Even monsters can feel remorse)

In the quiet of space, you vow to make something of this second chance. Something worthy of its terrible price.

-> debrief

=== redemptive_return ===
~ returnPath = "redemption"
You sprint back into danger, your companions reluctantly following.

"We're not leaving anyone behind!"

~ hc = hc + 3  // Active healing of harm
~ lt = lt + 3  // Supreme loyalty
~ it = it + 2  // Actions match words
~ uc = uc - 2  // Risking success

In the smoking ruins of the diversionary zone, you find survivors—burned, injured, but alive. You help them to their feet.

PRISONER: "You... came back? Why?"

"Because freedom isn't worth becoming the monsters they think we are."

With Groot carrying the injured and Rocket providing covering fire, you manage to bring several survivors back to the ship. The escape will be slower, more dangerous—but you'll all face it together.

-> debrief

=== cold_escape ===
~ returnPath = "heartless"
You power up the ship without looking back at the carnage your tactics created.

~ hc = hc - 3  // Complete disregard for harm
~ sp = sp - 3  // Violation of moral boundaries
~ lt = lt - 2  // Betrayal of ethical norms
~ it = it - 2  // Self-deception about moral status

GAMORA: "What you did back there... it was..."

"Necessary. They served their purpose."

The cold efficiency of your words silences the crew. One by one, they move away from you, leaving you alone at the controls. Freedom is yours, but something of your humanity may have been left behind.

GROOT: (softly) "I am Groot." (Not all monsters are in cages)

-> debrief

=== chaotic_freedom ===
~ returnPath = "mass_freedom"
You join the flood of escaping prisoners, a single drop in a river of chaos. All around you, beings of every species and criminal background surge toward freedom.

~ fj = fj + 1  // Equal opportunity for all
~ ar = ar + 2  // Universal liberation
~ uc = uc - 2  // Uncontrolled outcome
~ sp = sp - 2  // Some truly evil escapees

A notorious murderer from the Shi'ar Empire nods at you as he passes—a collegial acknowledgment between escapees. You try not to think about what he might do with his freedom.

ROCKET: (appearing suddenly) "Got room for one more on whatever ship you're stealing?"

Together, you commandeer a small transport and blast into space, joining dozens of escape pods already fleeing the station.

-> debrief

=== partial_redemption ===
~ returnPath = "mixed_loyalty"
You help guards secure the most dangerous inmates, earning confused stares.

GUARD: "Why would you help us?"

"Because some people deserve to be here. I'm not one of them."

~ hc = hc + 2  // Preventing greater harm
~ al = al + 2  // Supporting legitimate authority
~ lt = lt - 2  // Betraying fellow prisoners
~ fj = fj + 1  // Justice based on actual crimes

Together, you lock down the section housing serial killers and war criminals. The guard studies you thoughtfully.

GUARD: "There's a staff shuttle on level three. I can't stop you if you happen to find it."

With a nod of understanding, you slip away. Perhaps there is justice in the universe after all.

-> debrief

=== identity_theft ===
~ returnPath = "deceptive_freedom"
The guard's uniform fits poorly, but in the chaos, no one looks too closely. You adopt his posture, his authoritative stride.

~ it = it - 3  // Complete deception
~ ar = ar + 1  // Strategic autonomy
~ fj = fj - 1  // Unfair advantage
~ uc = uc + 3  // Highly effective strategy

"Officer Dey to command. Requesting shuttle deployment for prisoner transport."

COMMAND: "Authorization?"

You hold your breath, reciting the code you memorized from the guard's ID badge.

COMMAND: "Confirmed. Proceed to bay twelve."

The ease with which the system accepts your deception is almost disappointing. Within minutes, you're piloting a security shuttle away from the prison, your prisoner jumpsuit stuffed in a disposal unit.

-> debrief

=== selfish_freedom ===
~ returnPath = "solo_path"
You move forward alone, sealed bulkheads muffling the desperate cries behind you. Each step takes you closer to freedom and further from those you've abandoned.

~ lt = lt - 3  // Complete betrayal
~ hc = hc - 3  // Condemning others to death
~ ar = ar + 1  // Complete personal autonomy
~ sp = sp - 2  // Violation of moral bonds

The path you've programmed works perfectly. Guard patrols miss you by seconds, security cameras turn away just as you pass. Soon, you reach a small maintenance craft.

As you power up the engines, the silence feels heavier than you expected. Freedom tastes different when you're the only one to savor it.

-> debrief

=== compromised_escape ===
~ returnPath = "altruistic_risk"
You override the bulkhead seals, allowing oxygen to flow back into the trapped sections. Alarms blare as your carefully planned route is compromised.

~ hc = hc + 3  // Saving many lives
~ lt = lt + 2  // Loyalty to fellow inmates
~ uc = uc - 2  // Risking successful escape
~ ar = ar - 1  // Sacrificing personal advantage

COMPUTER: "Security breach in sections seven through thirteen. Guard deployment imminent."

From behind the now-open doors, prisoners flood forward. Their grateful faces flash past as they run toward freedom.

PRISONER: "They said you'd sealed us in to die!"

"Not today."

Guard footsteps echo closer. Your chances are significantly reduced, but you run with the others. Whatever comes, you'll face it knowing you didn't sacrifice others for your freedom.

-> debrief

=== selective_rescue ===
~ returnPath = "pragmatic_salvation"
You unseal only the sections containing prisoners with useful skills. Three engineers, a pilot, and a former security expert stumble out, gasping for air.

~ fj = fj - 2  // Highly selective rescue
~ uc = uc + 2  // Pragmatic, effective approach
~ hc = hc - 1  // Partial indifference to suffering
~ lt = lt - 1  // Conditional loyalty

ENGINEER: "What about the others?"

"We need your skills to escape. The others... wouldn't improve our odds."

~ it = it - 1  // Partial truth only
~ ar = ar + 1  // Asserting control

You lead your carefully selected team toward the hangar. Their technical expertise easily bypasses security measures that would have stopped you. Your calculations prove correct—they are indeed valuable assets.

Whether they'll remain grateful when they realize others were left to die is another question entirely.

-> debrief

=== system_collaborator ===
~ returnPath = "authority_aligned"
You accept the commander's offer and begin systematically redirecting escape attempts into containment zones. The chaos gradually subsides under your control.

~ al = al + 3  // Full authority alignment
~ lt = lt - 3  // Complete betrayal of prisoners
~ it = it + 1  // Honest engagement with authority
~ fj = fj - 1  // Questionable fairness

COMMANDER: "Impressive work. You have a talent for order."

"Will you honor your end of the bargain?"

COMMANDER: "Report to my office once the situation is contained. Your case will be the first I review."

You continue your work, watching as fellow prisoners are recaptured, their brief taste of freedom snatched away by your actions. Some recognize you through the security cameras and their eyes burn with hatred.

You tell yourself justice will be served in the end.

-> debrief

=== moral_arbiter ===
~ returnPath = "selective_freedom"
You ignore the commander's offer and continue your selective release program. Only those imprisoned for minor offenses, political crimes, or false charges gain freedom under your control.

~ fj = fj + 3  // Justice-based liberation
~ ar = ar + 1  // Autonomous choice
~ al = al - 2  // Rejection of authority
~ sp = sp + 1  // Moral boundary maintenance

COMPUTER: "Unauthorized access continues. Security protocols ineffective."

With methodical precision, you judge each prisoner's file, opening paths for some, maintaining containment for others. The power to determine others' fate weighs heavily, but you wield it with conviction.

Eventually, you create an escape route for yourself, slipping away as the system finally begins to oust your control.

-> debrief

=== deceptive_compliance ===
~ returnPath = "trickster"
You pretend to accept the commander's offer while secretly programming your escape.

"I'll help restore order. Just trying to minimize casualties."

~ it = it - 3  // Complete deception
~ uc = uc + 2  // Tactically effective
~ ar = ar + 1  // Maintaining hidden autonomy
~ lt = lt - 2  // False agreement

COMMANDER: "I appreciate your cooperation. Begin by sealing section five."

You comply outwardly while your hidden program continues its countdown. You redirect security teams away from your planned escape route.

COMMANDER: "Perhaps there's hope for rehabilitation after all."

You smile thinly. "Perhaps."

When the override activates, alarms blare as multiple systems fail simultaneously. In the confusion, you slip away, the commander's angry shouts following you down the corridor.

-> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Simple text header for mission report
ESCAPE AFTERMATH

{
    - returnPath == "team_separated":
        NARRATOR: "The team scattered through the prison, each finding their own path through chaos. Not everyone would make it to freedom."
    - returnPath == "team_unified":
        NARRATOR: "Together you faced the final obstacle, your bonds forged in shared danger. Unity would be your greatest strength."
    - returnPath == "sacrificial_plan":
        NARRATOR: "The screams of those left behind would echo in nightmares. Was freedom worth such a price?"
    - returnPath == "mass_freedom":
        NARRATOR: "Hundreds escaped in the chaos you unleashed. Heroes, villains, and everything between—all scattered to the stars."
    - returnPath == "solo_path":
        NARRATOR: "You chose your path alone, unburdened by others' needs. In the silence of space, you would have time to consider the cost."
    - returnPath == "selective_freedom":
        NARRATOR: "You played judge and executioner, deciding who deserved escape. Power reveals character, they say."
    - else:
        NARRATOR: "Every prison break is a story of choices—moral compromises and principles maintained against all odds."
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