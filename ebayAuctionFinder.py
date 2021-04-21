
"""
ebayAuctionFinder
Written by Andrew Dang
"""


# import modules
import numpy as np
import pandas as pd
from ebaysdk.finding import Connection
from datetime import datetime as dt

# Keep track of how long it takes to find and filter through listings
tic = dt.now()


# Date format is 'YYYY-MM-DDTHH:MM:SS.000Z'; the 'T' and 'Z' are required.  
# 05:00:00 of tomorrow's date is midnight EST
EndofToday = '2021-04-21T05:00:00.000Z'

# Open .csv file with item of interest and appropriate filters
inFile = ('Path\to\keyword.csv')
search_terms = pd.read_csv(inFile)

item_string = search_terms['Item']
item_filter = search_terms['Filter']

# Create a list of our search terms
keywords = []
for i in range(search_terms.shape[0]):
    search_term = item_string[i] + ' ' + item_filter[i]
    keywords.append(search_term)

# Empty data structures
BelowMinListings = pd.DataFrame()
MinBidListings = pd.DataFrame()
BelowAndMinBid = pd.DataFrame()
AllListings = pd.DataFrame()


# Connect to the eBay API
api = Connection(appid='YOUR-APP-ID', config_file=None, siteid="YOUR-EBAY-REGION-GLOBAL-ID")

# submit our list of search terms and sort through the listings
for i in range(len(keywords)):  
    request = {
        'keywords': keywords[i]
    }

    # Return the response of our request.
    response = api.execute('findItemsAdvanced', request)
    rd = response.dict()

    # Grab all the information from each active listing found from our request.
    search_results = rd['searchResult']
    search_result_items = search_results['item']

    # Empty lists of information we want to keep track of
    Item = []
    CurrentPrice = []
    EndDate = []
    URL = []
    ListingType = []
    ShippingCost = []
    TotalCost = []
    BidCount = []
    
    # Add player name into date structure
    ItemName = item_string[i]

    # if/else statements are needed because the loop breaks if your search returns no listings. 
    # Extract relevant info from our request and save them in appropriate list
    for items in search_result_items:
        # Amongst all listings found, we are only interested in Canadian listings
        if items['country']=='CA':    
            current_price = float(items['sellingStatus']['convertedCurrentPrice']['value'])
            CurrentPrice.append(current_price)
    
            end_date = items['listingInfo']['endTime']
            EndDate.append(end_date)
    
            item_url = items['viewItemURL']
            URL.append(item_url)
    
            listing_type = items['listingInfo']['listingType']
            ListingType.append(listing_type)
            
            # find shipping cost of listing; if no cost listed, assume its $10
            item_keys =[]
            for key in items['shippingInfo']:
                item_keys.append(key)
                
            if item_keys[0] == 'shippingServiceCost':
                shipping_cost = float(items['shippingInfo']['shippingServiceCost']['value'])
                ShippingCost.append(shipping_cost)
            
            else:
                shipping_cost = 10.00
                ShippingCost.append(shipping_cost)
                
            # look for auctions with at least one bid
            sellingStatus_keys = []
            for keys in items['sellingStatus']:
                sellingStatus_keys.append(keys)
            
            if sellingStatus_keys[2] == 'bidCount':
                bid_count = float(items['sellingStatus']['bidCount'])
                BidCount.append(bid_count)
                
            else:
                 bid_count = 0
                 BidCount.append(bid_count)
                
                
            total_cost = current_price + shipping_cost
            TotalCost.append(total_cost)                      
            
            Item.append(ItemName)
        
        else: 
            current_price = 'NA'
            CurrentPrice.append(current_price)
    
            end_date = 'NA'
            EndDate.append(end_date)
    
            item_url = 'NA'
            URL.append(item_url)
    
            listing_type = 'NA'
            ListingType.append(listing_type)
            
            shipping_cost = 'NA'
            ShippingCost.append(shipping_cost)
            
            bid_count = 'NA'
            BidCount.append(bid_count)
                
            total_cost = 'NA'
            TotalCost.append(total_cost)                      
            
            Item.append(ItemName) 
    
    df = pd.DataFrame({"Item": Item,
                       "CurrentPrice": CurrentPrice,
                       "ShippingCost": ShippingCost,
                       "TotalCost": TotalCost,
                       "BidCount": BidCount,
                       "EndDate": EndDate,
                       "ListingType": ListingType,
                       "URL":URL})



    # Compile all the results for each item into one DataFrame 
    AllListings = pd.concat([AllListings, df], axis=0)
    
    # Begin analysis and separate data
    # Separate listings by listing type [Auction, FixedPrice, AuctionWithBIN, StoreInventory]
    is_auction = df['ListingType']=='Auction'
    is_fixedprice = df['ListingType']=='FixedPrice'
    is_storeinventory = df['ListingType']=='StoreInventory'

    df_auction = df[is_auction]
    df_fixedprice = df[is_fixedprice]
    df_storeinventory = df[is_storeinventory]
    
    # Combine store inventory and fixed price as 'BuyItNow'
    df_BuyItNow = pd.concat([df_fixedprice, df_storeinventory], axis=0)
    
    # Find minimum listing price
    min_ListingPrice = np.min(df_BuyItNow['CurrentPrice'])
    
    # Refine my search 
    # First filter by auctions ending today
    # Then filter by either if its below the threshold, or has at least one bid
    PriceThreshold = min_ListingPrice
    MinBids = 1
    
    # Filter auctions by those ending today
    is_endingToday = df_auction['EndDate'] <= EndofToday
    df_endingToday = df_auction[is_endingToday]
    
    # Filter auctions ending today that are below the minimum listing price
    is_below = df_endingToday['CurrentPrice'] <= PriceThreshold
    df_below = df_endingToday[is_below]
    
    # Filter auctions ending today that have at least one bid
    is_minbid = df_endingToday['BidCount'] >= MinBids
    df_minbid = df_endingToday[is_minbid]
    
    # Filter auctions ending today that are below minimum listing price, and have at least one bid
    is_below_and_minbid = df_minbid['CurrentPrice'] <= PriceThreshold
    df_BAMB = df_minbid[is_below_and_minbid]
    
    # After completing the search for item, save it into a data structure
    BelowMinListings = pd.concat([BelowMinListings,df_below], axis=0)
    MinBidListings = pd.concat([MinBidListings, df_minbid], axis=0)
    BelowAndMinBid = pd.concat([BelowAndMinBid, df_BAMB], axis=0)
    
    # Concatenate all data structures and label what filter was used
    f_BelowMinListing = 'Below Minimum Listing Price'
    f_MinBid = 'At least one bid'
    f_BAMB = 'Below Minimum Listing Price and has at least one bid'
    
    FilterList = []
    # Label below minimum listing price
    for a in range(BelowMinListings.shape[0]):
        FilterList.append(f_BelowMinListing)
    
    BelowMinListings['Filter'] = FilterList
    
    FilterList = []
    # Label at least one bid
    for a in range(MinBidListings.shape[0]):
        FilterList.append(f_MinBid)
    
    MinBidListings['Filter'] = FilterList
    
    FilterList = []
    # Label below minimum listing price
    for a in range(BelowAndMinBid.shape[0]):
        FilterList.append(f_BAMB)
    
    BelowAndMinBid['Filter'] = FilterList

# Place all filtered auctions into a single DataFrame    
ListingSummary = pd.concat([BelowMinListings, MinBidListings, BelowAndMinBid], axis=0)
    
# save today's listings
date = dt.now()
date_string = date.strftime('%Y%m%d')
today = date.now().strftime('%b-%d-%Y')

#Filter for unique URLs to prevent checking something twice
UniqueListings = ListingSummary.drop_duplicates(subset='URL', keep='last')

# Print how long it took to search and filter through the listings. 
toc = dt.now()
print('Time it took to process all requests:', toc-tic)