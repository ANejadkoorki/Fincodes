from time import sleep
from math import e
from pprint import pprint


# par : the face value of bond / ccr : continuously compounded rate of return / t : time to maturity
# m : number of compounding times per year
def macaulay_duration_calculator(par, ccr_return, coupon_rate, t, m):
    number_of_cash_flows = round(t * m) + 1
    # present_values : a list of tuple of time and its corresponding present value [(t1,v1), (t2,v2), (t3,v3), ...]
    present_values = list()
    duration = 0
    convexity = 0
    final_information = {'I)Cash Flow List : ': list()}
    for cash_flow in range(1, number_of_cash_flows):
        # cf : cash flow amount, vi : present value of each cash flow
        cf = (par * coupon_rate) / m if cash_flow != (number_of_cash_flows - 1) else par + ((par * coupon_rate) / m)
        time = cash_flow / m
        # e : euler`s number
        vi = cf * (e ** (-1 * ccr_return * time))
        present_values.append((time, vi))
        final_information['I)Cash Flow List : '].append(
            {
                'CASH FLOW': cash_flow,
                'a) Time(years)': time,
                'b) Cash Flow($)': cf,
                'c) Present Value($)': round(vi, 3),
            }
        )
    bond_pv = round(sum([value[1] for value in present_values]), 3)
    # pprint(final_information)
    for present_value in present_values:
        cash_flow, vi = present_value
        duration += cash_flow * (vi / bond_pv)
        convexity += (cash_flow ** 2) * (vi / bond_pv)
        final_information['I)Cash Flow List : '][present_values.index(present_value)].update(
            {'d) Weight': round(vi / bond_pv, 3)})
        final_information['I)Cash Flow List : '][present_values.index(present_value)].update(
            {'e) Time * Weight': round(cash_flow * (vi / bond_pv), 3)})
    duration = round(duration, 3)
    convexity = round(convexity, 3)
    final_information.update(
        {
            'II)Bond Price': bond_pv,
            'III)Duration': duration,
            'IV)Convexity': convexity,

        }
    )
    return final_information


pprint('WELCOME TO MACAULAY DURATION-CONVEXITY CALCULATOR\nTHIS PROGRAM DEVELOPED BY Nejadkoorki.A.H')
par = float(input('please enter the Par Value of Bond : '))
rc_return = float(input('please enter the Bond`s Continuously Compounded rate of return : '))
coupon_rate = float(input('please enter the bond`s coupon rate: '))
t = float(input('please enter years to maturity  : '))
m = float(input('please enter the number of compounding times per year : '))

# pprint(macaulay_duration_calculator(100, 0.052, 0.04, 1.5, 2))
pprint(macaulay_duration_calculator(par, rc_return, coupon_rate, t, m))

# delay
sleep(600)
