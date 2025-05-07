## Items To Do:
- Continuous GitHub backup of all the work.  

- Learn the LightRAG db manipulation commands and see if these will work on VideoRAG database.   

- Selective searching of index given a video name or document name rather than creating response from the entire index.  

- Report timestamps on videos in a usable way.  

- LightRAG Server for Video as well as documents.  
  - See if the VideoRAG db can be converted to LightRAG db or the otherway around so that both video and documents can be queried in the same context.
  - The best way will likely be to abandon VideoRAG and work directly with whisper to create transcripts of the video.  
  - These trascripts will import into LightRAG with no issues.  

- How can we get the two stage script to run?

- Try ingesting the LightRAG libraries into a LightRAG index to see if it can map logic flow to a knowledge graph.

- Watch VideoRAG, LightRAG, and LightRAG Server run in a debugger to get a feeling for how the logic flows?

- Figure out how to pull YouTube channel metadata and document metadata into the database?

Pull video metadata into the system.
```json
    "language": "en",
    "metadata": {
        "channelName": "Abraham Hicks Tips",
        "videoTitle": "Your \u2018Reality\u2019 Is Lying to You! \u2705 Abraham Hicks 2025",
        "url": "https://www.youtube.com/watch?v=0k2tTiDTn-c",
        "videoPostDate": "2025-01-19T17:30:00Z"
    },
    "text": " Hi Abraham.",
    "segments": [
        {
            "id": 0,
            "start": 0.0,
            "end": 7.36,
            "text": " Hi Abraham. I teach this yoga class and I base it on law of attraction and I say"
        },
        {
            "id": 1,
            "start": 7.36,
            "end": 13.58,
            "text": " this thing and I was questioning it on the way over here. I say if we really did",
            "avg_logprob": -0.12857116887598863,
            "compression_ratio": 1.687830687830688,
            "no_speech_prob": 0.16776621341705322,
            "speaker": "SPEAKER_01"
        },... more segments continue until the end
     ]
```
    
- Add more videos to the index.  

- Prevent duplication of videos in the index with a check before adding.  

- See how to delete videos from the index.  
  - Currently LightRAG team is having hallucination issues after deleting documents from the index.

- Have later videos take precidence over earlier.  
  - The default prompt will need to be modified.  

- Develop a list of questions and answer pairs for fine-tuning.
  - Fine-tune an LLM on Abraham's and Charles' way of thinking and manner.
  - Fine-tune how the answers are phrased (to sound even more like Abraham and Charles)

- Clone Esther's and Charles' voice.

- Generate a moving cartoon image for Esther and Charles'.  
  - Cartoon instead of deep-fake because we want users to understand they are working with an avatar and not the actual person used as the model.  

- Deploy system on a cloud computer.  

- Setup a web interface for the public to use.  

- Consider integrating with LOLLMs because there is already some functionality for modeling personalities.

## Items on the back burner but need to be done:
- Test the effect of smaller chunks on the following question:

```python
>query = "Using only the text to answer, " \
"The Mod-Linx conveyor is stopping and starting by itself. What should I do? , "\
"Please use only the provided text when forming your answer."<
```

- What is the effect on index size and quality of answers?
  
- Test the effect of a smaller embedding dimension.
  
- What is the effect on index size and quality of answers?

- What does the following message mean?  
  - "Special tokens have been added in the vocabulary, make sure the associated word embeddings are fine-tuned or trained."  

## Done:
- Document VideoRAG and LightRAG setup.  
- Turn off collection of video (only audio) or connect everything to a nondiscrptive jpg.  
- Pull PDFs into the RAG system: perhaps use LightRAG with VideoRAG database? 
- Split the script into index and query.  
- How can we get accurate sources in the output?  
- There is a citation function in the readme.  
- tesseract option for ingesting documents   
- Fix misinformation in git notes for updating code from upstream (original) repositories.  
- I noticed that LightRag server does not append to the response file.  
- I noticed that _1_audio_rag_pipeline_07.py does not incure charges from OpenAI event though it calls openai_4o_mini over the net.  
- Look at LightRAG Server.  
- Understand what each db file is used in indexing and query and what is stored in each.


