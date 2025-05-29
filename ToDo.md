## Items To Do:
All of the following are with regard to the first big milestone: The setting up the Retrieval Augmented Generation (RAG) system.  
See the the [README.md](https://github.com/johnshearing/deep_avatar/blob/main/README.md) for the overall roadmap.  

- Continuous GitHub backup of all the work

- Run LightRAG python scripts, and LightRAG Server in a debuggers to get a feeling for how the logic flows?
    
- Selective searching of the index given a video name or document name rather than creating a response from the entire index of videos.
  - There is a native function and parameter for this (ids) but it has been disabled by the LightRAG developers.
  - I need to see if I can get "ids" functionality working.  

- Convert from LightRAG's native nano_vectordb to one of the following: Neo4J, PostgreSQL, Faiss for storage.

- Select an open source LLM which has been trained on open source data.
  - Currently OpenAi's closed source gpt-4o-mini is being used to index transcripts and form responses from the data.
  - This LLM will be fine-tuned on the data collected to become a deep avatar of Charles.  
  - While not 100% open source, the [DeepSeek Prover-V2 7B: Formal Theorem Proving in Lean 4](https://youtu.be/Y-bsdjB21DI?si=F_IE_eNrnWjpMoDZ) might be selected.
  - [Charles donated 20M to Carnegie Mellon University to open the Hoskinson center for formal mathematics which is focused on developing the Lean 4 Theorem Proving System](https://youtu.be/gCLJOrJFLZQ?si=KDRdKWIFGNrXlZFF&t=258).
  - He did this because he wants to embed soul and ethics into the Cardano protocol in a way that the system itself will understand.  
  - [The following is a direct quote from the video:](https://www.youtube.com/watch?v=H9wAyW_EcDA&t=1462s) "There's a question of how much should the ethics, the integrity the soul the intentions of the system be machine understandable? Because if their machine understandable you can then build protocols that can actually operate on the intent and embed them as kind of a regulator of the system for all smart contracts"
  - From this we can see that the DeepSeek Prover-V2 7B is likely the very LLM that Charles himself would select if he were doing this project.

- Buy a powerful computer - lots of ram, storage, several GPUs - specifically for ai.

- Scrape the Internet for all videos and documents regarding Charles and Cardano - including all code and technical papers.

- Have later videos take precedence  over earlier in the responses.  
  - The default prompt will need to be modified.
  
- Develop a list of questions and answer pairs taken from the videos for fine-tuning the LLM.
  - This is exactly what LightRAG does.

- Fine-tune an LLM on Charles' way of thinking, manner, and personal knowledge.  
- Fine-tune how the answers are phrased (to sound like Charles)
- Clone Charles' voice.
- Generate an animated cartoon image for Charles'.  
  - Cartoon animations instead of deep-fake because we want users to understand they are working with an avatar and not the actual person used as the model.

- Deploy system to the Internet with a web interface for the public to use and provide feedback.  

- Consider integrating with LOLLMs because there is already some functionality for modeling personalities.

## Items on the back burner but need to be done:  
- Test the effect of index size with respect to quality of answers?

- Test the effect of a smaller embedding dimension with respect to quality of answers. 

- Test the effect of smaller chunks on the following question:

- Test the effect of changing the cosine value.

- Test the effect of entity_extract_max_gleaning during the indexing process.

```python
>query = "Using only the text to answer, " \
"The Mod-Linx conveyor is stopping and starting by itself. What should I do? , "\
"Please use only the provided text when forming your answer."<
```
  
- I noticed that _1_audio_rag_pipeline_07.py does not incur charges from OpenAI even though it seems to call openai_4o_mini over the net. 

#### Done:
- Document VideoRAG and LightRAG setup.  
- Turn off collection of video (only audio) or connect everything to a descriptive jpg.  
- Pull PDFs into the RAG system: perhaps use LightRAG with VideoRAG database? 
- Split the script into index and query.   
- tesseract option for ingesting documents   
- Fix misinformation in git notes for updating code from upstream (original) repositories.    
- Understand what each LightRAG db file is used for with respect to indexing and querying and what is stored in each.

#### Done:
- Switched to LightRAG Server for Video as well as documents.   
  - The best way to create transcripts of the video was to abandon VideoRAG and [work directly with whisper](https://github.com/johnshearing/scrape_yt_mk_transcripts).  
    - The advantage of VideoRAG is that it does object detection on the video but since we are only interested in the conversation we don't need the complications of managing another database.  
    - Scraping the audio and creating transcripts with whisper is a better option.  
    - These transcripts will import into LightRAG with no issues.

#### Done:
- Figure out how to pull YouTube channel metadata and document metadata into the LightRAG database?
  - This was accomplished by [merged??.py](https://github.com/johnshearing/scrape_yt_mk_transcripts) which converts the entire transcript from json to a segmented text.
  - The metadata collected during the process is coverted to json via a template and this is automatically imported into the LightRAG index via the rag.insert_custom_kg(custom_kg) function.
  - The LightRAG sever now reports all the metadata on the videos.
Sample of the video metadata pulled into the database.
```json
    "language": "en",
    "metadata": {
        "channelName": "Abraham Hicks Tips",
        "videoTitle": "Your \u2018Reality\u2019 Is Lying to You! \u2705 Abraham Hicks 2025",
        "url": "https://www.youtube.com/watch?v=0k2tTiDTn-c",
        "videoPostDate": "2025-01-19T17:30:00Z"

```

#### Done:
- Get more familiar with the LightRAG knowledge graph manipulation python commands.
- Get more familiar with the LightRAG Server knowledge graph manipulation API commands. 

#### Done:
- Prevent duplication of video transcripts in the index with a check before adding anything new.

#### Done:
- Fix bug in python script for global and mixed queries against LightRAG index

#### Done:
- Try ingesting the LightRAG libraries into a LightRAG index to see if it can map its own logic flow to a knowledge graph.
  - This worked the LightRAG server is able to explain its own libraries and logic flow.

#### Done:
- Feeding responses back into a query for a more thoughtful response - Investigate a two stage query script or include an agent?
  - The LighRAG library actually does this when indexing
  - This is controlled by the parameter entity_extract_max_gleaning
    
#### Done:
- Report timestamps and diarization in videos in a more usable way
  -  Done: Generate links with each answer so that users can watch the videos from which the responses have been derived.  
  -  Done: Links must include the timestamp so that the videos are queued up to the correct moment where the answers are sourced.

 #### Done:
- Done: Improve the way LightRAG Server cites source material.

 #### Done:
- See how to delete video transcripts from the index in case it is misrepresentative or if it is a duplicate.  
  - Currently the LightRAG team is having hallucination issues after deleting documents from the index.
  - For now this can be done manually through the API where all entities and relationships are reassigned.
  - Or we can simply reindex all the data without the items we wish to delete.


