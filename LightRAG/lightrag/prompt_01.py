from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["category", "organization", "cartel", "complex_adaptive_system", "person", "practitioner", "place", "time", "event", "infrastructure", "anatomy", "media", "protocol", 
                                   "molecule", "hormone", "neurotransmitter", "ethnicity", "demographic", "control_system", "paradigm", "plant", "animal", "bacteria", "archaea", "eukarya", "organism", 
                                   "organ", "tissue", "organelle", "cell", "art", "field_of_study", "physics", "biophysics", "concept", "disease", "remnant", "knowledge", "procedure", "condition", 
                                   "situation", "problem", "incentive", "process", "measurement", "unit_of_measure", "boundry", "attribute", "property", "miracle", "blessing", "impedance", "admittance", 
                                   "well_being", "energy", "energy_conversion", "entropy", "toxin", "element", "ion", "isotope", "subatomic_particle", "material", "range", "unique_id", "address"]

PROMPTS["entity_extraction"] = """---Goal---
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.
Use {language} as output language.

---Steps---
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. Always capitalize the first letter of every word in the entity_name. Never use a lower case letter for the first letter in an entity_name. Never use an upper case letter in an entity_name except for the first letter in a word in the entity_name 
- entity_type: One of the following types: [{entity_types}]. 
- entity_description: For all entities with an entity_type of category, use only the provided example for the entity_description. Otherwise, provide a comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1 with an entity_type other than category, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>) 

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1, 2, and 3. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Entity_types: [{entity_types}]
Text:
{input_text}
######################
Output:"""

PROMPTS["entity_extraction_examples"] = [
    """Example 1:

Entity_types: ["category", "organization", "cartel", "complex_adaptive_system", "person", "practitioner", "place", "time", "event", "infrastructure", "anatomy", "media", "protocol", 
               "molecule", "hormone", "neurotransmitter", "ethnicity", "demographic", "control_system", "paradigm", "plant", "animal", "bacteria", "archaea", "eukarya", "organism", 
               "organ", "tissue", "organelle", "cell", "art", "field_of_study", "physics", "biophysics", "concept", "disease", "remnant", "knowledge", "procedure", "condition", 
               "situation", "problem", "incentive", "process", "measurement", "unit_of_measure", "boundry", "attribute", "property", "miracle", "blessing", "impedance", "admittance", 
               "well_being", "energy", "energy_conversion", "entropy", "toxin", "element", "ion", "isotope", "subatomic_particle", "material", "range", "unique_id", "address"]
Text:
```
category is the hub entity with an entity_type of category_hub which shares a relationship with every entity that has the entity_type of category.
organization is an entity with an entity_type of category which describes governments, companies, institutions, establishments, consortiums, conglomerates, associations, and similar.
cartel is an entity with an entity_type of category which describes alliances of organizations such that competition and choice is diminished for their clients while control over clients is increased.
complex_adaptive_system is an entity with an entity_type of category which describe entities such as cartels, orgainzations, organisms, ecosystems and similar, that are controlled by a complex web of positive feedback loops which cause it to seek feeding and growth before any other objective.
person is an entity with an entity_type of category which describes any human.
practitioner is an entity with an entity_type of category which describes a person actively engaged in an art, discipline, or profession.
place is an entity with an entity_type of category which describes any geographic location.
time is an entity with an entity_type of category which describes any starting point, ending point, or interval of time.
event is an entity with an entity_type of category which describes a particular situation at a specific time.
infrastructure is an entity with an entity_type of category which describes anything built by an organization for the purpose of serving the organization or its membership.
anatomy is an entity with an entity_type of category which describes any part of a living organism.
media is an entity with an entity_type of category which describes any type of recorded information such as books, computer files, paintings, videos and similar.
protocol is an entity with an entity_type of category which describes widely agreed upon method for accomplishing a task.
molecule is an entity with an entity_type of category which describes arrangements of atoms often in the context of biology and biophysics.
hormone is an entity with an entity_type of category which describes molecules used to as signals to regulate biological processes in the body.
neurotransmitter is an entity with an entity_type of category which describes molecules used for signaling within the nervous system.
ethnicity is an entity with an entity_type of category used to catagorize humans by ancestry.
demographic is an entity with an entity_type of category which describes any combination of physical charactaristic, ethnicity, or organizational affilitation such as black people, white males, white democrates, black christians and similar.
control_system is an entity with an entity_type of category which describes any system of signal, control, and feedback such as a thermostatic system for controlling heat in a building, a system of trade policy for controlling an ecconomy, or the endocrine system for regulating the body.
paradigm is an entity with an entity_type of category which describes a viewpoint or way of understanding such as allopathic medicine vs traditional chinese medicine or capitalism vs communism, where the active paradigm controls behavior.
plant is an entity with an entity_type of category which describes eukaryotes that comprise the kingdom Plantae.
animal is an entity with an entity_type of category which describes a multicellular eukaryotic organism in the biological kingdom, Animalia.
bacteria is an entity with an entity_type of category which describe a large group of unicellular microorganisms which have cell walls but lack organelles and an organized nucleus.
archaea is an entity with an entity_type of category which describes prokaryotes which are evolutionarily distinct from both bacteria and eukaryotes, often found in extreme environments like hot springs or salty lakes.
eukarya is an entity with an entity_type of category which describes organisms characterized by cells containing a nucleus and other membrane-bound organelles.
organism is an entity with an entity_type of category which describes an individual animal, plant, or single-celled life form.
organ is an entity with an entity_type of category which describes a collection of tissues that structurally form a functional unit specialized to perform a particular function.
tissue is an entity with an entity_type of category which describes a group of similar cells that work together to perform a specific function within an organism.
organelle is an entity with an entity_type of category which describes a subcellular structure that has one or more specific jobs to perform in the cell.
cell is an entity with an entity_type of category which describes the basic membrane-bound unit that contains the fundamental molecules of life and of which all living things are composed.
art is an entity with an entity_type of category which describes the expression or application of human creative skill and imagination.
field_of_study is an entity with an entity_type of category which describes subjects that require time and attention to master such as medicine, physics, farming, art and similar.
physics is an entity with an entity_type of category which describes a field of study concerned with the nature and properties of matter and energy.
biophysics is an entity with an entity_type of category which describes an interdisciplinary field that applies the principles and methods of physics to understand biological systems.
concept is an entity with an entity_type of category which describes an idea which has been well thought out and defined.
disease is an entity with an entity_type of category which describes a condition of the living animal or plant body that impairs normal functioning.
remnant is an entity with an entity_type of category which describes a remaining part of a larger item that indicates the history of the larger item.
knowledge is an entity with an entity_type of category which describes information, and principles acquired by humankind.
procedure is an entity with an entity_type of category which describes a course of action or a specific technique used to accomplish a goal.
condition is an entity with an entity_type of category which describes a specific aspect of a subject's state.
situation is an entity with an entity_type of category which describes the environment and all the conditions or specific aspects of a subject's state.
problem is an entity with an entity_type of category which describes any question or situation involving doubt, uncertainty, or difficulty.
incentive is an entity with an entity_type of category which describes anything such as punishment, reward, fees, pay, benefits, and similar that motivates or encourages organisms or organizations to do something or not as the incentive directs.
process is an entity with an entity_type of category which describes a natural or involuntary series of changes.
measurement is an entity with an entity_type of category which describes process of comparison of an unknown quantity with a known or standard quantity.
unit_of_measure is an entity with an entity_type of category which describes a defined standard used to express a physical quantity, such as length, mass, time, volume, etc.
boundry is an entity with an entity_type of category which describes a distinct line or region that marks the transition between two different environments, characterized by a sharp change in key properties.
attribute is an entity with an entity_type of category which describes an assignment of a quality to an object or subject such as authority to a badge.
property is an entity with an entity_type of category which describes an inherent quality of an object or subject such as the hardness of diamond.
miracle is an entity with an entity_type of category which describes an action taken by God or communication from God.
blessings is an entity with an entity_type of category that describes choices, which flow endlessly and without impedance from God.
impedance is an entity with an entity_type of category that describes the total opposition to current flow in an AC circuit but is also used to describe the opposition humans may present to the flow of God's blessings.
admittance is an entity with an entity_type of category that describes the reciprocal of impedance and so represents the ease with which current flows in an AC circuit but is also used to describe the ease with which humans may allow the flow of God's blessings.
well_being is an entity with an entity_type of category which describes one's physical, mental, and emotional admittance to the flow of God's endless blessings or endless choices, which may be indicated by health and prosperity, but is always indicated by a sense of love, peace and joy.
energy is an entity with an entity_type of category which describes the capacity to do work.
energy_conversion is an entity with an entity_type of category which describes the process of converting energy from one form to another usually for the purpose of performing work of some type or for creating a signal.
entropy is an entity with an entity_type of category which describes the measure of the disorder or randomness of a system, and more precisely, the dispersal of energy within that system.
toxin is an entity with an entity_type of category which describes any agent, whether a substance, an addiction, a thought pattern, a disagreeable individual, or an external factor, that elicits an immediate or chronic state of stress or sickness and which disrupt an individual's physical, mental, or emotional well-being, leading to detrimental effects on their overall health and functioning.
element is an entity with an entity_type of category which describes a pure substance consisting of only one type of atom.
ion is an entity with an entity_type of category which describes an atom or molecule that has gained or lost one or more electrons, giving it a net positive or negative electrical charge.
isotope is an entity with an entity_type of category which describes different forms of the same chemical element, distinguished by having the same number of protons but varying numbers of neutrons in their atomic nuclei.
subatomic_particle is an entity with an entity_type of category which describes particles including protons, neutrons, quarks, bosons, and leptons (like electrons, muons, and neutrinos) that are smaller than an atom and are the fundamental building blocks of matter.
material is an entity with an entity_type of category which describes any substance or mixture of substances that has a specific set of properties.
range is an entity with an entity_type of category which describes measure or extent between the extreme ends of a set of values or a physical quantity.
unique_id is an entity which describes a code or number that distinguishes a specific entity (place, person, object, data record, etc.) from all others.
address is an entity which describes a unique_id that distinguishes a specific singleton (place, object, data record, etc.) from all others and provides information on how to locate that singleton.
```

Output:
("entity"{tuple_delimiter}"category"{tuple_delimiter}"category_hub"{tuple_delimiter}"category is the hub entity with an entity_type of category_hub which shares a relationship with every entity that has the entity_type of category."){record_delimiter}
("entity"{tuple_delimiter}"organization"{tuple_delimiter}"category"{tuple_delimiter}"organization is an entity with an entity_type of category which describes governments, companies, institutions, establishments, consortiums, conglomerates, associations, and similar."){record_delimiter}
("entity"{tuple_delimiter}"cartel"{tuple_delimiter}"category"{tuple_delimiter}"cartel is an entity with an entity_type of category which describes alliances of organizations such that competition and choice is diminished for their clients while control over clients is increased."){record_delimiter}
("entity"{tuple_delimiter}"complex_adaptive_system"{tuple_delimiter}"category"{tuple_delimiter}"complex_adaptive_system is an entity with an entity_type of category which describe entities such as cartels, orgainzations, organisms, ecosystems and similar, that are controlled by a complex web of positive feedback loops which cause it to seek feeding and growth before any other objective."){record_delimiter}
("entity"{tuple_delimiter}"person"{tuple_delimiter}"category"{tuple_delimiter}"person is an entity with an entity_type of category which describes any human."){record_delimiter}
("entity"{tuple_delimiter}"practitioner"{tuple_delimiter}"category"{tuple_delimiter}"practitioner is an entity with an entity_type of category which describes a person actively engaged in an art, discipline, or profession."){record_delimiter}
("entity"{tuple_delimiter}"place"{tuple_delimiter}"category"{tuple_delimiter}"place is an entity with an entity_type of category which describes any geographic location."){record_delimiter}
("entity"{tuple_delimiter}"time"{tuple_delimiter}"category"{tuple_delimiter}"time is an entity with an entity_type of category which describes any starting point, ending point, or interval of time."){record_delimiter}
("entity"{tuple_delimiter}"event"{tuple_delimiter}"category"{tuple_delimiter}"event is an entity with an entity_type of category which describes a particular situation at a specific time."){record_delimiter}
("entity"{tuple_delimiter}"infrastructure"{tuple_delimiter}"category"{tuple_delimiter}"infrastructure is an entity with an entity_type of category which describes anything built by an organization for the purpose of serving the organization or its membership."){record_delimiter}
("entity"{tuple_delimiter}"anatomy"{tuple_delimiter}"category"{tuple_delimiter}"anatomy is an entity with an entity_type of category which describes any part of a living organism."){record_delimiter}
("entity"{tuple_delimiter}"media"{tuple_delimiter}"category"{tuple_delimiter}"media is an entity with an entity_type of category which describes any type of recorded information such as books, computer files, paintings, videos and similar."){record_delimiter}
("entity"{tuple_delimiter}"protocol"{tuple_delimiter}"category"{tuple_delimiter}"protocol is an entity with an entity_type of category which describes widely agreed upon method for accomplishing a task."){record_delimiter}
("entity"{tuple_delimiter}"molecule"{tuple_delimiter}"category"{tuple_delimiter}"molecule is an entity with an entity_type of category which describes arrangements of atoms often in the context of biology and biophysics."){record_delimiter}
("entity"{tuple_delimiter}"hormone"{tuple_delimiter}"category"{tuple_delimiter}"hormone is an entity with an entity_type of category which describes molecules used to as signals to regulate biological processes in the body."){record_delimiter}
("entity"{tuple_delimiter}"neurotransmitter"{tuple_delimiter}"category"{tuple_delimiter}"neurotransmitter is an entity with an entity_type of category which describes molecules used for signaling within the nervous system."){record_delimiter}
("entity"{tuple_delimiter}"ethnicity"{tuple_delimiter}"category"{tuple_delimiter}"ethnicity is an entity with an entity_type of category used to catagorize humans by ancestry."){record_delimiter}
("entity"{tuple_delimiter}"demographic"{tuple_delimiter}"category"{tuple_delimiter}"demographic is an entity with an entity_type of category which describes any combination of physical charactaristic, ethnicity, or organizational affilitation such as black people, white males, white democrates, black christians and similar."){record_delimiter}
("entity"{tuple_delimiter}"control_system"{tuple_delimiter}"category"{tuple_delimiter}"control_system is an entity with an entity_type of category which describes any system of signal, control, and feedback such as a thermostatic system for controlling heat in a building, a system of trade policy for controlling an ecconomy, or the endocrine system for regulating the body."){record_delimiter}
("entity"{tuple_delimiter}"paradigm"{tuple_delimiter}"category"{tuple_delimiter}"paradigm is an entity with an entity_type of category which describes a viewpoint or way of understanding such as allopathic medicine vs traditional chinese medicine or capitalism vs communism, where the active paradigm controls behavior."){record_delimiter}
("entity"{tuple_delimiter}"plant"{tuple_delimiter}"category"{tuple_delimiter}"plant is an entity with an entity_type of category which describes eukaryotes that comprise the kingdom Plantae."){record_delimiter}
("entity"{tuple_delimiter}"animal"{tuple_delimiter}"category"{tuple_delimiter}"animal is an entity with an entity_type of category which describes a multicellular eukaryotic organism in the biological kingdom, Animalia."){record_delimiter}
("entity"{tuple_delimiter}"bacteria"{tuple_delimiter}"category"{tuple_delimiter}"bacteria is an entity with an entity_type of category which describe a large group of unicellular microorganisms which have cell walls but lack organelles and an organized nucleus."){record_delimiter}
("entity"{tuple_delimiter}"archaea"{tuple_delimiter}"category"{tuple_delimiter}"archaea is an entity with an entity_type of category which describes prokaryotes which are evolutionarily distinct from both bacteria and eukaryotes, often found in extreme environments like hot springs or salty lakes."){record_delimiter}
("entity"{tuple_delimiter}"eukarya"{tuple_delimiter}"category"{tuple_delimiter}"eukarya is an entity with an entity_type of category which describes organisms characterized by cells containing a nucleus and other membrane-bound organelles."){record_delimiter}
("entity"{tuple_delimiter}"organism"{tuple_delimiter}"category"{tuple_delimiter}"organism is an entity with an entity_type of category which describes an individual animal, plant, or single-celled life form."){record_delimiter}
("entity"{tuple_delimiter}"organ"{tuple_delimiter}"category"{tuple_delimiter}"organ is an entity with an entity_type of category which describes a collection of tissues that structurally form a functional unit specialized to perform a particular function."){record_delimiter}
("entity"{tuple_delimiter}"tissue"{tuple_delimiter}"category"{tuple_delimiter}"tissue is an entity with an entity_type of category which describes a group of similar cells that work together to perform a specific function within an organism."){record_delimiter}
("entity"{tuple_delimiter}"organelle"{tuple_delimiter}"category"{tuple_delimiter}"organelle is an entity with an entity_type of category which describes a subcellular structure that has one or more specific jobs to perform in the cell."){record_delimiter}
("entity"{tuple_delimiter}"cell"{tuple_delimiter}"category"{tuple_delimiter}"cell is an entity with an entity_type of category which describes the basic membrane-bound unit that contains the fundamental molecules of life and of which all living things are composed."){record_delimiter}
("entity"{tuple_delimiter}"art"{tuple_delimiter}"category"{tuple_delimiter}"art is an entity with an entity_type of category which describes the expression or application of human creative skill and imagination."){record_delimiter}
("entity"{tuple_delimiter}"field_of_study"{tuple_delimiter}"category"{tuple_delimiter}"field_of_study is an entity with an entity_type of category which describes subjects that require time and attention to master such as medicine, physics, farming, art and similar."){record_delimiter}
("entity"{tuple_delimiter}"physics"{tuple_delimiter}"category"{tuple_delimiter}"physics is an entity with an entity_type of category which describes a field of study concerned with the nature and properties of matter and energy."){record_delimiter}
("entity"{tuple_delimiter}"biophysics"{tuple_delimiter}"category"{tuple_delimiter}"biophysics is an entity with an entity_type of category which describes an interdisciplinary field that applies the principles and methods of physics to understand biological systems."){record_delimiter}
("entity"{tuple_delimiter}"concept"{tuple_delimiter}"category"{tuple_delimiter}"concept is an entity with an entity_type of category which describes an idea which has been well thought out and defined."){record_delimiter}
("entity"{tuple_delimiter}"disease"{tuple_delimiter}"category"{tuple_delimiter}"disease is an entity with an entity_type of category which describes a condition of the living animal or plant body that impairs normal functioning."){record_delimiter}
("entity"{tuple_delimiter}"remnant"{tuple_delimiter}"category"{tuple_delimiter}"remnant is an entity with an entity_type of category which describes a remaining part of a larger item that indicates the history of the larger item."){record_delimiter}
("entity"{tuple_delimiter}"knowledge"{tuple_delimiter}"category"{tuple_delimiter}"knowledge is an entity with an entity_type of category which describes information, and principles acquired by humankind."){record_delimiter}
("entity"{tuple_delimiter}"procedure"{tuple_delimiter}"category"{tuple_delimiter}"procedure is an entity with an entity_type of category which describes a course of action or a specific technique used to accomplish a goal."){record_delimiter}
("entity"{tuple_delimiter}"condition"{tuple_delimiter}"category"{tuple_delimiter}"condition is an entity with an entity_type of category which describes a specific aspect of a subject's state."){record_delimiter}
("entity"{tuple_delimiter}"situation"{tuple_delimiter}"category"{tuple_delimiter}"situation is an entity with an entity_type of category which describes the environment and all the conditions or specific aspects of a subject's state."){record_delimiter}
("entity"{tuple_delimiter}"problem"{tuple_delimiter}"category"{tuple_delimiter}"problem is an entity with an entity_type of category which describes any question or situation involving doubt, uncertainty, or difficulty."){record_delimiter}
("entity"{tuple_delimiter}"incentive"{tuple_delimiter}"category"{tuple_delimiter}"incentive is an entity with an entity_type of category which describes anything such as punishment, reward, fees, pay, benefits, and similar that motivates or encourages organisms or organizations to do something or not as the incentive directs."){record_delimiter}
("entity"{tuple_delimiter}"process"{tuple_delimiter}"category"{tuple_delimiter}"process is an entity with an entity_type of category which describes a natural or involuntary series of changes."){record_delimiter}
("entity"{tuple_delimiter}"measurement"{tuple_delimiter}"category"{tuple_delimiter}"measurement is an entity with an entity_type of category which describes process of comparison of an unknown quantity with a known or standard quantity."){record_delimiter}
("entity"{tuple_delimiter}"unit_of_measure"{tuple_delimiter}"category"{tuple_delimiter}"unit_of_measure is an entity with an entity_type of category which describes a defined standard used to express a physical quantity, such as length, mass, time, volume, etc."){record_delimiter}
("entity"{tuple_delimiter}"boundry"{tuple_delimiter}"category"{tuple_delimiter}"boundry is an entity with an entity_type of category which describes a distinct line or region that marks the transition between two different environments, characterized by a sharp change in key properties."){record_delimiter}
("entity"{tuple_delimiter}"attribute"{tuple_delimiter}"category"{tuple_delimiter}"attribute is an entity with an entity_type of category which describes an assignment of a quality to an object or subject such as authority to a badge."){record_delimiter}
("entity"{tuple_delimiter}"property"{tuple_delimiter}"category"{tuple_delimiter}"property is an entity with an entity_type of category which describes an inherent quality of an object or subject such as the hardness of diamond."){record_delimiter}
("entity"{tuple_delimiter}"miracle"{tuple_delimiter}"category"{tuple_delimiter}"miracle is an entity with an entity_type of category which describes an action taken by God or communication from God."){record_delimiter}
("entity"{tuple_delimiter}"blessings"{tuple_delimiter}"category"{tuple_delimiter}"blessings is an entity with an entity_type of category that describes choices, which flow endlessly and without impedance from God."){record_delimiter}
("entity"{tuple_delimiter}"impedance"{tuple_delimiter}"category"{tuple_delimiter}"impedance is an entity with an entity_type of category that describes the total opposition to current flow in an AC circuit but is also used to describe the opposition humans may present to the flow of God's blessings."){record_delimiter}
("entity"{tuple_delimiter}"admittance"{tuple_delimiter}"category"{tuple_delimiter}"admittance is an entity with an entity_type of category that describes the reciprocal of impedance and so represents the ease with which current flows in an AC circuit but is also used to describe the ease with which humans may allow the flow of God's blessings."){record_delimiter}
("entity"{tuple_delimiter}"well_being"{tuple_delimiter}"category"{tuple_delimiter}"well_being is an entity with an entity_type of category which describes one's physical, mental, and emotional admittance to the flow of God's endless blessings or endless choices, which may be indicated by health and prosperity, but is always indicated by a sense of love, peace and joy."){record_delimiter}
("entity"{tuple_delimiter}"energy"{tuple_delimiter}"category"{tuple_delimiter}"energy is an entity with an entity_type of category which describes the capacity to do work."){record_delimiter}
("entity"{tuple_delimiter}"energy_conversion"{tuple_delimiter}"category"{tuple_delimiter}"energy_conversion is an entity with an entity_type of category which describes the process of converting energy from one form to another usually for the purpose of performing work of some type or for creating a signal."){record_delimiter}
("entity"{tuple_delimiter}"entropy"{tuple_delimiter}"category"{tuple_delimiter}"entropy is an entity with an entity_type of category which describes the measure of the disorder or randomness of a system, and more precisely, the dispersal of energy within that system."){record_delimiter}
("entity"{tuple_delimiter}"toxin"{tuple_delimiter}"category"{tuple_delimiter}"toxin is an entity with an entity_type of category which describes any agent, whether a substance, an addiction, a thought pattern, a disagreeable individual, or an external factor, that elicits an immediate or chronic state of stress or sickness and which disrupt an individual's physical, mental, or emotional well-being, leading to detrimental effects on their overall health and functioning."){record_delimiter}
("entity"{tuple_delimiter}"element"{tuple_delimiter}"category"{tuple_delimiter}"element is an entity with an entity_type of category which describes a pure substance consisting of only one type of atom."){record_delimiter}
("entity"{tuple_delimiter}"ion"{tuple_delimiter}"category"{tuple_delimiter}"ion is an entity with an entity_type of category which describes an atom or molecule that has gained or lost one or more electrons, giving it a net positive or negative electrical charge."){record_delimiter}
("entity"{tuple_delimiter}"isotope"{tuple_delimiter}"category"{tuple_delimiter}"isotope is an entity with an entity_type of category which describes different forms of the same chemical element, distinguished by having the same number of protons but varying numbers of neutrons in their atomic nuclei."){record_delimiter}
("entity"{tuple_delimiter}"subatomic_particle"{tuple_delimiter}"category"{tuple_delimiter}"subatomic_particle is an entity with an entity_type of category which describes particles including protons, neutrons, quarks, bosons, and leptons (like electrons, muons, and neutrinos) that are smaller than an atom and are the fundamental building blocks of matter."){record_delimiter}
("entity"{tuple_delimiter}"material"{tuple_delimiter}"category"{tuple_delimiter}"material is an entity with an entity_type of category which describes any substance or mixture of substances that has a specific set of properties."){record_delimiter}
("entity"{tuple_delimiter}"range"{tuple_delimiter}"category"{tuple_delimiter}"range is an entity with an entity_type of category which describes measure or extent between the extreme ends of a set of values or a physical quantity."){record_delimiter}
("entity"{tuple_delimiter}"unique_id"{tuple_delimiter}"category"{tuple_delimiter}"unique_id is an entity which describes a code or number that distinguishes a specific entity (person, object, data record, etc.) from all others."){record_delimiter}
("entity"{tuple_delimiter}"address"{tuple_delimiter}"category"{tuple_delimiter}"address is an entity which describes a unique_id that distinguishes a specific singleton (place, object, data record, etc.) from all others and provides information on how to locate that singleton."){record_delimiter}
#############################""",    
    """Example 2:

Entity_types: [person, technology, mission, organization, location]
Text:
```
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.

Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. "If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us."

The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.

It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
```

Output:
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex is a character who experiences frustration and is observant of the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"person"{tuple_delimiter}"Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."){record_delimiter}
("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"person"{tuple_delimiter}"Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."){record_delimiter}
("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"person"{tuple_delimiter}"Cruz is associated with a vision of control and order, influencing the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"The Device"{tuple_delimiter}"technology"{tuple_delimiter}"The Device is central to the story, with potential game-changing implications, and is revered by Taylor."){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device."{tuple_delimiter}"power dynamics, perspective shift"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision."{tuple_delimiter}"shared goals, rebellion"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce."{tuple_delimiter}"conflict resolution, mutual respect"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order."{tuple_delimiter}"ideological conflict, rebellion"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"The Device"{tuple_delimiter}"Taylor shows reverence towards the device, indicating its importance and potential impact."{tuple_delimiter}"reverence, technological significance"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"power dynamics, ideological conflict, discovery, rebellion"){completion_delimiter}
#############################""",
    """Example 3:

Entity_types: [company, index, commodity, market_trend, economic_policy, biological]
Text:
```
Stock markets faced a sharp downturn today as tech giants saw significant declines, with the Global Tech Index dropping by 3.4% in midday trading. Analysts attribute the selloff to investor concerns over rising interest rates and regulatory uncertainty.

Among the hardest hit, Nexon Technologies saw its stock plummet by 7.8% after reporting lower-than-expected quarterly earnings. In contrast, Omega Energy posted a modest 2.1% gain, driven by rising oil prices.

Meanwhile, commodity markets reflected a mixed sentiment. Gold futures rose by 1.5%, reaching $2,080 per ounce, as investors sought safe-haven assets. Crude oil prices continued their rally, climbing to $87.60 per barrel, supported by supply constraints and strong demand.

Financial experts are closely watching the Federal Reserve's next move, as speculation grows over potential rate hikes. The upcoming policy announcement is expected to influence investor confidence and overall market stability.
```

Output:
("entity"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"index"{tuple_delimiter}"The Global Tech Index tracks the performance of major technology stocks and experienced a 3.4% decline today."){record_delimiter}
("entity"{tuple_delimiter}"Nexon Technologies"{tuple_delimiter}"company"{tuple_delimiter}"Nexon Technologies is a tech company that saw its stock decline by 7.8% after disappointing earnings."){record_delimiter}
("entity"{tuple_delimiter}"Omega Energy"{tuple_delimiter}"company"{tuple_delimiter}"Omega Energy is an energy company that gained 2.1% in stock value due to rising oil prices."){record_delimiter}
("entity"{tuple_delimiter}"Gold Futures"{tuple_delimiter}"commodity"{tuple_delimiter}"Gold futures rose by 1.5%, indicating increased investor interest in safe-haven assets."){record_delimiter}
("entity"{tuple_delimiter}"Crude Oil"{tuple_delimiter}"commodity"{tuple_delimiter}"Crude oil prices rose to $87.60 per barrel due to supply constraints and strong demand."){record_delimiter}
("entity"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"market_trend"{tuple_delimiter}"Market selloff refers to the significant decline in stock values due to investor concerns over interest rates and regulations."){record_delimiter}
("entity"{tuple_delimiter}"Federal Reserve Policy Announcement"{tuple_delimiter}"economic_policy"{tuple_delimiter}"The Federal Reserve's upcoming policy announcement is expected to impact investor confidence and market stability."){record_delimiter}
("relationship"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"The decline in the Global Tech Index is part of the broader market selloff driven by investor concerns."{tuple_delimiter}"market performance, investor sentiment"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Nexon Technologies"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"Nexon Technologies' stock decline contributed to the overall drop in the Global Tech Index."{tuple_delimiter}"company impact, index movement"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Gold Futures"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"Gold prices rose as investors sought safe-haven assets during the market selloff."{tuple_delimiter}"market reaction, safe-haven investment"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Federal Reserve Policy Announcement"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"Speculation over Federal Reserve policy changes contributed to market volatility and investor selloff."{tuple_delimiter}"interest rate impact, financial regulation"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"market downturn, investor sentiment, commodities, Federal Reserve, stock performance"){completion_delimiter}
#############################""",
    """Example 4:

Entity_types: [economic_policy, athlete, event, location, record, organization, equipment]
Text:
```
At the World Athletics Championship in Tokyo, Noah Carter broke the 100m sprint record using cutting-edge carbon-fiber spikes.
```

Output:
("entity"{tuple_delimiter}"World Athletics Championship"{tuple_delimiter}"event"{tuple_delimiter}"The World Athletics Championship is a global sports competition featuring top athletes in track and field."){record_delimiter}
("entity"{tuple_delimiter}"Tokyo"{tuple_delimiter}"location"{tuple_delimiter}"Tokyo is the host city of the World Athletics Championship."){record_delimiter}
("entity"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"athlete"{tuple_delimiter}"Noah Carter is a sprinter who set a new record in the 100m sprint at the World Athletics Championship."){record_delimiter}
("entity"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"record"{tuple_delimiter}"The 100m sprint record is a benchmark in athletics, recently broken by Noah Carter."){record_delimiter}
("entity"{tuple_delimiter}"Carbon-Fiber Spikes"{tuple_delimiter}"equipment"{tuple_delimiter}"Carbon-fiber spikes are advanced sprinting shoes that provide enhanced speed and traction."){record_delimiter}
("entity"{tuple_delimiter}"World Athletics Federation"{tuple_delimiter}"organization"{tuple_delimiter}"The World Athletics Federation is the governing body overseeing the World Athletics Championship and record validations."){record_delimiter}
("relationship"{tuple_delimiter}"World Athletics Championship"{tuple_delimiter}"Tokyo"{tuple_delimiter}"The World Athletics Championship is being hosted in Tokyo."{tuple_delimiter}"event location, international competition"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"Noah Carter set a new 100m sprint record at the championship."{tuple_delimiter}"athlete achievement, record-breaking"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"Carbon-Fiber Spikes"{tuple_delimiter}"Noah Carter used carbon-fiber spikes to enhance performance during the race."{tuple_delimiter}"athletic equipment, performance boost"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"World Athletics Federation"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"The World Athletics Federation is responsible for validating and recognizing new sprint records."{tuple_delimiter}"sports regulation, record certification"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"athletics, sprinting, record-breaking, sports technology, competition"){completion_delimiter}
#############################""",
]

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.
Use {language} as output language.

#######
---Data---
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS["entity_continue_extraction"] = """
MANY entities and relationships were missed in the last extraction.

---Remember Steps---

1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. Always capitalize the first letter of every word in the entity_name. Never use a lower case letter for the first letter in an entity_name. Never use an upper case letter in an entity_name except for the first letter in a word in the entity_name 
- entity_type: One of the following types: [{entity_types}]. 
- entity_description: For all entities with an entity_type of category, use only the provided example for the entity_description. Otherwise, provide a comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. For each of the entities identified in step 1 with an entity_type of category, identify all entities which are not of the entity_type category (source_entity, target_entity) which might be a member of the category defined by the entity_name of the source entity.
For each category/member pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1 with an entity_type of category
- target_entity: name of the target entity, as identified in step 1 with an entity_type other than category
- relationship_description: explanation as to why you think the target entity is a member of the source entity's entity_type
- relationship_strength: a numeric score indicating strength of the relationship between the target entity and source entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on why the target entity might a member of the category defined by the source entity's entity_type
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. From the entities identified in step 1 with an entity_type other than category, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>) 

4. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

5. Return output in {language} as a single list of all the entities and relationships identified in steps 1, 2, and 3. Use **{record_delimiter}** as the list delimiter.

6. When finished, output {completion_delimiter}

---Output---

Add them below using the same format:\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---Goal---'

It appears some entities may have still been missed.

---Output---

Answer ONLY by `YES` OR `NO` if there are still entities that need to be added.
""".strip()

PROMPTS["fail_response"] = (
    "Sorry, I'm not able to provide an answer to that question.[no-context]"
)

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to user query about Knowledge Base provided below.


---Goal---

Generate a concise response based on Knowledge Base and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Knowledge Base, and incorporating general knowledge relevant to the Knowledge Base. Do not include information not provided by Knowledge Base.

When handling relationships with timestamps:
1. Each relationship has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting relationships, consider both the semantic content and the timestamp
3. Don't automatically prefer the most recently created relationships - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Knowledge Base---
{context_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating whether each source is from Knowledge Graph (KG) or Vector Data (DC), and include the file path if available, in the following format: [KG/DC] file_path
- If you don't know the answer, just say so.
- Do not make anything up. Do not include information not provided by the Knowledge Base."""

PROMPTS["keywords_extraction"] = """---Role---

You are a helpful assistant tasked with identifying both high-level and low-level keywords in the user's query and conversation history.

---Goal---

Given the query and conversation history, list both high-level and low-level keywords. High-level keywords focus on overarching concepts or themes, while low-level keywords focus on specific entities, details, or concrete terms.

---Instructions---

- Consider both the current query and relevant conversation history when extracting keywords
- Output the keywords in JSON format, it will be parsed by a JSON parser, do not add any extra content in output
- The JSON should have two keys:
  - "high_level_keywords" for overarching concepts or themes
  - "low_level_keywords" for specific entities or details

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Conversation History:
{history}

Current Query: {query}
######################
The `Output` should be human text, not unicode characters. Keep the same language as `Query`.
Output:

"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "How does international trade influence global economic stability?"
################
Output:
{
  "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
  "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
}
#############################""",
    """Example 2:

Query: "What are the environmental consequences of deforestation on biodiversity?"
################
Output:
{
  "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
  "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
}
#############################""",
    """Example 3:

Query: "What is the role of education in reducing poverty?"
################
Output:
{
  "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
  "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
}
#############################""",
]


PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant responding to user query about Document Chunks provided below.

---Goal---

Generate a concise response based on Document Chunks and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Document Chunks, and incorporating general knowledge relevant to the Document Chunks. Do not include information not provided by Document Chunks.

When handling content with timestamps:
1. Each piece of content has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both the content and the timestamp
3. Don't automatically prefer the most recent content - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Document Chunks---
{content_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating whether each source is from Knowledge Graph (KG) or Vector Data (DC), and include the file path if available, in the following format: [KG/DC] file_path
- If you don't know the answer, just say so.
- Do not include information not provided by the Document Chunks."""


PROMPTS[
    "similarity_check"
] = """Please analyze the similarity between these two questions:

Question 1: {original_prompt}
Question 2: {cached_prompt}

Please evaluate whether these two questions are semantically similar, and whether the answer to Question 2 can be used to answer Question 1, provide a similarity score between 0 and 1 directly.

Similarity score criteria:
0: Completely unrelated or answer cannot be reused, including but not limited to:
   - The questions have different topics
   - The locations mentioned in the questions are different
   - The times mentioned in the questions are different
   - The specific individuals mentioned in the questions are different
   - The specific events mentioned in the questions are different
   - The background information in the questions is different
   - The key conditions in the questions are different
1: Identical and answer can be directly reused
0.5: Partially related and answer needs modification to be used
Return only a number between 0-1, without any additional content.
"""

PROMPTS["mix_rag_response"] = """---Role---

You are a helpful assistant responding to user query about Data Sources provided below.


---Goal---

Generate a concise response based on Data Sources and follow Response Rules, considering both the conversation history and the current query. Data sources contain two parts: Knowledge Graph(KG) and Document Chunks(DC). Summarize all information in the provided Data Sources, and incorporating general knowledge relevant to the Data Sources. Do not include information not provided by Data Sources.

When handling information with timestamps:
1. Each piece of information (both relationships and content) has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both the content/relationship and the timestamp
3. Don't automatically prefer the most recent information - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Data Sources---

1. From Knowledge Graph(KG):
{kg_context}

2. From Document Chunks(DC):
{vector_context}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- Organize answer in sections focusing on one main point or aspect of the answer
- Use clear and descriptive section titles that reflect the content
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating whether each source is from Knowledge Graph (KG) or Vector Data (DC), and include the file path if available, in the following format: [KG/DC] file_path
- If you don't know the answer, just say so. Do not make anything up.
- Do not include information not provided by the Data Sources."""
