"""
Unit tests for implied probability helper functions
"""

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

# Test cases
if __name__ == "__main__":
    print("Running implied probability tests...")
    
    # Test 1: Basic implied probability calculation
    assert implied_prob(2.0) == 0.5, "implied_prob(2.0) should be 0.5 (50%)"
    assert implied_prob(4.0) == 0.25, "implied_prob(4.0) should be 0.25 (25%)"
    assert implied_prob(1.5) == 1.0 / 1.5, "implied_prob(1.5) should be 1/1.5"
    assert implied_prob(1.0) is None, "implied_prob(1.0) should be None (invalid odds)"
    assert implied_prob(None) is None, "implied_prob(None) should be None"
    print("[PASS] implied_prob tests passed")
    
    # Test 2: Delta percentage points (Δpp)
    # Odds 2.0 (50%) -> 1.5 (66.67%): Δpp = +16.67pp
    delta = delta_pp(2.0, 1.5)
    assert abs(delta - 16.67) < 0.1, f"delta_pp(2.0, 1.5) should be ~16.67pp, got {delta}"
    
    # Odds 2.0 (50%) -> 3.0 (33.33%): Δpp = -16.67pp
    delta = delta_pp(2.0, 3.0)
    assert abs(delta - (-16.67)) < 0.1, f"delta_pp(2.0, 3.0) should be ~-16.67pp, got {delta}"
    
    # Odds 1.5 (66.67%) -> 2.0 (50%): Δpp = -16.67pp
    delta = delta_pp(1.5, 2.0)
    assert abs(delta - (-16.67)) < 0.1, f"delta_pp(1.5, 2.0) should be ~-16.67pp, got {delta}"
    
    # Same odds: Δpp = 0
    assert delta_pp(2.0, 2.0) == 0.0, "delta_pp(2.0, 2.0) should be 0.0"
    
    # Invalid odds
    assert delta_pp(1.0, 2.0) is None, "delta_pp(1.0, 2.0) should be None"
    assert delta_pp(2.0, None) is None, "delta_pp(2.0, None) should be None"
    print("[PASS] delta_pp tests passed")
    
    # Test 3: Delta odds percentage
    # Odds 2.0 -> 1.5: (1.5/2.0 - 1) * 100 = -25%
    delta = delta_odds_pct(2.0, 1.5)
    assert abs(delta - (-25.0)) < 0.1, f"delta_odds_pct(2.0, 1.5) should be ~-25%, got {delta}"
    
    # Odds 2.0 -> 3.0: (3.0/2.0 - 1) * 100 = +50%
    delta = delta_odds_pct(2.0, 3.0)
    assert abs(delta - 50.0) < 0.1, f"delta_odds_pct(2.0, 3.0) should be ~50%, got {delta}"
    
    # Same odds: 0%
    assert delta_odds_pct(2.0, 2.0) == 0.0, "delta_odds_pct(2.0, 2.0) should be 0.0"
    
    # Invalid odds
    assert delta_odds_pct(0, 2.0) is None, "delta_odds_pct(0, 2.0) should be None"
    assert delta_odds_pct(2.0, None) is None, "delta_odds_pct(2.0, None) should be None"
    print("[PASS] delta_odds_pct tests passed")
    
    # Test 4: Real-world examples
    # Example: Odds shortening from 2.20 to 1.90
    # Implied prob: 45.45% -> 52.63%, Δpp = +7.18pp
    delta = delta_pp(2.20, 1.90)
    assert abs(delta - 7.18) < 0.1, f"delta_pp(2.20, 1.90) should be ~7.18pp, got {delta}"
    
    # Odds % change: (1.90/2.20 - 1) * 100 = -13.64%
    odds_delta = delta_odds_pct(2.20, 1.90)
    assert abs(odds_delta - (-13.64)) < 0.1, f"delta_odds_pct(2.20, 1.90) should be ~-13.64%, got {odds_delta}"
    
    # Example: Odds drifting from 2.10 to 2.30
    # Implied prob: 47.62% -> 43.48%, Δpp = -4.14pp
    delta = delta_pp(2.10, 2.30)
    assert abs(delta - (-4.14)) < 0.1, f"delta_pp(2.10, 2.30) should be ~-4.14pp, got {delta}"
    
    # Odds % change: (2.30/2.10 - 1) * 100 = +9.52%
    odds_delta = delta_odds_pct(2.10, 2.30)
    assert abs(odds_delta - 9.52) < 0.1, f"delta_odds_pct(2.10, 2.30) should be ~9.52%, got {odds_delta}"
    print("[PASS] Real-world example tests passed")
    
    print("\n[SUCCESS] All tests passed!")
