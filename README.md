# SageMaker - JSON to CSV (FOCUS)
## Goal
<p>FOCUS from the FinOps Foundation is aiming to be a shared model for billing data in the cloud space. I had an old script lying around that ingested pricing data for AWS SageMaker and its commitment-based discounts from the AWS API's and converts them from JSON to CSV for easy ingestion into a database.
The goal is to be able to add recent pricing data to your environment to evaluate options for SavingsPlans pricing in your own homebrew tools (useful if you run a multi-cloud datalake). It also allows you to build a recommendation engine based on the pricing options ingested.</p>

<p>With the uptick in AI and AI-related infrastructure, leveraging commitment based discounts might be very useful for your organisation or project. The script can be reused for other AWS products, though I wouldn't be surprised if the API for other pricing lists doesn't function in the same way. AWS has a tendency to do things different for each product, sadly.</p>

## Breaking down the script
The AWS pricing API is a bit messy in my opinion. It has a bunch of different JSON files and indexes for SageMaker and in the beginning I found it confusing to know what I needed. In essence, the script follows the following logic:
* Download the JSON data of the on-demand pricing for all SageMaker-related products
* Write that data to a CSV with one line per SkuId

For the on-demand pricing all data for all regions are in one single JSON file, which is convenient. For the Commitment-based discounts, the data is spread out across different JSONS for different regions. Each of them are luckily structured in the same way, so we can loop through them easily.
This is what the second part of the script does, it loops through the commitment-based pricing JSONS for each region and adds lines to the CSV again based on SkuId. 

This way, a typical component that is covered under a SageMaker Savings Plan has 7 lines in the CSV:
* The on-demand Pricing
* No Upfront / 1 Year
* Partial Upfront / 1 Year
* All Upfront / 1 Year
* No Upfront / 3 Year
* Partial Upfront / 3 Year
* All Upfront / 3 Year

These can then be turned into one line in a nice SQL view if you so choose, after ingesting the csv in your database.

## Leveraging the FOCUS framework
While I discuss the specifics of using the **[FOCUS](https://focus.finops.org/)** framework and the columns used for this script more in depth in my blog **[FinOps Scribbler](https://medium.com/@finopsscribbler)**, I did want to draw some attention to this here.
The columns that the CSV produces are either part of the Columns described in the Specification and Documentation, or columns I thought were necesarry to not lose information from the JSON. These are prefixed with the FOCUS-mandated 'x_' prefix, identifying them as external, custom columns and distinguish them from FOCUS columns to avoid conflicts in future releases.
Feel free to adapt the script if the information in those columns fits an existing column in the specification, but based on my knowledge of the data this was the best solution. 



## How to use the script
It's relatively simple, all you really need to do is change the variable 'folder_path' to where you want your script to put its output. Upon running/reviewing it, you'll see you might need to install a few libraries that you don't already have. The error messages in the terminal are your best friend.
If you end up using it, feel free to reach out to me on **[LinkedIn](https://www.linkedin.com/in/benjamin-van-der-maas-71168466/)** and tell me about it!

## Sources
For mapping the pricing list columns to FOCUS-compatible column names, I mainly used the following documentation:
- The FOCUS Specification document
- [The FOCUS Column Library](https://focus.finops.org/focus-columns/)
- [The FOCUS Converter](https://github.com/finopsfoundation/focus_converters/tree/dev) (mainly to reference how they looked at existing column names from AWS raw data)
- [FOCUS 1.0 with AWS Columns](https://docs.aws.amazon.com/cur/latest/userguide/table-dictionary-focus-1-0-aws-columns.html)