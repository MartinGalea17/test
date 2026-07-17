import random 


players_money = 100

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
    # ===== 6 OF A KIND =====
    tuple(sorted(["🐟"] * 6)): 1000,
    tuple(sorted(["🌊"] * 6)): 1200,
    tuple(sorted(["🐚"] * 6)): 1500,
    tuple(sorted(["🪼"] * 6)): 2000,
    tuple(sorted(["🐬"] * 6)): 3000,
    tuple(sorted(["🧜"] * 6)): 5000,

    # ===== 5 OF A KIND + 1 =====
    tuple(sorted(["🐟"] * 5 + ["🌊"])): 500,
    tuple(sorted(["🌊"] * 5 + ["🐚"])): 600,
    tuple(sorted(["🐚"] * 5 + ["🪼"])): 700,
    tuple(sorted(["🪼"] * 5 + ["🐬"])): 900,
    tuple(sorted(["🐬"] * 5 + ["🧜"])): 1200,

    # ===== 4 OF A KIND + PAIR =====
    tuple(sorted(["🐟"] * 4 + ["🌊"] * 2)): 300,
    tuple(sorted(["🌊"] * 4 + ["🐚"] * 2)): 350,
    tuple(sorted(["🐚"] * 4 + ["🪼"] * 2)): 450,
    tuple(sorted(["🪼"] * 4 + ["🐬"] * 2)): 600,
    tuple(sorted(["🐬"] * 4 + ["🧜"] * 2)): 800,

    # ===== FULL HOUSE (3 + 3) =====
    tuple(sorted(["🐟"] * 3 + ["🌊"] * 3)): 250,
    tuple(sorted(["🌊"] * 3 + ["🐚"] * 3)): 300,
    tuple(sorted(["🐚"] * 3 + ["🪼"] * 3)): 400,
    tuple(sorted(["🪼"] * 3 + ["🐬"] * 3)): 600,
    tuple(sorted(["🐬"] * 3 + ["🧜"] * 3)): 1000,

    # ===== THREE PAIRS =====
    tuple(sorted(["🐟"] * 2 + ["🌊"] * 2 + ["🐚"] * 2)): 150,
    tuple(sorted(["🌊"] * 2 + ["🐚"] * 2 + ["🪼"] * 2)): 175,
    tuple(sorted(["🐚"] * 2 + ["🪼"] * 2 + ["🐬"] * 2)): 225,
    tuple(sorted(["🪼"] * 2 + ["🐬"] * 2 + ["🧜"] * 2)): 300,

    # ===== ALL SIX DIFFERENT =====
    tuple(sorted(["🐟", "🌊", "🐬", "🪼", "🧜", "🐚"])): 500,

    # ===== 4 OF A KIND + TWO SINGLES =====
    tuple(sorted(["🐟"] * 4 + ["🐚", "🐬"])): 200,
    tuple(sorted(["🌊"] * 4 + ["🪼", "🧜"])): 250,
    tuple(sorted(["🐚"] * 4 + ["🐟", "🧜"])): 300,
    tuple(sorted(["🪼"] * 4 + ["🌊", "🐬"])): 350,
    tuple(sorted(["🐬"] * 4 + ["🐟", "🐚"])): 450,

    # ===== 5 UNIQUE + PAIR =====
    tuple(sorted(["🐟", "🌊", "🐬", "🪼", "🧜", "🧜"])): 180,
    tuple(sorted(["🐟", "🌊", "🐬", "🪼", "🐚", "🐚"])): 180,
    tuple(sorted(["🐟", "🌊", "🐬", "🐚", "🧜", "🧜"])): 200,

    # ===== JACKPOT BONUS PATTERNS =====
    tuple(sorted(["🧜"] * 3 + ["🐬"] * 2 + ["🪼"])): 1500,
    tuple(sorted(["🧜"] * 2 + ["🐬"] * 2 + ["🪼"] * 2)): 2000,
    tuple(sorted(["🧜"] * 4 + ["🐬"] * 2)): 2500,
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
    special_spin = random.choices(special_symbols, weights=special_weights, k=6)
    return special_spin

def calculate_payout(spin, payout_table):
    combination = tuple(sorted(spin))
    payout = payout_table.get(combination, 0)
    return payout

def calculate_special_payout(spin,special_payout_table):
    combination = tuple(sorted(spin))
    special_payout = special_payout_table.get(combination,0)
    return special_payout

def calculate_payin():
    pass




#call functions
spin = spin_reels()

payout = calculate_payout(spin, payout_table)
special_payout = calculate_special_payout(spin, special_payout_table)


print("Your Result:")
print(" ")
print(" | ".join(spin))
print(f"Payout: €{payout}")

print("You just won 5 special spins!")

total_special_payout = 0

if spin == "💎💎💎":
    for i in range(5):
        special_spin = spin_special_reels()
        payout = calculate_special_payout(special_spin, special_payout_table)
        total_special_payout += payout

        print(f"\nSpecial Spin {i+1}:")
        print(" | ".join(special_spin))
        print(f"Payout: €{payout}")

print(f"\nTotal Special Winnings: €{total_special_payout}")

    