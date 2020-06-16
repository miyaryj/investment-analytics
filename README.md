# investment-analytics

Python script to manage investment data.  
Currently SBI sec. is only supported as the investment data.

## Preparation

- Download CSVs of trade history and deposits inquiry
- Open the CSVs by Numbers
- Remove the unnecessary lines at the head
- Export as a new CSV

## Usage

```
python track_investment_balance.py -i data/DetailInquiry_xxxx.csv -t data/SaveFile_xxxx.csv -s 2020-06-16
```

- `-i inquiry` : The path of the deposits inquiry CSV
- `-t trade` : The path of the trade history CSV
- `-s since` : Ignore the data of date before this