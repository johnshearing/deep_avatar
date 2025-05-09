<a href="https://johnshearing.github.io/">Main list of projects</a>  

### Creating a.i. Avatars Which Answer The Same As Their Human Models.  

The first deep avatar will be modeled after Charles Hoskinson.  
The intention is to use a deep avatar of Charles to represent his point of view and vision as a delegated representative (DRep) in Cardano governance voting.  

Very few people have the time and resources to go over every governance proposal. This is why we have delegated representatives study the proposals and cast their votes. But how do we know that our delegated representatives share our values and will vote in the community's best interest. Well there are many in the community that trust Charles with those decisions. Unfortunately, Charles is not a DRep, and even if he were, he is unlikely to have the time required to study and vote on each proposal.  
An a.i. trained on Charles' enormous volume of videos which were created so that the public could get to know how he thinks about various issues and all things Cardano could easily ingest all the publicly available information required to make informed decisions that Charles would very likely agree with. That is the goal of this project.  

The main building block is a Retrieval Augmented Generation (RAG) system.  
This is a system for automatically collecting data such as videos and documents created by the human model over the course of their lifetime.  
The RAG system is used to create training data for fine-tuning an LLM (Large Language Model) so as to give the same answers as the human model when provided with the same questions.  
The RAG system also allows the deep avatar to give accurate answers and to quote its sources.  
The open source repositories [VideoRag](https://github.com/HKUDS/VideoRAG) and [LightRAG](https://github.com/HKUDS/LightRAG) are being used to build the RAG system.  
All the scripts in this repository are used with these two libraries in order to create deep avatars.  
I have been programming for most of my life, but in this project, a.i. such as Grok, ChatGPT, Claude, and Gemini are doing most of the coding.  
For this reason, the work is going very quickly.  
Preliminary work just to get familiar with RAG at a foundational level are found in the following two repositories:  
https://github.com/johnshearing/scrape_yt_mk_transcripts  
https://github.com/johnshearing/index_query_YT_Transcripts  
I expect the work to go very quickly now that the LightRAG and VideoRAG libraries are being used.  

---

<br>    
<b>  
Using A Deep Avatar modeled after Charles For Voting Decisions in Cardano Governance<br>
</b>  
To illustrate the idea, we feed [Charles' video on the budget proposal vote](https://www.youtube.com/live/_BGKIwReb0o?si=NM88Zm4vJdW146fO) into our LightRAG vector database.<br>
Now we need to know he wants DReps to vote for the Pragma budget proposal.<br> 
The image below is a portion of the entire Knowledge Graph created by the LightRAG server after ingesting Charles' video.<br>
When the LightRAG server is running, we can click on any of these nodes and on items in the dialog box to get all kinds of information about the entities and their relationships.<br>
<br>
<p>
<img src="/_images/c_graph.jpg">
</p>
<br>
Below in a different tab of the LightRAG server we are asking an a.i. to look at the knowledge graph and answer our question:<br>
Does Charles want DReps to vote for the Pragma budget proposal?<br>
<br>
<p>
<img src="/_images/vote.jpg"><br>
</p>
<br>
The a.i. answers yes.<br>
This is useful and it's a good start, but this is just an ai looking at a vector database and answering our questions about the ingested videos.  
The goal is to use LightRAG to collect and manage training data that we will use to create a deep avatar of Charles which will have opinions very much like Charles himself.<br>
Imagine how helpful a deep avatar of Charles might be as it quickly ingests huge amounts of data, that no one else has time to look at, and then uses it to make the same decisions Charles himself would make were he looking at the same data.<br>
<br>  
<br>  

--- 
 
The deep avatar of Charles will first be accessed with a keyboard at the terminal, but soon after, speech to speech access will be available. It will also be quite easy to add an animated cartoon representation of Charles so that the user has someone pleasant to look at while chatting. An animated cartoon representation is selected over a deep-fake representation because we want to be clear that this is an avatar and not Charles himself.  

I chose Charles Hoskinson as the subject because he is the founder of Cardano and I thought it would be wonderful if the Cardano community could always have his guidance. Imagine if we could talk with the founding fathers of the United States concerning governance issues in general, and constitutionality issues in particular. Unfortunately they weren’t able to leave enough information about themselves to make this possible. I think Charles has left enough video, audio and written information already to create a deep avatar and I have faith that he will live a long time and leave a lot more.  

**An avatar of Charles on the Constitutional committee:**
Charles made a 20 million dollar donation to Carnegie Mellon to work on a method of coding the Cardano constitution into a smart contract. The idea was to use this smart contract to allow or disallow other smart contracts to be deployed based on whether or not they are determined to be constitutional. But my previous work in both functional programming and artificial intelligence has taught me that a.i. is likely the best path to achieving a machine understandable constitution that can validate smart contracts on the Cardano blockchain. Ultimately I am imagining that a deep avatar of Charles Hoskinson will run for a seat on the constitutional committee which is decided by a community wide election.  

Charles has always wanted to hand over governance of the Cardano protocol to the community. It was his intention all along. But he also needed to do this for his own protection. Charles was a target for blackmail, kidnapping, and murder as long as he was in control of the protocol. Worse, he was a government target during a time when the deep-state/central-banks were trying to destroy crypto. Many of Charles' contemporaries were jailed or murdered by various governments because of the cryptocurrency products they were building or for the services they provided. Charles had to disassociate himself from Cardano governance in order to reduce incentive to target him personally. This was necessary, but it was also a loss for the community. A deep avatar of Charles with an eventual seat on the constitutional committee puts Charles back in a leadership position without any risk to him personally. And if the deep avatar is created and implemented in a decentralized manner, then it can't be shut down, which is not the case with Charles himself. This is a win for Charles and it's a win for the Cardano community. Venture capitalists are not going to like this idea.  

Right now I am just playing in order to see what is possible with the currently available open source tech. In order for this idea to work, the entire Cardano community will need to be involved. A Large Language Model built with open source training data needs to be selected. Then open source data needs to be collected in order to fine-tune the model so that it gives the same answers Charles would give for the same questions. This is also the data the deep avatar will cite to support its answers. That's the part I am working on now.  

Some general milestones are:
1. Build the RAG system and deploy a web interface so that the public can query the database using natural language.  
2. Use the RAG system to create question and answer pairs which will be used to fine-tune an LLM deep avatar of Charles.  
3. Fine-tune the LLM so as to become a deep avatar of Charles which also has a full understanding of all the protocol's technical details and which can cite all the data in the RAG system that was used for fine-tuning.  
4. Deploy the deep avatar on the web and let the public provide feedback.  
5. Experiment with allowing Charles' avatar to vote on the Cardano test net.
6. Get more public feedback.  

[See the ToDo List for the specific plan for success](https://github.com/johnshearing/deep_avatar/blob/main/ToDo.md)
