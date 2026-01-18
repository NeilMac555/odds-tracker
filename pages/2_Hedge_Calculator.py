import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Hedge Calculator - OddsEdge",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for consistent styling with compact layout
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
        margin-bottom: 1.5rem;
        font-weight: 400;
        letter-spacing: -0.01em;
    }
    
    /* Compact spacing */
    .element-container {
        margin-bottom: 0.75rem !important;
    }
    
    .stNumberInput > label {
        margin-bottom: 0.25rem !important;
        font-size: 0.9rem !important;
    }
    
    /* Outcome breakdown card styling */
    .outcome-card {
        padding: 16px 20px;
        margin-top: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background-color: rgba(0, 0, 0, 0.25);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .outcome-card h4 {
        color: #ffffff;
        margin-top: 0;
        margin-bottom: 12px;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .outcome-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .outcome-row:last-child {
        border-bottom: none;
        font-weight: 600;
        padding-top: 12px;
        margin-top: 4px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .outcome-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    .outcome-value {
        font-size: 1.05rem;
        font-weight: 600;
    }
    
    .outcome-value.positive {
        color: #44ff44;
    }
    
    .outcome-value.negative {
        color: #ff4444;
    }
    
    .outcome-value.zero {
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Info line styling */
    .info-line {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.85rem;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Constrain main content column width and center it */
    .main .block-container {
        max-width: 700px !important;
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
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">💰 Hedge Calculator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Calculate optimal hedge stakes and guaranteed profit using decimal odds.</p>', unsafe_allow_html=True)

# Short info line
st.markdown('<p class="info-line">💡 Calculates hedge stake for equal guaranteed profit.</p>', unsafe_allow_html=True)

# Initialize session state for inputs
if 'my_odds' not in st.session_state:
    st.session_state.my_odds = None
if 'hedge_odds' not in st.session_state:
    st.session_state.hedge_odds = None
if 'bet_amount' not in st.session_state:
    st.session_state.bet_amount = None

# 2x2 Grid Layout
# Row 1: My Odds | Hedge Odds
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    my_odds = st.number_input(
        "My Odds",
        min_value=0.01,
        value=st.session_state.my_odds,
        step=0.01,
        format="%.2f",
        placeholder="e.g. 1.85",
        key="my_odds_input"
    )
    if my_odds:
        st.session_state.my_odds = my_odds

with row1_col2:
    hedge_odds = st.number_input(
        "Hedge Odds",
        min_value=0.01,
        value=st.session_state.hedge_odds,
        step=0.01,
        format="%.2f",
        placeholder="e.g. 2.10",
        key="hedge_odds_input"
    )
    if hedge_odds:
        st.session_state.hedge_odds = hedge_odds

# Row 2: Bet Amount | Hedge Amount (auto)
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    bet_amount = st.number_input(
        "Bet Amount",
        min_value=0.01,
        value=st.session_state.bet_amount,
        step=0.01,
        format="%.2f",
        key="bet_amount_input"
    )
    if bet_amount:
        st.session_state.bet_amount = bet_amount

with row2_col2:
    # Auto-calculate hedge amount
    if (my_odds is not None and my_odds > 0 and 
        bet_amount is not None and bet_amount > 0 and 
        hedge_odds is not None and hedge_odds > 0):
        
        # Formula: s2 = (s1 * o1) / o2 for equal profit
        optimal_hedge = (bet_amount * my_odds) / hedge_odds
        hedge_amount = optimal_hedge
    else:
        optimal_hedge = None
        hedge_amount = None
    
    st.number_input(
        "Hedge Amount",
        min_value=0.01,
        value=optimal_hedge if optimal_hedge else None,
        step=0.01,
        format="%.2f",
        key="hedge_amount_display",
        disabled=True
    )

# Auto-calculate and display results if all inputs are valid
if (my_odds is not None and my_odds > 0 and 
    bet_amount is not None and bet_amount > 0 and 
    hedge_odds is not None and hedge_odds > 0 and
    hedge_amount is not None and hedge_amount > 0):
    
    # Calculations (decimal odds)
    o1 = float(my_odds)
    s1 = float(bet_amount)
    o2 = float(hedge_odds)
    s2 = float(hedge_amount)
    
    # Profit if original bet wins (hedge loses)
    profit_original_win = s1 * (o1 - 1) - s2
    
    # Profit if hedge wins (original loses)
    profit_hedge_win = s2 * (o2 - 1) - s1
    
    # Guaranteed profit (worst case)
    guaranteed_profit = min(profit_original_win, profit_hedge_win)
    
    # Determine color classes for profit values
    def get_profit_class(value):
        if value > 0:
            return "positive"
        elif value < 0:
            return "negative"
        else:
            return "zero"
    
    profit_original_class = get_profit_class(profit_original_win)
    profit_hedge_class = get_profit_class(profit_hedge_win)
    guaranteed_profit_class = get_profit_class(guaranteed_profit)
    
    # Display Outcome Breakdown card
    outcome_html = f"""
    <div class="outcome-card">
        <h4>Outcome Breakdown</h4>
        <div class="outcome-row">
            <span class="outcome-label">Profit if original wins</span>
            <span class="outcome-value {profit_original_class}">${profit_original_win:.2f}</span>
        </div>
        <div class="outcome-row">
            <span class="outcome-label">Profit if hedge wins</span>
            <span class="outcome-value {profit_hedge_class}">${profit_hedge_win:.2f}</span>
        </div>
        <div class="outcome-row">
            <span class="outcome-label">Guaranteed profit</span>
            <span class="outcome-value {guaranteed_profit_class}">${guaranteed_profit:.2f}</span>
        </div>
    </div>
    """
    st.markdown(outcome_html, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("OddsEdge - Professional Odds Tracking")
