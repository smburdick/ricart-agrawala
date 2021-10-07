# ricart-agrawala
## setup
* Use Python3.8 (I have only tested this on Python 3.8.12)
* Run `pip install -r requirements.txt`
* In separate `tmux` windows (so that all processes may be monitored simultaneously) run
```
python Node.py 9000 9001 9002
python Node.py 9001 9000 9002
python Node.py 9002 9001 9000
```
And in the fourth window, to run the RPCs:
```
python Main.py 9000 9001 9002
```
You may use other port numbers

## Actions
```
P1: DepositCash(4, 'A', 20), ApplyInterest(57, 'C', .10), CheckBalance(200, 'A')
P2: WithdrawCash(4, 'C', 30), DepositCash(63, 'B', 40), CheckBalance(200, 'B')
P3: ApplyInterest(2, 'B', .10), WithdrawCash(68, 'A', 10), CheckBalance(200, 'C')
```
Interest Formula: `ApplyInterest(P, r) = P(1 + r)`

Should have `P1.port < P2.port < P3.port` (use 6000, 6001, 6002 for example)

## Order of events
```py
ApplyInterest(2, 'B', .10)
DepositCash(4, 'A', 20)
WithdrawCash(4, 'C', 30)
ApplyInterest(57, 'C', .10)
DepositCash(63, 'B', 40)
WithdrawCash(68, 'A', 10)
CheckBalance(200, 'A')
CheckBalance(200, 'B')
CheckBalance(200, 'C')
```
Expected results (all accounts start at 100)
```
A = 110
B = 150
C = 77
```

[Sample output](https://imgur.com/a/O85K9sJ)
