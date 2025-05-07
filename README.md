<a href="https://johnshearing.github.io/">Main list of projects</a>  

### Creating a.i. Avatars Which Answer The Same As Their Human Models.  

The first deep avatar will be modeled after Abraham Hicks.  
The second deep avatar will be modeled after Charles Hoskinson.  

The main building block is a Retrieval Augmented Generation (RAG) system.  
This is a system for automatically collecting data such as videos and documents created by the human model over the course of their lifetime.  
The RAG system is used to create training data for fine-tuning an LLM so as to give the same answers as the human model when provided with the same questions.  
The RAG system also allows the deep avatar to give accurate answers and to quote its sources.  
The open source repositories [VideoRag](https://github.com/HKUDS/VideoRAG) and [LightRAG](https://github.com/HKUDS/LightRAG) are being used to build the RAG system.  
All the scripts in this repository are used with these two libraries in order to create deep avatars.   
I have been programming for most of my life, but in this project, a.i. such as Grok, ChatGPT, Claude, and Gemini are doing most all of the coding. For this reason, the work is going very quickly.  
Preliminary work just to get familiar with RAG at a foundational level are found in the following two repositories:  
https://github.com/johnshearing/scrape_yt_mk_transcripts  
https://github.com/johnshearing/index_query_YT_Transcripts  
I expect the work to go very quickly now that the LightRAG and VideoRAG libraries are being used.  

---

<br>    
<b>  
Using An deep avatar for voting decisions<br>
</b>  
We feed the book "Hydrogen Sonata" into our vector database<br>
Now we need to know if we should vote for the character Banstegeyn to be our leader<br> 
The image below is a small part of the entire Knowledge Graph created by the LightRAG server<br>
We can click on any of these nodes to get all kinds of information about these entities.<br>
<br>
<p>
<img src="/illustrations/hs_graph.jpg">
</p>
<br>
Below we see that we are asking an a.i. to look at the knowledge graph and answer our question:<br>
Should we vote for Banstegeyn<br>
<br>
<p>
<img src="/illustrations/vote.jpg"><br>
</p>
<br>
The a.i. does not give us a direct answer yet because it is acting in an advisory capacity as most LLMs are trained to do.<br>
The goal is to use this LightRAG to collect training data for training a deep avatar of Charles which will have an opinion of its own on the matter.<br>
Of course the Hydrogen Sonata is a science fiction fantasy, but the Cardano protocol and its community are very real.<br>
So imagine how helpful a deep avatar of Charles might be when advising on Cardano governance decisions.<br>
<br>  
<br>  

--- 

I chose Abraham Hicks as my first subject because I wanted a way to find relevant sections from all the thousands of Abraham Hicks videos by using natural language queries.  
Soon I realized it would be very beneficial if people could talk with Abraham directly even if Esther Hicks is not available.  
The deep avatar of Abraham will first be accessed with a keyboard at the terminal, but soon after, speech to speech access will be available.  
It will also be quite easy to add a video representation of the deep avatar so that the user has someone pleasant to look at while chatting.  

I chose Charles Hoskinson as my second subject because he is the founder of Cardano and I thought I would be wonderful if the Cardano community could always have his guidance. Imagine if we could talk with the founding fathers of the United States concerning governance issues in general, and constitutionality issues in particular. Unfortunately they weren’t able to leave enough information about themselves to make this possible. I think Charles has left enough video, audio and written information already to create a deep avatar and I have faith that he will live a long time and leave a lot more.  

Charles made a 20 million dollar donation to Carnegie Mellon to work on a method of coding the Cardano constitution into a smart contract. The idea was to use this smart contract to allow or disallow other smart contracts to be deployed based on whether or not they are determined to be constitutional. But my previous work in both functional programming and artificial intelligence has taught me that a.i. is likely the best path to achieving a machine understandable constitution that can validate smart contracts on the Cardano blockchain. Ultimately I am imagining that a deep avatar of Charles Hoskinson will run for a seat on the constitutional committee which is decided by a community wide election.  

Charles has always wanted to hand over governance of the Cardano protocol to the community. It was his intention all along. But he also needed to do this for his own protection. Charles was a target for blackmail, kidnapping, and murder as long as he was in control of the protocol. Worse, he was a government target during a time when the deep-state/central-banks were trying to destroy crypto. Many of Charles' contemporaries were jailed or murdered by various governments because of the cryptocurrency products they were building or for the services they provided. Charles had to disassociate himself from Cardano government in order to reduce incentive to target him personally. This was necessary, but it was also a loss for the community. A deep avatar of Charles with an eventual seat on the constitutional committee puts Charles back in a leadership position without any risk to him personally. And if the deep avatar is created and implemented in a decentralized manner, then it can't be shut down, which is not the case with Charles himself. This is a win for Charles and it's a win for the Cardano community. Venture capitalists are not going to like this idea.  

Right now I am just playing in order to see what is possible with the currently available open source tech. In order for this idea to work, the entire Cardano community will need to be involved. A Large Language Model built with open source training data needs to be selected. Then open source data needs to be collected in order to fine-tune the model so that it gives the same answers Charles would give for the same questions. This is also the data the deep avatar will cite to support its answers. That's the part I am working on now.  

Some milestones are:
1. Build the RAG system and deploy a web interface so that the public can query the database using natural language.  
2. Use the RAG system to create question and answer pairs which will be used to fine-tune an LLM deep avatar.  
3. Fine-tune an LLM so as to become a deep avatar of Charles which also has a full understanding of all the protocol's technical details and which can cite all the data in the RAG system that was used for fine-tuning.  
4. Deploy the deep avatar on the web and let the public provide feedback.

