import streamlit as st
import psycopg2
from datetime import datetime, timedelta
import os
import pandas as pd
import plotly.graph_objects as go

# Page configuration with custom favicon
st.set_page_config(
    page_title="OddsEdge - Live Odds Tracker",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding and segmented control with modern typography
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
    
    /* Modern expander/card styling */
    .stExpander {
        margin-bottom: 16px;
    }
    
    .stExpander summary {
        padding: 16px 20px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background-color: rgba(0, 0, 0, 0.25) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stExpander summary:hover {
        background-color: rgba(0, 0, 0, 0.35) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), 0 2px 6px rgba(0, 0, 0, 0.15) !important;
    }
    
    .stExpander > div {
        border-radius: 0 0 14px 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: none !important;
        background-color: rgba(0, 0, 0, 0.15) !important;
        padding: 20px 24px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Remove heavy dividers */
    hr {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin: 2.5rem 0;
    }
    
    /* Increase spacing between sections */
    .element-container {
        margin-bottom: 2rem;
    }
    
    /* Modern subheader styling */
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        margin-bottom: 1.5rem !important;
        margin-top: 2rem !important;
    }
    
    /* Modern table styling */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Responsive odds display */
    .odds-table-container {
        width: 100%;
    }
    
    /* Desktop: show table, hide cards */
    .odds-table-desktop {
        display: table;
        width: 100%;
        border-collapse: collapse;
    }
    
    .odds-cards-mobile {
        display: none;
    }
    
    /* Mobile card styling */
    .odds-card-mobile {
        background-color: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .odds-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .odds-card-header strong {
        color: #ffffff;
        font-size: 1rem;
    }
    
    .odds-card-updated {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.85rem;
    }
    
    .odds-card-body {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .odds-card-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
    }
    
    .odds-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .odds-value {
        color: #ffffff;
        font-size: 0.95rem;
        text-align: right;
    }
    
    /* Mobile responsive: hide table, show cards */
    @media screen and (max-width: 768px) {
        .odds-table-desktop {
            display: none !important;
        }
        
        .odds-cards-mobile {
            display: block !important;
        }
        
        /* Adjust main content for mobile */
        .main .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* Adjust header for mobile */
        .main-header {
            font-size: 2rem !important;
        }
        
        .sub-header {
            font-size: 1.1rem !important;
        }
        
        /* Adjust expander padding for mobile */
        .stExpander > div {
            padding: 16px !important;
        }
        
        /* Mobile sidebar improvements - make it full width and clear */
        section[data-testid="stSidebar"] {
            min-width: 100% !important;
            max-width: 100% !important;
            width: 100% !important;
            background-color: rgba(0, 0, 0, 0.6) !important;
            backdrop-filter: blur(10px) !important;
            border-right: none !important;
        }
        
        /* Navigation container styling */
        section[data-testid="stSidebar"] nav {
            padding: 8px 12px !important;
        }
        
        /* Make navigation items very visible and clear on mobile */
        section[data-testid="stSidebar"] nav a {
            color: rgba(255, 255, 255, 0.9) !important;
            opacity: 1 !important;
            font-size: 1.15rem !important;
            font-weight: 500 !important;
            padding: 16px 18px !important;
            margin: 6px 0 !important;
            border-radius: 10px !important;
            background-color: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            display: flex !important;
            align-items: center !important;
            min-height: 52px !important;
            transition: all 0.2s ease !important;
            text-decoration: none !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] nav a:active {
            color: #ffffff !important;
            background-color: rgba(255, 255, 255, 0.15) !important;
            border-color: rgba(255, 255, 255, 0.25) !important;
            transform: translateX(4px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Active navigation item - very prominent on mobile */
        section[data-testid="stSidebar"] nav a[aria-current="page"],
        section[data-testid="stSidebar"] nav a[class*="active"] {
            color: #ffffff !important;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.15)) !important;
            border: 2px solid rgba(255, 255, 255, 0.4) !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        }
        
        /* Make icons larger and more visible on mobile */
        section[data-testid="stSidebar"] .nav-icon {
            width: 22px !important;
            height: 22px !important;
            margin-right: 14px !important;
            opacity: 1 !important;
            flex-shrink: 0 !important;
        }
        
        section[data-testid="stSidebar"] nav a::before {
            width: 22px !important;
            height: 22px !important;
            margin-right: 14px !important;
            opacity: 1 !important;
        }
        
        /* Sidebar headings - make them stand out */
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] .stMarkdown h3 {
            color: rgba(255, 255, 255, 0.95) !important;
            font-weight: 700 !important;
            font-size: 1.3rem !important;
            margin-bottom: 16px !important;
            margin-top: 12px !important;
            padding-bottom: 8px !important;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2) !important;
        }
        
        /* League buttons - more visible on mobile */
        .stSidebar button[kind="secondary"] {
            padding: 14px 18px !important;
            font-size: 1.05rem !important;
            color: rgba(255, 255, 255, 0.85) !important;
            background-color: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            min-height: 48px !important;
            font-weight: 500 !important;
        }
        
        .stSidebar button[kind="primary"] {
            padding: 14px 18px !important;
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            min-height: 48px !important;
            background-color: rgba(255, 255, 255, 0.2) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
        }
        
        /* Ensure sidebar content is readable */
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] p {
            color: rgba(255, 255, 255, 0.85) !important;
            font-size: 1rem !important;
        }
        
        /* Ensure navigation text is clear */
        section[data-testid="stSidebar"] nav a > div {
            font-weight: inherit !important;
        }
    }
    
    /* Compact status text */
    .status-text {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.5);
        text-align: right;
        margin-top: 0.5rem;
        margin-bottom: 0;
        padding-top: 0;
    }
    
    /* Constrain main content column width and center it */
    .main .block-container {
        padding-top: 1rem !important;
        max-width: 1400px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    /* Reduce spacing after header */
    .main .block-container > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Compact spacing for tape view */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Today's Tape table styling */
    .tape-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 0.5rem;
    }
    
    .tape-table th {
        background-color: rgba(0, 0, 0, 0.3);
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.85rem;
        font-weight: 600;
        padding: 8px 12px;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .tape-table td {
        padding: 10px 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.9rem;
    }
    
    .tape-row {
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    
    .tape-row:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }
    
    .tape-row.selected {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .strength-badge-tape {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .strength-badge-tape.strong {
        background-color: rgba(255, 100, 100, 0.2);
        color: #ff6464;
        border: 1px solid rgba(255, 100, 100, 0.3);
    }
    
    .strength-badge-tape.medium {
        background-color: rgba(255, 200, 100, 0.2);
        color: #ffc864;
        border: 1px solid rgba(255, 200, 100, 0.3);
    }
    
    /* Biggest Movers card styling */
    .mover-card {
        padding: 20px 24px;
        margin-bottom: 16px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background-color: rgba(0, 0, 0, 0.25);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .mover-card:hover {
        background-color: rgba(0, 0, 0, 0.35);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), 0 2px 6px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    .mover-match {
        font-size: 1.15rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 8px;
        letter-spacing: -0.01em;
    }
    
    .mover-details {
        color: rgba(255, 255, 255, 0.75);
        font-size: 0.95rem;
        margin-top: 6px;
        display: inline-block;
        line-height: 1.6;
    }
    
    /* Ensure flag emojis render properly */
    .flag-emoji {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", "Android Emoji", "EmojiSymbols", "EmojiOne Mozilla", "Twemoji Mozilla", "Segoe UI Symbol", sans-serif;
        font-size: 1.2em;
        display: inline-block;
        line-height: 1;
    }
    
    /* Segmented Control Styling - ONLY for Home/Draw/Away tabs inside expanders */
    /* Completely exclude sidebar - use very specific selectors */
    section[data-testid="stSidebar"] .stRadio,
    [data-testid="stSidebar"] .stRadio,
    .css-1d391kg .stRadio {
        all: unset !important;
        display: block !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div,
    [data-testid="stSidebar"] .stRadio > div,
    .css-1d391kg .stRadio > div {
        all: revert !important;
    }
    
    section[data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio label,
    .css-1d391kg .stRadio label {
        all: revert !important;
    }
    
    /* Target ONLY radio buttons inside expander content (where Home/Draw/Away tabs are) */
    .stExpander .element-container .stRadio > div {
        display: flex !important;
        gap: 6px !important;
        margin-bottom: 12px !important;
        flex-direction: row !important;
    }
    
    .stExpander .element-container .stRadio > div[role="radiogroup"] {
        display: flex !important;
        gap: 6px !important;
        width: 100% !important;
        flex-direction: row !important;
    }
    
    /* Compact tab styling - only in expanders */
    .stExpander .element-container .stRadio > div > label,
    .stExpander .element-container .stRadio > div[role="radiogroup"] > label {
        flex: 1 !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: rgba(255, 255, 255, 0.6) !important;
        text-align: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
        position: relative !important;
        margin-bottom: 0 !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 32px !important;
        box-sizing: border-box !important;
        font-size: 0.9rem !important;
    }
    
    .stExpander .element-container .stRadio > div > label:hover,
    .stExpander .element-container .stRadio > div[role="radiogroup"] > label:hover {
        background-color: rgba(0, 0, 0, 0.4) !important;
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Active tab styling - only in expanders */
    .stExpander .element-container .stRadio > div > label:has(input[type="radio"]:checked),
    .stExpander .element-container .stRadio > div[role="radiogroup"] > label:has(input[type="radio"]:checked) {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        font-weight: 600 !important;
    }
    
    /* Active tab underline - only in expanders */
    .stExpander .element-container .stRadio > div > label:has(input[type="radio"]:checked)::after,
    .stExpander .element-container .stRadio > div[role="radiogroup"] > label:has(input[type="radio"]:checked)::after {
        content: '' !important;
        position: absolute !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 2px !important;
        background-color: #4ECDC4 !important;
        border-radius: 0 0 6px 6px !important;
    }
    
    /* Hide default radio button circles - only in expanders */
    .stExpander .element-container .stRadio input[type="radio"] {
        position: absolute !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        pointer-events: none !important;
    }
    
    /* Ensure proper spacing - only in expanders */
    .stExpander .element-container .stRadio {
        margin-bottom: 8px !important;
    }
    
    /* Style the label text container - only in expanders */
    .stExpander .element-container .stRadio label > div {
        width: 100% !important;
        text-align: center !important;
    }
    
    /* Reduce sidebar width */
    section[data-testid="stSidebar"] {
        min-width: 18rem !important;
        max-width: 18rem !important;
    }
    
    /* Make sidebar feel secondary - reduce overall visual weight */
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Lower contrast for sidebar headings */
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: rgba(255, 255, 255, 0.5) !important;
        font-weight: 500 !important;
    }
    
    /* Lower contrast for inactive navigation items */
    section[data-testid="stSidebar"] nav a {
        color: rgba(255, 255, 255, 0.4) !important;
        opacity: 0.7 !important;
    }
    
    section[data-testid="stSidebar"] nav a:hover {
        color: rgba(255, 255, 255, 0.6) !important;
        opacity: 0.85 !important;
    }
    
    /* Keep active navigation item clearly highlighted */
    section[data-testid="stSidebar"] nav a[aria-current="page"],
    section[data-testid="stSidebar"] nav a[class*="active"],
    section[data-testid="stSidebar"] nav a:has([data-baseweb="base-select"]),
    section[data-testid="stSidebar"] nav a[href]:focus {
        color: rgba(255, 255, 255, 0.95) !important;
        opacity: 1 !important;
        font-weight: 600 !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 4px !important;
    }
    
    /* Lower contrast for sidebar text content */
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Style league selection buttons in sidebar - lower contrast */
    .stSidebar button[kind="secondary"] {
        width: 100% !important;
        text-align: left !important;
        padding: 8px 12px !important;
        margin-bottom: 4px !important;
        border-radius: 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background-color: rgba(0, 0, 0, 0.15) !important;
        color: rgba(255, 255, 255, 0.5) !important;
        transition: all 0.2s ease !important;
    }
    
    .stSidebar button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Keep primary (active) button prominent */
    .stSidebar button[kind="primary"] {
        background-color: rgba(255, 255, 255, 0.12) !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        font-weight: 600 !important;
    }
    
    .stSidebar button[kind="primary"]:hover {
        background-color: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
    }
    
    /* Sidebar navigation icons styling */
    .nav-icon {
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 8px;
        vertical-align: middle;
        opacity: 0.7;
        flex-shrink: 0;
    }
    
    section[data-testid="stSidebar"] nav a,
    section[data-testid="stSidebar"] a[href] {
        display: flex !important;
        align-items: center !important;
    }
    
    section[data-testid="stSidebar"] nav a:hover .nav-icon,
    section[data-testid="stSidebar"] a:hover .nav-icon {
        opacity: 1;
    }
    
    /* CSS fallback for Dashboard icon using ::before */
    section[data-testid="stSidebar"] nav a[href="/"]::before,
    section[data-testid="stSidebar"] nav a[href=""]::before {
        content: '';
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 8px;
        vertical-align: middle;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.7)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='7' height='7'/%3E%3Crect x='14' y='3' width='7' height='7'/%3E%3Crect x='14' y='14' width='7' height='7'/%3E%3Crect x='3' y='14' width='7' height='7'/%3E%3C/svg%3E");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.7;
        flex-shrink: 0;
    }
    
    /* CSS fallback for Biggest Movers icon */
    section[data-testid="stSidebar"] nav a[href*="Biggest_Movers"]::before,
    section[data-testid="stSidebar"] nav a[href*="biggest"]::before {
        content: '';
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 8px;
        vertical-align: middle;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.7)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='23 6 13.5 15.5 8.5 10.5 1 18'/%3E%3Cpolyline points='17 6 23 6 23 12'/%3E%3C/svg%3E");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.7;
        flex-shrink: 0;
    }
    
    /* CSS fallback for Hedge Calculator icon */
    section[data-testid="stSidebar"] nav a[href*="Hedge_Calculator"]::before,
    section[data-testid="stSidebar"] nav a[href*="hedge"]::before {
        content: '';
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 8px;
        vertical-align: middle;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.7)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='4' y='2' width='16' height='20' rx='2'/%3E%3Cline x1='8' y1='6' x2='16' y2='6'/%3E%3Cline x1='8' y1='10' x2='16' y2='10'/%3E%3Cline x1='8' y1='14' x2='16' y2='14'/%3E%3Cline x1='8' y1='18' x2='16' y2='18'/%3E%3C/svg%3E");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.7;
        flex-shrink: 0;
    }
    </style>
    <script>
    // Add icons to sidebar navigation and capitalize Dashboard
    function addNavIcons() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (!sidebar) {
            // Try alternative selector
            setTimeout(addNavIcons, 100);
            return;
        }
        
        // Find all navigation links - try multiple selectors
        let navLinks = sidebar.querySelectorAll('nav a');
        if (navLinks.length === 0) {
            navLinks = sidebar.querySelectorAll('a[href]');
        }
        if (navLinks.length === 0) {
            navLinks = sidebar.querySelectorAll('[data-testid*="nav"] a, [class*="nav"] a');
        }
        
        navLinks.forEach(link => {
            // Skip if icon already added
            if (link.querySelector('.nav-icon')) return;
            
            const text = link.textContent.trim();
            const href = link.getAttribute('href') || '';
            const textLower = text.toLowerCase();
            
            let iconSvg = '';
            let shouldCapitalize = false;
            
            // Dashboard icon (grid/layout) - check for dashboard (case insensitive)
            if (textLower === 'dashboard' || href === '/' || href === '' || href === '/dashboard' || href.includes('dashboard')) {
                iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>';
                shouldCapitalize = true;
            }
            // Biggest Movers icon (trending up)
            else if (textLower.includes('biggest movers') || textLower.includes('biggest_movers') || href.includes('Biggest_Movers') || href.includes('biggest')) {
                iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>';
            }
            // Hedge Calculator icon (calculator)
            else if (textLower.includes('hedge calculator') || textLower.includes('hedge_calculator') || href.includes('Hedge_Calculator') || href.includes('hedge')) {
                iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"></rect><line x1="8" y1="6" x2="16" y2="6"></line><line x1="8" y1="10" x2="16" y2="10"></line><line x1="8" y1="14" x2="16" y2="14"></line><line x1="8" y1="18" x2="16" y2="18"></line></svg>';
            }
            
            if (iconSvg) {
                const icon = document.createElement('span');
                icon.className = 'nav-icon';
                icon.innerHTML = iconSvg;
                link.insertBefore(icon, link.firstChild);
            }
            
            // Capitalize Dashboard text
            if (shouldCapitalize && textLower === 'dashboard') {
                const textNode = Array.from(link.childNodes).find(node => node.nodeType === 3);
                if (textNode) {
                    textNode.textContent = 'Dashboard';
                } else {
                    // If no direct text node, try to update the text content
                    const currentText = link.textContent.trim();
                    if (currentText.toLowerCase() === 'dashboard') {
                        link.innerHTML = link.innerHTML.replace(/dashboard/gi, 'Dashboard');
                    }
                }
            }
        });
    }
    
    // Run immediately and on load
    addNavIcons();
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addNavIcons);
    }
    
    // Re-run after Streamlit navigation (using MutationObserver)
    setTimeout(() => {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            const observer = new MutationObserver(() => {
                setTimeout(addNavIcons, 50);
            });
            observer.observe(sidebar, { childList: true, subtree: true });
        }
    }, 500);
    
    // Also run after a delay to catch late-rendered elements
    setTimeout(addNavIcons, 1000);
    setTimeout(addNavIcons, 2000);
    </script>
""", unsafe_allow_html=True)

# Header with compact status
header_col1, header_col2 = st.columns([0.7, 0.3])
with header_col1:
    st.markdown('<p class="main-header">OddsEdge</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time Soccer Betting Odds Tracker</p>', unsafe_allow_html=True)
with header_col2:
    # Status placeholder - will be updated after odds_data loads
    status_placeholder = st.empty()

# Initialize session state for time window (shared with Biggest Movers)
if 'time_window_selection' not in st.session_state:
    st.session_state.time_window_selection = "6h"

# Time window selector
time_window_options = ["1h", "3h", "6h", "24h", "Since Open"]
time_window_col1, time_window_col2 = st.columns([0.2, 0.8])
with time_window_col1:
    selected_window = st.selectbox("Time Window", time_window_options, 
                                    index=time_window_options.index(st.session_state.time_window_selection),
                                    key="time_window_selector")
    st.session_state.time_window_selection = selected_window

# Convert time window to timedelta
if selected_window == "Since Open":
    window_timedelta = None
else:
    hours = int(selected_window.replace("h", ""))
    window_timedelta = timedelta(hours=hours)

# Search box
search_query = st.text_input("Search matches", placeholder="Filter by team name...", key="match_search")

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    st.error("Database connection not configured")
    st.stop()

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)

# Helper functions for implied probability calculations
def implied_prob(o):
    """Calculate implied probability from decimal odds"""
    if o and o > 1:
        return 1.0 / o
    return None

def delta_pp(open_o, now_o):
    """Calculate percentage point change in implied probability"""
    open_prob = implied_prob(open_o)
    now_prob = implied_prob(now_o)
    if open_prob is not None and now_prob is not None:
        return (now_prob - open_prob) * 100
    return None

def delta_odds_pct(open_o, now_o):
    """Calculate percentage change in odds"""
    if open_o and open_o > 0 and now_o and now_o > 0:
        return (now_o / open_o - 1) * 100
    return None

def implied_prob_pct_change(open_o, now_o):
    """Calculate percentage change in implied probability (not percentage points)"""
    open_prob = implied_prob(open_o)
    now_prob = implied_prob(now_o)
    if open_prob is not None and now_prob is not None and open_prob > 0:
        return ((now_prob - open_prob) / open_prob) * 100
    return None

def load_latest_odds():
    """Load the most recent odds for each match (next 3 days only)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT league, home_team, away_team, bookmaker, home_odds, away_odds, draw_odds, timestamp, commence_time
    FROM (
        SELECT *, 
               ROW_NUMBER() OVER (
                   PARTITION BY league, home_team, away_team, bookmaker 
                   ORDER BY timestamp DESC
               ) as rn
        FROM odds
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
          AND (
              commence_time IS NOT NULL 
              AND commence_time >= CURRENT_DATE 
              AND commence_time < CURRENT_DATE + INTERVAL '3 days'
          )
    ) ranked
    WHERE rn = 1
    ORDER BY league, home_team, bookmaker
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def load_odds_history(league, home_team, away_team, hours=24):
    """Load historical odds for a specific match"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT bookmaker, home_odds, away_odds, draw_odds, timestamp
    FROM odds
    WHERE league = %s 
        AND home_team = %s 
        AND away_team = %s
        AND timestamp >= NOW() - INTERVAL '%s hours'
    ORDER BY timestamp ASC
    """
    
    cursor.execute(query, (league, home_team, away_team, hours))
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def get_opening_odds(league, home_team, away_team, bookmaker, time_window=None):
    """Get the first recorded odds for a match within time window (opening odds)
    
    Args:
        time_window: timedelta object for time window, or None for "Since Open"
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if time_window is None:
        # "Since Open" - get earliest recorded odds
        query = """
        SELECT home_odds, away_odds, draw_odds, timestamp
        FROM odds
        WHERE league = %s 
            AND home_team = %s 
            AND away_team = %s
            AND bookmaker = %s
        ORDER BY timestamp ASC
        LIMIT 1
        """
        cursor.execute(query, (league, home_team, away_team, bookmaker))
    else:
        # Get earliest odds within time window
        cutoff_time = datetime.now() - time_window
        query = """
        SELECT home_odds, away_odds, draw_odds, timestamp
        FROM odds
        WHERE league = %s 
            AND home_team = %s 
            AND away_team = %s
            AND bookmaker = %s
            AND timestamp >= %s
        ORDER BY timestamp ASC
        LIMIT 1
        """
        cursor.execute(query, (league, home_team, away_team, bookmaker, cutoff_time))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'home_odds': row[0],
            'away_odds': row[1],
            'draw_odds': row[2],
            'timestamp': row[3]
        }
    return None

def calculate_odds_change(opening_odds, current_odds):
    """Calculate percentage change and direction for odds"""
    if opening_odds is None or current_odds is None:
        return None, None, None
    
    change = ((current_odds - opening_odds) / opening_odds) * 100
    
    if change > 0:
        # Odds increased (less likely to win) - green up arrow
        return change, "↑", "green"
    elif change < 0:
        # Odds decreased (more likely to win) - red down arrow
        return abs(change), "↓", "red"
    else:
        # No change
        return 0, "—", "gray"

def get_biggest_mover_for_match(league, home_team, away_team, bookmaker, current_odds, time_window=None):
    """Get the biggest mover (by absolute implied probability delta) for a match
    
    Returns: (outcome, opening_odds, current_odds, delta_pp, movement_text, movement_color, strength_badge)
    """
    opening = get_opening_odds(league, home_team, away_team, bookmaker, time_window)
    if not opening:
        return None
    
    home_delta_pp = delta_pp(opening['home_odds'], current_odds['home_odds'])
    draw_delta_pp = delta_pp(opening['draw_odds'], current_odds['draw_odds'])
    away_delta_pp = delta_pp(opening['away_odds'], current_odds['away_odds'])
    
    if all([home_delta_pp is not None, draw_delta_pp is not None, away_delta_pp is not None]):
        deltas = [
            (abs(home_delta_pp), home_delta_pp, 'Home', opening['home_odds'], current_odds['home_odds']),
            (abs(draw_delta_pp), draw_delta_pp, 'Draw', opening['draw_odds'], current_odds['draw_odds']),
            (abs(away_delta_pp), away_delta_pp, 'Away', opening['away_odds'], current_odds['away_odds'])
        ]
        max_abs_delta_pp, signed_delta_pp, outcome, opening_odds_val, current_odds_val = max(deltas, key=lambda x: x[0])
        
        # Determine movement
        if current_odds_val < opening_odds_val:
            movement_text = "shortened"
            movement_color = "#44ff44"  # Green
        else:
            movement_text = "drifted"
            movement_color = "#ff4444"  # Red
        
        # Determine strength badge
        strength_badge = ""
        if abs(signed_delta_pp) >= 5:
            strength_badge = "STRONG"
        elif abs(signed_delta_pp) >= 3:
            strength_badge = "MEDIUM"
        
        return {
            'outcome': outcome,
            'opening_odds': opening_odds_val,
            'current_odds': current_odds_val,
            'delta_pp': signed_delta_pp,
            'abs_delta_pp': abs(signed_delta_pp),
            'movement_text': movement_text,
            'movement_color': movement_color,
            'strength_badge': strength_badge
        }
    
    return None

def calculate_no_vig_probability(home_odds, draw_odds, away_odds):
    """Calculate no-vig implied probabilities from decimal odds"""
    if not all([home_odds, draw_odds, away_odds]):
        return None, None, None
    
    # Calculate implied probabilities (1/odds)
    home_implied = 1.0 / home_odds
    draw_implied = 1.0 / draw_odds
    away_implied = 1.0 / away_odds
    
    # Total market margin (vig)
    total_implied = home_implied + draw_implied + away_implied
    
    # Remove vig by normalizing
    home_no_vig = home_implied / total_implied
    draw_no_vig = draw_implied / total_implied
    away_no_vig = away_implied / total_implied
    
    return home_no_vig, draw_no_vig, away_no_vig

def get_biggest_movers():
    """Get the top 10 matches with largest absolute implied probability changes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all unique matches from last 24 hours
    # Exclude finished and in-play matches - only include future matches (commence_time > NOW)
    query = """
    SELECT DISTINCT league, home_team, away_team, bookmaker
    FROM odds
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
      AND commence_time IS NOT NULL 
      AND commence_time > NOW()
    """
    
    cursor.execute(query)
    matches = cursor.fetchall()
    
    movers = []
    
    for league, home_team, away_team, bookmaker in matches:
        # Get opening odds (first in last 24h)
        opening_query = """
        SELECT home_odds, away_odds, draw_odds, timestamp
        FROM odds
        WHERE league = %s 
          AND home_team = %s 
          AND away_team = %s
          AND bookmaker = %s
          AND timestamp >= NOW() - INTERVAL '24 hours'
        ORDER BY timestamp ASC
        LIMIT 1
        """
        
        cursor.execute(opening_query, (league, home_team, away_team, bookmaker))
        opening_row = cursor.fetchone()
        
        # Get latest odds
        latest_query = """
        SELECT home_odds, away_odds, draw_odds, timestamp
        FROM odds
        WHERE league = %s 
          AND home_team = %s 
          AND away_team = %s
          AND bookmaker = %s
          AND timestamp >= NOW() - INTERVAL '24 hours'
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        cursor.execute(latest_query, (league, home_team, away_team, bookmaker))
        latest_row = cursor.fetchone()
        
        if opening_row and latest_row:
            opening_home, opening_away, opening_draw, opening_time = opening_row
            latest_home, latest_away, latest_draw, latest_time = latest_row
            
            # Calculate implied probability deltas (Δpp) for each outcome
            home_delta_pp = delta_pp(opening_home, latest_home)
            draw_delta_pp = delta_pp(opening_draw, latest_draw)
            away_delta_pp = delta_pp(opening_away, latest_away)
            
            if all([home_delta_pp is not None, draw_delta_pp is not None, away_delta_pp is not None]):
                # Find the largest absolute delta_pp
                deltas = [
                    (abs(home_delta_pp), home_delta_pp, 'Home', opening_home, latest_home),
                    (abs(draw_delta_pp), draw_delta_pp, 'Draw', opening_draw, latest_draw),
                    (abs(away_delta_pp), away_delta_pp, 'Away', opening_away, latest_away)
                ]
                max_abs_delta_pp, signed_delta_pp, outcome, opening_odds, latest_odds = max(deltas, key=lambda x: x[0])
                
                # Calculate implied probability percentage change for display (not percentage points)
                prob_pct_change = implied_prob_pct_change(opening_odds, latest_odds)
                
                # Calculate minutes ago
                minutes_ago = int((datetime.now() - latest_time).total_seconds() / 60)
                
                movers.append({
                    'league': league,
                    'home_team': home_team,
                    'away_team': away_team,
                    'outcome': outcome,
                    'delta_pp': signed_delta_pp,  # Keep for internal ranking
                    'abs_delta_pp': max_abs_delta_pp,  # Keep for internal ranking
                    'prob_pct_change': prob_pct_change,  # For display
                    'opening_odds': opening_odds,
                    'latest_odds': latest_odds,
                    'minutes_ago': minutes_ago
                })
    
    conn.close()
    
    # Sort by absolute delta_pp descending and return top 10
    movers.sort(key=lambda x: x['abs_delta_pp'], reverse=True)
    return movers[:10]

def get_odds_direction(history, odds_type):
    """Calculate odds movement direction"""
    if len(history) < 2:
        return None, None
    
    first_value = history[0][odds_type]
    last_value = history[-1][odds_type]
    
    if last_value > first_value:
        return "↑", "green"
    elif last_value < first_value:
        return "↓", "red"
    else:
        return "—", "gray"

# League to country code mapping for flag images
LEAGUE_COUNTRY_CODES = {
    'EPL': 'GB',
    'Italy Serie A': 'IT',
    'Spain La Liga': 'ES',
    'Germany Bundesliga': 'DE',
    'France Ligue One': 'FR'
}

def get_league_flag_html(league):
    """Get flag as HTML img tag using CDN"""
    country_code = LEAGUE_COUNTRY_CODES.get(league, '')
    if country_code:
        # Using flagcdn.com CDN for reliable flag images
        flag_url = f"https://flagcdn.com/w20/{country_code.lower()}.png"
        return f'<img src="{flag_url}" alt="{country_code}" style="width: 20px; height: 15px; vertical-align: middle; margin-right: 4px; border: 1px solid rgba(255,255,255,0.2);">'
    return '⚽'  # Fallback to soccer ball emoji

# League navigation mapping (database name -> display name with flag)
# Using HTML img tags for flags in sidebar
LEAGUE_DISPLAY_NAMES = {
    None: '🌍 All Leagues',
    'EPL': f"{get_league_flag_html('EPL')} Premier League",
    'Italy Serie A': f"{get_league_flag_html('Italy Serie A')} Serie A",
    'Spain La Liga': f"{get_league_flag_html('Spain La Liga')} La Liga",
    'Germany Bundesliga': f"{get_league_flag_html('Germany Bundesliga')} Bundesliga",
    'France Ligue One': f"{get_league_flag_html('France Ligue One')} Ligue 1"
}

def get_league_flag(league):
    """Get flag HTML for a league (for use in markdown)"""
    return get_league_flag_html(league)

# Supported leagues (always show all, even if 0 matches)
SUPPORTED_LEAGUES = ['EPL', 'Italy Serie A', 'Spain La Liga', 'Germany Bundesliga', 'France Ligue One']

# Load current odds
odds_data = load_latest_odds()

# League navigation in sidebar
# Initialize session state for selected league
if 'selected_league' not in st.session_state:
    st.session_state.selected_league = None

st.sidebar.markdown("### Leagues")

# Display clickable league options with flags
for league in [None] + SUPPORTED_LEAGUES:
    if league is None:
        # All Leagues option
        is_selected = st.session_state.selected_league is None
        # Use columns to display flag and button
        col1, col2 = st.sidebar.columns([0.15, 0.85])
        with col1:
            st.markdown("🌍")
        with col2:
            if st.button("All Leagues", key=f"league_{league}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.selected_league = None
                st.rerun()
    else:
        # Individual league options
        flag_html = get_league_flag_html(league)
        league_name = "Premier League" if league == 'EPL' else league.replace('Italy ', '').replace('Spain ', '').replace('Germany ', '').replace('France ', '')
        is_selected = st.session_state.selected_league == league
        
        # Use columns to display flag and button
        col1, col2 = st.sidebar.columns([0.15, 0.85])
        with col1:
            st.markdown(flag_html, unsafe_allow_html=True)
        with col2:
            if st.button(league_name, key=f"league_{league}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state.selected_league = league
                st.rerun()

# Get the selected league value
selected_league = st.session_state.selected_league

# Update status text
if odds_data:
    latest_update = max(row[7] for row in odds_data)
    minutes_ago = int((datetime.now() - latest_update).total_seconds() / 60)
    status_placeholder.markdown(f'<div class="status-text">Feed active · updated {minutes_ago}m ago</div>', unsafe_allow_html=True)
else:
    status_placeholder.markdown('<div class="status-text">Feed active · no data</div>', unsafe_allow_html=True)

# Initialize selected match in session state
if 'selected_match' not in st.session_state:
    st.session_state.selected_match = None

if not odds_data:
    st.warning("No odds data available yet. The data collector may still be gathering initial data.")
    st.info("Check back in a few minutes, or verify that the data collector is running.")
else:
    # Apply league filter
    filtered_data = odds_data
    if selected_league is not None:
        filtered_data = [row for row in filtered_data if row[0] == selected_league]
    
    # Apply search filter
    if search_query:
        search_lower = search_query.lower()
        filtered_data = [row for row in filtered_data 
                        if search_lower in row[1].lower() or search_lower in row[2].lower()]
    
    # Group by date first, then by match
    matches_by_date = {}
    for row in filtered_data:
        league, home, away = row[0], row[1], row[2]
        match_date = row[8].date() if row[8] else row[7].date()  # Use commence_time if available, else timestamp
        
        if match_date not in matches_by_date:
            matches_by_date[match_date] = {}
        
        key = (league, home, away)
        if key not in matches_by_date[match_date]:
            matches_by_date[match_date][key] = []
        matches_by_date[match_date][key].append(row)
    
    # Filter to show only today's matches for compact tape view
    today = datetime.now().date()
    if today in matches_by_date:
        st.markdown("### Today's Tape")
        
        # Build compact table
        table_rows_html = []
        for (league, home, away), match_data in matches_by_date[today].items():
            # Get latest odds for this match (from first bookmaker in match_data, should be Pinnacle)
            latest_row = match_data[0]
            bookmaker = latest_row[3]
            home_odds = latest_row[4]
            draw_odds = latest_row[6]
            away_odds = latest_row[5]
            commence_time = latest_row[8] if latest_row[8] else None
            timestamp = latest_row[7]
            
            # Format kickoff time
            if commence_time:
                kickoff_str = commence_time.strftime('%H:%M')
            else:
                kickoff_str = "—"
            
            # Calculate minutes ago
            minutes_ago_val = int((datetime.now() - timestamp).total_seconds() / 60)
            if minutes_ago_val < 1:
                updated_str = "just now"
            else:
                updated_str = f"{minutes_ago_val}m ago"
            
            # Get biggest mover
            current_odds_dict = {
                'home_odds': home_odds,
                'draw_odds': draw_odds,
                'away_odds': away_odds
            }
            biggest_mover = get_biggest_mover_for_match(league, home, away, bookmaker, current_odds_dict, window_timedelta)
            
            # Format mover info
            if biggest_mover:
                mover_display = f"{biggest_mover['outcome']} — <span style='color: {biggest_mover['movement_color']};'>{biggest_mover['movement_text']}</span> ({biggest_mover['opening_odds']:.2f} → {biggest_mover['current_odds']:.2f})"
                strength_badge_html = ""
                if biggest_mover['strength_badge']:
                    badge_class = biggest_mover['strength_badge'].lower()
                    strength_badge_html = f"<span class='strength-badge-tape {badge_class}'>{biggest_mover['strength_badge']}</span>"
            else:
                mover_display = "—"
                strength_badge_html = ""
            
            # Create match key for selection
            match_key = f"{league}_{home}_{away}"
            is_selected = st.session_state.selected_match == match_key
            
            # Build row HTML
            row_class = "tape-row selected" if is_selected else "tape-row"
            row_html = f"""
            <tr class="{row_class}" onclick="window.location.hash='match_{match_key}'" style="cursor: pointer;">
                <td>{kickoff_str}</td>
                <td><strong>{home} vs {away}</strong></td>
                <td style="text-align: center;">{home_odds:.2f} / {draw_odds:.2f} / {away_odds:.2f}</td>
                <td>{mover_display}</td>
                <td>{strength_badge_html}</td>
                <td style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">{updated_str}</td>
            </tr>
            """
            table_rows_html.append((match_key, row_html, (league, home, away), match_data))
        
        # Display table with clickable rows
        if table_rows_html:
            # Create table header
            tape_table_html = """
            <table class="tape-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Match</th>
                        <th style="text-align: center;">1X2 Odds</th>
                        <th>Biggest Mover</th>
                        <th>Strength</th>
                        <th>Updated</th>
                    </tr>
                </thead>
                <tbody>
            """
            for match_key, row_html, match_info, match_data in table_rows_html:
                tape_table_html += row_html
            tape_table_html += "</tbody></table>"
            st.markdown(tape_table_html, unsafe_allow_html=True)
            
            # Store match data in session state for detail view access
            if 'match_data_cache' not in st.session_state:
                st.session_state.match_data_cache = {}
            
            # Create clickable row buttons (positioned below table for selection)
            st.markdown("<br>", unsafe_allow_html=True)
            match_options = ["— Select a match —"] + [f"{h} vs {a} ({l})" for _, _, (l, h, a), _ in table_rows_html]
            match_keys_list = [None] + [mk for mk, _, _, _ in table_rows_html]
            
            selected_idx = 0
            if st.session_state.selected_match:
                try:
                    selected_idx = match_keys_list.index(st.session_state.selected_match)
                except ValueError:
                    selected_idx = 0
            
            selected_match_display = st.selectbox("Select match for details", match_options, index=selected_idx, key="match_selector")
            
            if selected_match_display != "— Select a match —":
                selected_match_idx = match_options.index(selected_match_display) - 1
                st.session_state.selected_match = match_keys_list[selected_match_idx + 1]
                # Store match data
                _, _, match_info, match_data = table_rows_html[selected_match_idx]
                st.session_state.match_data_cache[st.session_state.selected_match] = (match_info, match_data)
            else:
                st.session_state.selected_match = None
        else:
            st.info("No matches found for today.")
    
    # Display selected match detail view
    if st.session_state.selected_match and 'match_data_cache' in st.session_state:
        if st.session_state.selected_match in st.session_state.match_data_cache:
            match_info, selected_match_data = st.session_state.match_data_cache[st.session_state.selected_match]
            league, home, away = match_info
            
            st.markdown("---")
            st.markdown(f"### {home} vs {away} ({league})")
            
            # Display full match detail view
            league_flag_html = get_league_flag(league)
            flag_col, detail_col = st.columns([0.05, 0.95])
            with flag_col:
                st.markdown(league_flag_html, unsafe_allow_html=True)
            with detail_col:
                    # Display odds table
                    st.markdown("#### Current Odds")
                    
                    # Create table with opening odds comparison
                    table_rows = []
                    for row in selected_match_data:
                        bookmaker = row[3]
                        home_odds = row[4]
                        draw_odds = row[6]
                        away_odds = row[5]
                        timestamp = row[7].strftime('%H:%M:%S')
                        
                        # Get opening odds for this bookmaker with time window
                        opening = get_opening_odds(league, home, away, bookmaker, window_timedelta)
                        
                        # Format Home odds with Open, Current, and implied probability change
                        if opening:
                            home_prob_pct = implied_prob_pct_change(opening['home_odds'], home_odds)
                            if home_prob_pct is not None:
                                # Determine shortened/drifted
                                if home_odds < opening['home_odds']:
                                    home_movement = "shortened"
                                    home_color = "#44ff44"  # Green
                                    home_arrow = "↓"
                                else:
                                    home_movement = "drifted"
                                    home_color = "#ff4444"  # Red
                                    home_arrow = "↑"
                                home_prob_display = f"<span style='color: {home_color}; font-weight: bold;'>{home_arrow} {home_prob_pct:+.1f}%</span>"
                                home_display = f"{opening['home_odds']:.2f} → {home_odds:.2f} ({home_movement}) {home_prob_display}"
                            else:
                                home_display = f"{opening['home_odds']:.2f} → {home_odds:.2f}"
                        else:
                            home_display = f"{home_odds:.2f} (No opening data)"
                        
                        # Format Draw odds
                        if opening:
                            draw_prob_pct = implied_prob_pct_change(opening['draw_odds'], draw_odds)
                            if draw_prob_pct is not None:
                                if draw_odds < opening['draw_odds']:
                                    draw_movement = "shortened"
                                    draw_color = "#44ff44"
                                    draw_arrow = "↓"
                                else:
                                    draw_movement = "drifted"
                                    draw_color = "#ff4444"
                                    draw_arrow = "↑"
                                draw_prob_display = f"<span style='color: {draw_color}; font-weight: bold;'>{draw_arrow} {draw_prob_pct:+.1f}%</span>"
                                draw_display = f"{opening['draw_odds']:.2f} → {draw_odds:.2f} ({draw_movement}) {draw_prob_display}"
                            else:
                                draw_display = f"{opening['draw_odds']:.2f} → {draw_odds:.2f}"
                        else:
                            draw_display = f"{draw_odds:.2f} (No opening data)"
                        
                        # Format Away odds
                        if opening:
                            away_prob_pct = implied_prob_pct_change(opening['away_odds'], away_odds)
                            if away_prob_pct is not None:
                                if away_odds < opening['away_odds']:
                                    away_movement = "shortened"
                                    away_color = "#44ff44"
                                    away_arrow = "↓"
                                else:
                                    away_movement = "drifted"
                                    away_color = "#ff4444"
                                    away_arrow = "↑"
                                away_prob_display = f"<span style='color: {away_color}; font-weight: bold;'>{away_arrow} {away_prob_pct:+.1f}%</span>"
                                away_display = f"{opening['away_odds']:.2f} → {away_odds:.2f} ({away_movement}) {away_prob_display}"
                            else:
                                away_display = f"{opening['away_odds']:.2f} → {away_odds:.2f}"
                        else:
                            away_display = f"{away_odds:.2f} (No opening data)"
                        
                        table_rows.append({
                            'Bookmaker': bookmaker,
                            'Home': home_display,
                            'Draw': draw_display,
                            'Away': away_display,
                            'Updated': timestamp
                        })
                    
                    # Create HTML table
                    html_table = "<div class='odds-table-container'>"
                    html_table += "<table class='odds-table-desktop' style='width: 100%; border-collapse: collapse;'>"
                    html_table += "<thead><tr style='border-bottom: 2px solid rgba(255,255,255,0.2);'>"
                    html_table += "<th style='text-align: left; padding: 8px;'>Bookmaker</th>"
                    html_table += "<th style='text-align: center; padding: 8px;'>Home</th>"
                    html_table += "<th style='text-align: center; padding: 8px;'>Draw</th>"
                    html_table += "<th style='text-align: center; padding: 8px;'>Away</th>"
                    html_table += "<th style='text-align: right; padding: 8px;'>Updated</th>"
                    html_table += "</tr></thead><tbody>"
                    
                    for row_data in table_rows:
                        html_table += "<tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>"
                        html_table += f"<td style='padding: 8px;'><strong>{row_data['Bookmaker']}</strong></td>"
                        html_table += f"<td style='padding: 8px; text-align: center;'>{row_data['Home']}</td>"
                        html_table += f"<td style='padding: 8px; text-align: center;'>{row_data['Draw']}</td>"
                        html_table += f"<td style='padding: 8px; text-align: center;'>{row_data['Away']}</td>"
                        html_table += f"<td style='padding: 8px; text-align: right;'>{row_data['Updated']}</td>"
                        html_table += "</tr>"
                    
                    html_table += "</tbody></table></div>"
                    st.markdown(html_table, unsafe_allow_html=True)
                    
                    # Historical trends
                    history_data = load_odds_history(league, home, away, hours=24)
                    
                    if history_data and len(history_data) >= 2:
                        # Process history data
                        history = []
                        for row in history_data:
                            history.append({
                                'timestamp': row[4],
                                'home_odds': row[1],
                                'draw_odds': row[3],
                                'away_odds': row[2]
                            })
                        
                        history.sort(key=lambda x: x['timestamp'])
                        
                        seen_timestamps = set()
                        unique_history = []
                        for h in reversed(history):
                            if h['timestamp'] not in seen_timestamps:
                                seen_timestamps.add(h['timestamp'])
                                unique_history.append(h)
                        unique_history.reverse()
                        
                        if len(unique_history) >= 2:
                            timestamps = [h['timestamp'] for h in unique_history]
                        home_vals = [float(h['home_odds']) for h in unique_history]
                        draw_vals = [float(h['draw_odds']) for h in unique_history]
                        away_vals = [float(h['away_odds']) for h in unique_history]
                        
                        home_open = home_vals[0]
                        home_now = home_vals[-1]
                        draw_open = draw_vals[0]
                        draw_now = draw_vals[-1]
                        away_open = away_vals[0]
                        away_now = away_vals[-1]
                        
                        match_key_detail = f"{league}_{home}_{away}_detail_tab"
                        selected_tab = st.radio(
                            "Outcome",
                            ["Home", "Draw", "Away"],
                            key=match_key_detail,
                            horizontal=True,
                            label_visibility="collapsed"
                        )
                        
                        st.markdown("#### Odds Movement (Last 24h)")
                        
                        def create_focused_graph(timestamps, values, outcome_name, color, open_val, now_val):
                            if values:
                                y_min = min(values)
                                y_max = max(values)
                                padding = (y_max - y_min) * 0.05
                                if padding == 0:
                                    padding = y_min * 0.01 if y_min > 0 else 0.1
                                y_range = [max(0, y_min - padding), y_max + padding]
                            else:
                                y_range = None
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=timestamps,
                                y=values,
                                mode='lines+markers',
                                name=outcome_name,
                                line=dict(color=color, width=2),
                                marker=dict(size=4)
                            ))
                            
                            fig.update_layout(
                                height=400,
                                xaxis_title="Time",
                                yaxis_title="Odds",
                                yaxis=dict(range=y_range) if y_range else {},
                                hovermode='x unified',
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='white')
                            )
                            
                            return fig
                        
                        if selected_tab == "Home":
                            st.markdown(f"**Open:** {home_open:.2f} • **Now:** {home_now:.2f}")
                            fig_home = create_focused_graph(timestamps, home_vals, 'Home', '#FF6B6B', home_open, home_now)
                            st.plotly_chart(fig_home, use_container_width=True)
                        elif selected_tab == "Draw":
                            st.markdown(f"**Open:** {draw_open:.2f} • **Now:** {draw_now:.2f}")
                            fig_draw = create_focused_graph(timestamps, draw_vals, 'Draw', '#4ECDC4', draw_open, draw_now)
                            st.plotly_chart(fig_draw, use_container_width=True)
                        else:  # Away
                            st.markdown(f"**Open:** {away_open:.2f} • **Now:** {away_now:.2f}")
                            fig_away = create_focused_graph(timestamps, away_vals, 'Away', '#95E1D3', away_open, away_now)
                            st.plotly_chart(fig_away, use_container_width=True)
                    else:
                        st.info("Not enough historical data yet. Check back after a few updates.")
    
    # Auto-refresh toggle
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=False)
    
    if auto_refresh:
        st.sidebar.info("Page will refresh every 60 seconds")
        import time
        time.sleep(60)
        st.rerun()

# Footer
st.markdown("---")
st.caption("OddsEdge - Professional Odds Tracking | Data updates every 15 minutes")
