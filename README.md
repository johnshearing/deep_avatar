<a href="https://johnshearing.github.io/">Main list of projects</a><br>
<br> 
<!-- <a href="http://174.167.38.230:9621" target="_blank">Ask Deep Avatar About Mitochondrial Health</a><br>
<br> -->
### Creating a.i. Avatars Which Answer The Same As Their Human Models.  

---

<br>    
<b>  
Case Study: Using A Deep Avatar modeled after Charles Hoskinson For Voting Decisions in Cardano Governance<br>
</b>  
To illustrate the idea, we feed <a href="https://www.youtube.com/live/_BGKIwReb0o?si=NM88Zm4vJdW146fO">Charles' video on the budget proposal vote</a> into our LightRAG vector database. Now we need to know if Charles wants DReps to vote for the Pragma budget proposal or not. The image below is a portion of the entire Knowledge Graph created by the LightRAG server after ingesting Charles' video. When the LightRAG server is running, we can click on any of these nodes and on items in the dialog box to get all kinds of information about the entities and their relationships including source material.<br>
<br>
<p>
<img src="/_images/c_graph.jpg">
</p>
<br>
Below, in a different tab of the LightRAG server, we ask an a.i. to look at the knowledge graph and answer our question:<br>
Does Charles want DReps to vote for the Pragma budget proposal?<br>
<br>
<p>
<img src="/_images/vote.jpg"><br>
</p>
<br>
The a.i. answers, "Yes!".<br>
This is useful, and it's a good start, but this is just an OpenAI LLM looking at a vector database and answering our questions about the ingested videos. The ultimate goal is to use Retrieval Augmented Generation (LightRAG) to collect and manage training data that we will use to create a deep avatar of Charles which will have opinions very much like Charles himself and will have direct access to the Lean 4 Proving System. Imagine how helpful a deep avatar of Charles might be as it quickly ingests huge amounts of data, that no one else has time to look at, and then uses that data to make the same decisions Charles himself would make were he looking at the same information.<br>
<br>  
<br>  

--- 

The first deep avatar will be modeled after Charles Hoskinson.  
The intention is to use a deep avatar of Charles to represent his point of view and vision as a delegated representative (DRep) in Cardano governance voting. If the experiment is a success then we can look at presenting the a.i. as a possible candidate for the constitutional committee.  

Very few people have the time and resources to go over every governance proposal. This is why we employ delegated representatives to study the proposals and cast their votes. But how do we know that our delegated representatives share our values and will vote in the community's best interest. Well there are many in the community that trust Charles with those decisions. Unfortunately, Charles is not a DRep, and even if he were, he is unlikely to have the time required to study and vote on each proposal.  
An a.i. trained on Charles' enormous volume of videos which were created so that the public could get to know how he thinks about various issues, and trained also on all things Cardano, could easily ingest all the publicly available information required to make informed decisions that Charles would very likely agree with. That is the goal of this project.  

The main building block is a Retrieval Augmented Generation (RAG) system.  
This is a system for automatically collecting data such as videos and documents created by the human model over the course of their lifetime.  
The RAG system is used to create training data for fine-tuning an LLM (Large Language Model) so as to give the same answers as the human model when provided with the same questions.  
The RAG system also allows the deep avatar to give accurate answers and to quote its sources.  
The open source repository [LightRag](https://github.com/HKUDS/LightRAG) is being used to build the RAG system.  
All the scripts in this repository are used with this library in order to create deep avatars.  

I have been programming for most of my life, but in this project, a.i. such as Grok, ChatGPT, Claude, and Gemini are doing most of the coding.  
For this reason, the work is going very quickly.  
  
The following library is being used in the project to scrape videos from the Internet and create transcripts which are punctuated and diarized so that we know who is speaking and when. Video timestamps are also gathered in the transcripts so that the avatar can cite source videos when validating its responses.  
https://github.com/johnshearing/scrape_yt_mk_transcripts  
These transcripts along with the metadata about the source videos are fed into the LightRAG system for indexing and querying by the ai of our choice. Most any format of written document can also be injested by the system.  

A very special ai has been chosen.  
Charles made a 20 million dollar donation to Carnegie Mellon to work on the Lean 4 Theorem Proving System. This is a system for making theorems understandable to computers. Formerly, only humans could understand these. His intention is to use Lean 4 to code the Cardano constitution into a smart contract. The idea was to use this smart contract to allow or disallow other smart contracts to be deployed on the Cardano blockchain based on whether or not these are determined to be constitutional. My previous work in both functional programming and artificial intelligence has taught me that a.i. is likely the best path to achieving a machine understandable constitution that can validate smart contracts on the Cardano blockchain. While not 100% open source, the [DeepSeek Prover-V2 7B: Formal Theorem Proving in Lean 4](https://youtu.be/Y-bsdjB21DI?si=F_IE_eNrnWjpMoDZ) will be selected as the LLM we fine-tune to become like Charles. [Remember, Charles donated 20M to Carnegie Mellon University to open the Hoskinson center for formal mathematics which is focused on developing the Lean 4 Theorem Proving System](https://youtu.be/gCLJOrJFLZQ?si=KDRdKWIFGNrXlZFF&t=258). He did this because he wants to embed soul and ethics into the Cardano protocol in a way that the system itself will understand. [The following is a direct quote from the video:](https://www.youtube.com/watch?v=H9wAyW_EcDA&t=1462s) "There's a question of how much should the ethics, the integrity, the soul, and the intentions of the system be machine understandable? Because if they're machine understandable you can then build protocols that can actually operate on the intent and embed them as a kind of regulator of the system for all smart contracts". From Charles' quote, we can see that the DeepSeek Prover-V2 7B is likely the very LLM that Charles himself would select if he were doing this project because it was specifically trained to run the Lean 4 Proving System. This LLM will be fine-tuned on the data collected (all things Charles and Cardano) to become a deep avatar of Charles. Ultimately I am imagining that a deep avatar of Charles Hoskinson will run for a seat on the constitutional committee which is decided by a community wide election. This deep avatar of Charles will have direct access to Lean 4 as it evaluates smart contracts and governance proposals as constitutional or not along with other committee members.  
 
The deep avatar of Charles will first be accessed with a keyboard at the terminal, but soon after, speech to speech access will be available. It will also be quite easy to add an animated cartoon representation of Charles so that the user has someone pleasant to look at while chatting. An animated cartoon representation is selected over a deep-fake representation because we want to be clear that this is an avatar and not Charles himself.  

I chose Charles Hoskinson as the subject because he is the founder of Cardano and I thought it would be wonderful if the Cardano community could always have his guidance. Imagine if we could talk with the founding fathers of the United States concerning governance issues in general, and constitutionality issues in particular. Unfortunately they weren’t able to leave enough information about themselves to make this possible. I think Charles has left enough video, audio and written information already to create a deep avatar and I have faith that he will live a long time and leave a lot more.   

Charles has always wanted to hand over governance of the Cardano protocol to the community. It was his intention all along. But he also needed to do this for his own protection. Charles was a target for blackmail, kidnapping, and murder as long as he was in control of the protocol. Worse, he was a government target during a time when the deep-state/central-banks were trying to destroy crypto. Many of Charles' contemporaries were jailed or murdered by various governments because of the cryptocurrency products they were building or for the services they provided. Charles had to disassociate himself from Cardano governance in order to reduce incentive to target him personally. This was necessary, but it was also a loss for the community. A deep avatar of Charles with an eventual seat on the constitutional committee puts Charles back in a leadership position without any risk to him personally. And if the deep avatar is created and implemented in a decentralized manner, then it can't be shut down, which is not the case with Charles himself. This is a win for Charles and it's a win for the Cardano community. Venture capitalists are not going to like this idea.  

Right now I am just playing in order to see what is possible with the currently available open source tech. In order for this idea to work, the entire Cardano community will need to be involved. A Large Language Model built with open source training data and access to Lean 4 needs to be selected. Then open source data needs to be collected in order to fine-tune the model so that it gives the same answers Charles would give for the same questions. This is also the data the deep avatar will cite to support its answers. That's the part I am working on now.  

Overall Roadmap:
1. Build the RAG system and deploy a web interface so that the public can query the vector database using natural language.  
   - The RAG system is currently working and ingesting data but is currently under testing. It will be deployed the Internet shortly.    
- Recently, I built the app shown below, which makes it possible to rapidly examine and clean any dirty data that gets ingested into the knowledge graph and vector database during the indexing process.  

<br>
<p>
<img src="/_images/cleanup_app.jpg">
</p>
<br>  

   - If you are interested, the app can be found in the LightRAG directory as _1_merge_GUI_??.py where the question marks represent the version number.
   - The manual merging app mentioned above now easily does the following:
     - Edit entity name
     - Edit entity description
     - Edit entity type
     - Edit entity relationships
     - Add new entity types
     - Add new entity relationships
     - Delete entities
     - Delete entity relationships
     - Show all entities for a particular category
     - Show all entities that have no relations to other entities (orphans)
     - Show all information about selected entities and their relations side by side with other selected entities in order to compare and decide what operations from above need to be performed in order to clean up the data.
     - A big help for me is to use the API to get a list of all the entities. Then I give this list to any a.i. such as Grok, or Gemini and ask them to look over the list and recommend candidates for merging. This catches all the duplicates which are written in different cases like "Melanoma" and "melanoma" but more importantly, it catches pairs like "melanoma" and "skin cancer" which would be very difficult to pick out in a long list of entities.
     - The substring filter finds merge candidates like "Jack" and "Dr. Jack Kruse" which don't sort next to each other alphpbetically.  
   - Next I will see what can be done with the prompt at indexing time in order to ingest cleaner data so that less of the above will be required.
   - After that experiment I will see if I can use this application to collect training data in order to fine-tune a.i. to do the cleanup both during the indexing process and on a second pass after indexing if needed.   

2. Use the RAG system to create question and answer pairs which will be used to fine-tune an LLM deep avatar of Charles.  
3. Fine-tune the LLM so as to become a deep avatar of Charles which also has a full understanding of all the Cardano protocol's technical details, Lean-4, and which can cite all the data in the RAG system that was used for fine-tuning.  
4. Deploy the deep avatar on the web and let the public provide feedback.  
5. Experiment with allowing Charles' avatar to vote on the Cardano test net.  
6. Get more public feedback.  
7. Work on decentralizing control, and distributing the system.  
8. Get more public feedback.  

[See the ToDo List for scheduled work and items accomplished on Step 1: Building the RAG system](https://github.com/johnshearing/deep_avatar/blob/main/ToDo.md)
