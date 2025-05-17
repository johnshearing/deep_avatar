# Define your input text here
raw_text = r"""
[That's what metastasis effectively is.](https://www.youtube.com/watch?v=Ln3WszTq0uA&t=5782s) So we have everything completely
[5782.62 > 5789.82] (Jack) backward. And if you think about chemotherapeutic drugs, every single drug is targeted at mitosis
[5789.82 > 5795.66] (Jack) at some level. So if you really understand what I'm saying, we're doing everything wrong.
[5797.66 > 5803.34] (Jack) And this is why you see all those things that I post and people in Australia lose their mind.
[5803.34 > 5811.82] (Jack) I'm like, the vaccine for melanoma, the vaccine for skin cancer is UV light. On the surface,
[5811.82 > 5820.38] (Jack) it sounds so crazy until you understand what I told you in the last hour and 40 minutes.
[5822.06 > 5828.7] (Max) And I want to make a distinct section where we go over the pathology and how it relates to light.
[5828.78 > 5833.9] (Max) But suffice to say, the melanoma patients that I've encountered in the clinic and in the emergency
[5833.9 > 5840.14] (Max) department, I took a detailed history from them. And overwhelmingly, they didn't go in the sun.
[5841.26 > 5847.42] (Max) They were overweight. That's the fastest way to get melanoma. That's the reason why people in
[5847.42 > 5856.06] (Jack) Australia have it. You guys stick out like a sore thumb. And Jack, maybe we'll talk about this
[5856.06 > 5861.58] (Max) another time, but I quickly want to make the mention of omega-6 fatty acids and linoleic acid
[5861.58 > 5870.14] (Max) in the skin. I mean, empirically, people reduce the linoleic acid content of their diet and their
[5870.14 > 5876.62] (Max) skin burning ability goes down. They become more resistant to sunburn. So surely that's got a role
[5876.62 > 5880.86] (Max) too in the development of melanoma in skin cancer. It's got a role, but it's not as big a role as you
[5880.86 > 5888.3] (Jack) think. It's got a role, but it's not as big as you think. I will tell you that the single best
[5888.3 > 5894.86] (Jack) thing that you can do is you got to use red light from the sun, like from sunrise to the transition
[5894.86 > 5901.74] (Jack) of UVA, wherever you are in your latitude. What people don't realize is that red light preconditions
[5901.74 > 5908.14] (Jack) your skin for UV. This is the reason why morning light is irreplaceable. I always tell people when
[5908.14 > 5913.42] (Jack) I do podcasts, they always say, Jack, give us your one actionable task. The actionable task is
[5913.98 > 5919.26] (Jack) you need to harvest as much red light as you possibly can when you have atrophic skin. Like
[5919.26 > 5924.7] (Jack) for example, Max, I want you, hopefully when you examine all this and jump down the rabbit hole,
[5924.7 > 5929.42] (Jack) realize that just about everybody in Australia, just think about the evolutionary biology of
[5929.42 > 5935.18] (Jack) Australia. You guys, none of you belong in Australia. You all came there through imperialism.
[5935.82 > 5941.66] (Jack) Your Northern European, your haplotypes all support that. You guys all have atrophic white skin.
[5942.38 > 5946.86] (Jack) That's the reason why the Aborigines look so different than you. They're built perfectly
[5946.86 > 5954.7] (Jack) for Australia and you're not. You have to realize when I say atrophic skin, I'm not just talking
[5954.7 > 5961.42] (Jack) about thin. I'm talking about you have no melanin anywhere. Australian women are all blonde hair,
[5961.42 > 5969.02] (Jack) blue eyes. That means their exteriors are devoid of POMC. And then what do you do? Then you put
[5969.02 > 5976.38] (Max) sunglasses, sunscreen and clothes on even more. Yeah. And we can go real deep into exactly why
[5976.38 > 5983.34] (Max) that doesn't make sense. But I want to really tie a bow on the light story because we're really
[5983.34 > 5991.58] (Max) close to I guess piecing some big pieces together. So we've talked about basically humans as creatures
[5991.58 > 5999.58] (Max) of light. And what Jack's told you and explained is that not only are we adapted to receiving
[5999.58 > 6006.14] (Max) external light sources through our eyes and our central retinal pathways and how that
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