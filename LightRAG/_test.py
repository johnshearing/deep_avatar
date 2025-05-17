# Define your input text here
raw_text = r"""
\[3253.18 > 3259.18] (Jack) [medical school that I learned about iron and hemoglobin.](https://www.youtube.com/watch?v=Ln3WszTq0uA&t=3253s)
\[3259.18 > 3262.34] (Jack) And that iron and hemoglobin comes in two states.
\[3262.34 > 3263.82] (Jack) One is ferric, the other one's ferrous.
\[3263.82 > 3266.34] (Jack) One is plus two, the other one's plus three.
\[3266.34 > 3273.38] (Jack) When hemoglobin is plus three, it releases oxygen and nitric oxide at terminal electronic
\[3273.38 > 3274.38] (Jack) receptors and mitochondria.
\[3274.38 > 3277.82] (Jack) And I'm going, somehow I think this is going to be important.
\[3277.82 > 3284.42] (Jack) Turns out it's really important for POMC because you have to have massive amounts of
\[3284.42 > 3290.98] (Jack) oxygen around to renovate melanin to make alpha MSH, beta MSH, and gamma MSH.
\[3290.98 > 3298.66] (Jack) So Max, the story that I'm weaving for you right now is how did I come to realize that
\[3298.66 > 3300.26] (Jack) light was really important?
\[3300.26 > 3305.94] (Jack) I knew that light was tied to POMC because only UV light stimulates it.
\[3305.94 > 3312.1] (Jack) I knew that it was a semiconductor protein, and it turned out it made semiconductor proteins
\[3312.1 > 3314.7] (Jack) that responded to different frequencies of color.
\[3314.7 > 3317.74] (Jack) For example, ACTH responds more to blue light.
\[3317.74 > 3324.58] (Jack) And it turns out the alpha MSH, all of them, beta and gamma, respond to really big time
\[3324.58 > 3325.58] (Jack) UV light.
\[3325.58 > 3331.5] (Jack) In fact, UV light that is stronger than the spectrum of the sun.
\[3331.5 > 3340.06] (Jack) So I went back to that Robin Sharma book, and I thought about what Robin said in that
\[3340.06 > 3349.26] (Jack) book about Julian Battle and how his life changed so rapidly and so fast, and I started
\[3349.26 > 3350.26] (Jack) to put two and two together.
\[3350.26 > 3357.42] (Jack) I said, is this because he was actually able to reestablish POMC in his body to sculpt
\[3357.42 > 3359.1] (Jack) himself?
\[3359.1 > 3363.58] (Jack) That's actually what I took out of the book, not what the lady wanted me to believe.
\[3363.58 > 3369.58] (Jack) She wanted me to go after Amgen and how they shelved the leptin trials.
\[3369.58 > 3377.36] (Jack) I took it a totally different way, and I kind of figured out pretty quickly that this story
\[3377.36 > 3380.02] (Jack) of POMC is the story of all of us.
\[3380.02 > 3384.22] (Jack) It's the story of what's going on on the surface of our planet, in our clinics.
\[3384.22 > 3387.16] (Jack) It's the reason why everybody's getting sick.
\[3387.16 > 3392.82] (Jack) Where disease functionally is linked to if you can't make enough POMC in that tissue,
\[3392.82 > 3398.76] (Jack) you're going to have a problem, and that problem is going to manifest in your mitochondria.
\[3398.76 > 3405.04] (Jack) I began to realize very, very quickly how it all worked, and I started working this
\[3405.04 > 3406.04] (Jack) out.
\[3406.04 > 3410.28] (Jack) The first person I ever did the leptin prescription in beside myself was my son.
\[3410.28 > 3411.28] (Jack) I fixed him.
\[3411.28 > 3413.68] (Jack) Then I did it with my nephew, fixed him.
\[3413.68 > 3421.36] (Jack) I had one of my gastroenterologists who was amazed at how much weight I had lost so fast,
\[3421.36 > 3423.44] (Jack) and I told him, I said, Don, I think I found something.
\[3423.44 > 3426.68] (Jack) He says, well, look, I got this patient I can't do anything with.
\[3426.68 > 3433.32] (Jack) They've got esophageal, I mean, eosinophilic esophagitis, and Max, you know that a neurosurgeon
\[3433.32 > 3436.32] (Jack) would never take care of that in conventional medicine.
\[3436.32 > 3439.
"""

# Clean the lines
cleaned_lines = []
for line in raw_text.strip().splitlines():
    cleaned_line = line.lstrip("\\") + "  "
    cleaned_lines.append(cleaned_line)

# Output to a text file
output_filename = "_formatted_output.txt"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write("\n".join(cleaned_lines))

print(f"Formatted text written to '{output_filename}'")