# Lecture PDF to MD

Converts a PDF of lecture slides (or a set of slides) into a single markdown document

## Setup and Execution

1. Create a (virtual environment)[https://docs.python.org/3/library/venv.html]
2. Install [**pdfplumber**](https://github.com/jsvine/pdfplumber)
3. Create a folder called `input`
4. Place all your PDFs in that folder
5. Run the code with `python3 main.py`

## Heuristics

This script is obviously made for a very specific format of slides. This is for my CS 6334: Virtual Reality class, taught by [Dr. Jin Ryong Kim](https://jessekim.com). The slides are extremely simple, with basically just a heading followed by bullet points. Some slides only have videos and a youtube link. The only other type of slide is a slide with only a title. This would be a subsection slide. Here are the rules that I follow as I parse the PDF:

* The first slide of each deck is the title slide; only extract the first line seen
* The title of a slide consists of all the text found on the FIRST line
* If a slide ONLY contains a title (and nothing else), then it is a subsection slide
* All links will be removed
* It is assumed all non-title lines start with a bullet point -- therefore, if we encounter a line without a bullet point, it is assumed that it is part of the previous line
* The indention of the bullets depend on where the first bullet is placed -- that is considered indention level 0
    * For each bullet that is further indented than that, it will have its indention level incremented by 1
    * The position of each indention will be tracked in a list so we can return to a lower level of indention if needed
* Slides with ONLY a link will be ignored
* Slides that do not contain a bulleted list following the title will just have its text dumped plaintext onto the output
* If two consecutive slides share the same title, they will be merged into one subsubsection

## Output format

* h1 - Title of each slide deck
* h2 - Subsection title (if exists)
* h3 - Slide title (subsubsection)
* Each bullet point is on its own line of indention, with the outermost having an indention of 0 (indention = tab)
