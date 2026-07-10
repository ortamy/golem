#!/usr/bin/env python3
"""
Генератор PDF-таблицы «Палео-ивритский алфавит» с русским переводом.
Источник: library/Paleo-Hebrew-Alphabet-Chart.pdf (fathersalphabet.com)
Использует Helvetica (без засечек) для английского + стандартную кодировку.
"""

from fpdf import FPDF

class PaleoPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "PALEO-HEBREW ALPHABET CHART", 0, 1, "C")
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 5, "Based on: Father's Alphabet (www.fathersalphabet.com)", 0, 1, "C")
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")


def build_pdf():
    pdf = PaleoPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ─── DATA ──────────────────────────────────────────────────
    # Fields: (num, name, sound_EN, picture_EN, meaning_EN, example_EN)
    letters = [
        ("1",  "Alef",     "A, E (glottal stop)",   "Bull head with horns",           "Chief, leader, strength, power",                "Eleph (H504): oxen"),
        ("2",  "Bet",      "B, V",                   "Father's House / Temple",         "In, inside, within, house, temple",              "Bayit (H1004): YHVH's temple"),
        ("3",  "Gimmel",   "G",                      "Camel foot / leg",               "Lift, walk, strength, ability",                  "Gamal (H1581): camel"),
        ("4",  "Dalet",    "D",                      "Tent door",                       "Door, gate, move, movement, low",                "Delet (H1817): door, gate"),
        ("5",  "Hey",      "H, -ah",                 "Man with arms raised",            "Look, lo, behold, reveal, man, life",            "He (H1887): behold, lo"),
        ("6",  "Vav",      "V",                      "Hook / peg",                      "And, with, to join things together",             "Vav (H2053): tabernacle hook"),
        ("7",  "Zayin",    "Z",                      "Plow's edge / weapon",           "Cut, shake, make ready, overturn",               "—"),
        ("8",  "Chet",     "Ch, -ach",               "Wall / fence",                    "Wall, end, obstruction, outside",                "Chet (H2399): sin"),
        ("9",  "Tet",      "T",                      "Container / basket / snake",      "Surround, store, keep, contain, cover, food",    "Teet (H2916): mud, clay"),
        ("10", "Yod",      "Y",                      "Hand and arm",                    "Work, do, make, hand, power, authority",         "Yad (H3028): hand, power"),
        ("11", "Kaf",      "K, Kh, -akh",            "Palm of hand",                    "Hand, palm, crush, grip, grasp, cover",          "Kaph (H3709): hand, palm"),
        ("12", "Lamed",    "L",                      "Shepherd's staff",                "Staff, lead, guide, teach, protect, toward",     "Lamed (H3925): teach"),
        ("13", "Mem",      "M",                      "Water / waves",                   "Waters, sea, drink, tumult, many, people",       "Mayim (H4325): waters"),
        ("14", "Nachash",  "N",                      "Serpent / snake",                 "Reflective, shiny, God-given, life, spiritual",  "Nachash (H5175): serpent"),
        ("15", "Samek",    "S",                      "Barb / thorn / support",          "Hold, establish, prevent, turn",                 "Samak (H5564): uphold"),
        ("16", "Ayin",     "A, E, O",                "Eye",                             "Eye, sight, knowledge, understanding",           "Ayin (H5869): eye, knowledge"),
        ("17", "Peh",      "P",                      "Mouth",                           "Mouth, opening, edge, saying, command",          "Peh (H6310): mouth, command"),
        ("18", "Tsade",    "Ts",                     "Man on his side / hook",          "Lie in wait, hunt, side, wait",                  "Tsad (H6654): side; Tsud (H6679): hunt"),
        ("19", "Quf",      "Q",                      "Sun at horizon / back of head",   "Circuit, sun, day, gather, encompass",           "Tequphah (H8622): circuit"),
        ("20", "Resh",     "R",                      "Head of a man",                   "Head, chief, top, first, beginning",             "Rosh (H7218): head, beginning"),
        ("21", "Shin",     "Sh, S",                  "Teeth",                           "Teeth, eat, front, consume, destroy",            "Shin (H8127): tooth"),
        ("22", "Tav",      "T",                      "Mark / cross / seal",             "A mark, strong indicator, covenant",             "Tav (H8420): mark"),
    ]

    # ─── COLUMN WIDTHS ──────────────────────────────────────────
    col_w = [8, 14, 20, 30, 55, 38]
    headers = ["#", "Name", "Sound", "Picture", "Meaning", "Example (Strong's)"]

    # ─── PRINT HEADER ROW ───────────────────────────────────────
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(40, 40, 60)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, 1, 0, "C", True)
    pdf.ln()

    # ─── PRINT DATA ROWS ───────────────────────────────────────
    pdf.set_text_color(0, 0, 0)
    for idx, (num, name, sound, picture, meaning, example) in enumerate(letters):
        row_h = 8
        for txt in [picture, meaning]:
            lines = max(1, len(txt) // 28 + 1)
            row_h = max(row_h, lines * 5)

        row_h = max(row_h, 10)

        if pdf.get_y() + row_h > 268:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_fill_color(40, 40, 60)
            pdf.set_text_color(255, 255, 255)
            for i, h in enumerate(headers):
                pdf.cell(col_w[i], 8, h, 1, 0, "C", True)
            pdf.ln()
            pdf.set_text_color(0, 0, 0)

        x_start = pdf.get_x()
        y_start = pdf.get_y()

        # Alternating row colors
        fill_r = 235 if idx % 2 == 0 else 255
        fill_g = 240 if idx % 2 == 0 else 255
        fill_b = 250 if idx % 2 == 0 else 255
        pdf.set_fill_color(fill_r, fill_g, fill_b)

        # Draw cells
        cell_x = x_start
        for ci, w in enumerate(col_w):
            pdf.rect(cell_x, y_start, w, row_h, "D")
            pdf.rect(cell_x, y_start, w, row_h, "F")
            cell_x += w

        # Number
        pdf.set_xy(x_start + 1, y_start + 1)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(col_w[0] - 2, row_h - 2, num, 0, 0, "C")

        # Name
        pdf.set_xy(x_start + sum(col_w[:1]) + 1, y_start + 1)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(col_w[1] - 2, row_h - 2, name, 0, 0, "C")

        # Sound
        pdf.set_xy(x_start + sum(col_w[:2]) + 1, y_start + 1)
        pdf.set_font("Helvetica", "I", 7)
        pdf.cell(col_w[2] - 2, row_h - 2, sound, 0, 0, "C")

        # Picture
        pdf.set_xy(x_start + sum(col_w[:3]) + 1, y_start + 1)
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(col_w[3] - 2, row_h - 2, picture, 0, 0, "L")

        # Meaning
        pdf.set_xy(x_start + sum(col_w[:4]) + 1, y_start + 1)
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(col_w[4] - 2, row_h - 2, meaning, 0, 0, "L")

        # Example
        pdf.set_xy(x_start + sum(col_w[:5]) + 1, y_start + 1)
        pdf.set_font("Helvetica", "I", 7)
        pdf.cell(col_w[5] - 2, row_h - 2, example, 0, 0, "L")

        pdf.set_xy(x_start, y_start + row_h)

    # ─── SAVE ──────────────────────────────────────────────────
    pdf.output("PALEO-ALPHABET-CHART.pdf")
    print("PDF generated: PALEO-ALPHABET-CHART.pdf")


if __name__ == "__main__":
    build_pdf()