#!/usr/bin/env python

from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=40)
pdf.cell(50, 50, txt="This PDF is written in Helvetica")
pdf.output("helvetica_with_no_embedded_fonts.pdf")
