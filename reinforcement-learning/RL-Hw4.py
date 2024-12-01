from email.policy import default

import numpy as np
import random
from typing import Tuple,List
import matplotlib.pyplot as plt
from collections import defaultdict

np.random.seed(1234)
class BlackjackRules:

    # this probably should be up to the player and dealer
    # bcs if he has aces he can use those
    @staticmethod
    def hand_went_bust(hand):
        if Deck.evaluate_hand(hand) > 21:
            return True
        else:
            return False
    @staticmethod
    def dealer_hits(hand):
        if Deck.evaluate_hand(hand) >= 17:
            #sticks
            return False
        else:
            return True

class Deck:

    cards = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']

    @staticmethod
    def has_usable_ace(hand):
        # to use it we will convert it to '1'
        return 'A' in hand

    @staticmethod
    def use_ace(hand):
        if not Deck.has_usable_ace(hand):
            return hand
        for pos,card in enumerate(hand):
            if card == 'A':
                hand[pos] = '1'


    @staticmethod
    def evaluate_hand(hand):
        return sum(map(lambda x: Deck.card_value(x),hand))
    @staticmethod
    def card_value(card):
        if card == '10' or card == 'J' or card == 'Q' or card == 'K':
            return 10
        if card == 'A':
            # this is probs wrong
            return 11
        else:
            return int(card)

    #todo randomness
    @staticmethod
    def deal_two_cards_each():

        return ([np.random.choice(Deck.cards), np.random.choice(Deck.cards)],
                [np.random.choice(Deck.cards), np.random.choice(Deck.cards)])

    @staticmethod
    def deal_two_cards_each_with_unusable_ace():
        # '1' is the unusable ace
        return ([np.random.choice(Deck.cards + ['1']), np.random.choice(Deck.cards + ['1'])],
                [np.random.choice(Deck.cards), np.random.choice(Deck.cards)])

    @staticmethod
    def deal_card():
        return np.random.choice(Deck.cards)
    @staticmethod
    def convert_hands_to_state(player_hand,dealer_hand):
        player_has_ace = Deck.has_usable_ace(player_hand)
        player_value = Deck.evaluate_hand(player_hand)
        # We can only see one dealer card
        visible_dealer_value = Deck.evaluate_hand(dealer_hand[0:1])
        # we might need the dealer's hand too dunno
        return [(player_value,visible_dealer_value,player_has_ace,dealer_hand)]
    @staticmethod
    def convert_hands_and_action_to_pair(player_hand,dealer_hand,action):
        player_has_ace = Deck.has_usable_ace(player_hand)
        player_value = Deck.evaluate_hand(player_hand)
        # We can only see one dealer card
        visible_dealer_value = Deck.evaluate_hand(dealer_hand[0:1])
        # S,A
        return player_value, visible_dealer_value, player_has_ace, dealer_hand,action

# i need it to also return a List[(pl_value,dl_value,has_usable_ace)] object
# just basically change all returns to reward,(pl_value,dl_value,has_usable_ace)
# Game Loop
def play_game(policy,player_hand,dealer_hand,player_sticks,dealer_sticks,states_in_game):
    #
    # player_hand,dealer_hand = Deck.deal_two_cards_each()
    print("BlackjackRules Turn:")
    print("Player Hand: ",player_hand)
    print("Dealer Hand: ",dealer_hand)
    has_ace = Deck.has_usable_ace(player_hand)
    player_value = Deck.evaluate_hand(player_hand)
    dealer_value = Deck.evaluate_hand(dealer_hand)
    print("Player Value: ",player_value)
    print("Dealer Value: ",dealer_value)
    # I should only concat the states when something was played and not just sticked
    if player_value == 21:
        if dealer_value == 21:
            #draw
            return 0,states_in_game
        else:
            return 1,states_in_game
    if BlackjackRules.hand_went_bust(player_hand):
        if not has_ace:
            return -1,states_in_game
        else:
            Deck.use_ace(player_hand)
            return play_game(policy,player_hand,dealer_hand,
                             player_sticks,dealer_sticks,
                             states_in_game + Deck.convert_hands_to_state(player_hand,dealer_hand))
    elif BlackjackRules.hand_went_bust(dealer_hand):
        if not Deck.has_usable_ace(dealer_hand):
            return 1,states_in_game
        else:
            Deck.use_ace(dealer_hand)
            return play_game(policy, player_hand, dealer_hand, player_sticks, dealer_sticks,states_in_game + Deck.convert_hands_to_state(player_hand,dealer_hand))

    if player_sticks and dealer_sticks:
        if player_value > dealer_value:
            return 1,states_in_game
        elif player_value < dealer_value:
            return -1,states_in_game
        else:
            return 0,states_in_game

    if player_sticks:
        #time for the dealer to play
        if BlackjackRules.dealer_hits(dealer_hand):
            dealer_hand.append(Deck.deal_card())
            return play_game(policy,player_hand,dealer_hand,player_sticks,False,states_in_game + Deck.convert_hands_to_state(player_hand,dealer_hand))
        else:
            # dealer sticks
            return play_game(policy,player_hand,dealer_hand,player_sticks,True,states_in_game)
    else:
        visible_dealer_value = Deck.evaluate_hand(dealer_hand[0:1])
        # i need to convert the values into the array positions of 10x10x2
        if player_value <= 11:
            # it doesnt make sense to not hit while hand<=10
            # we do this to reduce the state space searched
            player_hand.append(Deck.deal_card())
            return play_game(policy, player_hand, dealer_hand, False, dealer_sticks,states_in_game + Deck.convert_hands_to_state(player_hand,dealer_hand))
        print(f"Policy for: {player_value - 12},{visible_dealer_value - 2}")
        # visible dealer value - 2 bcs we mapping 2-11 to 0-9 which are the array dims
        player_action = policy[player_value-12,visible_dealer_value - 2,int(has_ace)]
        if player_action == 1:
            player_hand.append(Deck.deal_card())
            return play_game(policy,player_hand,dealer_hand,False,dealer_sticks,states_in_game + Deck.convert_hands_to_state(player_hand,dealer_hand))
        else:
            return play_game(policy, player_hand, dealer_hand, True, dealer_sticks,states_in_game)

def play_game_for_MCC(policy,player_hand,dealer_hand,player_sticks,dealer_sticks,states_in_game):
    #
    # player_hand,dealer_hand = Deck.deal_two_cards_each()
    # print("BlackjackRules Turn:")
    # print("Player Hand: ",player_hand)
    # print("Dealer Hand: ",dealer_hand)
    has_ace = Deck.has_usable_ace(player_hand)
    player_value = Deck.evaluate_hand(player_hand)
    dealer_value = Deck.evaluate_hand(dealer_hand)


    # print("Player Value: ",player_value)
    # print("Dealer Value: ",dealer_value)
    # I should only concat the states when something was played and not just sticked
    if player_value == 21:
        if dealer_value == 21:
            #draw
            return 0,states_in_game
        else:
            return 1,states_in_game
    if BlackjackRules.hand_went_bust(player_hand):
        if not has_ace:
            return -1,states_in_game
        else:
            Deck.use_ace(player_hand)
            player_action = False
            return play_game(policy,player_hand,dealer_hand,
                             False,dealer_sticks,
                             states_in_game + Deck.convert_hands_and_action_to_pair(player_hand,dealer_hand,player_action))
    elif BlackjackRules.hand_went_bust(dealer_hand):
        if not Deck.has_usable_ace(dealer_hand):
            return 1,states_in_game
        else:
            Deck.use_ace(dealer_hand)
            # todo understand how dealer sticking goes
            return play_game(policy, player_hand, dealer_hand, player_sticks, dealer_sticks,states_in_game + Deck.convert_hands_and_action_to_pair(player_hand,dealer_hand,True))

    if player_sticks and dealer_sticks:
        if player_value > dealer_value:
            return 1,states_in_game
        elif player_value < dealer_value:
            return -1,states_in_game
        else:
            return 0,states_in_game

    if player_sticks:
        #time for the dealer to play
        if BlackjackRules.dealer_hits(dealer_hand):
            dealer_hand.append(Deck.deal_card())
            return play_game(policy,player_hand,dealer_hand,player_sticks,False,states_in_game + Deck.convert_hands_and_action_to_pair(player_hand,dealer_hand,player_sticks))
        else:
            # dealer sticks
            return play_game(policy,player_hand,dealer_hand,player_sticks,True,states_in_game)
    else:
        visible_dealer_value = Deck.evaluate_hand(dealer_hand[0:1])
        # i need to convert the values into the array positions of 10x10x2
        if player_value <= 11:
            # it doesnt make sense to not hit while hand<=10
            # we do this to reduce the state space searched
            player_hand.append(Deck.deal_card())
            return play_game(policy, player_hand, dealer_hand, False, dealer_sticks,states_in_game + Deck.convert_hands_and_action_to_pair(player_hand,dealer_hand,False))
        print(f"Policy for: {player_value - 12},{visible_dealer_value - 2}")
        # visible dealer value - 2 bcs we mapping 2-11 to 0-9 which are the array dims
        player_action = policy[player_value-12,visible_dealer_value - 2,int(has_ace)]
        if player_action == 1:
            player_hand.append(Deck.deal_card())
            return play_game(policy,player_hand,dealer_hand,False,dealer_sticks,states_in_game + Deck.convert_hands_and_action_to_pair(player_hand,dealer_hand,bool(player_action)))
        else:
            return play_game(policy, player_hand, dealer_hand, True, dealer_sticks,states_in_game + Deck.convert_hands_and_action_to_pair(player_hand,dealer_hand,False))
# By default the values are True


def play_game_for_MCC_iterative(policy,initial_player_hand,initial_dealer_hand,initial_action):
    player_hand = initial_player_hand
    dealer_hand = initial_dealer_hand


    # Hit -> True
    # Stick -> False
    states = [Deck.convert_hands_and_action_to_pair(player_hand,dealer_hand,True)]
    reward = None
    dealer_hits = True
    player_hits = initial_action
    dealer_value = Deck.evaluate_hand(dealer_hand)
    player_value = Deck.evaluate_hand(player_hand)
    # Player's turn
    while player_hits:
        has_ace = Deck.has_usable_ace(player_hand)
        player_value = Deck.evaluate_hand(player_hand)
        # print(f"Hands are: {player_hand},{dealer_hand} and {player_hits},{dealer_hits}")
        if player_value == 21 and dealer_value == 21:
            reward = 0
            break
        if player_value == 21 and not(dealer_value == 21):
            reward = 1
            break
        if BlackjackRules.hand_went_bust(player_hand):
            if not has_ace:
                reward = -1
                break
            else:
                states.append(Deck.convert_hands_and_action_to_pair(player_hand, dealer_hand,player_hits))
                Deck.use_ace(player_hand)
                player_hits = True
                continue
        if player_value <= 11:
            # it doesnt make sense to not hit while hand<=10
            # we do this to reduce the state space searched
            print("Under 11 cards value we just hit")
            player_hits = True
            player_hand.append(Deck.deal_card())
            states.append(Deck.convert_hands_and_action_to_pair(player_hand,dealer_hand,player_hits))
            continue

        visible_dealer_value = Deck.evaluate_hand(dealer_hand[0:1])
        # print(f"Policy for: {player_value - 12},{visible_dealer_value - 2}")
        # visible dealer value - 2 bcs we mapping 2-11 to 0-9 which are the array dims
        player_action = policy[player_value - 12, visible_dealer_value - 2, int(has_ace)]
        # print(f"Action: {bool(player_action)}")
        if player_action == 1:
            player_hand.append(Deck.deal_card())
            player_hits = True
        else:
            player_hits = False
        states.append(Deck.convert_hands_and_action_to_pair(player_hand, dealer_hand, bool(player_action)))
        continue
    # Dealer's Turn
    while dealer_hits:
        if BlackjackRules.hand_went_bust(dealer_hand):
            if not Deck.has_usable_ace(dealer_hand):
                reward = 1
                break
            else:
                Deck.use_ace(dealer_hand)
                states.append(Deck.convert_hands_and_action_to_pair(player_hand, dealer_hand, True))
                continue

        if BlackjackRules.dealer_hits(dealer_hand):
            dealer_hand.append(Deck.deal_card())
            dealer_hits = True
            states.append(Deck.convert_hands_and_action_to_pair(player_hand, dealer_hand,
                                                                                player_hits))
        else:
            # dealer sticks
            dealer_hits = False
            continue
    if reward is not None:
        return reward,states
    if player_value > dealer_value:
        reward = 1
    elif player_value < dealer_value:
        reward = -1
    else:
        reward = 0

    assert(reward is not None)
    return reward,states
value_fn = np.ndarray(shape=(10, 10, 2), dtype='int')
value_fn[:,:,:] = 0

def MonteCarloPrediction():
    player_policy = np.ndarray(shape=(10, 10, 2), dtype='bool')

    # Going for figure 5.2 of the book
    player_policy[:,:,:] = 1
    # sticks on 21,20,19,18
    player_policy[6, :, :] = 0
    player_policy[7, :, :] = 0
    player_policy[8,:,:] = 0
    player_policy[9,:,:] = 0
    # contains arbitrary vals initially
    global value_fn
    returns_of_states = {(-1,-1,False):[1,-1,0]}
    # pl_hand = ['4','6']
    # dl_hand = ['8','6']
    iterations = 10000
    for i in range(iterations):
        pl_hand, dl_hand = Deck.deal_two_cards_each()
        result,states = play_game(player_policy,pl_hand,dl_hand,False,False,[])
        for state in states:
            # print(f"For Pl={player_val},Dl={dealer_val},A={has_ace} Result was {result}")
            # in our Scenario this is simple as states do not repeat
            G = result
            player_value,dealer_value,has_ace,dealer_hand = state
            if (player_value,dealer_value,has_ace) in returns_of_states.keys():
                returns_of_states[(player_value,dealer_value,has_ace)].append(G)
            else:
                returns_of_states[(player_value,dealer_value,has_ace)] = [G]
            if player_value <= 12 or player_value > 21:
                # we do not need a policy for these we just skip those
                continue
            #[2,11] -> [0,9]
            visible_dealer_value = Deck.evaluate_hand(dealer_hand[0:1])
            # print(f"Policy for: {player_value - 12},{visible_dealer_value - 2}")
            value_fn[player_value-12-1,visible_dealer_value-2,int(has_ace)] = np.average(np.asarray(returns_of_states[(player_value,dealer_value,has_ace)]))

    print(returns_of_states)

    # plt.show()
    print("Value Function is: ",value_fn)
    # print(result,states)


def plot_value_fn_after(fn,V,label_extra):
    fn()
    print("Array shape:", V.shape)
    # V = V.transpose()
    channel_1 = V[:, :, 0]  # No usable ace
    channel_2 = V[:, :, 1]  # usable ace

    # for index,elem in np.ndenumerate(V):
    #     new_V[index[1],index[0],index[2]] = V[index[0],index[1],index[2]]
    # channel_1 = new_V[:, :, 0]  # No usable ace
    # channel_2 = new_V[:, :, 1]  # usable ace

    # Plotting the two channels
    fig1, ax1 = plt.subplots(figsize=(7, 6))
    im1 = ax1.imshow(channel_1, cmap='hot', extent=[12, 21, 1, 10], origin='lower')
    ax1.set_title("No usable ace")
    ax1.set_xlabel("Player Sum")
    ax1.set_ylabel("Dealer Showing")
    ax1.set_xticks(range(12, 22))  # X-ticks in range 12 to 21
    ax1.set_yticks(range(1, 11))  # Y-ticks for dealer showing
    fig1.colorbar(im1, ax=ax1)
    plt.tight_layout()
    plt.show()

    # Second Figure: Channel 2
    fig2, ax2 = plt.subplots(figsize=(7, 6))
    im2 = ax2.imshow(channel_2 , cmap='hot', extent=[12, 21, 1, 10], origin='lower')
    ax2.set_title("Usable ace")
    ax2.set_xlabel("Player Sum")
    ax2.set_ylabel("Dealer Showing")
    ax2.set_xticks(range(12, 22))  # X-ticks in range 12 to 21
    ax2.set_yticks(range(1, 11))  # Y-ticks for dealer showing
    fig2.colorbar(im2, ax=ax2)
    plt.tight_layout()
    plt.savefig(f"Policy-For-Blackjack-{label_extra}.pdf", format="pdf", bbox_inches="tight")
    plt.show()



def choose_initial_state_action_pair():
    stick_hit = [False,True]
    player_hand,dealer_hand = Deck.deal_two_cards_each_with_unusable_ace()
    return player_hand,dealer_hand,Deck.has_usable_ace(player_hand),np.random.choice(stick_hit)


def MonteCarloControl(iterations=100_000):
    # value_fn = np.ndarray(shape=(10, 10, 2), dtype='int')
    # global value_fn
    #TODO, add off-policy actions
    # and randomize with pre-selected seed so i can
    # get consistent results
    #TODO
    np.set_printoptions(precision=2)
    # value_fn[:, :, :] = 0
    # contains arbitrary vals initially
    player_policy = np.ndarray(shape=(10, 10, 2), dtype='bool')
    player_policy = np.random.choice([True,False],size=(10,10,2))
    Q_s_a = defaultdict(float)

    returns_of_state_action_pairs = defaultdict(list)
    # pl_hand = ['4','6']
    # dl_hand = ['8','6']
    # iterations = 1_000_000
    # iterations = 100_000
    for i in range(iterations):
        player_hand, dealer_hand, usable_ace, stick_or_hit = choose_initial_state_action_pair()
        result, states = play_game_for_MCC_iterative(player_policy, player_hand, dealer_hand,stick_or_hit)
        print("First five states", states[:5])
        # Policy Evaluation
        for state in states:
            # in our Scenario this is simple as states do not repeat
            G = result
            player_value, dealer_value, has_ace, dealer_hand,action = state
            visible_dealer_value = Deck.evaluate_hand(dealer_hand[0:1])
            if player_value <= 12 or player_value > 21:
                # we do not need a policy for these we just skip those
                continue
            returns_of_state_action_pairs[(player_value, visible_dealer_value, has_ace, action)].append(G)
            returns = returns_of_state_action_pairs[(player_value, visible_dealer_value, has_ace, action)]
            if len(returns) == 0:
                # mhpws tha eprepe na einai float?
                Q_s_a[(player_value, visible_dealer_value, has_ace, action)] = 0
            else:
                Q_s_a[(player_value, visible_dealer_value, has_ace, action)] = sum(returns) / len(returns)

        # Policy Improvement
        for state in states:
            player_value, dealer_value, has_ace, dealer_hand, action = state
            visible_dealer_value = Deck.evaluate_hand(dealer_hand[0:1])
            if player_value <= 11 or player_value > 21:
                continue
            chosen_action = None
            value_of_hit = Q_s_a.get((player_value, visible_dealer_value, has_ace, True),0)
            value_of_stick = Q_s_a.get((player_value, visible_dealer_value, has_ace, False),0)
            if value_of_stick > value_of_hit:
                chosen_action = False
            elif value_of_stick < value_of_hit:
                chosen_action = True
            else:
                # Random Tie breaker
                chosen_action = np.random.choice([True,False])
            # [2,11] -> [0,9]
            player_policy[player_value-12,visible_dealer_value-2,:] = chosen_action

    return player_policy


for iteration_amount in [100_000]:
    def nothing():
        pass
    optimal_mcc_policy = MonteCarloControl(iteration_amount)
    plot_value_fn_after(nothing, optimal_mcc_policy,iteration_amount)

# plot_value_fn_after(MonteCarloPrediction,value_fn)

# for this Player Hand:  ['4', '6']
# Dealer Hand:  ['8', '6']
# it gets stuck in loop
