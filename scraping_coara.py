import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin  # To handle relative URLs
import datetime

# Function to store the current date in a file (clean and write)
def store_current_date(file_name):
    current_date = datetime.date.today().isoformat()
    with open(file_name, 'w') as file:  # Open in write mode to clean the file
        file.write(current_date + "\n")


# Function to read the stored date from the file
def read_stored_date(file_name):
    try:
        with open(file_name, 'r') as file:
            return file.read().strip()  # Read the only date present in the file
    except FileNotFoundError:
        return "No update available yet."


# File where the date will be stored
file_name = 'last_update.txt'




def fetch_signatories_data(url="https://coara.eu/agreement/signatories/"):
    """
    Function to scrape signatories' data from the COARA website.

    Args:
    url (str): URL of the COARA signatories page.

    Returns:
    DataFrame: Pandas DataFrame containing scraped country and organization data.
    """

    try:

        # Send a request to fetch the webpage
        response = requests.get(url)

        # Parse the webpage content
        soup = BeautifulSoup(response.content, 'html.parser')

        countries = ['All']  # During the first iteration, there is no span.text for the span element.
        countries_href = []  # During the first iteration, there is no href for the href element.

        # Use CSS selector to target the divs
        for row in soup.select('#signatories > div > div.flex.items-center.flex-wrap.justify-center.mb-12'):
            links = row.find_all('a')

            # Iterate through the links and extract href and text from <span>
            for link in links:
                href = link.get('href')
                if href:
                    countries_href.append(href)

                span = link.find('span', class_='py-[14px]')
                if span:
                    countries.append(span.text)

        # Remove first 'All' entries
        countries.pop(0)
        countries_href.pop(0)

        # Global list to collect all h3 text items
        h3_list = []
        data = dict()

        def scrape_page(any_url):
            mylist = []
            # Send a request to fetch the webpage
            response = requests.get(any_url)

            # Parse the webpage content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract h3 elements from the page
            for row in soup.find_all('div', class_='grid gird-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20'):
                all_h3 = row.find_all('h3', class_="mt-4 mb-20 text-left txt-lg")
                for h3 in all_h3:
                    h3_text = h3.get_text(strip=True)
                    mylist.append(h3_text)
                    h3_list.append(h3_text)

            return mylist, soup

        for country_index, country in enumerate(countries):
            # Initialize list to store h3 items per country
            data[country] = []

            # Start scraping the first page
            current_url = countries_href[country_index]

            while current_url:
                # Scrape the current page
                mylist, soup = scrape_page(current_url)

                # Accumulate the h3 items for this country
                data[country].extend(mylist)

                # Handle pagination (look for the next page link)
                next_page_div = soup.find('div', class_='-mt-px w-0 flex-1 flex justify-end')

                if next_page_div:
                    # Find the first <a> tag, which is assumed to be the "next" button
                    next_link = next_page_div.find('a')

                    if next_link:
                        # Get the href and join it with the base URL if it's relative
                        next_url = next_link.get('href')
                        current_url = urljoin(current_url, next_url)
                    else:
                        break
                else:
                    break

        # Flatten the dictionary
        rows = []
        for country, organizations in data.items():
            for org in organizations:
                rows.append({'Country': country.strip(), 'Organization': org.strip()})

        # Create a dataframe from the flattened data
        my_df = pd.DataFrame(rows, columns=['Country', 'Organization'])

        store_current_date(file_name)

        return my_df
    except:
        pass

def save_to_csv(df, filename="coara_signatories.csv"):
    """
    Save the DataFrame to a CSV file.

    Args:
    df (DataFrame): The DataFrame to save.
    filename (str): The name of the file to save the data.
    """
    try:
        df.to_csv(filename, index=False)
        # print(f"Data saved to {filename}")
    except:
        pass



