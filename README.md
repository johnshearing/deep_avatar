<a href="https://johnshearing.github.io/">Main list of projects</a><br>
<br> 
<!-- <a href="http://174.167.38.230:9621" target="_blank">Ask Deep Avatar About Mitochondrial Health</a><br>
<br> -->
## What Can We Do Right Now With Deep Avatar?
### Rapidly create a.i. avatars which answer the same as their human models. 
### Rapidly create a.i. experts in any knowledge domain by ingesting scientific papers and videos.  
### Rapidly create a.i. helpers for troubleshooting and repair of complex machines and systems.  
### Rapidly create thousands of question and answer pairs for fine-tuning LLMs on a particular knowledge domain.

---

<br>    
<b>  
Case Study: Using A Deep Avatar modeled after Charles Hoskinson For Voting Decisions in Cardano Governance<br>
</b>  
To illustrate the idea, we feed <a href="https://www.youtube.com/live/_BGKIwReb0o?si=NM88Zm4vJdW146fO">Charles' video on the budget proposal vote</a> into our LightRAG knowledge graph and vector database. Now we need to know if Charles wants DReps to vote for the Pragma budget proposal or not. The image below is a portion of the entire Knowledge Graph created by the LightRAG server after ingesting Charles' video. When the LightRAG server is running, we can click on any of these nodes and on items in the dialog box to get all kinds of information about the entities and their relationships including source material.<br>
<br>
<p>
<img src="/_images/c_graph.jpg">
</p>
<br>
Below, in a different tab of the LightRAG server, we ask an a.i. to look at the knowledge graph and the vector database and answer our question:<br>
Does Charles want DReps to vote for the Pragma budget proposal?<br>
<br>
<p>
<img src="/_images/vote.jpg"><br>
</p>
<br>
The a.i. answers "yes" and explains why Charles would agree".<br>
This is useful, and it's a very good start. Already our RAG system can accurately predict what Charles will say when asked a question. The only thing left to do is to swap out the OpenAI LLM currently in use for the [DeepSeek Prover-V2 7B: Formal Theorem Proving in Lean 4](https://youtu.be/Y-bsdjB21DI?si=F_IE_eNrnWjpMoDZ). This will allow the system to prove in a rigorous mathematical way that a smart contract either is or is not constitutional. This will be discussed in more detail as we proceed.<br>
<br>  
<br>  

---   

 ### What else can we do already with the system?
Deep Avatar has been used to rapidly create specialized a.i. and for making sense of complex scientific papers and videos. It's like having an a.i. librarian that is intimately familiar with every book and every video in the library and that can talk intelligently about each and every one of them. For instance, I used the deep_avatar system to ingest and then help me make sense of more than 50 high-level esoteric medical videos curated specifically for specialists and researchers in the field. The collection explores the most granular complexities of mitochondrial health, often presenting data and methodologies that remain inscrutable to the layperson. Deep Avatar was able to look across all the videos when answering questions and was even able to produce correct answers by inference when the data was there but not plainly stated.
[The result was this webpage about mitochondrial health](https://johnshearing.github.io/mitochondria_in_vitality_healing_and_chronic_disease_prevention/) 

Deep Avatar has also been used to ingest service manuals for complicated factory machinery and then aid in troubleshooting and repair.

The main building block is a Retrieval Augmented Generation system.  
This is a system for automatically collecting and organizing data such as videos and multimedia documents.   
The RAG system gives accurate answers and quotes its sources.  
The open source repository [LightRag](https://github.com/HKUDS/LightRAG) was used to build the RAG system.  
All the scripts and applications in this repository are used together with the LightRAG library in order to create a.i. knowledge domain experts.  

I have been programming for most of my life, but in this project, a.i. such as Grok, ChatGPT, Claude, and Gemini are doing most of the coding.  
My job is to imagine what I want, make decisions about how to approach the implementation, ask for what I want in a way that a.i. can understand, test and tweek what code the a.i. returns, and decide if the new code should be included in the project or if another approach should be tried. Using this method, the work is going very quickly.  
  
I created the library linked below to scrape videos from the Internet and create transcripts which are punctuated and diarized so that we know who is speaking and when. Video timestamps are also gathered in the transcripts so that the avatar can cite source videos when validating its responses.  
https://github.com/johnshearing/scrape_yt_mk_transcripts  
These transcripts along with the metadata about the source videos are fed into the LightRAG system for indexing and querying by the ai of our choice. These a.i. can be run on a local computer so that all the data and queries remain private and secure. Most any type of multimedia document can also be ingested by the system.  

### Back to the case study

Very few people have the time and resources to go over every governance proposal. This is why we employ delegated representatives to study the proposals and cast their votes. But how do we know that our delegated representatives share our values and will vote in the community's best interest. Well there are many in the community that trust Charles with those decisions. Unfortunately, Charles is not a DRep, and even if he were, he is unlikely to have the time required to study and vote on each proposal.  
An a.i. trained on Charles' enormous volume of videos which were created so that the public could get to know how he thinks about various issues, and trained also on all things Cardano, could easily ingest all the publicly available information required to make informed decisions that Charles would very likely agree with. That is the goal of this project. 

A very special ai has been chosen for the deep avatar we are creating of Charles Hoskinson:
Charles made a 20 million dollar donation to Carnegie Mellon to work on the Lean 4 Theorem Proving System. This is a system for making theorems understandable to computers. Formerly, only humans could understand these. His intention is to use Lean 4 to code the Cardano constitution into a smart contract. The idea was to use this smart contract to allow or disallow other smart contracts to be deployed on the Cardano blockchain based on whether or not these are determined to be constitutional. My previous work in both functional programming and artificial intelligence has taught me that a.i. is likely the best path to achieving a machine understandable constitution that can validate smart contracts on the Cardano blockchain. While not 100% open source, the [DeepSeek Prover-V2 7B: Formal Theorem Proving in Lean 4](https://youtu.be/Y-bsdjB21DI?si=F_IE_eNrnWjpMoDZ) will be selected as the LLM we fine-tune to become like Charles. [Remember, Charles donated 20M to Carnegie Mellon University to open the Hoskinson center for formal mathematics which is focused on developing the Lean 4 Theorem Proving System](https://youtu.be/gCLJOrJFLZQ?si=KDRdKWIFGNrXlZFF&t=258). He did this because he wants to embed soul and ethics into the Cardano protocol in a way that the system itself will understand. [The following is a direct quote from the video:](https://www.youtube.com/watch?v=H9wAyW_EcDA&t=1462s) "There's a question of how much should the ethics, the integrity, the soul, and the intentions of the system be machine understandable? Because if they're machine understandable you can then build protocols that can actually operate on the intent and embed them as a kind of regulator of the system for all smart contracts". From Charles' quote, we can see that the DeepSeek Prover-V2 7B is likely the very LLM that Charles himself would select if he were doing this project because it was specifically trained to run the Lean 4 Proving System. This LLM will be fine-tuned on the data collected (all things Charles and Cardano) to become a deep avatar of Charles. Ultimately I am imagining that a deep avatar of Charles Hoskinson will run for a seat on the constitutional committee which is decided by a community wide election. This deep avatar of Charles will have direct access to Lean 4 as it evaluates smart contracts and governance proposals as constitutional or not along with other committee members.  
 
The deep avatar of Charles will be accessed with a keyboard at the terminal just as we are doing with the system already. It would be quite easy to add an a.i. generated representation of Charles to the human interface but we are NOT going to do that. We want to be clear that this is an avatar and not Charles himself.

I chose Charles Hoskinson as the subject because he is the founder of Cardano and I thought it would be wonderful if the Cardano community could always have his guidance. Imagine if we could talk with the founding fathers of the United States concerning governance issues in general, and constitutionality issues in particular. Unfortunately they weren’t able to leave enough information about themselves to make this possible. I think Charles has left enough video, audio and written information already to create a deep avatar and I have faith that he will live a long time and leave a lot more.   

Charles has always wanted to hand over governance of the Cardano protocol to the community. It was his intention all along. But he also needed to do this for his own protection. Charles was a target for blackmail, kidnapping, and murder as long as he was in control of the protocol. Worse, he was a government target during a time when the deep-state/central-banks were trying to destroy crypto. Many of Charles' contemporaries were jailed or murdered by various governments because of the cryptocurrency products they were building or for the services they provided. Charles had to disassociate himself from Cardano governance in order to reduce incentive to target him personally. This was necessary, but it was also a loss for the community. A deep avatar of Charles with an eventual seat on the constitutional committee puts Charles back in a leadership position without any risk to him personally. And if the deep avatar is created and implemented in a decentralized manner, then it can't be shut down, which is not the case with Charles himself. This is a win for Charles and it's a win for the Cardano community. Venture capitalists and central banks are not going to like this idea.  

In order for this idea to work, the entire Cardano community will need to be involved so as to make the project decentralized. But in order to start the conversation and create a proof of concept, I am experimenting in order to see what is possible with the currently available open source tech. Currently the system answers accurately, cites its sources, and stands ready to ingest all the information we can find about Charles and Cardano. I have deployed the system and tested that it can be accessed by anyone with a browser who has the correct privileges. Currently the system is running on my laptop which is great for testing but is not suitable for hosting an industrial sized LLM. So soon I will be purchasing a computer which is specifically built to host a large LLM. Then I need to swap out the OpenAI LLM currently in use for the [DeepSeek Prover-V2 7B: Formal Theorem Proving in Lean 4](https://youtu.be/Y-bsdjB21DI?si=F_IE_eNrnWjpMoDZ)
 

### Overall Roadmap:
1. Build the RAG system and deploy a web interface so that the public can query the vector database using natural language.
This is done.
    
2. Recently, I built the app shown below, which makes it possible to rapidly find and sanitize any dirty data that gets ingested into the knowledge graph and vector database during the indexing process.  
   - Currently I am porting this stand-alone Python app to JavaScript for seamless integration into the LightRAG WebUI so that only one single application is necessary to create and maintain the data and so that this application is available online to all with the correct privileges.  
<br>
<p>
<img src="/_images/cleanup_app.jpg">
</p>
<br>  

   - If you are interested, the stand-alone Python app can be found in the LightRAG directory as _1_merge_GUI_??.py where the question marks represent the version number.
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
     - The substring filter finds merge candidates like "Jack" and "Dr. Jack Kruse" which don't sort next to each other alphabetically.
    
3. Purchase a computer which is specifically built to host a large LLM locally. They are not very expensive these days. 
4. Swap out the OpenAI LLM currently in use for the [DeepSeek Prover-V2 7B: Formal Theorem Proving in Lean 4](https://youtu.be/Y-bsdjB21DI?si=F_IE_eNrnWjpMoDZ)
5. Collect, ingest, and sanitize all training data so we are starting with good information about Charles and Cardano.
6. Open a port to the host computer so that all can try it out.
7. Decentralize the LLM and the RAG system.
   -  Much like the Cardano blockchain uses thousands of stakepool operators to validate transactions, we can have multiple operators running the same LLM and RAG system to validate the answers provided by the system.
8. Experiment with allowing Charles' avatar to vote on the Cardano test net.  
6. Public feedback.  
  

