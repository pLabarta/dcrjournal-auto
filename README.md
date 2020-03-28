# dcrjournal-auto
Automated text generation and data stuff for the Decred Journal

## Transactions

Generates:
>This month, the blockchain size grew 112.98MB. Blocks had an average size of 13.92KB. The smallest block had a size of 1.36KB and the largest one 366.37KB.

>132323 transactions were included in the blockchain. On average, there were 4562 transactions per day. The busiest day saw 5175 TXs and the least one 3709.

Data Frame:
```
block_size: ['height','size','date']
tx_count: ['date','count']
```
