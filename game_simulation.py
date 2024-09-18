

import os
import numpy as np
import json
import random

def game_simulation_with_probabilities(rounds=1000, total_cards=False, data_file='game_data.json', deck_file='deck_history.json', win_counts_file='win_counts.json'):
    
    def create_hands():
        sequences = []
        for i in range(8):
            seq = [(i >> j) & 1 for j in range(2, -1, -1)]
            sequences.append(seq)
        return sequences

    def binary_to_string(seq):
        return ''.join(['R' if bit == 1 else 'B' for bit in seq])

    def deck_to_string(deck):
        return ''.join(['R' if card == 1 else 'B' for card in deck])

    def game_simulation(sequences, deck, total_cards=False):
        win_matrix = np.zeros((8, 8))
        player1_wins = 0
        player2_wins = 0

        for i, player1_seq in enumerate(sequences):
            for j, player2_seq in enumerate(sequences):
                points_player_1, points_player_2 = 0, 0
                cards_player_1, cards_player_2 = 0, 0
                card_pile = []

                k = 0
                while k <= len(deck) - 3:
                    current_sequence = deck[k:k+3]
                    card_pile += deck[k:k+3]

                    if current_sequence == player1_seq:
                        if total_cards:
                            cards_player_1 += len(card_pile)
                            card_pile = []
                        else:
                            points_player_1 += 1
                        k += 3
                    elif current_sequence == player2_seq:
                        if total_cards:
                            cards_player_2 += len(card_pile)
                            card_pile = []
                        else:
                            points_player_2 += 1
                        k += 3
                    else:
                        k += 1

                if total_cards:
                    if cards_player_1 > cards_player_2:
                        win_matrix[i, j] += 1
                        player1_wins += 1
                    elif cards_player_2 > cards_player_1:
                        player2_wins += 1
                else:
                    if points_player_1 > points_player_2:
                        win_matrix[i, j] += 1
                        player1_wins += 1
                    elif points_player_2 > points_player_1:
                        player2_wins += 1

        return win_matrix, player1_wins, player2_wins

    # Load data file if it exists, otherwise initialize empty win matrix and rounds played count
    # Load data with detailed sequence combinations
    def load_data(file):
        if os.path.exists(file):
            with open(file, 'r') as f:
                data = json.load(f)
                win_matrix = np.zeros((8, 8))  # Initialize empty matrix
                win_data = data['win_data']
                total_rounds_played = data['total_rounds_played']
            
            # Rebuild the matrix from the stored win data
                sequences = create_hands()
                for i in range(len(sequences)):
                    for j in range(len(sequences)):
                        p1_seq = binary_to_string(sequences[i])
                        p2_seq = binary_to_string(sequences[j])
                        combo_key = f"{p1_seq} vs {p2_seq}"
                        if combo_key in win_data:
                            win_matrix[i, j] = win_data[combo_key]  # Populate the matrix

                return win_matrix, total_rounds_played
        else:
            return np.zeros((8, 8)), 0
        
    def save_data(file, win_matrix, sequences, total_rounds_played):
        win_data = {}
    
    # Loop through each combination of Player 1 and Player 2 sequences
        for i in range(len(sequences)):
            for j in range(len(sequences)):
                p1_seq = binary_to_string(sequences[i])
                p2_seq = binary_to_string(sequences[j])
                wins = win_matrix[i, j]  # Number of wins for this combination
                win_data[f"{p1_seq} vs {p2_seq}"] = int(wins)  # Store as a human-readable key

    # Prepare the data to be saved
        data = {
            'win_data': win_data,  # Detailed win data
            'total_rounds_played': total_rounds_played  # Total number of games
        }

    # Save to JSON file
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

    # Load deck history if it exists, otherwise initialize an empty list
    def load_deck_history(deck_file):
        if os.path.exists(deck_file):
            with open(deck_file, 'r') as f:
                deck_history = json.load(f)
                return deck_history
        else:
            return []

    # Save the updated deck history back to the file
    def save_deck_history(deck_file, deck_history):
        with open(deck_file, 'w') as f:
            json.dump(deck_history, f)

    # Load win counts if they exist, otherwise initialize them
    def load_win_counts(win_counts_file):
        if os.path.exists(win_counts_file):
            with open(win_counts_file, 'r') as f:
                win_counts = json.load(f)
                return win_counts['player1_wins'], win_counts['player2_wins']
        else:
            return 0, 0

    # Save the updated win counts back to the file
    def save_win_counts(win_counts_file, player1_wins, player2_wins):
        with open(win_counts_file, 'w') as f:
            win_counts = {
                'player1_wins': player1_wins,
                'player2_wins': player2_wins
            }
            json.dump(win_counts, f)

    # Load existing data or initialize it
    sequences = create_hands()  
    overall_win_matrix, total_rounds_played = load_data(data_file)
    deck_history = load_deck_history(deck_file)
    player1_wins, player2_wins = load_win_counts(win_counts_file)

    # Run new simulations and update the overall win matrix, deck history, and win counts
    for _ in range(rounds):
        deck = [1] * 26 + [0] * 26  # Half red (1) and half black (0)
        random.shuffle(deck)
        win_matrix, p1_wins, p2_wins = game_simulation(sequences, deck, total_cards)
        overall_win_matrix += win_matrix  # Update with new simulation data
        deck_history.append(deck_to_string(deck))  # Convert deck to string and store it in history
        player1_wins += p1_wins  # Update Player 1 wins
        player2_wins += p2_wins  # Update Player 2 wins

    # Update the total number of rounds played
    total_rounds_played += rounds

    # Save the updated win matrix, total rounds played, deck history, and win counts
    save_data(data_file, overall_win_matrix, sequences, total_rounds_played)
    save_deck_history(deck_file, deck_history)
    save_win_counts(win_counts_file, player1_wins, player2_wins)

    # Recalculate probabilities based on the updated win matrix
    win_probabilities = overall_win_matrix / total_rounds_played  # Normalize by total rounds

    print("Winning probabilities for each sequence combination (Player 1 vs Player 2):\n")
    for i in range(len(sequences)):
        for j in range(len(sequences)):
            p1_seq = binary_to_string(sequences[i])
            p2_seq = binary_to_string(sequences[j])
            probability = win_probabilities[i, j]
            print(f"Player 1: {p1_seq} vs Player 2: {p2_seq} --> Probability that Player 1 wins: {probability:.5f}")

    print(f"\nTotal Wins: Player 1: {player1_wins}, Player 2: {player2_wins}")

    print("\nDeck history for this run (R for Red, B for Black):\n")
    for round_num, deck in enumerate(deck_history[-rounds:], start=1):
        print(f"Round {round_num}: {deck}")


# Example usage:
game_simulation_with_probabilities(rounds=2000, total_cards=False)
