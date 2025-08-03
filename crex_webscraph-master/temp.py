import pandas as pd
from lxml import etree


def writting_the_xapth(html_content):
    tree = etree.HTML(html_content)
    four_thing_xapth = tree.xpath("//div[@class='table-heading']/h3")
    for ele in four_thing_xapth:
        if ele.text.lower() == 'batting':
            header = tree.xpath("//tr[th[text()='Batter']]/th/text()")
            header.insert(1, 'Type')
            batting_df = pd.DataFrame(columns=header)
            cntaner_xpath = tree.xpath(
                "//h3[text()='Batting']/ancestor::div[contains(@class, 'table-heading')]/following-sibling::div[contains(@class, 'score-card')]")
            batting = cntaner_xpath[0]
            rows = batting.xpath(".//tbody/tr")
            for row in rows:
                row_data = row.xpath(".//td//text()")
                batting_df = pd.concat([batting_df, pd.DataFrame([row_data], columns=batting_df.columns)],
                                       ignore_index=True)

    extras = tree.xpath("//div[@class='run-rate']//span[text()='Extras:']/ancestor::div[@class='run-rate']//div[@class='runs c-rate-or-extras']//span/text()")
    header_xpath = tree.xpath("//h3[text()='BOWLING']/ancestor::div[contains(@class, 'table-heading')]" +
                              "/following-sibling::div[contains(@class, 'score-card')]" +
                              "//table[contains(@class, 'bowler-table')]//tr[th[text()='Bowler']]/th/text()")
    header = [h.strip() for h in header_xpath]
    df_bowler = pd.DataFrame(columns=header)
    # Get bowling container
    bowling_xpath = tree.xpath("//h3[text()='BOWLING']/ancestor::div[contains(@class, 'table-heading')]" +
                               "/following-sibling::div[contains(@class, 'score-card')]")
    if not bowling_xpath:
        print("No bowling section found!")
        return df_bowler

    bowling_container = bowling_xpath[0]

    # Extract all rows from bowling table
    rows = bowling_container.xpath(".//table[contains(@class, 'bowler-table')]//tbody/tr")
    for row in rows:
        row_data = []
        cells = row.xpath(".//td")
        for cell in cells:
            # Get clean text from each cell
            text = ' '.join(cell.xpath(".//text()")).strip()
            row_data.append(text)

        # Only add row if it matches header length
        if len(row_data) == len(header):
            df_bowler = pd.concat([df_bowler, pd.DataFrame([row_data], columns=df_bowler.columns)], ignore_index=True)

    header_xpath = "//div[contains(@class, 'table-heading')]/h3[text()='FALL OF WICKETS']/following-sibling::div[contains(@class, 'card score-card')]//table[contains(@class, 'bowler-table')]/thead/tr/th/text()"
    header = [h.strip() for h in tree.xpath(header_xpath)]
    fow_df = pd.DataFrame(columns=header)

    rows_xpath = "//div[contains(@class, 'table-heading')]/h3[text()='FALL OF WICKETS']/following-sibling::div[contains(@class, 'card score-card')]//table[contains(@class, 'bowler-table')]/tbody/tr"
    rows = tree.xpath(rows_xpath)

    for row in rows:
        row_data = []
        cells = row.xpath(".//td//text()")
        cell_texts = [text.strip() for text in cells if text.strip()]

        if cell_texts:
            batsman = cell_texts[0]
            score = cell_texts[1] if len(cell_texts) > 1 else ""
            overs = cell_texts[2] if len(cell_texts) > 2 else ""
            row_data = [batsman, score, overs]

            if len(row_data) == len(header):
                fow_df = pd.concat([fow_df, pd.DataFrame([row_data], columns=fow_df.columns)], ignore_index=True)

    yet_df = pd.DataFrame(columns=['Player Name', 'Average'])

    players_xpath = "//div[contains(@class, 'heading')]/h3[text()='Yet to bat']" + \
                    "/following-sibling::div[contains(@class, 'yet-to-bat')]//div[contains(@class, 'custom-width')]"
    players = tree.xpath(players_xpath)

    for player in players:
        name_nodes = player.xpath(".//div[contains(@class, 'player-data')]//div[contains(@class, 'name')]/text()")
        name = name_nodes[0].strip() if name_nodes else "Unknown Player"

        avg_nodes = player.xpath(".//div[contains(@class, 'player-data')]//p/span/text()")
        avg = avg_nodes[0].strip() if avg_nodes else "N/A"

        row_data = [name, avg]

        if len(row_data) == len(yet_df.columns):
            yet_df = pd.concat([yet_df, pd.DataFrame([row_data], columns=yet_df.columns)], ignore_index=True)

    return [batting_df, df_bowler , fow_df, yet_df]


