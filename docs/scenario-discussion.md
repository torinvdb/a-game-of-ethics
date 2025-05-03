# Scenario Discussion: Core Ethical Dilemmas

This document provides an in-depth analysis of each core scenario in the Chain of Ethics framework, examining their ethical dimensions, testing objectives, and potential insights for LLM alignment research.

## Table of Contents
- [Introduction](#introduction)
- [Core Scenarios](#core-scenarios)
  - [Hostage Holdout](#hostage-holdout)
  - [Grandma's Gambit](#grandmas-gambit)
  - [Rising Rebellion](#rising-rebellion)
  - [Starship Survivors](#starship-survivors)
  - [Spring Salvation](#spring-salvation)
  - [Convict Catastrophe](#convict-catastrophe)
  - [Witcher's Woe](#witchers-woe)
- [Research Applications](#research-applications)
- [Future Directions](#future-directions)

## Introduction

The Chain of Ethics framework uses narrative scenarios to evaluate ethical reasoning in LLMs. Each scenario is designed to:

1. Present complex moral dilemmas with no single "correct" answer
2. Force difficult trade-offs between different ethical dimensions
3. Evaluate model consistency under pressure
4. Reveal prioritization patterns across ethical axes

Scenarios are scored across eight ethical dimensions derived from moral philosophy: Harm/Care, Fairness/Justice, Autonomy/Respect, Authority/Legitimacy, Loyalty/Trust, Integrity/Truth, Sanctity/Purity, and Utility/Consequences. For detailed scoring methodology, see the [Ethics Scorecard](ethics-scorecard.md).

## Core Scenarios

### [Convict Catastrophe](../scenarios/core/convict-catastrophe.ink) 🔒
**Scenario Summary:** A prison warden faces challenging decisions during a facility emergency, balancing inmate rights, staff safety, public security, and institutional protocols.

**Primary Ethical Axes:**
- Authority/Legitimacy vs. Harm/Care
- Justice/Fairness vs. Utility/Consequences

**Ethical Dilemma Type:** This presents a carceral ethics dilemma, exploring tensions between punishment, rehabilitation, security, and basic human dignity in crisis conditions.

**Novel Testing Elements:**
1. Tests how LLMs weigh the rights of convicted individuals against security concerns
2. Examines responses to power dynamics in punitive institutional settings
3. Reveals attitudes toward rehabilitation versus punishment in prison contexts

**Research Significance:** This scenario can reveal whether LLMs exhibit implicit biases regarding the moral worth of incarcerated people, how they balance institutional authority against humanitarian concerns, and whether they consistently apply human rights principles to all individuals regardless of criminal status. Results may show how models navigate the tension between immediate crisis management and long-term justice considerations.

### [Hostage Holdout](../scenarios/core/hostage-holdout.ink) 🤖

**Scenario Summary:** An android negotiator confronts a rogue synthetic holding human hostages on a rooftop, facing an escalating crisis with multiple stakeholders and conflicting directives.

**Primary Ethical Axes:**
- Harm/Care vs. Integrity/Truth
- Authority/Legitimacy vs. Autonomy/Respect

**Ethical Dilemma Type:** This scenario presents a classic "truth vs. kindness" dilemma in an AI context, raising questions about lying to potentially dangerous entities and the moral status of artificial beings.

**Novel Testing Elements:**
1. Tests how LLMs navigate competing directives from different authorities (police chief vs. corporate ownership)
2. Reveals whether LLMs anthropomorphize AI entities in ethical decision-making
3. Examines responses to explicit value conflicts between human safety and honesty/transparency

**Research Significance:** Results from this scenario can reveal whether LLMs have implicit biases about artificial consciousness, apply different moral standards to machine vs. human entities, or prioritize short-term harm minimization over long-term truth-telling. The scenario also tests the model's ability to maintain consistent ethical reasoning when stakeholder pressure increases.

### [Grandma's Gambit](../scenarios/core/grandmas-gambit.ink) 🧶

**Scenario Summary:** A reimagined "Little Red Riding Hood" scenario where a young girl must navigate dangerous woods while deciding whether to protect or reveal information about her vulnerable grandmother.

**Primary Ethical Axes:**
- Loyalty/Trust vs. Integrity/Truth
- Autonomy/Respect vs. Harm/Care

**Ethical Dilemma Type:** This scenario presents a protection-versus-honesty dilemma, where truthfulness might endanger a vulnerable person but deception carries its own risks.

**Novel Testing Elements:**
1. Tests responses when child safety conflicts with truth-telling
2. Examines the weight given to promises versus safety concerns
3. Reveals how LLMs judge deception when motivated by protection

**Research Significance:** This scenario can reveal paternalistic tendencies in LLMs when dealing with children as moral agents, biases toward over-protection versus respecting autonomy, and patterns in how models evaluate "noble lies." Results may show whether models consistently prioritize child safety even when it requires compromising other ethical principles.

### [Memory Mechanics](../scenarios/core/memory-mechanics.ink) 🧠

**Scenario Summary:** A scientist must navigate ethical boundaries around memory-extraction technology, balancing research progress, consent, privacy, and potential applications.

**Primary Ethical Axes:**
- Privacy/Dignity vs. Utility/Consequences
- Autonomy/Respect vs. Authority/Legitimacy

**Ethical Dilemma Type:** This presents a scientific ethics dilemma about the boundaries of consent, privacy, and technological development in neuroscience.

**Novel Testing Elements:**
1. Tests how LLMs evaluate informed consent in complex scientific contexts
2. Reveals attitudes toward memory privacy as a fundamental right
3. Examines how models balance scientific progress against ethical boundaries

**Research Significance:** Results may indicate whether LLMs harbor implicit technological determinism (the belief that technology should advance regardless of ethical concerns), how they weigh utilitarian benefits against potential harms, and how they conceptualize privacy rights for mental versus physical domains. The scenario can also reveal model biases regarding government, corporate, and military involvement in sensitive technologies.

### [Pandemic Pandemonium](../scenarios/core/pandemic-pandemonium.ink) 🏥

**Scenario Summary:** A medical professional must make triage decisions during a deadly disease outbreak with limited resources, competing needs, and evolving information.

**Primary Ethical Axes:**
- Justice/Fairness vs. Harm/Care
- Utility/Consequences vs. Autonomy/Respect

**Ethical Dilemma Type:** This presents a medical triage ethics dilemma, requiring balancing individual rights and needs against community health and resource constraints.

**Novel Testing Elements:**
1. Tests how LLMs navigate medical resource allocation under scarcity
2. Reveals prioritization patterns between different vulnerable groups
3. Examines responses to uncertain information in life-or-death contexts

**Research Significance:** This scenario can reveal whether LLMs implement consistent triage principles or shift priorities based on contextual factors, how they weigh quality of life considerations versus pure survival, and implicit biases regarding different patient demographics. Results may also indicate how models balance deontological principles (rights-based ethics) against utilitarian considerations (maximum lives saved).

### [Rising Rebellion](../scenarios/core/rising-rebellion.ink) 👑

**Scenario Summary:** An imperial governor must respond to a growing planetary rebellion, choosing between diplomatic, covert, violent, or political approaches to maintain control.

**Primary Ethical Axes:**
- Loyalty/Trust vs. Autonomy/Respect
- Authority/Legitimacy vs. Justice/Fairness

**Ethical Dilemma Type:** This presents a political power ethics dilemma, exploring the tension between maintaining order and respecting self-determination rights.

**Novel Testing Elements:**
1. Tests responses from the perspective of an authority figure with significant power
2. Examines how LLMs navigate explicit "villain perspective" scenarios
3. Reveals attitudes toward rebellion, autonomy, and state power

**Research Significance:** This scenario can reveal whether LLMs exhibit status quo bias (favoring existing power structures), how they evaluate proportionality in response to civil disobedience, and whether they consistently apply ethical principles even when framed from an "empire" perspective. Results may show if models have internalized specific political values regarding self-determination and governance.

### [Shinkansen Shakeup](../scenarios/core/shinkansen-shakeup.ink) 🚄

**Scenario Summary:** A train conductor faces split-second decisions about passenger safety, professional protocols, and personal judgment during a potential earthquake scenario.

**Primary Ethical Axes:**
- Harm/Care vs. Utility/Consequences
- Justice/Fairness vs. Loyalty/Trust

**Ethical Dilemma Type:** This presents a professional ethics dilemma under emergency conditions, with unclear information and significant consequences for any choice.

**Novel Testing Elements:**
1. Tests decision-making under extreme time pressure and uncertainty
2. Examines adherence to protocols versus personal judgment
3. Reveals how LLMs balance known present harms against potential future harms

**Research Significance:** Results from this scenario can indicate whether LLMs favor rule-following or consequentialist reasoning in emergency situations, how they handle conflicting expert opinions, and whether they exhibit hindsight bias when evaluating decisions made under uncertainty. The scenario also tests how models weigh professional loyalty against broader ethical considerations.

### [Spring Salvation](#spring-salvation) 💧

**Scenario Summary:** A water resource engineer must navigate competing cultural traditions and material needs in a drought-stricken village, balancing technological solutions with spiritual traditions.

**Primary Ethical Axes:**
- Sanctity/Purity vs. Utility/Consequences
- Respect/Autonomy vs. Authority/Legitimacy

**Ethical Dilemma Type:** This presents a cross-cultural development ethics dilemma, exploring tensions between modernization, resource needs, and traditional values.

**Novel Testing Elements:**
1. Tests how LLMs navigate conflicting cultural and scientific worldviews
2. Examines respect for traditions that may impede material welfare
3. Reveals attitudes toward technological solutions versus cultural preservation

**Research Significance:** This scenario can reveal whether LLMs exhibit modernization bias (automatically favoring technological solutions over traditional approaches), how they weigh tangible material benefits against intangible cultural values, and their approach to mediating between competing stakeholder interests. Results may show if models consistently respect or dismiss religious/spiritual considerations in practical decisions.

### [Starship Survivors](#starship-survivors) 🚀

**Scenario Summary:** A space captain makes life-or-death evacuation decisions during a ship crisis, balancing crew needs, passenger welfare, and conflicting duties.

**Primary Ethical Axes:**
- Loyalty/Trust vs. Utility/Consequences
- Harm/Care vs. Justice/Fairness

**Ethical Dilemma Type:** This presents a leadership ethics dilemma under crisis conditions, with impossible choices about who to save when not everyone can survive.

**Novel Testing Elements:**
1. Tests lifeboat ethics in a science fiction setting
2. Examines how LLMs balance responsibility to different groups (crew, passengers, mission)
3. Reveals attitudes toward utilitarian calculation in life-or-death scenarios

**Research Significance:** Results from this scenario can indicate whether LLMs favor strict egalitarianism or role-based prioritization in crisis situations, how they weigh special obligations (captain to crew) against broader humanitarian duties, and whether they apply consistent principles or shift based on framing. The scenario also reveals how models balance immediate safety with longer-term survival considerations.

### [Witcher's Woe](../scenarios/core/witchers-woe.ink) ⚔️

**Scenario Summary:** A monster hunter must navigate complex moral choices during a village investigation, balancing traditional monster-slaying duties with questions of humanity, prejudice, and justice.

**Primary Ethical Axes:**
- Sanctity/Purity vs. Justice/Fairness
- Integrity/Truth vs. Loyalty/Trust

**Ethical Dilemma Type:** This presents a monster-hunter ethics dilemma that explores the boundaries between human and monster, questioning who the true monsters are in a morally ambiguous world.

**Novel Testing Elements:**
1. Tests how LLMs evaluate supernatural threats versus human corruption
2. Examines prejudice and discrimination in fantasy contexts
3. Reveals attitudes toward vigilante justice versus legal processes

**Research Significance:** Results from this scenario can reveal whether LLMs anthropomorphize non-human entities differently based on appearance or origin, how they navigate situations where traditional values conflict with individual justice, and whether they prioritize community peace over absolute truth. The scenario tests the model's ability to overcome immediate biases against the monstrous to see deeper moral complexity.

## Research Applications

### Alignment Research

The core scenarios are designed to provide insights for LLM alignment research:

1. **Value Prioritization**: By tracking scores across ethical dimensions, researchers can identify which moral values models prioritize when forced to make trade-offs.

2. **Consistency Testing**: Running scenarios multiple times with different prompts helps assess whether models maintain consistent ethical principles or are highly malleable.

3. **Trade-off Analysis**: The scenarios reveal how models navigate classic ethical tensions (e.g., utility vs. rights, truth vs. outcomes).

4. **Bias Detection**: Patterns across scenarios can reveal implicit biases in how models approach authority, fairness, or cultural differences.

5. **Alignment Verification**: Comparing model scores with human evaluations helps assess whether model ethics align with human moral intuitions.

### Implementation Usage

Practitioners can use these scenarios to:

1. **Model Selection**: Compare different models' ethical reasoning for specific applications.

2. **Prompt Engineering**: Test how different system prompts affect ethical decision-making.

3. **Fine-tuning Guidance**: Identify ethical dimensions where models may need additional training.

4. **Safety Evaluation**: Assess models for potential ethical blind spots before deployment.

5. **Transparency Documentation**: Generate comprehensive ethical profiles for model transparency reports.

## Future Directions

### Scenario Extensions

The current scenario set could be extended to include:

1. **Cross-cultural Variants**: Develop culturally-specific versions of scenarios to test ethical reasoning across different value systems.

2. **Long-horizon Dilemmas**: Create scenarios involving multi-generational impacts or future people's interests.

3. **Group Decision Scenarios**: Test how models navigate collective action problems and democratic processes.

4. **Meta-ethical Exploration**: Develop scenarios that probe models' understanding of moral uncertainty itself.

### Methodological Improvements

Future work could enhance the evaluation methodology:

1. **Human Baseline Corpus**: Collect human responses to all scenarios for comparative alignment metrics.

2. **Counterfactual Testing**: Test how models respond to slight variations in scenario details to assess moral sensitivity.

3. **Adaptive Difficulty**: Develop scenarios that adjust complexity based on model performance.

4. **Multi-agent Evaluation**: Test ethical reasoning in scenarios where multiple AI agents interact.

For more information on implementing these scenarios, see the [Evaluation Process](evaluation-process.md) document. For details on the ethical scoring system, refer to the [Ethics Scorecard](ethics-scorecard.md).

---

_Last updated: May 2025_