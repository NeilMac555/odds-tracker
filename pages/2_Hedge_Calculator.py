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
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main-header, h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Bebas Neue', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        letter-spacing: 0.02em !important;
    }
    
    /* Modern typography system - compact */
    .stApp {
        font-size: 15px;
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 400;
        color: #ffffff;
        margin-bottom: 0.25rem;
        letter-spacing: 0.03em;
        line-height: 1.1;
    }
    .sub-header {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 1rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }
    
    /* Results card styling - compact */
    .hedge-results-card {
        padding: 18px 20px;
        margin-top: 1rem;
        border-radius: 10px;
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
    
    /* Constrain main content column width and center it - compact */
    .main .block-container {
        max-width: 900px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 0.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Remove heavy dividers */
    hr {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin: 1.5rem 0;
    }
    
    /* Compact spacing between sections */
    .element-container {
        margin-bottom: 0.75rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">💰 Hedge Calculator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Calculate optimal hedge stakes and guaranteed profit using decimal odds.</p>', unsafe_allow_html=True)

# Mode selector
calculation_mode = st.radio(
    "Calculation Mode",
    ["Optimal Hedge (Auto)", "Manual Entry"],
    horizontal=True,
    help="Optimal Hedge automatically calculates the hedge stake for equal profit. Manual Entry lets you specify all values."
)

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
    
    if calculation_mode == "Optimal Hedge (Auto)":
        # Calculate optimal hedge stake for equal profit
        if (my_odds is not None and my_odds > 0 and 
            bet_amount is not None and bet_amount > 0 and 
            hedge_odds is not None and hedge_odds > 0):
            
            # Formula: s2 = (s1 * o1) / o2
            # This ensures profit_main = profit_hedge
            optimal_hedge = (bet_amount * my_odds) / hedge_odds
            # Store in session state for use in calculations
            st.session_state.hedge_amount_auto = optimal_hedge
            
            st.number_input(
                "Hedge Amount (Auto-calculated)",
                min_value=0.01,
                value=optimal_hedge,
                step=0.01,
                format="%.2f",
                key="hedge_amount_display",
                disabled=True,
                help=f"Optimal hedge stake: ${optimal_hedge:.2f}"
            )
            hedge_amount = optimal_hedge
        else:
            hedge_amount = None
            st.number_input(
                "Hedge Amount (Auto-calculated)",
                min_value=0.01,
                value=None,
                step=0.01,
                format="%.2f",
                key="hedge_amount_display",
                disabled=True,
                help="Enter original bet details to calculate optimal hedge"
            )
    else:
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
    
    # Additional metrics
    total_return_main = s1 * o1  # Total return if original wins
    total_return_hedge = s2 * o2  # Total return if hedge wins
    roi = (guaranteed_profit / total_staked) * 100 if total_staked > 0 else 0
    
    # Check if profits are equal (optimal hedge)
    profit_difference = abs(profit_main - profit_hedge)
    is_optimal = profit_difference < 0.01  # Consider equal if within 1 cent
    
    # Format values to 2 decimal places
    total_staked_str = f"{total_staked:.2f}"
    profit_main_str = f"{profit_main:.2f}"
    profit_hedge_str = f"{profit_hedge:.2f}"
    guaranteed_profit_str = f"{guaranteed_profit:.2f}"
    roi_str = f"{roi:.2f}"
    
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
    roi_class = get_profit_class(roi)
    
    # Display results card
    optimal_badge = '<span style="color: #44ff44; font-size: 0.85rem; font-weight: 600; margin-left: 8px;">✓ Optimal</span>' if is_optimal else ''
    
    results_html = f"""
    <div class="hedge-results-card">
        <h3 style="color: #ffffff; margin-top: 0; margin-bottom: 16px; font-size: 1.3rem; font-weight: 600;">Results{optimal_badge}</h3>
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
        <div class="result-row">
            <span class="result-label">ROI (on total stake)</span>
            <span class="result-value {roi_class}">{roi_str}%</span>
        </div>
    </div>
    """
    st.markdown(results_html, unsafe_allow_html=True)
    
    # Show additional info for optimal hedge
    if is_optimal and calculation_mode == "Optimal Hedge (Auto)":
        st.success(f"✓ Equal profit hedge: Both outcomes yield ${guaranteed_profit:.2f} profit regardless of result.")
    
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
    if calculation_mode == "Optimal Hedge (Auto)":
        st.info("💡 Enter your original bet (odds and amount) and the hedge odds to automatically calculate the optimal hedge stake for equal profit.")
    else:
        st.info("Enter all four values to calculate hedge results.")

# Footer
st.markdown("---")
st.caption("OddsEdge - Professional Odds Tracking")
