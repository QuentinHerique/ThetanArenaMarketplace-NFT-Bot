# coding: utf-8

import sys
import requests
import json
import time
import asyncio
import aiohttp
import web3.contract
from asgiref import sync
from dataclasses import dataclass
from web3 import Web3
from hexbytes import HexBytes
from eth_typing.evm import ChecksumAddress
from selenium import webdriver

# Data url
wbnb_price_url: str = 'https://exchange.thetanarena.com/exchange/v1/currency/price/32'
thc_price_url: str = 'https://exchange.thetanarena.com/exchange/v1/currency/price/1'
latest_marketplace_url: str = 'https://data.thetanarena.com/thetan/v1/nif/search?sort=Latest&from=0&size=4'
bsc_data_url: str = 'https://bsc-dataseed.binance.org/'
hero_webdriver_url: str = 'https://marketplace.thetanarena.com/item/'

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

# Skip hero verification based on price
price_skip_common: float = 0.2
price_skip_epic: float = 0.4
price_skip_legendary: float = 1.9

# Market vars
desired_winrate_profitability: float = 0.10  # percentage between 0 and 1
marketplace_fees: float = 0.0415  # percentage between 0 and 1
high_gas_fees: str = '20'
transaction_fee: float = int(high_gas_fees) / 10  # $ maximum transaction fees

# Wallet vars
public_address: str = ''
private_key: str = ''

# Web3 constructor
bsc_web: Web3 = Web3(Web3.HTTPProvider(bsc_data_url))

# Token and contract addresses
wbnb_token_address_string: str = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
thetan_nft_address_string: str = '0x98eb46CbF76B19824105DfBCfa80EA8ED020c6f4'
thetan_marketplace_address_string: str = '0x54ac76f9afe0764e6a8Ed6c4179730E6c768F01C'
wbnb_token_address: ChecksumAddress = Web3.toChecksumAddress(wbnb_token_address_string)
thetan_nft_address: ChecksumAddress = Web3.toChecksumAddress(thetan_nft_address_string)
thetan_marketplace_address: ChecksumAddress = Web3.toChecksumAddress(thetan_marketplace_address_string)
wbnb_token_abi: str = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],' \
                      '"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{' \
                      '"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{' \
                      '"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},' \
                      '{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],' \
                      '"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{' \
                      '"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad",' \
                      '"type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],' \
                      '"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,' \
                      '"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,' \
                      '"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],' \
                      '"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,' \
                      '"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"",' \
                      '"type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],' \
                      '"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],' \
                      '"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,' \
                      '"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst",' \
                      '"type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"",' \
                      '"type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},' \
                      '{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,' \
                      '"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"",' \
                      '"type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"",' \
                      '"type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},' \
                      '{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{' \
                      '"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},' \
                      '{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},' \
                      '{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,' \
                      '"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],' \
                      '"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst",' \
                      '"type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit",' \
                      '"type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},' \
                      '{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}] '
thetan_nft_abi: str = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,' \
                      '"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},' \
                      '{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,' \
                      '"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval",' \
                      '"type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address",' \
                      '"name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator",' \
                      '"type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],' \
                      '"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,' \
                      '"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,' \
                      '"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred",' \
                      '"type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32",' \
                      '"name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32",' \
                      '"name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32",' \
                      '"name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},' \
                      '{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role",' \
                      '"type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},' \
                      '{"indexed":true,"internalType":"address","name":"sender","type":"address"}],' \
                      '"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,' \
                      '"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,' \
                      '"internalType":"address","name":"account","type":"address"},{"indexed":true,' \
                      '"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked",' \
                      '"type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address",' \
                      '"name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to",' \
                      '"type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId",' \
                      '"type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE",' \
                      '"outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view",' \
                      '"type":"function"},{"inputs":[],"name":"MINTER_ROLE","outputs":[{"internalType":"bytes32",' \
                      '"name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{' \
                      '"internalType":"address","name":"proxy","type":"address"}],"name":"addApprovalWhitelist",' \
                      '"outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{' \
                      '"internalType":"address","name":"","type":"address"}],"name":"approvalWhitelists","outputs":[{' \
                      '"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},' \
                      '{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256",' \
                      '"name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],' \
                      '"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address",' \
                      '"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256",' \
                      '"name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{' \
                      '"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{' \
                      '"internalType":"address","name":"","type":"address"}],"stateMutability":"view",' \
                      '"type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],' \
                      '"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],' \
                      '"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32",' \
                      '"name":"role","type":"bytes32"},{"internalType":"uint256","name":"index","type":"uint256"}],' \
                      '"name":"getRoleMember","outputs":[{"internalType":"address","name":"","type":"address"}],' \
                      '"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32",' \
                      '"name":"role","type":"bytes32"}],"name":"getRoleMemberCount","outputs":[{' \
                      '"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view",' \
                      '"type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},' \
                      '{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],' \
                      '"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32",' \
                      '"name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],' \
                      '"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],' \
                      '"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address",' \
                      '"name":"owner","type":"address"},{"internalType":"address","name":"operator",' \
                      '"type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"",' \
                      '"type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{' \
                      '"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"isLocked","outputs":[{' \
                      '"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},' \
                      '{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"lock",' \
                      '"outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{' \
                      '"internalType":"uint256","name":"","type":"uint256"}],"name":"lockedTokens","outputs":[{' \
                      '"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},' \
                      '{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256",' \
                      '"name":"tokenId","type":"uint256"}],"name":"mint","outputs":[],"stateMutability":"nonpayable",' \
                      '"type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"",' \
                      '"type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner",' \
                      '"outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view",' \
                      '"type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],' \
                      '"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],' \
                      '"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address",' \
                      '"name":"proxy","type":"address"}],"name":"removeApprovalWhitelist","outputs":[],' \
                      '"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address",' \
                      '"name":"factory","type":"address"}],"name":"removeMintFactory","outputs":[],' \
                      '"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership",' \
                      '"outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{' \
                      '"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address",' \
                      '"name":"account","type":"address"}],"name":"renounceRole","outputs":[],' \
                      '"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32",' \
                      '"name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],' \
                      '"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[' \
                      '{"internalType":"address","name":"from","type":"address"},{"internalType":"address",' \
                      '"name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],' \
                      '"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},' \
                      '{"inputs":[{"internalType":"address","name":"from","type":"address"},' \
                      '{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256",' \
                      '"name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],' \
                      '"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},' \
                      '{"inputs":[{"internalType":"address","name":"operator","type":"address"},' \
                      '{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll",' \
                      '"outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{' \
                      '"internalType":"address","name":"factory","type":"address"}],"name":"setMintFactory",' \
                      '"outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{' \
                      '"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface",' \
                      '"outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view",' \
                      '"type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"",' \
                      '"type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{' \
                      '"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenByIndex","outputs":[{' \
                      '"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view",' \
                      '"type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},' \
                      '{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenOfOwnerByIndex",' \
                      '"outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view",' \
                      '"type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],' \
                      '"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],' \
                      '"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{' \
                      '"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view",' \
                      '"type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},' \
                      '{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256",' \
                      '"name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],' \
                      '"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address",' \
                      '"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],' \
                      '"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256",' \
                      '"name":"tokenId","type":"uint256"}],"name":"unlock","outputs":[],' \
                      '"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string",' \
                      '"name":"baseTokenURI","type":"string"}],"name":"updateBaseURI","outputs":[],' \
                      '"stateMutability":"nonpayable","type":"function"}] '
thetan_marketplace_abi: str = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256",' \
                              '"name":"tokenId","type":"uint256"},{"indexed":false,"internalType":"address",' \
                              '"name":"contractAddress","type":"address"},{"indexed":false,"internalType":"uint256",' \
                              '"name":"price","type":"uint256"},{"indexed":false,"internalType":"address",' \
                              '"name":"paymentToken","type":"address"},{"indexed":false,"internalType":"address",' \
                              '"name":"seller","type":"address"},{"indexed":false,"internalType":"address",' \
                              '"name":"buyer","type":"address"},{"indexed":false,"internalType":"uint256",' \
                              '"name":"fee","type":"uint256"}],"name":"MatchTransaction","type":"event"},' \
                              '{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address",' \
                              '"name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address",' \
                              '"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},' \
                              '{"inputs":[],"name":"feeToAddress","outputs":[{"internalType":"address","name":"",' \
                              '"type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{' \
                              '"internalType":"bytes32","name":"_messageHash","type":"bytes32"}],' \
                              '"name":"getEthSignedMessageHash","outputs":[{"internalType":"bytes32","name":"",' \
                              '"type":"bytes32"}],"stateMutability":"pure","type":"function"},{"inputs":[{' \
                              '"internalType":"address","name":"_nftAddress","type":"address"},' \
                              '{"internalType":"uint256","name":"_tokenId","type":"uint256"},' \
                              '{"internalType":"address","name":"_paymentErc20","type":"address"},' \
                              '{"internalType":"uint256","name":"_price","type":"uint256"},{"internalType":"uint256",' \
                              '"name":"_saltNonce","type":"uint256"}],"name":"getMessageHash","outputs":[{' \
                              '"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"pure",' \
                              '"type":"function"},{"inputs":[{"internalType":"address[2]","name":"addresses",' \
                              '"type":"address[2]"},{"internalType":"uint256[3]","name":"values","type":"uint256[' \
                              '3]"},{"internalType":"bytes","name":"signature","type":"bytes"}],' \
                              '"name":"ignoreSignature","outputs":[],"stateMutability":"nonpayable",' \
                              '"type":"function"},{"inputs":[{"internalType":"address[3]","name":"addresses",' \
                              '"type":"address[3]"},{"internalType":"uint256[3]","name":"values","type":"uint256[' \
                              '3]"},{"internalType":"bytes","name":"signature","type":"bytes"}],' \
                              '"name":"matchTransaction","outputs":[{"internalType":"bool","name":"","type":"bool"}],' \
                              '"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"owner",' \
                              '"outputs":[{"internalType":"address","name":"","type":"address"}],' \
                              '"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address",' \
                              '"name":"","type":"address"}],"name":"paymentTokens","outputs":[{"internalType":"bool",' \
                              '"name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{' \
                              '"internalType":"bytes32","name":"_ethSignedMessageHash","type":"bytes32"},' \
                              '{"internalType":"bytes","name":"_signature","type":"bytes"}],"name":"recoverSigner",' \
                              '"outputs":[{"internalType":"address","name":"","type":"address"}],' \
                              '"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address[]",' \
                              '"name":"_removedPaymentTokens","type":"address[]"}],"name":"removePaymentTokens",' \
                              '"outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],' \
                              '"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable",' \
                              '"type":"function"},{"inputs":[{"internalType":"address","name":"_feeToAddress",' \
                              '"type":"address"}],"name":"setFeeToAddress","outputs":[],' \
                              '"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[' \
                              ']","name":"_paymentTokens","type":"address[]"}],"name":"setPaymentTokens","outputs":[' \
                              '],"stateMutability":"nonpayable","type":"function"},{"inputs":[{' \
                              '"internalType":"uint256","name":"_transactionFee","type":"uint256"}],' \
                              '"name":"setTransactionFee","outputs":[],"stateMutability":"nonpayable",' \
                              '"type":"function"},{"inputs":[{"internalType":"bytes","name":"sig","type":"bytes"}],' \
                              '"name":"splitSignature","outputs":[{"internalType":"bytes32","name":"r",' \
                              '"type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"},' \
                              '{"internalType":"uint8","name":"v","type":"uint8"}],"stateMutability":"pure",' \
                              '"type":"function"},{"inputs":[],"name":"transactionFee","outputs":[{' \
                              '"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view",' \
                              '"type":"function"},{"inputs":[{"internalType":"address","name":"newOwner",' \
                              '"type":"address"}],"name":"transferOwnership","outputs":[],' \
                              '"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes",' \
                              '"name":"","type":"bytes"}],"name":"usedSignatures","outputs":[{"internalType":"bool",' \
                              '"name":"","type":"bool"}],"stateMutability":"view","type":"function"}] '

# Token contracts
wbnb_contract: web3.contract = bsc_web.eth.contract(address=wbnb_token_address, abi=wbnb_token_abi)
thetan_nft_contract: web3.contract = bsc_web.eth.contract(address=thetan_nft_address, abi=thetan_nft_abi)
thetan_marketplace_contract: web3.contract = bsc_web.eth.contract(address=thetan_marketplace_address,
                                                                  abi=thetan_marketplace_abi)


def get_wbnb_balance(): return bsc_web.fromWei(wbnb_contract.functions.balanceOf(public_address).call(), 'ether')


def get_thetan_nft_balance(): return thetan_nft_contract.functions.balanceOf(public_address).call()


def setup_chrome_driver():
    opt = webdriver.ChromeOptions()
    opt.add_argument('user-data-dir=C:\\User_Data')
    opt.add_argument('--headless')
    browser = webdriver.Chrome(options=opt)
    print('Headless Chrome connected')
    return browser


@dataclass
class ThetanHero:
    id: str
    refId: str
    price: float
    contractPrice: str
    rarity: int
    skinRarity: int
    level: int
    trophy: int
    battleCap: int
    name: str
    skinName: str
    profitability: float  # winrate percentage required to make profit
    priceDollars: float
    potentialGain: float  # potential gain based on the defined winrate percentage
    signature: str
    sellerAddress: str
    tokenId: str
    saltNonce: str

    def __init__(self, hero_id: str, hero_ref_id: str, price: int, rarity: int, skin_rarity: int, level: int,
                 trophy: int, battle_cap: int, name: str, skin_name: str, seller_address: str, token_id: str,
                 wbnb_price: float):
        self.id = hero_id
        self.refId = hero_ref_id
        self.price = price * (1 + marketplace_fees) / 100000000
        self.contractPrice = str(price)
        self.rarity = rarity
        self.skinRarity = skin_rarity
        self.level = level
        self.trophy = trophy
        self.battleCap = battle_cap
        self.name = name
        self.skinName = skin_name
        self.priceDollars = round(self.price * wbnb_price + transaction_fee, 2)
        self.profitability = 101.00
        self.potentialGain = -1.00
        self.sellerAddress = seller_address
        self.tokenId = token_id
        self.signature = ''
        self.saltNonce = ''

    def __str__(self):
        return self.id


class BotThetan:
    def __init__(self):
        self.wbnbPrice: float = 0.00
        self.thcPrice: float = 0.00
        self.heroList: list = []
        self.heroToBuy: list = []
        self.heroToSell: list = []
        self.heroSellingList: list = []
        self.doNotBuyHero: list = []
        self.heroInventory: list = []
        self.browser: webdriver.Chrome = setup_chrome_driver()
        self.accessKey: str = self.get_access_key()
        self.wbnbBalance: float = get_wbnb_balance()
        self.startTime = time.time()
        self.update_token_price()

    @staticmethod
    def get_token_price(url: str):
        return json.loads(requests.get(url).text)['data']

    def update_token_price(self):
        self.wbnbPrice = round(self.get_token_price(wbnb_price_url), 4)
        self.thcPrice = round(self.get_token_price(thc_price_url), 4)

    @staticmethod
    def get_market_data():
        return json.loads(requests.get(latest_marketplace_url).text)['data']

    def get_access_key(self):
        self.browser.get('https://marketplace.thetanarena.com/?batPercentMin=60&page=1&sort=Latest')
        return 'Bearer {0}'.format(self.browser.execute_script('return window.localStorage;')['theta/accessToken'])

    def get_selling_data(self, hero: ThetanHero):
        # Asynchronous call for 2 requests
        async def get_all(urls):
            async with aiohttp.ClientSession() as session:
                async def fetch(url):
                    async with session.get(url, headers={'authorization': '{0}'.format(self.accessKey)}) as response:
                        return await response.json()
                return await asyncio.gather(*[fetch(url) for url in urls])

        # Sync all the data fetch
        res: list = sync.async_to_sync(get_all)(
            [f'https://data.thetanarena.com/thetan/v1/items/{hero.id}/signed-signature?id={hero.id}',
             f'https://data.thetanarena.com/thetan/v1/items/{hero.id}?id={hero.id}'])

        hero.signature = res[0]['data']
        hero.saltNonce = res[1]['data']['saltNonce']

    def process_market_data(self, data: list):
        hero_list: list = [str(l) for l in self.heroList]
        for h in data:
            if str(h['id']) not in hero_list:
                self.heroList.append(ThetanHero(
                    hero_id=h['id'], hero_ref_id=h['refId'], price=h['price'], rarity=h['heroRarity'],
                    skin_rarity=h['skinRarity'], level=h['level'], trophy=h['trophyClass'], battle_cap=h['battleCap'],
                    name=h['name'], skin_name=h['skinName'], seller_address=h['ownerAddress'], token_id=h['tokenId'],
                    wbnb_price=self.wbnbPrice))

    def calculate_profitability(self, hero: ThetanHero):
        # Ignore if battle cap is 0
        if hero.battleCap <= 50 or hero.price > self.wbnbBalance or \
                hero.id in self.doNotBuyHero or hero.id in self.heroInventory or \
                (hero.rarity == 0 and hero.price > price_skip_common) or \
                (hero.rarity == 1 and hero.price > price_skip_epic) or \
                (hero.rarity == 2 and hero.price > price_skip_legendary):
            return

        # Default win gain
        win_gain: float = thc_battle_win

        # Add rarity and level win bonus
        if hero.rarity == 0:
            win_gain += thc_rarity_common + sum(thc_level_common[:hero.level + 1])
        elif hero.rarity == 1:
            win_gain += thc_rarity_epic + sum(thc_level_epic[:hero.level + 1])
        else:
            win_gain += thc_rarity_legendary + sum(thc_level_legendary[:hero.level + 1])
        win_gain = round(win_gain, 2)

        # Total gain for the winrate percentage
        hero.potentialGain = round((int(hero.battleCap * desired_winrate_profitability) * win_gain * self.thcPrice) +
                                   (int(hero.battleCap * (1 - desired_winrate_profitability)) * thc_battle_lose *
                                    self.thcPrice), 2)

        # Calculate the exact winrate required to make profit
        hero.profitability = round(((hero.priceDollars / ((win_gain + thc_battle_lose) * self.thcPrice)) /
                                    hero.battleCap) * 100, 2)

        # If winrate profitability is better than defined winrate, add to the buy list
        if hero.potentialGain > hero.priceDollars:
            self.heroToBuy.append(hero)
            self.log_hero_actions(hero=hero, text='Hero added to the internal buying list')

    def calculate_heroes_profitability(self):
        for hero in self.heroList:
            self.calculate_profitability(hero=hero)

    def _buy_hero(self, hero: ThetanHero):
        try:
            self.get_selling_data(hero=hero)
            transaction = thetan_marketplace_contract.functions.matchTransaction(
                [Web3.toChecksumAddress(hero.sellerAddress), thetan_nft_address, wbnb_token_address],
                [int(hero.tokenId), int(hero.contractPrice), int(hero.saltNonce)],
                HexBytes(hero.signature)).buildTransaction(
                {'gas': 250000,
                 'gasPrice': Web3.toWei(high_gas_fees, 'gwei'),
                 'from': public_address,
                 'nonce': bsc_web.eth.get_transaction_count(public_address)})
            signed_txn = bsc_web.eth.account.sign_transaction(transaction_dict=transaction, private_key=private_key)
            bsc_web.eth.sendRawTransaction(signed_txn.rawTransaction)
        except Exception as e:
            self.log_hero_actions(hero=hero, text=f'An error occurred during the transaction process: {e}')
            return False
        return True

    def buy_market_heroes(self):
        if len(self.heroToBuy) == 0:
            return
        self.heroList: list = []
        wbnb_balance: float = float(get_wbnb_balance())
        for hero in self.heroToBuy:
            if not (hero.id in self.doNotBuyHero or hero.id in self.heroInventory):
                if hero.price < wbnb_balance:
                    self.doNotBuyHero.append(hero.id)
                    self.heroInventory.append(hero.id)
                    state = self._buy_hero(hero=hero)
                    if state is True:
                        wbnb_balance -= float(hero.price)
                        self.log_hero_actions(hero=hero, text='Hero buy transaction sent, waiting for confirmation, '
                                                              'new WBNB balance: {0}'.format(wbnb_balance))
                        print("Full process buying hero: --- %s seconds ---" % (time.time() - self.startTime))
                else:
                    self.log_hero_actions(hero=hero, text='Buy canceled: Not enough founds')
        self.clean_buying_lists()

    def sell_market_heroes(self):
        pass

    def clean_buying_lists(self):
        do_not_buy: list = self.doNotBuyHero
        hero_to_buy: list = [str(l) for l in self.heroToBuy]
        for el in do_not_buy:
            if el not in hero_to_buy:
                self.doNotBuyHero.remove(el)
        self.heroToBuy: list = []

    def log_hero_actions(self, hero: ThetanHero, text: str = ''):
        print(' --------------------------------------------------------------------------------\n'
              '| Hero: {0} ({1})\n'
              '| Rarity: {2}, Skin Rarity: {3}, Level: {4}, Trophy: {5}\n'
              '| BattleCap : {6}, Price: {7} wbnb ({8}$)\n'
              '| Benefit winrate: {9}%, Potential gain: {10}$ for {11}% winrate\n'
              '| Logs: {12}\n'
              '|--------------------------------------------------------------------------------\n'
              '| Wallet WBNB balance: {13}\n'
              '| WBNB price: {14}$, THC price: {15}$\n'
              ' --------------------------------------------------------------------------------'
              .format(hero.name, hero.skinName, hero.rarity, hero.skinRarity, hero.level, hero.trophy, hero.battleCap,
                      int(hero.contractPrice) / 100000000, hero.priceDollars, hero.profitability, hero.potentialGain,
                      round(desired_winrate_profitability * 100, 2), text, self.wbnbBalance,
                      round(self.wbnbPrice, 2), round(self.thcPrice, 3)))


if __name__ == '__main__':
    # Setup asyncio for windows
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print(f'Winrate profitability required: {desired_winrate_profitability * 100}%')

    # Check BSC connection
    if bsc_web.isConnected():
        print('Connected to Binance Smart Chain')
    else:
        input('Cannot connect to Binance Smart Chain')
        sys.exit()

    # Bot starting
    bot = BotThetan()
    print('Thetan bot Started')
    update_time = 0

    while True:
        try:
            bot.startTime = time.time()
            bot.process_market_data(bot.get_market_data())
            # print("Get and Process market data: --- %s seconds ---" % (time.time() - bot.startTime))
            bot.calculate_heroes_profitability()
            bot.buy_market_heroes()
            if update_time == 1200:
                bot.update_token_price()
                update_time = 0
            else:
                update_time += 1
            # print("Loop time: --- %s seconds ---" % (time.time() - bot.startTime))
        except Exception as e:
            print(f'Kicked by the Thetan marketplace: {e}')
            time.sleep(5)
