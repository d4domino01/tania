import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from io import BytesIO
import datetime

st.set_page_config(page_title="UK SA105 Rental Filing Assistant", layout="wide")

st.title("🇬🇧 UK Rental Property – SA105 Filing Assistant")
st.markdown("Enter annual figures for the UK tax year (6 April – 5 April).")

# ------------------------
# INPUT SECTION
# ------------------------

other_income = st.number_input("Other taxable income (SA100) (£)", min_value=0.0, step=1000.0)
num_properties = st.number_input("Number of rental properties", 1, 20, 4)

total_rent = 0
total_expenses = 0
total_interest = 0

st.subheader("Property Details")

for i in range(int(num_properties)):
    st.markdown(f"### Property {i+1}")
    rent = st.number_input(f"Annual rent (£)", min_value=0.0, key=f"rent{i}")
    expenses = st.number_input(f"Allowable expenses (excluding mortgage interest) (£)", min_value=0.0, key=f"exp{i}")
    interest = st.number_input(f"Mortgage interest (£)", min_value=0.0, key=f"int{i}")

    total_rent += rent
    total_expenses += expenses
    total_interest += interest

# ------------------------
# CALCULATIONS
# ------------------------

profit_before_interest = total_rent - total_expenses
taxable_income_before_pa = profit_before_interest + other_income

personal_allowance = 12570
if taxable_income_before_pa > 100000:
    reduction = (taxable_income_before_pa - 100000) / 2
    personal_allowance = max(0, 12570 - reduction)

taxable_income = max(0, taxable_income_before_pa - personal_allowance)

tax = 0
if taxable_income <= 37700:
    tax = taxable_income * 0.20
elif taxable_income <= 125140:
    tax = 37700 * 0.20 + (taxable_income - 37700) * 0.40
else:
    tax = (
        37700 * 0.20 +
        (125140 - 37700) * 0.40 +
        (taxable_income - 125140) * 0.45
    )

mortgage_tax_credit = total_interest * 0.20
final_tax = max(0, tax - mortgage_tax_credit)

# ------------------------
# SA105 BOX OUTPUT
# ------------------------

st.header("📋 SA105 Entry Guide")

st.success(f"Box 20 – Total rents and income: £{total_rent:,.2f}")
st.success(f"Box 24–29 – Total allowable expenses (excluding interest): £{total_expenses:,.2f}")
st.success(f"Box 44 – Residential property finance costs: £{total_interest:,.2f}")
st.success(f"Box 45 – Net profit: £{profit_before_interest:,.2f}")

# ------------------------
# TAX SUMMARY
# ------------------------

st.header("🧮 Tax Summary")

st.write(f"Other income: £{other_income:,.2f}")
st.write(f"Personal Allowance applied: £{personal_allowance:,.2f}")
st.write(f"Taxable income after allowance: £{taxable_income:,.2f}")
st.write(f"Income tax before mortgage credit: £{tax:,.2f}")
st.write(f"Section 24 mortgage tax credit (20%): £{mortgage_tax_credit:,.2f}")
st.error(f"Estimated Final Tax Payable: £{final_tax:,.2f}")

# ------------------------
# VALIDATION
# ------------------------

st.header("⚠ Validation Checks")

if total_rent == 0:
    st.warning("Rental income is zero – check input.")

if total_expenses > total_rent:
    st.warning("Expenses exceed rent – possible loss situation.")

if taxable_income_before_pa > 100000:
    st.warning("Personal allowance taper has been applied (income over £100k).")

if total_interest > total_rent:
    st.warning("Mortgage interest unusually high relative to rent.")

# ------------------------
# PDF GENERATION (IN MEMORY)
# ------------------------

def generate_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    style = styles["Normal"]

    elements.append(Paragraph("UK Rental Property – SA105 Filing Summary", style))
    elements.append(Spacer(1, 0.3 * inch))

    data = [
        ["Total Rent (Box 20)", f"£{total_rent:,.2f}"],
        ["Allowable Expenses", f"£{total_expenses:,.2f}"],
        ["Mortgage Interest (Box 44)", f"£{total_interest:,.2f}"],
        ["Net Profit (Box 45)", f"£{profit_before_interest:,.2f}"],
        ["Personal Allowance Used", f"£{personal_allowance:,.2f}"],
        ["Income Tax Before Credit", f"£{tax:,.2f}"],
        ["Mortgage Tax Credit", f"£{mortgage_tax_credit:,.2f}"],
        ["Final Estimated Tax", f"£{final_tax:,.2f}"],
    ]

    table = Table(data, colWidths=[3 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN',(1,0),(-1,-1),'RIGHT')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Generated: {datetime.date.today()}", style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button("📄 Generate PDF Summary"):
    pdf_buffer = generate_pdf()
    st.download_button(
        label="Download PDF",
        data=pdf_buffer,
        file_name="SA105_Rental_Summary.pdf",
        mime="application/pdf"
    )
