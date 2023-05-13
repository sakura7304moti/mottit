from . import const, utils

output = const.Output()
driver = utils.init_driver()
image_driver = utils.init_driver()


def base_scraper(fullName: str, first_name, last_name: str = None):
    if type(first_name) == float:
        first_name = fullName
    if type(last_name) == float:
        last_name = None

    url = utils.page_url(first_name, last_name)
    df = utils.get_df(driver, image_driver, url)
    df_save_path = output.database(fullName)
    df.to_csv(df_save_path)
    return df


def main_scraper():
    df = const.holo_df()
    for index, row in df.iterrows():
        print(f"index {index + 1}/{len(df)}")
        fullName = row.FullName
        firstName = row.FirstName
        lastName = row.LastName

        if type(firstName) == float:
            firstName = fullName
        if type(lastName) == float:
            lastName = None

        base_scraper(fullName, firstName, lastName)
