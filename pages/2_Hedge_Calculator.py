import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Hedge Calculator - OddsEdge",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for consistent styling with the rest of the app
st.markdown("""
    <style>
    /* Modern typography system */
    .stApp {
        font-size: 16px;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 3rem;
        font-weight: 400;
        letter-spacing: -0.01em;
    }
    
    /* Results card styling */
    .hedge-results-card {
        padding: 24px;
        margin-top: 2rem;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background-color: rgba(0, 0, 0, 0.25);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .result-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .result-row:last-child {
        border-bottom: none;
    }
    
    .result-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1rem;
        font-weight: 500;
    }
    
    .result-value {
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .result-value.positive {
        color: #44ff44;
    }
    
    .result-value.negative {
        color: #ff4444;
    }
    
    .result-value.zero {
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Constrain main content column width and center it */
    .main .block-container {
        max-width: 900px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 1rem !important;
    }
    
    /* Remove heavy dividers */
    hr {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin: 2.5rem 0;
    }
    
    /* Increase spacing between sections */
    .element-container {
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">💰 Hedge Calculator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Calculate hedge stakes and profit using decimal odds.</p>', unsafe_allow_html=True)

# Input section with two columns (responsive)
col1, col2 = st.columns(2)

with col1:
    my_odds = st.number_input(
        "My Odds (decimal)",
        min_value=0.01,
        value=None,
        step=0.01,
        format="%.2f",
        placeholder="e.g. 1.85",
        key="my_odds"
    )
    
    bet_amount = st.number_input(
        "Bet Amount",
        min_value=0.01,
        value=None,
        step=0.01,
        format="%.2f",
        key="bet_amount"
    )

with col2:
    hedge_odds = st.number_input(
        "Hedge Odds (decimal)",
        min_value=0.01,
        value=None,
        step=0.01,
        format="%.2f",
        placeholder="e.g. 2.10",
        key="hedge_odds"
    )
    
    hedge_amount = st.number_input(
        "Hedge Amount",
        min_value=0.01,
        value=None,
        step=0.01,
        format="%.2f",
        key="hedge_amount"
    )

# Validation
all_inputs_provided = all([
    my_odds is not None and my_odds > 0,
    bet_amount is not None and bet_amount > 0,
    hedge_odds is not None and hedge_odds > 0,
    hedge_amount is not None and hedge_amount > 0
])

# Calculate results if all inputs are valid
if all_inputs_provided:
    # Calculations (decimal odds)
    o1 = float(my_odds)
    s1 = float(bet_amount)
    o2 = float(hedge_odds)
    s2 = float(hedge_amount)
    
    # Total staked
    total_staked = s1 + s2
    
    # Profit if original bet wins (hedge loses)
    profit_main = s1 * (o1 - 1) - s2
    
    # Profit if hedge wins (original loses)
    profit_hedge = s2 * (o2 - 1) - s1
    
    # Guaranteed profit (worst case)
    guaranteed_profit = min(profit_main, profit_hedge)
    
    # Format values to 2 decimal places
    total_staked_str = f"{total_staked:.2f}"
    profit_main_str = f"{profit_main:.2f}"
    profit_hedge_str = f"{profit_hedge:.2f}"
    guaranteed_profit_str = f"{guaranteed_profit:.2f}"
    
    # Determine color classes for profit values
    def get_profit_class(value):
        if value > 0:
            return "positive"
        elif value < 0:
            return "negative"
        else:
            return "zero"
    
    profit_main_class = get_profit_class(profit_main)
    profit_hedge_class = get_profit_class(profit_hedge)
    guaranteed_profit_class = get_profit_class(guaranteed_profit)
    
    # Display results card
    results_html = f"""
    <div class="hedge-results-card">
        <h3 style="color: #ffffff; margin-top: 0; margin-bottom: 16px; font-size: 1.3rem; font-weight: 600;">Results</h3>
        <div class="result-row">
            <span class="result-label">Total Staked</span>
            <span class="result-value zero">${total_staked_str}</span>
        </div>
        <div class="result-row">
            <span class="result-label">Profit if original wins</span>
            <span class="result-value {profit_main_class}">${profit_main_str}</span>
        </div>
        <div class="result-row">
            <span class="result-label">Profit if hedge wins</span>
            <span class="result-value {profit_hedge_class}">${profit_hedge_str}</span>
        </div>
        <div class="result-row">
            <span class="result-label">Guaranteed profit (worst case)</span>
            <span class="result-value {guaranteed_profit_class}">${guaranteed_profit_str}</span>
        </div>
    </div>
    """
    st.markdown(results_html, unsafe_allow_html=True)
    
elif any([
    my_odds is not None and my_odds <= 0,
    bet_amount is not None and bet_amount <= 0,
    hedge_odds is not None and hedge_odds <= 0,
    hedge_amount is not None and hedge_amount <= 0
]):
    # Some inputs provided but invalid
    st.warning("Please ensure all odds and amounts are positive numbers.")
else:
    # Not all inputs provided yet
    st.info("Enter all four values to calculate hedge results.")

# Footer
st.markdown("---")
st.caption("OddsEdge - Professional Odds Tracking")
