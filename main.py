import functions_framework
from bs4 import BeautifulSoup
import requests
import pandas as pd

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args
    name = ''
    if request_json and 'makanan' in request_json:
        name = request_json['makanan']
    else:
      return {'error': 'Parameter "makanan" not found or empty'}, 400
    Alamat_Food_Drink = name.replace(" ", "-")
    url = "https://www.fatsecret.co.id/kalori-gizi/umum/" + Alamat_Food_Drink

    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")
    # Find all 'td' elements with class 'fact'
    facts = soup.find_all('td', class_='fact')

    # Prepare lists to store the titles and values
    titles = []
    values = []

    # Loop through the facts and append the title and value to the lists
    for fact in facts:
        title = fact.find('div', class_='factTitle').text
        value = fact.find('div', class_='factValue').text
        titles.append(title)
        values.append(value)

    # Create a DataFrame from the lists
    df_food_drink = pd.DataFrame({'Nutrisi': titles, 'Jumlah': values})

    # Remove the first row
    df_food_drink = df_food_drink.iloc[1:]

    # Convert the 'Jumlah' column to numeric values
    df_food_drink['Jumlah'] = df_food_drink['Jumlah'].str.replace('g', '').str.replace(',', '.').astype(float)

    # Calculate the total amount
    total_amount = df_food_drink['Jumlah'].sum()

    # Calculate the proportion of each nutrient and add it as a new column
    df_food_drink['Persen'] = df_food_drink['Jumlah'] / total_amount

    # Print the DataFrame
    # print(df_food_drink)

    # Find the table
    table = soup.find('table', class_='generic')

    # Find all 'tr' elements in the table
    rows = table.find_all('tr')

    # Prepare lists to store the portion sizes and calories
    portion_sizes = []
    calories = []
    data = []

    # Loop through the rows (skip the first one because it's the header)
    for row in rows[1:]:
        # Find the 'td' elements in the row
        cells = row.find_all('td')

        # Check if there are two 'td' elements
        if len(cells) == 2 and cells[0].text.strip() and cells[1].text.strip() and cells[0].text.strip() != 'Tanggal:' and cells[0].text.strip() != 'Makanan:':
            # Get the portion size and calorie count and append them to the lists
            vit = {}
            portion_size = cells[0].text.strip()
            calorie_count = cells[1].text.strip()+' kkal'
            portion_sizes.append(portion_size)
            calories.append(calorie_count)
            link = cells[0].find('a').get('href')
            page2 = requests.get("https://www.fatsecret.co.id" + link)
            soup2 = BeautifulSoup(page.text,features="html.parser")
            # Find all 'td' elements with class 'fact'
            facts2 = soup.find_all('td', class_='fact')
            vit = {
                'Karbohidrat': facts2[2].find('div', class_='factValue').text,
                'Protein': facts2[3].find('div', class_='factValue').text,
                'Lemak': facts2[1].find('div', class_='factValue').text
            }
            data.append({
            'porsi':portion_size,
            'kalori': calorie_count,
            'detail': vit
            })


    # Create a DataFrame from the lists
    # df_porsi = pd.DataFrame({'Ukuran Porsi': portion_sizes, 'Kalori': calories})
    return {'data': data}
