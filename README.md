# ricart-agrawala
## Actions
```
P1: DepositCash(4, 'A', 20), ApplyInterest(57, 'C', .10), CheckBalance(200, 'A')
P2: WithdrawCash(4, 'C', 30), DepositCash(63, 'B', 40), CheckBalance(200, 'B')
P3: ApplyInterest(2, 'B', .10), WithdrawCash(68, 'A', 10), CheckBalance(200, 'C')
```
Order of events: `ApplyInterest(P, r) = P(1 + r)`
Should have `P1.port < P2.port < P3.port` (use 6000, 6001, 6002 for example)
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