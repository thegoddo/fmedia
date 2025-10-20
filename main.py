from io import StringIO
import subprocess
from bs4 import BeautifulSoup
import pandas as pd
import requests


def main():
    query = input("Enter: ")
    base = "https://rarbgdump.com/search/"
    url = base + query

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        req = response.text

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return

    soup = BeautifulSoup(req, "html.parser")
    table = soup.find_all("table", {"class": "w-full"})

    magnet = 'No Magnet Found. Sorry!!!'
    df_table = html_to_table(req)
    print(df_table)

    if df_table is not None:
        index_loc = int(input("Enter the index(start from 0)? "))
        target_df = df_table.iloc[index_loc]
        movie_id = target_df['ID']
        magnet = find_magnet(table, movie_id)
        stream_torrent_to_vlc(magnet)

    print(magnet)


def stream_torrent_to_vlc(magnet_link):
    command = f'peerflix "{magnet_link}" -l| vlc -'
    # command = f'peerflix -l -k "{magnet_link}"'
    # command = f'qbittorrent "{magnet_link}"'

    try:
        subprocess.run(command, shell=True, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Streaming command failed with error code: {e.returncode}")
        print("Ensure 'peerflix' and 'vlc' is installed in your computer and accessible from your computer system path.")
    except FileNotFoundError:
        print("Error: 'Peerflix' or 'vlc' command not found. Check your PATH")


def find_magnet(table, movie_id):

    if not table:
        return None

    tbody = table[0].find("tbody")
    if tbody:
        all_rows = tbody.find_all("tr")
        for row in all_rows:
            tds = row.find_all("td")
            if not tds:
                continue
            if movie_id in tds[0].text.strip():
                magnet = tds[2].find("a")
                return magnet.get("href") if magnet else None

    return None


def html_to_table(html_doc, table_index=0):

    try:
        # Wrap the whole html to StringIO,
        # instead of passing the whole html.
        df_list = pd.read_html(StringIO(html_doc))

        if not df_list:  # check if no table contains
            print("An Error Occured. Please try again later!!!")
            return None

        df = df_list[table_index]  # first table
        df.drop(columns="Actions", inplace=True)
        return df
    except Exception as e:
        print(f"An error occured: {e}")
        return None


if __name__ == "__main__":
    main()
