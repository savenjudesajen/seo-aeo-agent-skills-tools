# Chapters from a transcript

Many webinar-platform and meeting-tool transcripts carry speaker turns as `Name` followed by `MM:SS - MM:SS`.
One long turn (a single presenter's demo, for example) has no inner timestamps, so chapters inside it are
estimated.

## Method

1. List every speaker turn with its start time.
2. Inside long turns, split the text into topic sections (a new demo step, a new pillar, "let's move to ...") and
   estimate each section's start by its character position:
   `turn_start + (chars_before / turn_chars) * turn_length`. Round to the nearest 5 seconds.
3. Offset: the transcript clock starts at recording start. If the uploaded file is trimmed, shift every chapter
   by the trim. Check one chapter against the video before publishing.
4. 6 to 15 chapters for a 20 to 60 minute webinar. The first is `00:00`, ascending, each 10 seconds or longer.
5. **Label** each chapter with what is said, using the head term or a noun buyers search where it fits
   naturally: "Breaking activities into daily crew tasks", not "Part 2". Verb-led labels work well.
6. Mark estimated chapters in the tracker notes ("chapters estimated from transcript, verify against video").
   Don't present an estimate as exact in notes to the client.

## Q&A

If the session ends with Q&A, give it a chapter and name the main question asked, e.g.
"Q&A: scheduling around weather delays".
