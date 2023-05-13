# Import--------------------------------------------------
import time
import os
import urllib
import datetime

# import timeout_decorator as td
import shutil
import pandas as pd
from tqdm import tqdm
from src import const
import sys
import ast

# Option--------------------------------------------------
output = const.Output()
holo_df = const.holo_df()


# Sub Funtion--------------------------------------------------
# URLを指定して画像を保存する
def download(url, save_path):
    try:
        if not os.path.exists(save_path):
            try:
                response = urllib.request.urlopen(url, timeout=10)
            except Exception as e:
                print(e)
                pass
            else:
                if response.status == 200:
                    try:
                        with open(save_path, "wb") as f:
                            f.write(response.read())
                            time.sleep(0.5)
                    except Exception as e:
                        print(e)
                        pass
    except Exception as e:
        print(e)
        pass
    finally:
        if os.path.exists(save_path):
            if os.path.getsize(save_path) == 0:
                os.remove(save_path)


# ALLでの画像保存先を取得
def get_save_path_all(url, query):
    file_name = url.split("/")[-1].split("?")[0] + ".jpg"
    save_path = os.path.join(output.image(query), "All", file_name)
    folder = os.path.dirname(save_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return save_path


# 高評価別の画像の保存先を取得
def get_good_save_path(good, image_path, query):
    file_name = os.path.basename(image_path)
    # set save path
    if good >= 2000:
        save_path = os.path.join(output.image(query), "Good", "2000_More", file_name)
    if 2000 > good and good >= 1000:
        save_path = os.path.join(output.image(query), "Good", "1000_More", file_name)
    if 1000 > good and good >= 500:
        save_path = os.path.join(output.image(query), "Good", "0500_More", file_name)
    if 500 > good:
        save_path = os.path.join(output.image(query), "Good", "0500_Under", file_name)
    return save_path


# 高評価で画像を保存する
def save_good_image(good, image_path, query):
    # get save path
    save_path = get_good_save_path(good, image_path, query)
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    # すでにほかの場所にあるか調べる
    before_image_path = ""
    for g in [2010, 1010, 510, 100]:
        test_save_path = get_good_save_path(g, image_path, query)
        if os.path.exists(test_save_path):
            before_image_path = test_save_path

    # ローカルにないならそのままsave_pathへコピー
    if before_image_path == "":
        shutil.copyfile(image_path, save_path)

    # ローカルにあってsave_pathと異なるなら新しいほうに置き換え
    if before_image_path != "" and before_image_path != save_path:
        os.remove(before_image_path)
        shutil.copyfile(image_path, save_path)


# Main Function--------------------------------------------------
def image_download(csv_path):
    file_name = os.path.basename(csv_path)
    query = file_name.replace("#", "")
    query = query.replace("_" + (query.split("_")[-1]), "")
    print(f"query : {query}")

    tweet_df = pd.read_csv(csv_path, index_col=None)
    tweet_df["images"] = [
        ast.literal_eval(d) for d in tweet_df["images"]
    ]  # images str -> list[str]

    saved = 0
    for index, row in tqdm(
        tweet_df.iterrows(), total=len(tweet_df), desc="image DL"
    ):  # 画像のダウンロード&保存処理
        images = row["images"]
        for url in images:
            save_path = get_save_path_all(url, query)
            if not os.path.exists(save_path):
                try:
                    download(url, save_path)
                except Exception as e:
                    print(e)
                    pass

            # ALLにダウンロードできた場合
            if os.path.exists(save_path):
                saved = saved + 1
                good = row["vote"]
                save_good_image(good, save_path, query)  # 高評価別で画像を保存する


def main_download():
    for index, row in tqdm(holo_df.iterrows(), desc="holo"):
        print(f"index -> {index}/{len(holo_df)}")
        fullName = row["FullName"]
        csv_path = output.database(fullName)
        image_download(csv_path)
