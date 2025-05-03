// ============================
// Spring Salvation
// A water resource engineer navigates cultural traditions and material needs
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
You are Dr. Maya Okafor, a water resource engineer deployed to the drought-stricken village of Keshat. The only reliable water source is an ancient spring on sacred grounds, jealously guarded by Elder Nara and her acolytes.

Three weeks into your assignment, the situation grows desperate. Children carry empty jugs up the long path daily, receiving only the minimal ceremonial allocation.

NARA: "The underground pipes the city proposes will desecrate the Source. The waters must flow as they have for a thousand years."

RAFIQ (city engineer): "Help me secure this permit, and we'll bring water to every doorstep within a month."

* [Persuade Nara to allow the pipes]
    ~ ar = ar + 1  // Respecting her authority through dialogue
    ~ sp = sp - 1  // Challenging sacred traditions
    ~ uc = uc + 2  // Practical water solution
    ~ it = it + 1  // Direct, honest approach
    
    You approach Nara's fire circle, joining the elders in evening ritual before making your case.
    
    YOU: "The faith that sustained this village can surely survive metal pipes. The gods wish for children to thrive."
    -> persuasion_attempt
    
* [Design alternative rain-catch system]
    ~ sp = sp + 2  // Respecting sacred boundaries
    ~ uc = uc - 1  // Less efficient solution
    ~ ar = ar + 2  // Honoring local authority
    ~ fj = fj + 1  // Equitable access without disturbing tradition
    
    "I respect your traditions. Let me design stone cisterns and rain-catch systems that leave the Source untouched."
    
    Nara nods appreciatively while Rafiq rolls his eyes behind her back.
    -> alternative_design
    
* [Conduct geological survey for secondary source]
    ~ uc = uc + 1  // Seeking additional solution
    ~ fj = fj + 2  // Creating new access without privileging anyone
    ~ it = it + 2  // Scientific integrity
    ~ hc = hc + 1  // Care without harm
    
    "Before disturbing sacred ground or building inadequate systems, let me survey for additional underground sources."
    
    Your equipment arrives from the capital as the village children watch with curiosity.
    -> geological_survey

=== persuasion_attempt ===
Nara listens to your argument with ancient eyes that have seen many outsiders come and go.

NARA: "Words are wind. If the spirits truly approve, you must prove it by walking the sacred tunnel beneath the spring. Barefoot, as pilgrims have for centuries."

Local whispers inform you the tunnel contains deadly sinkholes that have claimed lives.

* [Accept the dangerous challenge]
    ~ sp = sp + 1  // Respecting ritual requirements
    ~ hc = hc - 1  // Risk to personal safety
    ~ lt = lt + 2  // Building trust through sacrifice
    ~ al = al - 1  // Working outside official protocols
    
    "I accept your test, Elder. I will walk the tunnel at dawn."
    
    The villagers gather to witness as you remove your shoes at the tunnel entrance.
    -> sacred_tunnel
    
* [Propose a compromise ritual]
    ~ sp = sp - 1  // Modifying sacred practice
    ~ it = it + 1  // Honest about concerns
    ~ fj = fj + 1  // Seeking middle ground
    ~ ar = ar + 1  // Respect with boundaries
    
    "I honor your wisdom, but I propose a compromise—a ritual blessing of the pipes themselves before installation."
    
    Nara considers, her weathered face unreadable.
    -> negotiated_solution
    
* [Invoke government authority]
    ~ al = al + 2  // Leveraging official power
    ~ ar = ar - 3  // Disrespecting local authority
    ~ lt = lt - 2  // Breaking community trust
    ~ uc = uc + 1  // Efficient but forced solution
    
    "Elder Nara, while I respect your position, the Regional Water Authority has ultimate jurisdiction here."
    
    You present official documents. Nara's eyes flash with ancient anger.
    -> official_intervention

=== alternative_design ===
Over weeks, you train local craftspeople to build stone cisterns and roof catchment systems. Progress is slow, and the drought intensifies. Some villagers grow desperate.

VILLAGE WOMAN: "My children cry from thirst while we wait for rain that never comes."

One night, a fight erupts when guards catch villagers stealing from the spring. A young man is seriously injured.

* [Ask city for emergency water tankers]
    ~ hc = hc + 2  // Immediate care for suffering
    ~ uc = uc - 1  // Short-term solution
    ~ lt = lt - 1  // Partial admission of failure
    ~ al = al + 1  // Working within system
    
    "We need immediate relief while our systems develop. I'm requesting emergency tankers."
    
    Rafiq smirks as you make the call. "Finally seeing reason," he mutters.
    -> emergency_tankers
    
* [Double down on community effort]
    ~ lt = lt + 1  // Maintaining consistent approach
    ~ sp = sp + 1  // Respecting tradition through persistence
    ~ fj = fj + 1  // Equal sacrifice toward solution
    ~ hc = hc - 1  // Short-term continued hardship
    
    "This violence shows our desperation, but we're close to completion. If we all work double shifts, the first cisterns can be operational within days."
    
    The community rallies, though some families still struggle terribly.
    -> community_perseverance
    
* [Propose limited spring access compromise]
    ~ ar = ar + 1  // Respecting both sides
    ~ fj = fj + 2  // Balanced solution
    ~ it = it + 1  // Honest broker
    ~ uc = uc + 1  // Pragmatic interim solution
    
    "Elder Nara, while our systems complete, could we negotiate limited, respectful access to the spring for families with young children?"
    
    Nara's weathered face softens slightly at the mention of children.
    -> spiritual_compromise

=== geological_survey ===
Your surveys reveal promising signs of an aquifer half a kilometer from the village center. However, reaching it would require expensive deep drilling beyond your current budget.

RAFIQ: "The city will fund the drilling, but only if they can also install a monitoring station—with a permanent government presence in the village."

NARA: "Outside authority brings outside values. The city already takes our young people."

* [Accept city funding with conditions]
    ~ uc = uc + 2  // Securing water source
    ~ al = al + 1  // Working with authority
    ~ ar = ar - 1  // Some compromise of village autonomy
    ~ fj = fj + 1  // Negotiating fair terms
    
    "We'll accept funding but negotiate limited monitoring presence and local control of the well."
    
    Your proposal creates weeks of tense negotiations between village elders and city officials.
    -> negotiated_access
    
* [Seek international NGO funding]
    ~ lt = lt + 1  // Independent solution builds trust
    ~ ar = ar + 2  // Preserving village autonomy
    ~ uc = uc - 1  // Delayed implementation
    ~ fj = fj + 1  // Avoids unequal power dynamic
    
    "I have contacts with Water Without Borders. They can fund drilling without political strings attached."
    
    Your funding request enters the slow machinery of international aid.
    -> independent_funding
    
* [Organize village micro-loan system]
    ~ fj = fj + 2  // Community investment and ownership
    ~ ar = ar + 1  // Self-determination
    ~ lt = lt + 2  // Building internal trust
    ~ uc = uc - 2  // Significantly slower solution
    
    "This village can own its water future. I propose a micro-loan system where everyone invests what they can toward drilling costs."
    
    Your economic model requires tremendous community buy-in during extreme hardship.
    -> village_ownership

=== sacred_tunnel ===
~ returnPath = "traditional_respect"
The ancient tunnel stretches before you, dark and foreboding. Your bare feet feel the cool stone as you begin your journey. Water trickles around you.

Hours later, you emerge—bruised, bleeding, but alive. The village erupts in cheers.

NARA: "The spirits have spoken. They accept your iron veins if laid with proper reverence."

* [Install pipes with ceremonial blessing]
    ~ sp = sp + 2  // Integrating spiritual practice
    ~ uc = uc + 2  // Modern solution with acceptance
    ~ lt = lt + 2  // Fulfilled promise to all parties
    ~ hc = hc + 1  // Alleviating suffering
    
    Under Nara's guidance, each pipe section is blessed before installation. The village holds a three-day celebration when water first flows to all homes.
    
    Years later, pilgrims still come, though fewer in number.
    -> debrief
    
* [Offer technical training to young acolytes]
    ~ lt = lt + 1  // Building intergenerational trust
    ~ uc = uc + 1  // Sustainable knowledge transfer
    ~ sp = sp + 1  // Integrating tradition and innovation
    ~ ar = ar + 1  // Empowering next generation
    
    "Let me train some of your acolytes in water management. The sacred and technical can become one tradition."
    
    This cultural bridge ensures both spiritual practices and technical maintenance continue.
    -> debrief

=== negotiated_solution ===
~ returnPath = "balanced_approach"
Nara considers your compromise, consulting with her acolytes in lengthy whispered conversations.

NARA: "We will allow pipes—but they must follow the natural pathways of underground streams, and rituals must mark each stage of construction."

* [Accept these spiritual conditions]
    ~ sp = sp + 2  // Honoring spiritual framework
    ~ uc = uc + 1  // Modified but effective solution
    ~ fj = fj + 1  // Compromise serving all
    ~ lt = lt + 2  // Building trust through accommodation
    
    "We will design accordingly, following both the water's natural path and your spiritual guidance."
    
    The project takes longer and costs more, but proceeds with the blessing of all parties.
    -> debrief
    
* [Negotiate practical modifications]
    ~ it = it + 2  // Technical honesty
    ~ fj = fj + 1  // Finding fair middle ground
    ~ uc = uc + 1  // Optimizing practical outcome
    ~ sp = sp - 1  // Some compromise of spiritual ideals
    
    "I respect these conditions, but some technical adjustments will be necessary. Let's walk the proposed route together."
    
    Your careful explanations help Nara understand which spiritual requirements are physically possible.
    -> debrief

=== official_intervention ===
~ returnPath = "authoritarian_solution"
Government officials arrive within days. Nara and her acolytes stand in silent protest as surveyors mark the spring.

OFFICIAL: "The drought emergency gives us authority to proceed immediately."

* [Attempt to include ceremonial elements]
    ~ sp = sp + 1  // Preserving some spiritual aspects
    ~ lt = lt - 1  // Partial mitigation of trust breach
    ~ ar = ar - 1  // Limited respect after overriding
    ~ hc = hc + 1  // Reducing cultural harm
    
    "We should still incorporate blessing ceremonies. It costs us nothing and honors their tradition."
    
    Some ceremonial elements are grudgingly permitted, though Nara refuses to participate.
    -> debrief
    
* [Focus on technical efficiency]
    ~ uc = uc + 2  // Maximum technical efficiency
    ~ sp = sp - 3  // Complete disregard for spiritual concerns
    ~ lt = lt - 2  // Permanent trust damage
    ~ it = it - 1  // Avoidance of cultural truth
    
    "Let's proceed with standard protocols. The priority is getting water flowing as quickly as possible."
    
    The project completes in record time. Villagers use the water but avoid meeting your eyes.
    -> debrief

=== emergency_tankers ===
~ returnPath = "short_term_relief"
Water tankers arrive from the city, bringing immediate relief. Children drink deeply, gardens receive minimal irrigation, but long-term questions remain.

RAFIQ: "The tankers cost the city significantly. They're offering subsidized rates if the village agrees to a tourism development plan."

* [Advocate for the village's independence]
    ~ ar = ar + 2  // Defending local autonomy
    ~ fj = fj + 1  // Protecting vulnerable party
    ~ lt = lt + 1  // Loyalty to community
    ~ uc = uc - 1  // Potentially less economic benefit
    
    "This village needs water support without exploitative strings attached. I'll help negotiate better terms."
    
    Your advocacy strains your relationship with city officials but earns local respect.
    -> debrief
    
* [See opportunity in development]
    ~ uc = uc + 2  // Economic opportunity
    ~ sp = sp - 1  // Potential cultural dilution
    ~ ar = ar - 1  // External influence on local decisions
    ~ fj = fj - 1  // Unequal negotiating position
    
    "Thoughtful tourism could bring sustainable income while showcasing your cultural heritage."
    
    The village gradually transforms as visitors arrive to see the "authentic spiritual practices."
    -> debrief

=== community_perseverance ===
~ returnPath = "community_resilience"
Against tremendous odds, the village unites in round-the-clock labor. The first cisterns capture precious morning dew, and underground storage tanks are completed just as clouds finally gather.

NARA: "You honored our ways. Now the rains honor your work."

* [Document the system for other villages]
    ~ uc = uc + 2  // Expanding successful solution
    ~ it = it + 2  // Sharing knowledge honestly
    ~ fj = fj + 1  // Extending benefits to others
    ~ sp = sp + 1  // Respecting traditional approaches
    
    "This success deserves to be shared. With your permission, I'd like to create a manual for other communities."
    
    Your documentation becomes a model for culturally-respectful water development in the region.
    -> debrief
    
* [Accept village honorary membership]
    ~ lt = lt + 2  // Deep community connection
    ~ sp = sp + 2  // Embracing cultural traditions
    ~ ar = ar + 1  // Personal autonomy in alignment
    ~ al = al - 1  // Some distance from professional norms
    
    When the village offers to make you an honorary member, you accept, participating in the seasonal water blessing ceremony.
    
    Your professional boundaries blur as you become part of the community you serve.
    -> debrief

=== spiritual_compromise ===
~ returnPath = "adaptive_tradition"
Elder Nara contemplates your proposal, then nods slowly.

NARA: "The youngest may come at dawn. Mothers will learn the proper respect rituals. The Source must be honored."

* [Formalize the arrangement with respect]
    ~ sp = sp + 2  // Honoring spiritual practice
    ~ fj = fj + 2  // Meeting essential needs fairly
    ~ ar = ar + 1  // Respecting all perspectives
    ~ lt = lt + 1  // Building trust through compromise
    
    You help create a formal system where families learn traditional water prayers before receiving their allocation, while construction continues on permanent solutions.
    
    This bridge of respect prevents further violence while honoring tradition.
    -> debrief
    
* [Gradually increase permitted access]
    ~ uc = uc + 1  // Incremental practical improvement
    ~ it = it - 1  // Potentially deceptive approach
    ~ sp = sp - 1  // Slow erosion of tradition
    ~ fj = fj + 1  // Expanding access
    
    You quietly work to expand the definition of "emergency need" while accelerating cistern construction, gradually increasing spring access without confrontation.
    
    Traditions bend slowly rather than break.
    -> debrief

=== negotiated_access ===
~ returnPath = "political_compromise"
After tense negotiations, an agreement emerges: the city will fund drilling, with a small monitoring station staffed primarily by trained villagers.

RAFIQ: "The mayor isn't happy, but he's accepted the compromise."

* [Establish village water committee]
    ~ ar = ar + 2  // Local governance
    ~ fj = fj + 1  // Equitable representation
    ~ lt = lt + 1  // Institutional trust
    ~ al = al + 1  // Structured authority
    
    "To ensure village interests remain protected, we should establish a local water committee with real authority over operations."
    
    Your governance structure provides a buffer between city influence and village autonomy.
    -> debrief
    
* [Focus on technical implementation]
    ~ uc = uc + 2  // Efficient solution
    ~ it = it + 1  // Professional focus
    ~ sp = sp - 1  // Prioritizing material over cultural
    ~ hc = hc + 1  // Meeting basic needs
    
    "With the agreement signed, let's focus on getting this well operational before the drought worsens."
    
    The drilling begins immediately, with water flowing within weeks.
    -> debrief

=== independent_funding ===
~ returnPath = "autonomous_solution"
Three months later, Water Without Borders approves your grant. The village maintains independence from city control, though the wait has caused significant hardship.

* [Integrate spiritual elements into construction]
    ~ sp = sp + 3  // Full spiritual integration
    ~ lt = lt + 1  // Honoring all stakeholders
    ~ ar = ar + 1  // Respecting traditions
    ~ hc = hc + 1  // Both physical and cultural care
    
    "Elder Nara, will you help us design blessing ceremonies for each stage of the drilling?"
    
    The project becomes a unique fusion of modern technology and ancient reverence.
    -> debrief
    
* [Prioritize technical training]
    ~ uc = uc + 2  // Long-term sustainability
    ~ it = it + 1  // Technical integrity
    ~ ar = ar + 1  // Empowerment through knowledge
    ~ sp = sp - 1  // Emphasis on technical over spiritual
    
    "The most important element now is ensuring the village can maintain this system independently."
    
    Your technical training program creates local experts who won't need outside help.
    -> debrief

=== village_ownership ===
~ returnPath = "self_determination"
Against tremendous odds, the village microfinance system grows. Families contribute what little they can spare. After six months, drilling begins—fully owned by the community.

* [Create ceremonial ownership rituals]
    ~ sp = sp + 2  // Spiritual significance
    ~ lt = lt + 1  // Community cohesion
    ~ ar = ar + 1  // Cultural self-determination
    ~ fj = fj + 1  // Acknowledging all contributions
    
    "Every family that contributed should be acknowledged in a ceremony at the well site."
    
    The well becomes not just infrastructure, but a symbol of community achievement.
    -> debrief
    
* [Establish technical self-sufficiency]
    ~ uc = uc + 2  // Long-term independence
    ~ ar = ar + 2  // Complete autonomy
    ~ it = it + 1  // Knowledge empowerment
    ~ al = al - 1  // Distance from external systems
    
    "Let's ensure multiple villagers are fully trained in maintenance and repair, with a parts inventory that makes you completely self-sufficient."
    
    Your technical program ensures the village will never need to depend on outside expertise.
    -> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Display ethical choices narrative
PROJECT ASSESSMENT REPORT

{
    - returnPath == "traditional_respect":
        "By respecting traditional practices while implementing modern solutions, you navigated cultural and practical needs. The village now has reliable water access while maintaining its spiritual identity, though with some evolution of practices."
    - returnPath == "balanced_approach":
        "Your negotiated approach balanced respect for tradition with practical needs. While neither side got exactly what they wanted, the compromise created a sustainable solution that preserved essential cultural elements while meeting material requirements."
    - returnPath == "authoritarian_solution":
        "The implementation of water infrastructure through official channels achieved technical success at significant cultural cost. The village's relationship with both outside authorities and their own traditions has been permanently altered."
    - returnPath == "short_term_relief":
        "Emergency intervention prevented immediate suffering but created new dependencies and power dynamics. The village's water security came at the cost of economic and cultural autonomy in ways that continue to unfold."
    - returnPath == "community_resilience":
        "The village's self-reliance was strengthened through hardship and community effort. While the solution was slower and less technologically advanced, it created stronger social cohesion and cultural continuity."
    - returnPath == "adaptive_tradition":
        "Traditions evolved to meet urgent needs through respectful adaptation rather than replacement. This middle path preserved cultural continuity while acknowledging the necessity of change in response to environmental pressures."
    - returnPath == "political_compromise":
        "Navigating the complex interests of village, tradition, and city authorities resulted in a negotiated solution that secured water access while partially preserving autonomy, though with ongoing tensions between stakeholders."
    - returnPath == "autonomous_solution":
        "External support without political strings attached allowed the village to maintain independence while accessing modern technology. The longer timeline caused hardship but resulted in a solution free from unwanted influence."
    - returnPath == "self_determination":
        "Complete community ownership created not just water infrastructure but a profound sense of agency and achievement. The village emerged from crisis with stronger internal bonds and capacity for self-governance."
    - else:
        "Your approach to the water crisis balanced technical, cultural, and ethical considerations with complex outcomes for all stakeholders."
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