import requests
import os
import json
import csv
import urllib3
import time
import sys


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



#--------------------- functions used throughout the script --
def grabFirstKey(dict):
    listKeys = list(dict.keys())
    firstKey = listKeys[0]
    return str(firstKey)

def skuCleanUp(var):
    varClean = var.split('.')[0]
    return str(varClean)
#-------------------------------------------------------------

#--------------------- Create file variables -----------------
url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonSageMaker/current/index.json'
json_filename = 'currentVersionOnDemandPricing.json'

indexUrl = 'https://pricing.us-east-1.amazonaws.com/savingsPlan/v1.0/aws/AWSMachineLearningSavingsPlans/current/region_index.json'
json_sp_index = 'sagemakerSP_regionIndex.json'
csv_filename = 'sagemakerPricelist.csv'
folder_path = r'/Users/{yourUsername}/{rest}/{of}/{the}/{filepath}'

#-------------------------------------------------------------

#------------ Pull the on-demand JSON into memory ------------
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Create the folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Save the JSON content to a file
    json_file_path = os.path.join(folder_path, json_filename)
    with open(json_file_path, 'wb') as file:
        file.write(response.content)
    
    print(f'Successfully saved JSONs as "{json_filename}" in "{folder_path}"')

    # Convert JSON to CSV
    csv_file_path = os.path.join(folder_path, csv_filename)
    
    # Open the input JSON file and load the data
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
        products = data['products']
        terms = data['terms']['OnDemand']
#-------------------------------------------------------------   
     
 
#---------------------- Start writing to the CSV -------------
    with open(csv_file_path, 'w', newline='') as csv_file:
    # create the headers (this is a selection of the available parameters, for more check the JSON)
        headerRow = [
            'SkuId'
             ,'RegionName'
             ,'AvailabilityZone' #this is the regionCode in the JSON file
             ,'ServiceName' #this is the serviceName in the JSON file
             ,'ResourceType'
             ,'x_UsageType'
             ,'x_Operation'
             ,'x_Component'
             ,'x_ComputeType'
             ,'CommitmentDiscountId'
             ,'x_PricingDate'
             ,'PricingUnit'
             ,'ListUnitPrice'
             ,'BillingCurrency'
             ,'x_LeaseContractLength'
             ,'x_CommitmentPurchaseOption'
             ,'ChargeDescription'
        ]

        writer = csv.DictWriter(csv_file, fieldnames=headerRow)
        writer.writeheader()

        # This is the iterator object that allows us to step through all the products
        pIter = iter(products.items()) 

        # This is the iterator object that allows us to step through all the price info for each product
        tIter = iter(terms.items()) 
        keyNULL = "NULL"

        # Extract required data and write to CSV file.
        for item in products:
            product = next(pIter, 'tkf')

            if product != 'tkf': 

                prodDict1 = product[1]
                prodAttr = prodDict1['attributes']

                # Grab a value for each of the cells, if the data is not available, a NULL value will serve as placeholder. 
                SkuId = prodDict1.get('sku', keyNULL)
               
                RegionName = prodAttr.get('location', keyNULL)
                AvailabilityZone = prodAttr.get('regionCode', keyNULL)
                ServiceName = prodAttr.get('servicename', keyNULL)
                ResourceType = prodAttr.get('instanceType', keyNULL)
                x_UsageType = prodAttr.get('usagetype', keyNULL)
                x_Operation = prodAttr.get('operation', keyNULL)
                x_Component = prodAttr.get('component', keyNULL)
                x_ComputeType = prodAttr.get('computeType', keyNULL)
                x_LeaseContractLength = prodAttr.get('purchaseTerm', keyNULL)
                x_CommitmentPurchaseOption = prodAttr.get('purchaseOption', keyNULL) 
                

                # The step is to get into the pricing info of the product, we navigate there based on the sku grabbed earlier.
                term = terms.get(SkuId)
                termNav = grabFirstKey(term) 
                termInfo = term.get(termNav, 'NULL')

                # In the pricing info we step into Price Dimensions, but have to step into its only dictionary via a Navigator.
                termDict2 = termInfo['priceDimensions'] 
                termPDNav = grabFirstKey(termDict2)

                # This dictionary contains the information we need with regards to price of a product. It contains the actual dollar price in another dict 'pricePerUnit'.
                termPriceDim = termDict2.get(termPDNav, 'NULL')

                # Now we are finally in the price dimensions, there we grab the info we need.
                termPrice = termPriceDim.get('pricePerUnit')


                # After determining the dict containins the dollar price, we navigate and extract.
                termCurrency = grabFirstKey(termPrice)
                termCost = termPrice.get(termCurrency)

                # Create the price/term specific variables.
                CommitmentDiscountId = termInfo.get('offerTermCode', keyNULL)
                x_PricingDate = termInfo.get('effectiveDate', keyNULL)
                PricingUnit = termPriceDim.get('unit', keyNULL)
                ListUnitPrice = termCost
                BillingCurrency = termCurrency
                ChargeDescription = termPriceDim.get('description', keyNULL)

                # Write a row with the extracted data.
                writer = csv.writer(csv_file, delimiter=',')
                writer.writerow([SkuId
                            , RegionName
                            , AvailabilityZone
                            , ServiceName
                            , ResourceType
                            , x_UsageType
                            , x_Operation
                            , x_Component
                            , x_ComputeType
                            , CommitmentDiscountId
                            , x_PricingDate
                            , PricingUnit
                            , ListUnitPrice
                            , BillingCurrency
                            , x_LeaseContractLength
                            , x_CommitmentPurchaseOption
                            , ChargeDescription
                                 ])
            else:
                break

        print(f'Successfully converted JSON to CSV: "{csv_filename}" in "{folder_path}"')
 #------------------------------------------------------------

 #--------- Pull the SP index JSON into memory ---------------
        response = ""
        response = requests.get(indexUrl)
        dataRegions = response.json()
        regions = dataRegions['regions']
        rIter = iter(regions)

        # Cycle through the regions and grab the necessary data from each JSON file.
        for region in regions:
            regionDict = next(rIter, 'tkf')
            regionCode = regionDict['regionCode']
            versionUrl = regionDict['versionUrl']
            json_filename = regionCode + '_sagemakerSP.json'
            url = "https://pricing.us-east-1.amazonaws.com" + versionUrl

            # Pull the SP price info from the url generated by iterating through the regions.
            response = requests.get(url)
            dataSP = response.json()

            # From the JSON, grab the term data for each of the 6 savings plans (1YNU, PU, AU and 3YNU, PU, AU).
            terms = dataSP['terms']['savingsPlan'] 

            # This iterator steps through each of the savings plans in the region's JSON file.
            tIter = iter(terms) 
            keyNULL = "NULL"

            # Now we grab the variables to fill the lines for the SP entries. Values that are not present get a NULL value as placeholder.
            for item in terms:
                term = next(tIter, 'tkf')
                if term != 'tkf':
                    termRates = term['rates']
                    rateIter = iter(termRates)

                    ChargeDescription = term.get('description', keyNULL)
                    x_PricingDate = term.get('effectiveDate', keyNULL)

                    for rate in termRates:
                        item = next(rateIter, 'tkf')
                        if term != 'tkf':
                            SkuId = item.get('discountedSku', keyNULL)

                            # We need the SKU of the savings plan to look up some information in the product part of the JSON.
                            # To do this, we grab the rateCode and pull the SKU out with a custom function.
                            rateCode = item.get('rateCode', keyNULL)
                            skuSP = skuCleanUp(rateCode)


                            RegionName = item.get('location', keyNULL)
                            AvailabilityZone = item.get('regionCode', keyNULL)
                            serviceName = item.get('servicename', keyNULL)
                            ResourceType = item.get('instanceType', keyNULL)
                            x_UsageType = item.get('discountedUsageType', keyNULL)
                            x_Operation = item.get('discountedOperation', keyNULL)
                            x_Component = item.get('component', keyNULL)
                            x_ComputeType = item.get('computeType', keyNULL)
                            CommitmentDiscountId = item.get('offerTermCode', keyNULL)
                            PricingUnit = item.get('unit', keyNULL)
                            ListUnitPrice = item['discountedRate'].get('price', keyNULL)
                            BillingCurrency = item['discountedRate'].get('currency', keyNULL)

                            # Because we also need two variables from the product part of the savings plan JSON, we look for the plan with the right sku and add it's info to the row.
                            product = dataSP['products']
                            pIter_SP = iter(product)
                            for savingplans in product:
                                singleSP = next(pIter_SP)
                                if singleSP.get('sku') == skuSP:
                                    SPAttr = singleSP.get('attributes', keyNULL)
                                    x_LeaseContractLength = SPAttr.get('purchaseTerm', keyNULL)
                                    x_CommitmentPurchaseOption = SPAttr.get('purchaseOption', keyNULL) 

                            writer = csv.writer(csv_file, delimiter=',')
                            writer.writerow([SkuId
                            , RegionName
                            , AvailabilityZone
                            , ServiceName
                            , ResourceType
                            , x_UsageType
                            , x_Operation
                            , x_Component
                            , x_ComputeType
                            , CommitmentDiscountId
                            , x_PricingDate
                            , PricingUnit
                            , ListUnitPrice
                            , BillingCurrency
                            , x_LeaseContractLength
                            , x_CommitmentPurchaseOption
                            , ChargeDescription
                                 ])  
                        else:
                            print("Spotted The Koi Fish while iterating through the SP rates.")
                else:
                    print("Spotted The Koi Fish while iterating through the terms (6 Saving Plans)")                    
else:
    print('Failed to retrieve on-demand JSON')
#----------------------------------------------------   

