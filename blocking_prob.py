import matplotlib.pyplot as plt
# import seaborn as sns
import pandas as pd
import numpy as np



# if type == "small":

arrival_rate_stroke_PSC = 1.8
arrival_rate_stroke_CSC = 1.2
arrival_rate_non_stroke_csc_psc = 2.35


stroke_processing_rate = 1.0 / ((0.15)*(7) + (0.85)*(4))
non_stroke_processing_rate = 1.0 / (3.3)


def calculate_blocking_prob(num_beds, transfer_rate, plot = False, filename = ''):

    n = num_beds

    stroke_arrival_rate = transfer_rate*arrival_rate_stroke_PSC + arrival_rate_stroke_CSC

    beta = arrival_rate_non_stroke_csc_psc / (arrival_rate_non_stroke_csc_psc + stroke_arrival_rate)
    combined_arrival_rate = arrival_rate_non_stroke_csc_psc + stroke_arrival_rate
    combined_processing_rate = non_stroke_processing_rate * beta + stroke_processing_rate * (1 - beta)

    alpha = combined_arrival_rate / combined_processing_rate
    denom = [1, alpha]
    for i in range(2, n + 1):
        prev_value = denom[i-1]
        next_value = alpha * prev_value / i
        denom.append(next_value)
    denom_sum = sum(denom)
    # y_vals = denom[:]

    probs = [100 * x / denom_sum for x in denom]
    blocking_prob = denom[-1] / denom_sum
    
    # print(probs)

    if plot:
        numbers = [x for x in range(n+1)]
        plt.figure(figsize = (20, 5))
        plt.plot(numbers, probs, '-o')
        plt.ylabel("Percentage of time in state")
        plt.xlabel("Number of beds filled")
        plt.ylim(0, max(probs) + 0.1)
        plt.xticks(numbers)

        if filename:
            print("Saving file...")
            plt.savefig("{}.png".format(filename))
    
    return 100 * blocking_prob


def plot_results(lst_percentages, filename = ""):
    plt.figure(figsize = (20, 5))
    nums = [x/100 for x in range(len(lst_percentages))]
    # plt.xticks(nums)
    plt.plot(nums, lst_percentages, '-o')
    # plt.ylim(0, 100)
    plt.title("Percentage of Patients blocked by full ICU vs \
    Transfer Rate of Stroke Patients from PSCs for {} configuration".format(filename))
    plt.ylabel("% of Patients blocked by full ICU")
    plt.xlabel("Transfer Rate of Stroke Patients")
    plt.xlabel("")

    if filename:
        print("Saving file...")
        plt.savefig("{}.png".format(filename))

    plt.show()



p1 = .667



# print(p1, calculate_blocking_prob(28, .667))
# print(p1*1.05, calculate_blocking_prob(28, p1*1.05))
# print(p1*1.25, calculate_blocking_prob(28, p1*1.25))

# print(.185, calculate_blocking_prob(28, .185))
# print(.194, calculate_blocking_prob(28, .194))
# print(.231, calculate_blocking_prob(28, .231))

def overall_plots(n, sim_type = ""):
    block_prob_array = [calculate_blocking_prob(n, x/100) for x in range(0, 101)]
    plot_results(block_prob_array, filename = sim_type)
    return block_prob_array

# def two_dim_plots(sim_type = "", save = False):
#     twod_results = [
#                 [calculate_blocking_prob(n, x / 100) for x in range(0, 101)] 
#                 for n in range(0, 50)
#                 ]

#     plt.subplots(figsize=(15,10))
#     ax = sns.heatmap(twod_results, linewidth=0.0)
#     ax.invert_yaxis()
#     ax.set_ylabel("Number of beds at the CSC")
#     ax.set_xlabel("Transfer Rate of Stroke Patients from PSCs")

#     if sim_type and save:
#         fig = ax.get_figure()
#         fig.savefig('{}_heatmap.png'.format(sim_type))
#     plt.show()
#     return

def save_results():
    small = overall_plots(12, "small")
    med = overall_plots(23, "medium")
    large = overall_plots(28, "large")

    my_data = {'Transfer Rates': [x/100 for x in range(0, 101)], 
            'Small CSC': small,
            'Medium CSC': med,
            'Large CSC': large}


    df = pd.DataFrame(my_data)
    df.to_csv("Results.csv", index=False)


# two_dim_plots("small", save = True)
# two_dim_plots("medium", save = True)
# two_dim_plots("large", save = True)

print(calculate_blocking_prob(28, 0.13))




# df2 = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
# ...                    columns=['a', 'b', 'c'])

# df = pd.DataFrame(data = np.array([[x/100 for x in range(0, 101)], np.array(small), np.array(med), np.array(large)]), 
#                     columns = ['Transfer Rates', 'Small CSC', 'Medium CSC', 'Large CSC'])

# df.to_csv("Results.csv", index=False)

# calculate_blocking_prob(23, 0.13, "medium")


# print(block_prob_array[-])

# reVals = [x for x in range(0, 50)].reverse()

# twod_results = [
#                 [calculate_blocking_prob(n, x / 100) for x in range(0, 101)] 
#                 for n in range(0, 50)
#                 ]

# # plt.figure(figsize= (12, 10))
# # plt.imshow(twod_results, interpolation='nearest', origin = 'lower')
# # plt.xlabel("Transfer Percentage of Stroke Patients from PSC")
# # plt.ylabel("Number of beds at the CSC")
# # plt.show()


# ax = sns.heatmap(twod_results, linewidth=0.0)
# ax.invert_yaxis()
# ax.set_ylabel("Number of beds at the CSC")
# ax.set_xlabel("Transfer Rate of Stroke Patients from PSCs")
# plt.show()

