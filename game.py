import random 


players_money = 100
spin_cost = 5

payout_table = {

# winning combinations
    tuple(sorted(["🍒", "🍒", "🍋"])): 5,
    tuple(sorted(["🍒", "7️⃣", "7️⃣"])): 15,
    tuple(sorted(["🔔", "7️⃣", "💎"])): 25,

    tuple(sorted(["🍋", "🍋", "🍋"])): 8,
    tuple(sorted(["🍒", "🍒", "🍒"])): 10,
    tuple(sorted(["🔔", "🔔", "🔔"])): 20,
    tuple(sorted(["💎", "💎", "💎"])): 50,
    tuple(sorted(["7️⃣", "7️⃣", "7️⃣"])): 100,

    tuple(sorted(["🍋", "🍋", "🍒"])): 4,
    tuple(sorted(["🍒", "🍒", "🔔"])): 12,
    tuple(sorted(["🔔", "🔔", "💎"])): 30,
    tuple(sorted(["💎", "💎", "7️⃣"])): 75,

    tuple(sorted(["🍒", "💎", "💎"])): 35,
    tuple(sorted(["🍋", "💎", "💎"])): 30,
    tuple(sorted(["🍒", "🔔", "🔔"])): 18,
    tuple(sorted(["🍋", "7️⃣", "7️⃣"])): 20,
    tuple(sorted(["🔔", "7️⃣", "7️⃣"])): 40,

    tuple(sorted(["🍒", "🔔", "💎"])): 15,
    tuple(sorted(["🍋", "🔔", "💎"])): 18,
    tuple(sorted(["🍋", "🍒", "7️⃣"])): 10,
}


special_payout_table = {
    # ==================================================
    # SIX OF A KIND
    # ==================================================
    tuple(sorted(["🐟"] * 6)): 1000,
    tuple(sorted(["🌊"] * 6)): 1200,
    tuple(sorted(["🐬"] * 6)): 1800,
    tuple(sorted(["🪼"] * 6)): 2200,
    tuple(sorted(["🧜"] * 6)): 3000,
    tuple(sorted(["🐚"] * 6)): 4000,

    # ==================================================
    # FIVE OF A KIND + ONE OTHER SYMBOL
    # ==================================================
    tuple(sorted(["🐟"] * 5 + ["🌊"])): 400,
    tuple(sorted(["🌊"] * 5 + ["🐬"])): 450,
    tuple(sorted(["🐬"] * 5 + ["🪼"])): 600,
    tuple(sorted(["🪼"] * 5 + ["🧜"])): 750,
    tuple(sorted(["🧜"] * 5 + ["🐚"])): 1000,
    tuple(sorted(["🐚"] * 5 + ["🐟"])): 1300,

    # ==================================================
    # FOUR OF A KIND + ONE PAIR
    # ==================================================
    tuple(sorted(["🐟"] * 4 + ["🌊"] * 2)): 250,
    tuple(sorted(["🌊"] * 4 + ["🐬"] * 2)): 300,
    tuple(sorted(["🐬"] * 4 + ["🪼"] * 2)): 400,
    tuple(sorted(["🪼"] * 4 + ["🧜"] * 2)): 500,
    tuple(sorted(["🧜"] * 4 + ["🐚"] * 2)): 700,
    tuple(sorted(["🐚"] * 4 + ["🐟"] * 2)): 900,

    # ==================================================
    # FOUR OF A KIND + TWO DIFFERENT SYMBOLS
    # ==================================================
    tuple(sorted(["🐟"] * 4 + ["🐬", "🧜"])): 180,
    tuple(sorted(["🌊"] * 4 + ["🪼", "🐚"])): 220,
    tuple(sorted(["🐬"] * 4 + ["🐟", "🧜"])): 300,
    tuple(sorted(["🪼"] * 4 + ["🌊", "🐚"])): 380,
    tuple(sorted(["🧜"] * 4 + ["🐟", "🐬"])): 500,
    tuple(sorted(["🐚"] * 4 + ["🌊", "🪼"])): 650,

    # ==================================================
    # FULL HOUSE: THREE OF ONE + THREE OF ANOTHER
    # ==================================================
    tuple(sorted(["🐟"] * 3 + ["🌊"] * 3)): 220,
    tuple(sorted(["🐟"] * 3 + ["🐬"] * 3)): 270,
    tuple(sorted(["🐟"] * 3 + ["🪼"] * 3)): 320,
    tuple(sorted(["🌊"] * 3 + ["🧜"] * 3)): 400,
    tuple(sorted(["🐬"] * 3 + ["🐚"] * 3)): 550,
    tuple(sorted(["🪼"] * 3 + ["🧜"] * 3)): 650,

    # ==================================================
    # THREE DIFFERENT PAIRS
    # ==================================================
    tuple(sorted(["🐟"] * 2 + ["🌊"] * 2 + ["🐬"] * 2)): 100,
    tuple(sorted(["🐟"] * 2 + ["🪼"] * 2 + ["🧜"] * 2)): 140,
    tuple(sorted(["🌊"] * 2 + ["🐬"] * 2 + ["🐚"] * 2)): 180,
    tuple(sorted(["🌊"] * 2 + ["🪼"] * 2 + ["🐚"] * 2)): 220,
    tuple(sorted(["🐬"] * 2 + ["🧜"] * 2 + ["🐚"] * 2)): 280,

    # ==================================================
    # THREE OF A KIND + ONE PAIR + ONE SINGLE
    # ==================================================
    tuple(sorted(["🐟"] * 3 + ["🌊"] * 2 + ["🐬"])): 60,
    tuple(sorted(["🌊"] * 3 + ["🐬"] * 2 + ["🪼"])): 70,
    tuple(sorted(["🐬"] * 3 + ["🪼"] * 2 + ["🧜"])): 90,
    tuple(sorted(["🪼"] * 3 + ["🧜"] * 2 + ["🐚"])): 110,
    tuple(sorted(["🧜"] * 3 + ["🐚"] * 2 + ["🐟"])): 140,
    tuple(sorted(["🐚"] * 3 + ["🐟"] * 2 + ["🌊"])): 160,

    # ==================================================
    # BASIC THREE OF A KIND + THREE DIFFERENT SINGLES
    # Low payouts
    # ==================================================
    tuple(sorted(["🐟"] * 3 + ["🌊", "🐬", "🪼"])): 30,
    tuple(sorted(["🌊"] * 3 + ["🐟", "🐬", "🧜"])): 30,
    tuple(sorted(["🐬"] * 3 + ["🐟", "🪼", "🐚"])): 40,
    tuple(sorted(["🪼"] * 3 + ["🌊", "🐬", "🧜"])): 45,
    tuple(sorted(["🧜"] * 3 + ["🐟", "🪼", "🐚"])): 60,
    tuple(sorted(["🐚"] * 3 + ["🌊", "🐬", "🧜"])): 75,

    # ==================================================
    # ALL SIX SYMBOLS DIFFERENT
    # ==================================================
    tuple(sorted(["🐟", "🌊", "🐬", "🪼", "🧜", "🐚"])): 300,
}

symbols = ["🍒", "🍋", "🔔", "7️⃣", "💎"]

weights = [30, 30, 15, 15,80 ]

special_symbols = ["🐟","🌊","🐬","🪼","🧜","🐚"]

special_weights =[20,20,20,13,13,10]

def spin_reels():
    result = random.choices(
    symbols,weights=weights,k=3)
    return result

def spin_special_reels():
    special_spin = random.choices(
        special_symbols, weights=special_weights, k=6)
    return special_spin

def spin_jackpot_round():
    pass

def calculate_payout(spin, payout_table):
    combination = tuple(sorted(spin))
    payout = payout_table.get(combination, 0)
    return payout

def calculate_special_payout(spin,special_payout_table):
    combination = tuple(sorted(spin))
    special_payout = special_payout_table.get(combination,0)
    return special_payout

def calculate_payin(players_money, spin_cost):
    players_money -= spin_cost
    return players_money




#call functions
spin = spin_reels()

normal_payout = calculate_payout(spin, payout_table)
special_payout = calculate_special_payout(spin, special_payout_table)
payin = calculate_payin(players_money,spin_cost)

players_money += normal_payout

print(f"Your Balance:{players_money}")
print("Your Result:")
print(" ")
print(" | ".join(spin))
print(f"Payout: €{normal_payout}")



total_special_payout = 0

if spin == ["💎","💎","💎"]:
    print("🎇You just won 5 special spins!🎇")
    for i in range(5):
        special_spin = spin_special_reels()
        payout = calculate_special_payout(special_spin, special_payout_table)
        total_special_payout += payout

        print(f"\nSpecial Spin {i+1}:")
        print(" | ".join(special_spin))
        print(f"Payout: €{payout}")

    print(f"\nTotal Special Winnings: €{total_special_payout}")
    print(f"\nTotal winnings for this round:€{total_special_payout + normal_payout}")









special_symbols_price = {
    "🐟": 20,
    "🌊": 20,
    "🐬": 30,
    "🪼": 30,
    "🧜": 50,
    "🐚": 50
}

def calc_special_price():
    payout_table = {}
    for symbol, baseprice in special_symbols_price.items():
        combination = tuple(sorted([symbol]*6))
        price = baseprice * 25
        payout_table[combination] = price
        
        for extra_symbol in special_symbols_price:
            if extra_symbol != symbol:
                # Five copies of symbol plus extra_symbol
                combination = tuple(sorted([symbol] *5 + [extra_symbol]))
                price = baseprice * 12

                payout_table[combination] = price
                
        for pair_symbol in special_symbols_price:
            if pair_symbol != symbol:
                # Five copies of symbol plus extra_symbol
                combination = tuple(sorted([symbol] *4 + [pair_symbol] *2))
                price = baseprice * 9

                payout_table[combination] = price    
                
        for triple_symbol in special_symbols_price:
            if triple_symbol != symbol:
                # Five copies of symbol plus extra_symbol
                combination = tuple(sorted([symbol] *3 + [triple_symbol] *3))
                price = baseprice * 6

                payout_table[combination] = price 
        
    return payout_table
    
price = calc_special_price()

print(len(price))  
