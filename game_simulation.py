

import os                                                   # Import os module for operating system functionalities
import numpy as np                                         # Import numpy for numerical computations
import json                                                # Import json to handle JSON data
import random                                              # Import random for randomizing elements

def game_simulation_with_probabilities(rounds=1000, total_cards=False, data_file='game_data.json', deck_file='deck_history.json', win_counts_file='win_counts.json'):
                                                          # Define the main function with default parameters

    def create_hands():                                    # Define a function to create all possible sequences
        sequences = []                                     # Initialize an empty list to store sequences
        for i in range(8):                                 # Loop over numbers from 0 to 7
            seq = [(i >> j) & 1 for j in range(2, -1, -1)] # Convert number to a binary sequence
            sequences.append(seq)                          # Add the sequence to the list
        return sequences                                   # Return the list of sequences

    def binary_to_string(seq):                             # Define a function to convert binary to 'R' or 'B'
        return ''.join(['R' if bit == 1 else 'B' for bit in seq]) # Convert sequence to a string representation

    def deck_to_string(deck):                              # Define a function to convert the deck to a string
        return ''.join(['R' if card == 1 else 'B' for card in deck]) # Convert deck cards to 'R' or 'B'

    def game_simulation(sequences, deck, total_cards=False):   # Define a function to simulate one game
        win_matrix = np.zeros((8, 8))                          # Initialize a matrix to track wins
        player1_wins = 0                                       # Initialize Player 1's win tracker
        player2_wins = 0                                       # Initialize Player 2's win tracker

        for i, player1_seq in enumerate(sequences):        # Loop over all of Player 1's sequences
            for j, player2_seq in enumerate(sequences):    # Loop over all of Player 2's sequences
                points_player_1, points_player_2 = 0, 0    # Initialize points for both players
                cards_player_1, cards_player_2 = 0, 0      # Initialize card counts for both players
                card_pile = []                             # Initialize the card pile

                k = 0                                      # Start at the beginning of the deck
                while k <= len(deck) - 3:                  # Loop through the deck until the last 3 cards
                    current_sequence = deck[k:k+3]         # Get the current sequence of 3 cards
                    card_pile += deck[k:k+3]               # Add these cards to the card pile

                    if current_sequence == player1_seq:      # If the sequence matches Player 1's sequence
                        if total_cards:                      # If counting total cards
                            cards_player_1 += len(card_pile) # Add pile to Player 1's cards
                            card_pile = []                   # Reset the card pile being laid
                        else:
                            points_player_1 += 1               # Increment Player 1's point
                        k += 3                                 # Move forward by 3 cards
                    elif current_sequence == player2_seq:      # If the sequence matches Player 2's sequence
                        if total_cards:                        # If counting total cards
                            cards_player_2 += len(card_pile)   # Add pile to Player 2's cards
                            card_pile = []                     # Reset the card pile
                        else:
                            points_player_2 += 1           # Increment Player 2's point
                        k += 3                             # Move forward by 3 cards
                    else:
                        k += 1                             # Move forward by one card if no match

                if total_cards:                            # If counting total cards for the win condition
                    if cards_player_1 > cards_player_2:    # If Player 1 has more cards
                        win_matrix[i, j] += 1              # Increment win count in the matrix
                        player1_wins += 1                  # Increment Player 1's total wins
                    elif cards_player_2 > cards_player_1:  # If Player 2 has more cards
                        player2_wins += 1                  # Increment Player 2's total wins
                else:
                    if points_player_1 > points_player_2:      # If Player 1 has more points
                        win_matrix[i, j] += 1                  # Increment win count in the matrix
                        player1_wins += 1                      # Increment Player 1's total wins
                    elif points_player_2 > points_player_1:    # If Player 2 has more points
                        player2_wins += 1                      # Increment Player 2's total wins

        return win_matrix, player1_wins, player2_wins          # Return the results of the simulation

    def load_data(file):                                   # Define a function to load existing data
        if os.path.exists(file):                           # Check if the file exists
            with open(file, 'r') as f:                     # Open the file in read mode
                data = json.load(f)                        # Load data from the file
                win_matrix = np.zeros((8, 8))              # Initialize an empty win matrix
                win_data = data['win_data']                # Extract win data from the loaded data
                total_rounds_played = data['total_rounds_played'] # Extract total rounds played
                
            sequences = create_hands()                         # Generate all possible sequences
            for i in range(len(sequences)):                    # Loop over sequences for Player 1
                for j in range(len(sequences)):                # Loop over sequences for Player 2
                    p1_seq = binary_to_string(sequences[i])    # Convert Player 1's combo to string
                    p2_seq = binary_to_string(sequences[j])    # Convert Player 2's combo to string
                    combo_key = f"{p1_seq} vs {p2_seq}"        # Create a key for this sequence combination
                    if combo_key in win_data:                  # If this combination exists in the data
                        win_matrix[i, j] = win_data[combo_key] # Update the win matrix accordingly

            return win_matrix, total_rounds_played         # Return the loaded win matrix and rounds played
        else:
            return np.zeros((8, 8)), 0                     # Return default values if file doesn't exist
        
    def save_data(file, win_matrix, sequences, total_rounds_played): # Define a function to save data
        win_data = {}                                      # Initialize a dictionary to hold win data
    
        for i in range(len(sequences)):                        # Loop over sequences for Player 1
            for j in range(len(sequences)):                    # Loop over sequences for Player 2
                p1_seq = binary_to_string(sequences[i])        # Convert Player 1's sequence to string
                p2_seq = binary_to_string(sequences[j])        # Convert Player 2's sequence to string
                wins = win_matrix[i, j]                        # Get the number of wins for this combination
                win_data[f"{p1_seq} vs {p2_seq}"] = int(wins)  # Store it in the win data dictionary
    
        data = {
            'win_data': win_data,                          # Add win data to the data dictionary
            'total_rounds_played': total_rounds_played     # Add total rounds played to the data dictionary
        }

        with open(file, 'w') as f:                         # Open the file in write mode
            json.dump(data, f, indent=4)                   # Save the data as JSON with indentation

    def load_deck_history(deck_file):                      # Define a function to load deck history
        if os.path.exists(deck_file):                      # Check if the deck history file exists
            with open(deck_file, 'r') as f:                # Open the file in read mode
                deck_history = json.load(f)                # Load the deck history
                return deck_history                        # Return the loaded deck history
        else:
            return []                                      # Return an empty list if file doesn't exist

    def save_deck_history(deck_file, deck_history):        # Define a function to save deck history
        with open(deck_file, 'w') as f:                    # Open the file in write mode
            json.dump(deck_history, f)                     # Save the deck history to the file

    def load_win_counts(win_counts_file):                  # Define a function to load win counts
        if os.path.exists(win_counts_file):                # Check if the win counts file exists
            with open(win_counts_file, 'r') as f:          # Open the file in read mode
                win_counts = json.load(f)                  # Load the win counts
                return win_counts['player1_wins'], win_counts['player2_wins'] # Return the win counts
        else:
            return 0, 0                                    # Return zeros if file doesn't exist

    def save_win_counts(win_counts_file, player1_wins, player2_wins): # Define a function to save win counts
        with open(win_counts_file, 'w') as f:              # Open the file in write mode
            win_counts = {
                'player1_wins': player1_wins,              # Set Player 1's win count
                'player2_wins': player2_wins               # Set Player 2's win count
            }
            json.dump(win_counts, f)                       # Save the win counts to the file

    sequences = create_hands()                             # Generate all possible sequences
    overall_win_matrix, total_rounds_played = load_data(data_file) # Load existing data
    deck_history = load_deck_history(deck_file)            # Load existing deck history
    player1_wins, player2_wins = load_win_counts(win_counts_file) # Load existing win counts

    for _ in range(rounds):                                # Run the simulation for the specified number of rounds
        deck = [1] * 26 + [0] * 26                         # Create a deck with 26 reds and 26 blacks
        random.shuffle(deck)                               # Shuffle the deck randomly
        win_matrix, p1_wins, p2_wins = game_simulation(sequences, deck, total_cards) # Simulate the game
        overall_win_matrix += win_matrix                   # Update the overall win matrix
        deck_history.append(deck_to_string(deck))          # Add the current deck to the history
        player1_wins += p1_wins                            # Update Player 1's total wins
        player2_wins += p2_wins                            # Update Player 2's total wins

    total_rounds_played += rounds                          # Update the total number of rounds played

    save_data(data_file, overall_win_matrix, sequences, total_rounds_played) # Save the updated data
    save_deck_history(deck_file, deck_history)                 # Save the updated deck history
    save_win_counts(win_counts_file, player1_wins, player2_wins) # Save the updated win counts

    win_probabilities = overall_win_matrix / total_rounds_played # Calculate the winning probabilities

    print("Winning probabilities for each sequence combination (Player 1 vs Player 2):\n") # Display header
    for i in range(len(sequences)):                        # Loop over sequences for Player 1
        for j in range(len(sequences)):                    # Loop over sequences for Player 2
            p1_seq = binary_to_string(sequences[i])        # Get Player 1's sequence as a string
            p2_seq = binary_to_string(sequences[j])        # Get Player 2's sequence as a string
            probability = win_probabilities[i, j]          # Get the probability of Player 1 winning
            print(f"Player 1: {p1_seq} vs Player 2: {p2_seq} --> Probability that Player 1 wins: {probability:.5f}") # Display the probability

    print(f"\nTotal Wins: Player 1: {player1_wins}, Player 2: {player2_wins}") # Display total wins for both players

    print("\nDeck history for this run (R for Red, B for Black):\n")     # Display header for deck history
    for round_num, deck in enumerate(deck_history[-rounds:], start=1):   # Loop over the decks from the recent rounds
        print(f"Round {round_num}: {deck}")                              # Display the deck used in each round


# Example usage:
game_simulation_with_probabilities(rounds=2000, total_cards=False) # Run the simulation with specified parameters
