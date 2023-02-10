# ThetanArenaBot

Automated bot to buy and sell NFTs from ThetanArena marketplace.

Used to instantly buy extremely low price NFTs and sell it for a normal price afterward.
On bscscan, my bot was much faster than the 3 or 4 other bots in the same category used by other people.
## Important information

Old code quickly made without any code formating or test.
## Installation

Install Python3 and required dependencies

```bash
  pip install web3
  pip install asgiref
  pip install eth_typing
  pip install selenium
```
    
## Configuration

You can reconfigure the bot behavior by changing vars at the begining of the script

Data URLs: **Line 17**

```python
# Data url
wbnb_price_url: str = 'https://exchange.thetanarena.com/exchange/v1/currency/price/32'
thc_price_url: str = 'https://exchange.thetanarena.com/exchange/v1/currency/price/1'
latest_marketplace_url: str = 'https://data.thetanarena.com/thetan/v1/nif/search?sort=Latest&from=0&size=4'
bsc_data_url: str = 'https://bsc-dataseed.binance.org/'
hero_webdriver_url: str = 'https://marketplace.thetanarena.com/item/'
```

THC rewards: **Line 24**

```python
# THC rewards per battle
thc_battle_win: float = 6.00
thc_battle_lose: float = 1.00

# THC rewards per rarity
thc_rarity_common: float = 3.25
thc_rarity_epic: float = 6.50
thc_rarity_legendary: float = 23.55

# THC rewards per level for heroes from 0 to level 12 (bonus at levels 3, 5, 7, 9 and 11)
thc_level_common: list = [0, 0, 0, 0.006, 0, 0.01, 0, 0.01, 0, 0.02, 0, 0, 0]
thc_level_epic: list = [0, 0, 0, 0.117, 0, 0.2, 0, 0.27, 0, 0.35, 0, 0, 0]
thc_level_legendary: list = [0, 0, 0, 0.75, 0, 1.25, 0, 1.75, 0, 2.25, 0, 2.75, 0]
```

To speed up bot, skip verification process if price is considered unprofitable: **Line 38**

```python
# Skip hero verification if price is higher than vars
price_skip_common: float = 0.2
price_skip_epic: float = 0.4
price_skip_legendary: float = 1.9
```

Choose the requested profitability rate and gas price for the transactions: **Line 43**

```python
# Market vars
desired_winrate_profitability: float = 0.10  # percentage between 0 and 1, 0.10 = 10%
marketplace_fees: float = 0.0415  # percentage between 0 and 1
high_gas_fees: str = '20'
transaction_fee: float = int(high_gas_fees) / 10  # $ maximum transaction fees
```
## Usage

**WARNING**
Writing your private key anywhere on a computer is a big security issue and can end up with a wallet hack
**WARNING**

Setup Wallet vars: **Line 49**

```python
# Wallet vars
public_address: str = ''
private_key: str = ''
}
```

Save your chrome profile with your Metamask to C:\\User_Data

Start bot, you can see in the log console every actions taken from the bot for example which NFT is considered interesting and if it sent buying order or not.

## Author

- [@QuentinHerique](https://www.github.com/QuentinHerique)


## Support & Requests

Email: quentinherique07@gmail.com

