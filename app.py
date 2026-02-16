import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ========================
# PAGE CONFIG
# ========================
st.set_page_config(
    page_title="UK SA105 Rental Filing Assistant",
    page_icon="🇬🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# CUSTOM CSS - MODERN UK TAX THEME
# ========================
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Headers */
    h1 {
        color: #003078;
        font-weight: 700;
        padding-bottom: 1rem;
        border-bottom: 3px solid #003078;
    }
    
    h2 {
        color: #005ea5;
        font-weight: 600;
        margin-top: 2rem;
    }
    
    h3 {
        color: #0b0c0c;
        font-weight: 600;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #003078;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #505a5f;
    }
    
    /* Info boxes - UK Gov style */
    .info-box {
        background: #1d70b8;
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #003078;
    }
    
    .warning-box {
        background: #ffdd00;
        color: #0b0c0c;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #f47738;
    }
    
    .success-box {
        background: #00703c;
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #005a30;
    }
    
    .error-box {
        background: #d4351c;
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #942514;
    }
    
    /* Property cards */
    .property-card {
        background: linear-gradient(135deg, #f8f8f8 0%, #ffffff 100%);
        border: 2px solid #b1b4b6;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .property-card:hover {
        border-color: #1d70b8;
        box-shadow: 0 4px 8px rgba(29, 112, 184, 0.2);
    }
    
    /* Tax year banner */
    .tax-year-banner {
        background: linear-gradient(135deg, #003078 0%, #1d70b8 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Box reference styling */
    .box-ref {
        background: #f3f2f1;
        border-left: 4px solid #005ea5;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    
    .box-number {
        font-weight: 700;
        color: #003078;
        font-size: 1.1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: #00703c;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 0.25rem;
        padding: 0.75rem 2rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: #005a30;
        box-shadow: 0 4px 8px rgba(0, 112, 60, 0.3);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #f3f2f1;
        border-left: 4px solid #1d70b8;
        font-weight: 600;
    }
    
    /* Number input styling */
    input[type="number"] {
        border: 2px solid #b1b4b6 !important;
        border-radius: 0.25rem !important;
    }
    
    input[type="number"]:focus {
        border-color: #1d70b8 !important;
        box-shadow: 0 0 0 3px rgba(29, 112, 184, 0.1) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f8f8 0%, #ffffff 100%);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f3f2f1;
        border-radius: 0.25rem 0.25rem 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: #1d70b8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ========================
# SIDEBAR - SETTINGS & INFO
# ========================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/a/ae/Flag_of_the_United_Kingdom.svg", width=100)
    st.title("⚙️ Settings")
    
    st.subheader("Tax Year")
    current_year = datetime.datetime.now().year
    tax_year_end = st.selectbox(
        "Tax year ending 5 April:",
        options=[current_year, current_year + 1],
        index=0
    )
    
    st.divider()
    
    st.subheader("💡 Quick Tips")
    with st.expander("What is SA105?"):
        st.markdown("""
        **SA105** is the UK Self Assessment form for reporting:
        - Rental income from UK properties
        - Allowable expenses
        - Property finance costs (mortgage interest)
        
        Required if you're a landlord with property income.
        """)
    
    with st.expander("Section 24 Rules"):
        st.markdown("""
        **Since April 2020**, mortgage interest relief is:
        - No longer deductible from rental income
        - Instead given as a **20% tax credit**
        - Applied after calculating your tax bill
        
        This means higher-rate taxpayers get less relief than before.
        """)
    
    with st.expander("Personal Allowance Taper"):
        st.markdown("""
        If your income exceeds **£100,000**:
        - Personal allowance reduces by £1 for every £2 over
        - Fully tapers at £125,140
        - Creates effective 60% tax rate (£100k-£125k)
        """)
    
    st.divider()
    
    st.subheader("📞 Resources")
    st.markdown("""
    - [HMRC Self Assessment](https://www.gov.uk/self-assessment-tax-returns)
    - [SA105 Guidance](https://www.gov.uk/government/publications/self-assessment-uk-property-sa105-2023)
    - [Property Income Manual](https://www.gov.uk/hmrc-internal-manuals/property-income-manual)
    """)

# ========================
# MAIN CONTENT
# ========================

# Header
st.title("🇬🇧 UK Rental Property Filing Assistant")
st.markdown(f"""
<div class="tax-year-banner">
    Tax Year {tax_year_end-1}/{str(tax_year_end)[2:]} 
    (6 April {tax_year_end-1} – 5 April {tax_year_end})
</div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
<div class="info-box">
    <h3 style="color: white; margin-top: 0;">📋 How to Use This Tool</h3>
    <ol style="margin-bottom: 0;">
        <li>Enter your other taxable income (from employment, pensions, etc.)</li>
        <li>Add details for each rental property</li>
        <li>Review your SA105 box numbers and tax calculation</li>
        <li>Download a PDF summary for your records</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# ========================
# INPUT SECTION
# ========================

st.header("📝 Income & Property Details")

# Other Income
col1, col2 = st.columns([2, 1])
with col1:
    other_income = st.number_input(
        "Other taxable income (employment, pensions, savings, etc.)",
        min_value=0.0,
        step=1000.0,
        help="Total income from SA100 before rental income"
    )
with col2:
    st.metric("Other Income", f"£{other_income:,.0f}")

st.divider()

# Number of Properties
num_properties = st.number_input(
    "Number of rental properties",
    min_value=1,
    max_value=20,
    value=4,
    help="How many different rental properties do you own?"
)

# Initialize session state for properties
if 'properties' not in st.session_state:
    st.session_state.properties = []

# Property input tabs
st.subheader("🏠 Property Portfolio")

tabs = st.tabs([f"Property {i+1}" for i in range(int(num_properties))])

properties_data = []

for i in range(int(num_properties)):
    with tabs[i]:
        st.markdown(f"""
        <div class="property-card">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            property_name = st.text_input(
                "Property name/address (optional)",
                key=f"name_{i}",
                placeholder="e.g., 123 Main Street, London"
            )
        
        with col2:
            property_type = st.selectbox(
                "Property type",
                ["Residential", "Commercial", "Holiday Let"],
                key=f"type_{i}"
            )
        
        st.markdown("#### Income & Expenses")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            rent = st.number_input(
                "Annual rent received (£)",
                min_value=0.0,
                step=100.0,
                key=f"rent_{i}",
                help="Total rent received for the tax year"
            )
        
        with col2:
            expenses = st.number_input(
                "Allowable expenses (£)",
                min_value=0.0,
                step=100.0,
                key=f"exp_{i}",
                help="Repairs, insurance, letting fees, etc. (excluding mortgage interest)"
            )
        
        with col3:
            interest = st.number_input(
                "Mortgage interest (£)",
                min_value=0.0,
                step=100.0,
                key=f"int_{i}",
                help="Annual mortgage interest paid (not capital repayments)"
            )
        
        # Quick calculations for this property
        property_profit = rent - expenses
        gross_yield = (rent / (rent + expenses) * 100) if (rent + expenses) > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gross Income", f"£{rent:,.0f}")
        with col2:
            st.metric("Net Profit (before interest)", f"£{property_profit:,.0f}")
        with col3:
            color = "normal" if property_profit > 0 else "inverse"
            st.metric("Profit Margin", f"{(property_profit/rent*100):.1f}%" if rent > 0 else "N/A")
        
        # Validation warnings for individual property
        if expenses > rent:
            st.warning("⚠️ Expenses exceed rent - this property is making a loss")
        
        if interest > rent * 0.8:
            st.warning("⚠️ Mortgage interest is unusually high (>80% of rent)")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Store property data
        properties_data.append({
            "name": property_name or f"Property {i+1}",
            "type": property_type,
            "rent": rent,
            "expenses": expenses,
            "interest": interest,
            "profit": property_profit
        })

# ========================
# CALCULATIONS
# ========================

total_rent = sum(p["rent"] for p in properties_data)
total_expenses = sum(p["expenses"] for p in properties_data)
total_interest = sum(p["interest"] for p in properties_data)

profit_before_interest = total_rent - total_expenses
taxable_income_before_pa = profit_before_interest + other_income

# Personal allowance calculation with taper
personal_allowance_full = 12570
personal_allowance = personal_allowance_full

if taxable_income_before_pa > 100000:
    reduction = (taxable_income_before_pa - 100000) / 2
    personal_allowance = max(0, personal_allowance_full - reduction)

taxable_income = max(0, taxable_income_before_pa - personal_allowance)

# Tax calculation (2024/25 rates)
tax_bands = []
tax = 0

basic_rate_limit = 37700
higher_rate_limit = 125140

if taxable_income <= basic_rate_limit:
    basic_rate_tax = taxable_income * 0.20
    tax = basic_rate_tax
    tax_bands.append({"Band": "Basic Rate (20%)", "Income": taxable_income, "Tax": basic_rate_tax})
elif taxable_income <= higher_rate_limit:
    basic_rate_tax = basic_rate_limit * 0.20
    higher_rate_tax = (taxable_income - basic_rate_limit) * 0.40
    tax = basic_rate_tax + higher_rate_tax
    tax_bands.append({"Band": "Basic Rate (20%)", "Income": basic_rate_limit, "Tax": basic_rate_tax})
    tax_bands.append({"Band": "Higher Rate (40%)", "Income": taxable_income - basic_rate_limit, "Tax": higher_rate_tax})
else:
    basic_rate_tax = basic_rate_limit * 0.20
    higher_rate_tax = (higher_rate_limit - basic_rate_limit) * 0.40
    additional_rate_tax = (taxable_income - higher_rate_limit) * 0.45
    tax = basic_rate_tax + higher_rate_tax + additional_rate_tax
    tax_bands.append({"Band": "Basic Rate (20%)", "Income": basic_rate_limit, "Tax": basic_rate_tax})
    tax_bands.append({"Band": "Higher Rate (40%)", "Income": higher_rate_limit - basic_rate_limit, "Tax": higher_rate_tax})
    tax_bands.append({"Band": "Additional Rate (45%)", "Income": taxable_income - higher_rate_limit, "Tax": additional_rate_tax})

mortgage_tax_credit = total_interest * 0.20
final_tax = max(0, tax - mortgage_tax_credit)

# Effective tax rate
effective_rate = (final_tax / taxable_income_before_pa * 100) if taxable_income_before_pa > 0 else 0

# ========================
# RESULTS - TABBED INTERFACE
# ========================

st.header("📊 Results & Analysis")

tab1, tab2, tab3, tab4 = st.tabs(["📋 SA105 Boxes", "🧮 Tax Breakdown", "📈 Analysis", "⚠️ Warnings"])

# TAB 1: SA105 BOXES
with tab1:
    st.subheader("SA105 Form Entry Guide")
    
    st.markdown("""
    <div class="info-box">
        <strong>📝 Instructions:</strong> Enter these values in the corresponding boxes on your SA105 form
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="box-ref">
            <div class="box-number">Box 20 – Total rents and other income</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #00703c; margin-top: 0.5rem;">
                £{:,.2f}
            </div>
        </div>
        """.format(total_rent), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="box-ref">
            <div class="box-number">Boxes 24-29 – Allowable expenses</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #00703c; margin-top: 0.5rem;">
                £{:,.2f}
            </div>
            <small>Total of repairs, insurance, letting fees, etc. (excluding mortgage interest)</small>
        </div>
        """.format(total_expenses), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="box-ref">
            <div class="box-number">Box 44 – Residential property finance costs</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #1d70b8; margin-top: 0.5rem;">
                £{:,.2f}
            </div>
            <small>Total mortgage interest (Section 24 restriction applies)</small>
        </div>
        """.format(total_interest), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="box-ref">
            <div class="box-number">Box 45 – Adjusted profit for the year</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #00703c; margin-top: 0.5rem;">
                £{:,.2f}
            </div>
            <small>This is your taxable rental profit (before interest credit)</small>
        </div>
        """.format(profit_before_interest), unsafe_allow_html=True)
    
    st.divider()
    
    # Property breakdown table
    st.markdown("### Property-by-Property Breakdown")
    
    df_properties = pd.DataFrame(properties_data)
    df_properties['Rent'] = df_properties['rent'].apply(lambda x: f"£{x:,.0f}")
    df_properties['Expenses'] = df_properties['expenses'].apply(lambda x: f"£{x:,.0f}")
    df_properties['Interest'] = df_properties['interest'].apply(lambda x: f"£{x:,.0f}")
    df_properties['Net Profit'] = df_properties['profit'].apply(lambda x: f"£{x:,.0f}")
    
    display_df = df_properties[['name', 'type', 'Rent', 'Expenses', 'Interest', 'Net Profit']]
    display_df.columns = ['Property', 'Type', 'Rent', 'Expenses', 'Mortgage Interest', 'Net Profit']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# TAB 2: TAX BREAKDOWN
with tab2:
    st.subheader("Detailed Tax Calculation")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Income", f"£{taxable_income_before_pa:,.0f}")
    with col2:
        st.metric("Personal Allowance", f"£{personal_allowance:,.0f}")
    with col3:
        st.metric("Taxable Income", f"£{taxable_income:,.0f}")
    with col4:
        st.metric("Effective Rate", f"{effective_rate:.1f}%")
    
    st.divider()
    
    # Tax calculation breakdown
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Income Breakdown")
        income_data = {
            "Source": ["Other Income (SA100)", "Rental Profit", "**Total Income**", "", "Less: Personal Allowance", "**Taxable Income**"],
            "Amount": [
                f"£{other_income:,.0f}",
                f"£{profit_before_interest:,.0f}",
                f"**£{taxable_income_before_pa:,.0f}**",
                "",
                f"-£{personal_allowance:,.0f}",
                f"**£{taxable_income:,.0f}**"
            ]
        }
        df_income = pd.DataFrame(income_data)
        st.dataframe(df_income, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### Tax Calculation")
        if tax_bands:
            df_tax = pd.DataFrame(tax_bands)
            df_tax['Income'] = df_tax['Income'].apply(lambda x: f"£{x:,.0f}")
            df_tax['Tax'] = df_tax['Tax'].apply(lambda x: f"£{x:,.0f}")
            st.dataframe(df_tax, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        tax_summary_data = {
            "Description": ["Income Tax", "Less: Mortgage Tax Credit (20%)", "**Final Tax Payable**"],
            "Amount": [f"£{tax:,.2f}", f"-£{mortgage_tax_credit:,.2f}", f"**£{final_tax:,.2f}**"]
        }
        df_tax_summary = pd.DataFrame(tax_summary_data)
        st.dataframe(df_tax_summary, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Final tax display
    if final_tax > 0:
        st.markdown(f"""
        <div class="error-box">
            <h3 style="color: white; margin-top: 0;">💷 Estimated Tax Payable</h3>
            <div style="font-size: 2.5rem; font-weight: 700;">£{final_tax:,.2f}</div>
            <p style="margin-bottom: 0;">This is your estimated tax bill for {tax_year_end-1}/{str(tax_year_end)[2:]}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="success-box">
            <h3 style="color: white; margin-top: 0;">✅ No Tax Payable</h3>
            <p style="margin-bottom: 0;">Based on your income and allowances, no additional tax is due.</p>
        </div>
        """, unsafe_allow_html=True)

# TAB 3: ANALYSIS
with tab3:
    st.subheader("Portfolio Analysis")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_property_value_estimate = total_rent * 20  # Rough estimate at 5% yield
    total_portfolio_profit = profit_before_interest - total_interest
    portfolio_yield = (total_rent / total_property_value_estimate * 100) if total_property_value_estimate > 0 else 0
    net_margin = (total_portfolio_profit / total_rent * 100) if total_rent > 0 else 0
    
    with col1:
        st.metric("Total Rent Received", f"£{total_rent:,.0f}")
    with col2:
        st.metric("Total Expenses", f"£{total_expenses + total_interest:,.0f}")
    with col3:
        st.metric("Net Profit (after interest)", f"£{total_portfolio_profit:,.0f}")
    with col4:
        st.metric("Net Margin", f"{net_margin:.1f}%")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Income vs Expenses breakdown
        fig_breakdown = go.Figure(data=[
            go.Bar(name='Rent', x=['Income'], y=[total_rent], marker_color='#00703c'),
            go.Bar(name='Expenses', x=['Expenses'], y=[total_expenses], marker_color='#d4351c'),
            go.Bar(name='Interest', x=['Expenses'], y=[total_interest], marker_color='#f47738')
        ])
        
        fig_breakdown.update_layout(
            title='Income vs Expenses',
            barmode='group',
            height=350,
            yaxis_title='Amount (£)',
            showlegend=True
        )
        
        st.plotly_chart(fig_breakdown, use_container_width=True)
    
    with col2:
        # Property profit comparison
        property_names = [p['name'] for p in properties_data]
        property_profits = [p['profit'] for p in properties_data]
        
        colors_list = ['#00703c' if p > 0 else '#d4351c' for p in property_profits]
        
        fig_properties = go.Figure(data=[
            go.Bar(x=property_names, y=property_profits, marker_color=colors_list)
        ])
        
        fig_properties.update_layout(
            title='Profit by Property',
            height=350,
            yaxis_title='Profit (£)',
            showlegend=False
        )
        
        st.plotly_chart(fig_properties, use_container_width=True)
    
    st.divider()
    
    # Expense breakdown pie chart
    st.markdown("### Expense Breakdown")
    
    expense_breakdown = pd.DataFrame({
        'Category': ['Allowable Expenses', 'Mortgage Interest'],
        'Amount': [total_expenses, total_interest]
    })
    
    fig_pie = px.pie(
        expense_breakdown,
        values='Amount',
        names='Category',
        color_discrete_sequence=['#1d70b8', '#f47738'],
        hole=0.4
    )
    
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Tax efficiency insights
    st.markdown("### 💡 Tax Efficiency Insights")
    
    if taxable_income_before_pa > 100000:
        pa_loss = personal_allowance_full - personal_allowance
        st.markdown(f"""
        <div class="warning-box">
            <strong>⚠️ Personal Allowance Taper</strong><br>
            You've lost £{pa_loss:,.0f} of your personal allowance due to income over £100k.
            This creates an effective 60% tax rate on income between £100k-£125k.
            <br><br>
            <strong>Consider:</strong> Pension contributions or charitable donations to reduce adjusted net income.
        </div>
        """, unsafe_allow_html=True)
    
    if total_interest > total_rent * 0.5:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ High Mortgage Interest</strong><br>
            Your mortgage interest is more than 50% of your rental income. 
            Under Section 24 rules, you only get 20% tax relief on this.
            <br><br>
            <strong>Consider:</strong> Remortgaging to reduce interest, or restructuring through a limited company.
        </div>
        """, unsafe_allow_html=True)

# TAB 4: WARNINGS
with tab4:
    st.subheader("Validation & Warnings")
    
    warnings = []
    
    # Checks
    if total_rent == 0:
        warnings.append(("error", "No rental income entered", "Please check your property rental amounts"))
    
    if total_expenses > total_rent:
        warnings.append(("warning", "Total expenses exceed rental income", "You may have an overall rental loss"))
    
    if total_interest > total_rent:
        warnings.append(("warning", "Mortgage interest exceeds rental income", "This is unusually high and may indicate data entry error"))
    
    if taxable_income_before_pa > 100000:
        warnings.append(("info", "Personal allowance taper applies", f"Your PA has been reduced to £{personal_allowance:,.0f}"))
    
    if any(p['profit'] < 0 for p in properties_data):
        loss_properties = [p['name'] for p in properties_data if p['profit'] < 0]
        warnings.append(("warning", "Loss-making properties detected", f"Properties: {', '.join(loss_properties)}"))
    
    if final_tax > 10000:
        warnings.append(("info", "High tax liability", "Consider making advance payments on account to avoid interest"))
    
    if not warnings:
        st.markdown("""
        <div class="success-box">
            <h3 style="color: white; margin-top: 0;">✅ All Validation Checks Passed</h3>
            <p style="margin-bottom: 0;">No issues detected with your data entry.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for severity, title, message in warnings:
            if severity == "error":
                st.error(f"**{title}**: {message}")
            elif severity == "warning":
                st.warning(f"**{title}**: {message}")
            else:
                st.info(f"**{title}**: {message}")
    
    st.divider()
    
    st.markdown("### 📋 Pre-submission Checklist")
    
    checklist_items = [
        "✅ All rental income for the tax year is included",
        "✅ Only allowable expenses are claimed (no capital improvements)",
        "✅ Mortgage interest is only the interest portion (not capital repayments)",
        "✅ Personal allowance and tax rates are correct for the tax year",
        "✅ All properties are included in the calculation",
        "✅ Figures match your bank statements and mortgage statements"
    ]
    
    for item in checklist_items:
        st.checkbox(item, key=f"check_{item}")

# ========================
# PDF GENERATION
# ========================

st.header("📄 Export & Save")

def generate_enhanced_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003078'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#005ea5'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Title
    elements.append(Paragraph("UK Rental Property – SA105 Filing Summary", title_style))
    elements.append(Paragraph(f"Tax Year {tax_year_end-1}/{str(tax_year_end)[2:]} (6 April {tax_year_end-1} – 5 April {tax_year_end})", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # SA105 Boxes
    elements.append(Paragraph("SA105 Form Entry Guide", heading_style))
    
    sa105_data = [
        ['Box Number', 'Description', 'Amount'],
        ['Box 20', 'Total rents and other income', f'£{total_rent:,.2f}'],
        ['Boxes 24-29', 'Allowable expenses', f'£{total_expenses:,.2f}'],
        ['Box 44', 'Residential property finance costs', f'£{total_interest:,.2f}'],
        ['Box 45', 'Adjusted profit for the year', f'£{profit_before_interest:,.2f}'],
    ]
    
    sa105_table = Table(sa105_data, colWidths=[1.2*inch, 3.5*inch, 1.5*inch])
    sa105_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003078')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(sa105_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Property Breakdown
    elements.append(Paragraph("Property Portfolio Breakdown", heading_style))
    
    property_data = [['Property', 'Type', 'Rent', 'Expenses', 'Interest', 'Net Profit']]
    for p in properties_data:
        property_data.append([
            p['name'],
            p['type'],
            f"£{p['rent']:,.0f}",
            f"£{p['expenses']:,.0f}",
            f"£{p['interest']:,.0f}",
            f"£{p['profit']:,.0f}"
        ])
    
    property_table = Table(property_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    property_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#005ea5')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(property_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tax Calculation
    elements.append(Paragraph("Tax Calculation Summary", heading_style))
    
    tax_data = [
        ['Description', 'Amount'],
        ['Other taxable income', f'£{other_income:,.2f}'],
        ['Rental profit', f'£{profit_before_interest:,.2f}'],
        ['Total income before PA', f'£{taxable_income_before_pa:,.2f}'],
        ['Personal Allowance', f'£{personal_allowance:,.2f}'],
        ['Taxable income', f'£{taxable_income:,.2f}'],
        ['Income tax', f'£{tax:,.2f}'],
        ['Mortgage tax credit (20%)', f'£{mortgage_tax_credit:,.2f}'],
        ['Final tax payable', f'£{final_tax:,.2f}'],
    ]
    
    tax_table = Table(tax_data, colWidths=[4*inch, 2*inch])
    tax_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#d4351c')),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.whitesmoke),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 12),
        ('ROWBACKGROUNDS', (0,0), (-1,-2), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(tax_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph(f"Generated: {datetime.date.today().strftime('%d %B %Y')}", footer_style))
    elements.append(Paragraph("This is an estimate only. Please verify with HMRC guidance or consult a tax professional.", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("📄 Generate PDF Summary", use_container_width=True):
        pdf_buffer = generate_enhanced_pdf()
        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_buffer,
            file_name=f"SA105_Rental_Summary_{tax_year_end-1}_{tax_year_end}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

with col2:
    # Export to CSV
    if st.button("📊 Export to Excel", use_container_width=True):
        df_export = pd.DataFrame(properties_data)
        df_export['tax_year'] = f"{tax_year_end-1}/{tax_year_end}"
        
        csv = df_export.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"rental_properties_{tax_year_end-1}_{tax_year_end}.csv",
            mime="text/csv",
            use_container_width=True
        )

with col3:
    if st.button("🔄 Reset All Data", use_container_width=True):
        st.rerun()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #505a5f; font-size: 0.9rem; padding: 2rem 0;">
    <p><strong>Disclaimer:</strong> This tool provides estimates only and should not be considered professional tax advice.</p>
    <p>Always verify calculations with HMRC guidance or consult a qualified accountant.</p>
    <p>Made with ❤️ for UK landlords | Version 2.0 | {}</p>
</div>
""".format(datetime.date.today().strftime('%Y')), unsafe_allow_html=True)
