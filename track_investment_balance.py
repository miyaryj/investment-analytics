import argparse
import pathlib
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inquiry', type=lambda p: pathlib.Path(p))
parser.add_argument('-t', '--trade', type=lambda p: pathlib.Path(p))
parser.add_argument('-s', '--since')
args = parser.parse_args()

balance_df = pd.DataFrame(columns=['date', 'reason', 'brand', 'amount'])

# Inquiry
if args.inquiry:
  inquiry_df = pd.read_csv(args.inquiry)
  
  for inquiry in inquiry_df.itertuples():
    if inquiry.摘要.startswith('株式配当金'):
        balance_df = balance_df.append({
            'date': inquiry.入出金日,
            'reason': 'dividend',
            'brand': inquiry.摘要.split(' ')[1],
            'amount': int(inquiry.入金額)
        }, ignore_index=True)
    elif inquiry.摘要.startswith('譲渡益税源泉徴収金'):
        balance_df = balance_df.append({
            'date': inquiry.入出金日,
            'reason': 'duty',
            'brand': '',
            'amount': -int(inquiry.出金額)
        }, ignore_index=True)
    else:
        print('Unknown inquiry type!!: ' + inquiry.摘要)

# Trade
if args.trade:
  trade_df = pd.read_csv(args.trade)
  
  stock = {}
  for trade in trade_df.itertuples():
    # _11: 手数料/諸経費等
    if trade._11.isdigit() > 0:
        balance_df = balance_df.append({
            'date': trade.約定日,
            'reason': 'fee',
            'brand': '',
            'amount': -int(trade._11)
        }, ignore_index=True)
    if trade.取引 == '株式現物買':
        if trade.銘柄コード in stock:
            stock[trade.銘柄コード] = {
                'number': stock[trade.銘柄コード]['number'] + trade.約定数量,
                'price': stock[trade.銘柄コード]['price'] + trade.約定数量 * trade.約定単価
            }
        else:
            stock[trade.銘柄コード] = {
                'number': trade.約定数量,
                'price': trade.約定数量 * trade.約定単価
            }
    elif trade.取引 == '株式現物売':
        if trade.銘柄コード in stock:
            stock[trade.銘柄コード] = {
                'number': stock[trade.銘柄コード]['number'] - trade.約定数量,
                'price': stock[trade.銘柄コード]['price'] - trade.約定数量 * trade.約定単価
            }
            if stock[trade.銘柄コード]['number'] <= 0:
                balance_df = balance_df.append({
                    'date': trade.約定日,
                    'reason': 'trade',
                    'brand': trade.銘柄,
                    'amount': -stock[trade.銘柄コード]['price']
                }, ignore_index=True)
    elif trade.取引 == '投信金額買付' or trade.取引 == '分配金再投資':
        if trade.銘柄 in stock:
            stock[trade.銘柄] = {
                'number': stock[trade.銘柄]['number'] + trade.約定数量,
                'price': stock[trade.銘柄]['price'] + trade.約定数量 / 10000 * trade.約定単価
            }
        else:
            stock[trade.銘柄] = {
                'number': trade.約定数量,
                'price': trade.約定数量 / 10000 * trade.約定単価
            }
    elif trade.取引 == '投信金額解約':
        if trade.銘柄 in stock:
            stock[trade.銘柄] = {
                'number': stock[trade.銘柄]['number'] - trade.約定数量,
                'price': stock[trade.銘柄]['price'] - trade.約定数量 / 10000 * trade.約定単価
            }
            if stock[trade.銘柄]['number'] <= 0:
                balance_df = balance_df.append({
                    'date': trade.約定日,
                    'reason': 'trade',
                    'brand': trade.銘柄,
                    'amount': -stock[trade.銘柄]['price']
                }, ignore_index=True)
    else:
        print('Unknown trade type!!: ' + trade.取引)

# Result
balance_df['date'] = pd.to_datetime(balance_df['date'])
balance_df.set_index('date', inplace=True)
balance_df = balance_df.sort_values('date')

if args.since:
  balance_df = balance_df[args.since:]
print(balance_df.drop('brand', axis=1).groupby('reason').sum())

if args.since:
  dest = f'./data/balance_{args.since}.csv'
else:
  dest = './data/balance.csv'
balance_df.to_csv(dest)
print(f'Saved as {dest}')
