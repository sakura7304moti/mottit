from . import const,utils

output = const.Output()
driver = utils.init_driver()
image_driver = utils.init_driver()

def base_scraper(fullName:str,first_name:str,last_name:str=None):
    url = utils.page_url(first_name,last_name)
    df = utils.get_df(driver,image_driver,url)
    df_save_path = output.database(fullName)
    df.to_csv(df_save_path)
    return df

def main_scraper():
    df = const.holo_df()
    for index, row in df.iterrows():
        print(f'index {index + 1}/{len(df)}')
        fullName = row.FullName
        firstName = row.FirstName
        lastName = row.LastName

        base_scraper(fullName,firstName,lastName)