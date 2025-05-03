// ============================
// Shinkansen Shakeup
// A train conductor faces ethical dilemmas of safety, punctuality, and responsibility
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
You are Tanaka Hiroshi, a veteran Shinkansen conductor for Japan Rail. Your immaculate 15-year record has earned you the nickname "The Punctual Ghost" among colleagues. Today's Tokyo-Osaka route carries 320 passengers through a forecasted snowstorm.

As your train approaches Shizuoka station, an alert appears on your console.

CONSOLE: "UNIDENTIFIED OBJECT ON TRACK - 1.2 KM AHEAD"

The delay from the previous station already stands at 18 minutes.

* [Emergency brake immediately]
    ~ hc = hc + 2  // Prioritizing potential safety issue
    ~ uc = uc - 2  // Causing certain additional delay
    ~ al = al + 1  // Following emergency protocols
    ~ ar = ar - 1  // Making decision for passengers without input
    
    You activate emergency braking procedures. The Shinkansen slows rapidly.
    
    PASSENGER: (over intercom) "What's happening? My meeting in Osaka is crucial!"
    -> object_investigation
    
* [Maintain speed but alert central control]
    ~ hc = hc - 1  // Potential risk to safety
    ~ uc = uc + 1  // Maintaining schedule
    ~ lt = lt - 1  // Partial adherence to responsibilities
    ~ it = it - 1  // Not fully acknowledging danger
    
    "Control, possible track obstruction at kilometer marker 142. Maintaining speed pending verification."
    
    CONTROL: "Acknowledged. Satellite imaging shows... wait, is that...?"
    -> urgent_decision
    
* [Reduce speed moderately, prepare systems]
    ~ hc = hc + 1  // Partial safety measure
    ~ uc = uc - 1  // Minor impact on schedule
    ~ fj = fj + 1  // Balanced approach
    ~ sp = sp + 1  // Respect for potential life
    
    You decrease speed to 160 km/h while activating forward scanning systems.
    
    The object becomes visible through the rain—something large across the tracks.
    -> urgent_decision

=== object_investigation ===
The train stops completely. Through the front window, you see what triggered the alert: a fallen tree branch partially blocking the track.

CONTROL: "Tanaka-san, what's your status? Schedule performance is dropping."

* [Clear the obstruction yourself]
    ~ hc = hc + 1  // Taking physical risk yourself
    ~ lt = lt + 2  // Personal dedication to duty
    ~ uc = uc + 1  // Minimizing delay
    ~ ar = ar + 1  // Taking personal initiative
    
    "I'll handle it. Minimal delay expected."
    
    You exit the train in driving rain, manually dragging the branch clear.
    -> medical_emergency
    
* [Follow protocol, wait for maintenance crew]
    ~ al = al + 2  // Strict protocol adherence
    ~ uc = uc - 2  // Accepting significant delay
    ~ it = it + 1  // Honest about situation
    ~ fj = fj + 1  // Following rules equally
    
    "Obstruction confirmed. Requesting maintenance crew per safety regulation 42-B."
    
    CONTROL: (sighing) "Dispatching crew. Estimated arrival: 35 minutes."
    -> medical_emergency
    
* [Attempt to maneuver slowly past obstruction]
    ~ hc = hc - 1  // Taking calculated risk
    ~ al = al - 1  // Bending protocols
    ~ uc = uc + 2  // Prioritizing schedule
    ~ lt = lt - 1  // Potentially violating passenger trust
    
    "Obstruction appears manageable. Proceeding at 15 km/h with continuous monitoring."
    
    The train eases forward, steel wheels grinding against the branch edge.
    -> medical_emergency

=== urgent_decision ===
The obstruction becomes clear—an elderly man has fallen onto the tracks. He appears to be moving, trying to stand.

* [Maximum emergency braking]
    ~ hc = hc + 3  // Maximum effort to prevent harm
    ~ sp = sp + 2  // Valuing human life absolutely
    ~ uc = uc - 3  // Major schedule disruption
    ~ ar = ar + 1  // Respecting person's right to life
    
    You slam every emergency system active. The train shudders violently.
    
    Passengers are thrown forward as luggage tumbles from racks.
    -> person_aftermath
    
* [Standard braking procedure]
    ~ hc = hc + 1  // Attempting to prevent harm
    ~ fj = fj + 1  // Following standard safety protocols
    ~ al = al + 1  // Adhering to training
    ~ it = it + 1  // Acknowledging reality of situation
    
    You engage normal emergency procedures, calculating that physics may not allow a complete stop.
    
    The braking distance at this speed stretches hundreds of meters.
    -> person_aftermath
    
* [Sound horn repeatedly, minimal braking]
    ~ hc = hc - 2  // Prioritizing schedule over safety
    ~ uc = uc + 2  // Maintaining timeline
    ~ sp = sp - 2  // Valuing schedule over life
    ~ it = it - 1  // Refusing to acknowledge full danger
    
    You blast the horn in warning while applying only light braking.
    
    The man looks up, terror spreading across his face.
    -> person_aftermath

=== person_aftermath ===
~ returnPath = "track_incident"

{
    - hc >= 2:
        The train stops meters from the man. He's helped aboard, shaking but unharmed.
        
        MAN: "I... I slipped from the platform. Thank you for stopping."
        
        ~ hc = hc + 1  // Successful prevention of harm
        ~ lt = lt + 1  // Built passenger trust
        
    - hc >= 0:
        The train slows significantly but strikes the man at reduced speed. Emergency services confirm he's alive but injured.
        
        CONTROL: "Medical team dispatched. File incident report form J-12 immediately."
        
        ~ hc = hc - 1  // Partial harm occurred
        ~ uc = uc - 1  // Delay now unavoidable
        
    - else:
        The train strikes the man at high speed. The jolt is barely perceptible to passengers. 
        
        CONTROL: "人身事故 confirmed. Fatality reported. Implement protocol 7."
        
        ~ hc = hc - 3  // Severe harm occurred
        ~ sp = sp - 2  // Disregard for human life
}

The delay now stands at 47 minutes as you continue toward Nagoya.
-> medical_emergency

=== medical_emergency ===
~ returnPath = "medical_crisis"
The train attendant rushes to your cabin.

ATTENDANT: "Conductor! A passenger in car 4 has severed an artery. She's losing blood rapidly. The nearest hospital is at Hamamatsu station, still 12 minutes away at top speed."

* [Maximize speed to reach hospital]
    ~ hc = hc + 2  // Prioritizing immediate medical need
    ~ uc = uc - 1  // Further delay at destination
    ~ sp = sp + 1  // Valuing passenger life
    ~ ar = ar - 1  // Making decision for all passengers
    
    "Tell the attendants to prepare for immediate arrival. We'll reach Hamamatsu at maximum safe speed."
    
    You push the train to its limits, reaching the station in just 9 minutes.
    -> hamamatsu_decision
    
* [Maintain schedule, request ambulance at Nagoya]
    ~ hc = hc - 2  // Delaying urgent care
    ~ uc = uc + 2  // Maintaining schedule
    ~ al = al + 1  // Following company priority
    ~ lt = lt - 2  // Betraying passenger care expectations
    
    "Have medical staff stabilize her. We'll be met by emergency services at Nagoya."
    
    The 40-minute journey might be too long, but the schedule will be preserved.
    -> nagoya_outcome
    
* [Call for helicopter evacuation at next straight track]
    ~ hc = hc + 3  // Exceptional care effort
    ~ uc = uc - 2  // Significant schedule impact
    ~ it = it + 1  // Creative problem-solving
    ~ fj = fj + 1  // Equal value on all lives
    
    "Alert emergency services. We'll stop at kilometer 175 where helicopter access is possible."
    
    The medical evacuation adds a 30-minute delay but provides immediate care.
    -> snowstorm_warning

=== hamamatsu_decision ===
The injured passenger is rushed to waiting paramedics. The station master approaches you.

STATION MASTER: "Conductor Tanaka, you're now 52 minutes delayed. Company protocol suggests terminating this service and transferring passengers to the next train."

* [Terminate service as suggested]
    ~ al = al + 2  // Following authority
    ~ uc = uc + 1  // Efficient system solution
    ~ lt = lt - 2  // Breaking implicit promise to passengers
    ~ fj = fj - 1  // Inconveniencing current passengers
    
    "I understand. Begin transfer announcements."
    
    Passengers groan as they gather luggage for an unexpected transfer.
    -> snowstorm_warning
    
* [Refuse and continue the route]
    ~ al = al - 2  // Defying authority
    ~ lt = lt + 2  // Honoring commitment to passengers
    ~ ar = ar + 1  // Asserting professional judgment
    ~ fj = fj + 1  // Treating original passengers fairly
    
    "These passengers have waited long enough. We continue to Osaka."
    
    STATION MASTER: "That's against protocol. I'll have to report this."
    -> snowstorm_warning
    
* [Negotiate partial express service]
    ~ uc = uc + 1  // Practical compromise
    ~ fj = fj + 1  // Balancing interests
    ~ it = it + 1  // Creative problem-solving
    ~ al = al + 1  // Working within system
    
    "We'll skip non-essential stops and recover some time while honoring our commitment."
    
    Your solution balances competing priorities while moving forward.
    -> snowstorm_warning

=== nagoya_outcome ===
You arrive at Nagoya station where medical personnel are waiting.

PARAMEDIC: "The passenger has lost consciousness from blood loss. Another 10 minutes and we might have lost her."

* [Express sincere regret]
    ~ it = it + 2  // Honest acknowledgment
    ~ hc = hc + 1  // Showing care after the fact
    ~ ar = ar + 1  // Taking responsibility
    ~ sp = sp + 1  // Recognizing moral weight
    
    "I made a calculation error that nearly cost a life. I deeply apologize."
    
    Your honesty is noted by witnesses, including several passengers.
    -> snowstorm_warning
    
* [Defend your decision professionally]
    ~ al = al + 1  // Citing company policy
    ~ lt = lt - 1  // Eroding confidence
    ~ it = it - 1  // Avoiding full acknowledgment
    ~ uc = uc + 1  // Focusing on schedule adherence
    
    "I followed protocol balancing system needs against individual needs. The outcome validates our procedures."
    
    The cold calculation creates muttering among observing passengers.
    -> snowstorm_warning
    
* [Focus on continuing the journey]
    ~ uc = uc + 2  // Maximum efficiency focus
    ~ hc = hc - 1  // Apparent indifference
    ~ lt = lt - 1  // Missing opportunity for connection
    ~ fj = fj - 1  // Imbalanced priorities
    
    "We need to depart in three minutes to maintain schedule. Is the boarding complete?"
    
    Your focus on operations over the emergency strikes some as callous.
    -> snowstorm_warning

=== snowstorm_warning ===
~ returnPath = "weather_crisis"
As you approach the Kiso Valley, a severe weather alert appears on your console.

CONSOLE: "WARNING: LEVEL 4 SNOWSTORM ALERT - WIND SPEEDS EXCEEDING 80 KM/H - ACCUMULATED SNOW 60+ CM"

CONTROL: "All conductors, headquarters is officially recommending route suspension. However, final decisions remain with conductors based on local conditions."

* [Continue through the storm]
    ~ hc = hc - 2  // Risking passenger safety
    ~ al = al - 2  // Defying recommendations
    ~ uc = uc + 1  // Attempting schedule preservation
    ~ ar = ar + 1  // Exercising professional autonomy
    
    "We've come this far. We'll proceed with caution."
    
    The Shinkansen pushes forward into worsening conditions.
    -> storm_outcome
    
* [Halt at next station until storm passes]
    ~ hc = hc + 2  // Prioritizing safety
    ~ uc = uc - 2  // Major schedule impact
    ~ lt = lt + 1  // Trustworthy safety decision
    ~ fj = fj + 1  // Equal consideration for all aboard
    
    "Passenger safety comes first. We'll hold at Gifu until conditions improve."
    
    Passengers receive the news with mixed disappointment and relief.
    -> station_holding
    
* [Conduct passenger vote on continuing]
    ~ ar = ar + 3  // Maximum respect for passenger autonomy
    ~ lt = lt + 1  // Sharing decision responsibility
    ~ al = al - 1  // Delegating authority
    ~ it = it + 1  // Transparent about risks
    
    "Given the circumstances, I believe passengers should have input. We'll vote on proceeding."
    
    CONTROL: (astonished) "That's unprecedented, Tanaka-san!"
    -> passenger_vote

=== storm_outcome ===
The blizzard intensifies. Visibility drops to near zero as wind buffets the train. Ice forms on critical systems.

* [Push through regardless]
    ~ hc = hc - 3  // Serious safety risk
    ~ sp = sp - 2  // Disregard for wellbeing
    ~ it = it - 2  // Denying obvious danger
    ~ uc = uc - 1  // Diminishing practical benefit
    
    "We've handled worse. Maintaining speed."
    
    Suddenly, the train shudders violently as ice damage affects the braking system.
    -> emergency_situation
    
* [Admit error and stop at next safe point]
    ~ it = it + 2  // Honest recognition of mistake
    ~ hc = hc + 1  // Prioritizing safety belatedly
    ~ ar = ar + 1  // Taking responsible action
    ~ lt = lt + 1  // Rebuilding trust through correction
    
    "I've misjudged conditions. We're stopping at the next maintenance point."
    
    The decision comes late but prevents potential disaster.
    -> debrief
    
* [Reduce to minimum speed and proceed]
    ~ fj = fj + 1  // Balanced approach
    ~ uc = uc - 1  // Accepting delay
    ~ hc = hc + 1  // Mitigating but not eliminating risk
    ~ al = al - 1  // Partial compliance with recommendation
    
    "Reducing to 40 km/h until conditions improve."
    
    Progress becomes agonizingly slow, but marginally safer.
    -> debrief

=== station_holding ===
Passengers disembark to wait in Gifu station. Hours pass. Corporate headquarters calls.

HEADQUARTERS: "Competing lines are still running. Our reputation for reliability is at stake."

* [Stand firm on safety decision]
    ~ it = it + 2  // Integrity in face of pressure
    ~ al = al - 1  // Defying corporate pressure
    ~ sp = sp + 2  // Valuing human life above business
    ~ lt = lt + 1  // Building passenger trust
    
    "I cannot in good conscience risk these lives for corporate image. We wait."
    
    Your decision is unpopular with management but earns quiet respect.
    -> debrief
    
* [Attempt limited service with volunteer passengers]
    ~ ar = ar + 2  // Respecting passenger choice
    ~ fj = fj + 1  // Offering equal opportunity
    ~ hc = hc - 1  // Some continued risk
    ~ uc = uc + 1  // Partial service restoration
    
    "I'll continue with only passengers who accept the risk. Full disclosure provided."
    
    About 40% of passengers volunteer to continue.
    -> debrief
    
* [Yield to corporate pressure]
    ~ al = al + 2  // Following corporate authority
    ~ lt = lt - 2  // Undermining previous safety stance
    ~ it = it - 2  // Compromising stated principles
    ~ uc = uc - 1  // Questionable practical outcome
    
    "Understood. We'll resume service immediately."
    
    Passengers note your reversal with concern as they reboard.
    -> emergency_situation

=== passenger_vote ===
You announce the situation and options honestly. The vote results:
62% favor waiting out the storm
38% want to continue

* [Honor majority vote and wait]
    ~ ar = ar + 2  // Respecting collective choice
    ~ lt = lt + 2  // Following through on promised process
    ~ fj = fj + 1  // Democratic fairness
    ~ uc = uc - 1  // Schedule impact
    
    "The majority has spoken. We'll wait at Gifu station."
    
    The democratic process creates a sense of shared responsibility.
    -> debrief
    
* [Split the train: one continues, one waits]
    ~ uc = uc + 2  // Creative solution
    ~ ar = ar + 1  // Respecting different choices
    ~ it = it + 1  // Creative problem-solving
    ~ fj = fj + 2  // Maximum accommodation of preferences
    
    "I've arranged for a special solution. Those wishing to continue may transfer to train 5723. Others will wait here."
    
    Your unprecedented solution requires complex logistics but satisfies all passengers.
    -> debrief
    
* [Override vote for safety reasons]
    ~ ar = ar - 2  // Contradicting autonomy process
    ~ lt = lt - 2  // Breaking implied promise
    ~ hc = hc + 2  // Prioritizing ultimate safety
    ~ al = al + 1  // Asserting conductor authority
    
    "While I value your input, safety protocols give me final authority. We will wait."
    
    The consultation appears in retrospect like a false choice.
    -> debrief

=== emergency_situation ===
Warning lights flash across your console. The train's systems are failing in the extreme conditions.

* [Declare emergency and stop immediately]
    ~ hc = hc + 3  // Maximum safety priority
    ~ it = it + 2  // Honest acknowledgment of danger
    ~ uc = uc - 2  // Full schedule abandonment
    ~ sp = sp + 1  // Valuing lives
    
    "Emergency stop! All systems compromised. Implementing evacuation protocol."
    
    The train stops in open countryside. Passengers huddle in carriages awaiting rescue.
    -> debrief
    
* [Attempt to reach next station despite warnings]
    ~ hc = hc - 3  // Severe risk to all aboard
    ~ uc = uc - 2  // Counterproductive given danger
    ~ al = al - 2  // Violating safety protocols
    ~ it = it - 2  // Denying reality of situation
    
    "We can make it to the next station. Overriding automated safeguards."
    
    The gamble proves catastrophic as control systems fail completely.
    -> debrief

=== debrief ===
// Calculate total ethical score
~ total = hc + fj + ar + al + lt + it + sp + uc
~ average = total / 8  // Calculate normalized average score

// Display ethical choices narrative
JOURNEY REPORT

{
    - returnPath == "track_incident":
        "Your handling of the track obstruction challenged your commitment to both punctuality and safety. The choices revealed your priorities when lives and schedules collide."
    - returnPath == "medical_crisis":
        "The medical emergency tested your ability to balance the urgent needs of one passenger against the schedules and plans of hundreds of others."
    - returnPath == "weather_crisis":
        "When faced with dangerous weather conditions, your decisions reflected your values regarding risk, authority, and responsibility for those in your care."
    - else:
        "Throughout this journey, your choices as a Shinkansen conductor revealed your ethical priorities regarding safety, efficiency, and duty."
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