"""
Unit test for Move calculation sign verification.
Tests that the sign correctly reflects probability changes.
"""

def calculate_no_vig_probabilities(home_odds, draw_odds, away_odds):
    """Calculate no-vig implied probabilities from odds"""
    # Implied probabilities
    home_prob = 1.0 / home_odds
    draw_prob = 1.0 / draw_odds
    away_prob = 1.0 / away_odds
    
    # Total implied probability (includes vig)
    total = home_prob + draw_prob + away_prob
    
    # Remove vig by normalizing
    home_no_vig = home_prob / total
    draw_no_vig = draw_prob / total
    away_no_vig = away_prob / total
    
    return home_no_vig, draw_no_vig, away_no_vig

def test_move_calculation():
    """Test Move calculation with known values"""
    
    print("Testing Move calculation sign...")
    print("=" * 60)
    
    # Test Case 1: Odds increase -> Probability decreases -> Should show NEGATIVE
    print("\nTest Case 1: Away odds increase (4.56 -> 8.88)")
    open_home, open_draw, open_away = 2.09, 2.97, 4.56
    current_home, current_draw, current_away = 2.09, 2.97, 8.88
    
    open_probs = calculate_no_vig_probabilities(open_home, open_draw, open_away)
    current_probs = calculate_no_vig_probabilities(current_home, current_draw, current_away)
    
    # Calculate Away probability delta: p_now_nv - p_open_nv
    away_prob_delta = current_probs[2] - open_probs[2]
    away_prob_change_percent = abs(away_prob_delta) / open_probs[2] * 100
    
    print(f"  Open Away odds: {open_away:.2f} -> Probability: {open_probs[2]:.4f} ({open_probs[2]*100:.2f}%)")
    print(f"  Current Away odds: {current_away:.2f} -> Probability: {current_probs[2]:.4f} ({current_probs[2]*100:.2f}%)")
    print(f"  Probability delta (p_now - p_open): {away_prob_delta:.6f}")
    print(f"  Percentage change: {away_prob_change_percent:.2f}%")
    
    # Sign should be NEGATIVE (probability decreased)
    expected_sign = '-'
    actual_sign = '+' if away_prob_delta > 0 else '-'
    
    print(f"  Expected sign: {expected_sign}")
    print(f"  Actual sign: {actual_sign}")
    
    if actual_sign == expected_sign:
        print("  [PASS] Sign is correct (negative when odds increase)")
    else:
        print("  [FAIL] Sign is incorrect!")
    
    # Test Case 2: Odds decrease -> Probability increases -> Should show POSITIVE
    print("\nTest Case 2: Home odds decrease (2.22 -> 1.44)")
    open_home2, open_draw2, open_away2 = 2.22, 3.00, 4.15
    current_home2, current_draw2, current_away2 = 1.44, 3.83, 8.93
    
    open_probs2 = calculate_no_vig_probabilities(open_home2, open_draw2, open_away2)
    current_probs2 = calculate_no_vig_probabilities(current_home2, current_draw2, current_away2)
    
    # Calculate Home probability delta
    home_prob_delta = current_probs2[0] - open_probs2[0]
    home_prob_change_percent = abs(home_prob_delta) / open_probs2[0] * 100
    
    print(f"  Open Home odds: {open_home2:.2f} -> Probability: {open_probs2[0]:.4f} ({open_probs2[0]*100:.2f}%)")
    print(f"  Current Home odds: {current_home2:.2f} -> Probability: {current_probs2[0]:.4f} ({current_probs2[0]*100:.2f}%)")
    print(f"  Probability delta (p_now - p_open): {home_prob_delta:.6f}")
    print(f"  Percentage change: {home_prob_change_percent:.2f}%")
    
    # Sign should be POSITIVE (probability increased)
    expected_sign2 = '+'
    actual_sign2 = '+' if home_prob_delta > 0 else '-'
    
    print(f"  Expected sign: {expected_sign2}")
    print(f"  Actual sign: {actual_sign2}")
    
    if actual_sign2 == expected_sign2:
        print("  [PASS] Sign is correct (positive when odds decrease)")
    else:
        print("  [FAIL] Sign is incorrect!")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Test 1 (odds increase): {'PASS' if actual_sign == expected_sign else 'FAIL'}")
    print(f"  Test 2 (odds decrease): {'PASS' if actual_sign2 == expected_sign2 else 'FAIL'}")

if __name__ == "__main__":
    test_move_calculation()
