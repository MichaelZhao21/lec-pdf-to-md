import os
import re
import math
from enum import Enum
import pdfplumber
import pdfplumber.page


LineType = Enum('LineType', ['TITLE', 'SUBTITLE', 'SUBSUBTITLE', 'BULLET'])


class Line:
    def __init__(self, text: str, indent: int, type: LineType):
        self.text = text
        self.indent = indent
        self.type = type


def open_pdf(filename: str) -> pdfplumber.PDF:
    pdf = pdfplumber.open(filename)
    print(f'Loaded PDF from {filename} with {len(pdf.pages)} pages')
    return pdf


def clean_line(raw_text: str) -> tuple[bool, str]:
    # Check if the line starts with bullet point
    bullet = raw_text.strip().startswith("• ")

    # Remove prefix and trim line
    text = raw_text.strip().removeprefix("• ")

    # Remove hyperlinks
    text = re.sub('https?\:\/\/\S*', '', text)

    # Return empty string if just a number (page number)
    if text.isnumeric():
        return False, ""

    return bullet, text


def process_page(page: pdfplumber.page.Page) -> list[Line]:
    lines = []
    raw = False
    indents: list[float] = []
    for idx, obj in enumerate(page.extract_text_lines(return_chars=False)):
        # Process title
        if idx == 0:
            _, title = clean_line(obj['text'])

            # If title empty, exit and return empty array (blank slide or only URL)
            if title == "":
                return []

            # Otherwise append it to line and start output
            lines.append(Line(title, 0, LineType.SUBSUBTITLE))
            continue

        # Process the current line
        bullet, cl = clean_line(obj['text'])

        # Raw output mode
        if raw:
            lines.append(Line(cl, 0, LineType.BULLET))
            continue

        # Ignore empty lines or filtered lines
        if cl == "":
            continue

        # Check for raw input on line 1
        if idx == 1 and not bullet:
            print(f'\t[Warning] Page {page.page_number}: First line has no bullets, defaulting to raw file structure | First Line: {cl}')
            raw = True
            lines.append(Line(cl, 0, LineType.BULLET))
            continue
    
        # If line does not have a bullet point, append it to the previous line
        if not bullet:
            lines[len(lines) - 1].text += " " + cl
            continue

        # Calculate indent
        curr_ind = math.floor(obj['x0'])
        if curr_ind in indents:
            ind = indents.index(curr_ind)
        else:
            indents.append(curr_ind)
            ind = len(indents) - 1
        
        # Append line to output
        lines.append(Line(cl, ind, LineType.BULLET))
    
    # Return the current page's lines
    return lines


def process_pdf(filename: str) -> list[Line]:
    # Open PDF
    pdf = open_pdf(filename)

    # Process each file and append its content to the lines
    lines = []
    prev_title = ""
    for idx, page in enumerate(pdf.pages):
        # Process page
        page_lines = process_page(page)

        # If title page, ignore everything except first line
        if idx == 0:
            page_lines[0].type = LineType.TITLE
            lines.append(page_lines[0])
            continue

        # Ignore if no lines
        if len(page_lines) == 0:
            continue

        # If the page ONLY has a title, make it a subtitle
        if len(page_lines) == 1:
            page_lines[0].type = LineType.SUBTITLE
            lines.append(page_lines[0])
            continue

        # Remove title if it's a continuation of the last page
        if page_lines[0].text == prev_title:
            lines.extend(page_lines[1:])
        else:
            # Add to lines and update title
            lines.extend(page_lines)
            prev_title = page_lines[0].text

    # Return PDF lines
    return lines


def write_header(type: LineType) -> str:
    if type == LineType.TITLE:
        return "#"
    if type == LineType.SUBTITLE:
        return "##"
    if type == LineType.SUBSUBTITLE:
        return "###"
    return ""


def main():
    # Store final output
    lines: list[Line] = []

    # Iterate through directory and find all pdf files
    for file in os.listdir("input"):
        # Process PDF
        if file.endswith(".pdf"):
            lines.extend(process_pdf("input/" + file))
    
    # Create a markdown file and write lines to it
    with open("output.md", "w") as f:
        for l in lines:
            if l.type != LineType.BULLET:
                f.write(f'{write_header(l.type)} {l.text}\n')
            else:
                f.write(("\t" * l.indent) + "* " + l.text + "\n")


if __name__ == '__main__':
    main()
