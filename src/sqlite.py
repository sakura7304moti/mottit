from . import const
from .utils import message

output = const.Output()

"""
CREATE DB
"""
import sqlite3

# sns.dbを作成する
# すでに存在していれば、それにアスセスする。
dbname = output.sqlite_db()
conn = sqlite3.connect(dbname)

# データベースへのコネクションを閉じる。(必須)
conn.close()

"""
CREATE TABLE
"""
conn = sqlite3.connect(dbname)
# sqliteを操作するカーソルオブジェクトを作成
cur = conn.cursor()

# personsというtableを作成してみる
# 大文字部はSQL文。小文字でも問題ない。
cur.execute(
    """CREATE TABLE IF NOT EXISTS reddit(
            fullName STIRNG,
            firstName STRING,
            lastName STRING,
            url STRING,
            images STRING,
            videos STRING,
            vote INTEGER
            )
            """
)

# データベースへコミット。これで変更が反映される。
conn.commit()
conn.close()

"""
INSERT
"""
import re
import pandas as pd
import os
from tqdm import tqdm
import datetime
from . import const
from . import utils

output = const.Output()


def update(fullName: str, firstName: str, lastName: str):
    # 正規表現パターン
    pattern = r'[\'"\[\]]'

    # データベースに接続する
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    # csv読み込み
    csv_path = output.database(fullName)
    fullName = fullName.replace("'", "")
    firstName = firstName.replace("'", "")
    lastName = lastName.replace("'", "")
    df = pd.read_csv(csv_path)

    # レコードの存在をチェックするためのクエリを作成する
    check_query = f"SELECT * FROM reddit WHERE fullName = '{fullName}'"

    # クエリを実行して結果を取得する
    cursor.execute(check_query)
    result = cursor.fetchall()

    # fullName + URL のリストを作成
    if result is None:
        hash_list = []
    else:
        hash_list = [r[0] + r[3] for r in result]

    for index, row in tqdm(df.iterrows(), total=len(df), desc="INSERT"):
        # 要素の取得
        url = row["url"]
        images = row["images"]
        images = re.sub(pattern, "", images)
        videos = row["videos"]
        videos = re.sub(pattern, "", videos)
        vote = row["vote"]

        # レコードが存在しない場合は追加、存在する場合は更新する
        if fullName + url not in hash_list:
            # レコードを追加するクエリを作成する
            insert_query = f"""
                INSERT INTO reddit (fullName,firstName,lastName,url,images,videos,vote)
                VALUES ('{fullName}','{firstName}','{lastName}','{url}','{images}','{videos}',{vote})"""

            # レコードを追加する
            cursor.execute(insert_query)

    # 変更をコミットし、接続を閉じる
    conn.commit()
    conn.close()


"""
SELECT PAGE
"""


def searchQuery(
    page_no: int = 1,
    page_size: int = 30,
    fullName: str = "",
    firstName: str = "",
    lastName: str = "",
    min_like: int = 0,
    max_like: int = 0,
):
    # ページング設定
    offset = (max(page_no - 1, 0)) * page_size

    query = "SELECT * FROM reddit where 1 = 1 "
    if fullName != "":
        query = query + "and fullName like :fullName "
    if firstName != "":
        query = query + "and firstName like :firstName "
    if lastName != "":
        query = query + "and lastName like :lastName "
    if min_like != 0:
        query = query + "and vote >= :min_like "
    if max_like != 0:
        query = query + "and :max_like >= vote "
    query = query + "order by fullName desc,url "
    if page_size != 0:
        limit_sql = "limit :page_size offset :offset"
        query = query + limit_sql

    args = {
        "fullName": f"%{fullName}%",
        "firstName": f"%{firstName}%",
        "lastName": f"%{lastName}%",
        "min_like": min_like,
        "max_like": max_like,
        "page_size": page_size,
        "offset": offset,
    }
    return query, args


def search(
    page_no: int = 1,
    page_size: int = 30,
    fullName: str = "",
    firstName: str = "",
    lastName: str = "",
    min_like: int = 0,
    max_like: int = 0,
) -> list[const.RedditQueryRecord]:
    # データベースに接続する
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    # SELECTクエリを実行
    query, args = searchQuery(
        page_no, page_size, fullName, firstName, lastName, min_like, max_like
    )
    cursor.execute(query, args)
    results = cursor.fetchall()

    # 結果を表示
    records = []
    for row in results:
        rec = const.RedditQueryRecord(*row)
        records.append(rec)

    # 接続を閉じる
    conn.close()
    return records


"""
SEARCH COUNT
"""


def search_count(
    fullName: str = "",
    firstName: str = "",
    lastName: str = "",
    min_like: int = 0,
    max_like: int = 0,
):
    query, args = searchQuery(1, 0, fullName, firstName, lastName, min_like, max_like)

    # データベースに接続する
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    # 件数のみ取得
    count_query = f"select count(*) from ({query})"
    cursor.execute(count_query, args)
    results = cursor.fetchall()

    return results[0][0]


"""
UPDATE ALL
"""


def update_all():
    try:
        df = const.holo_df()
        for index, row in df.iterrows():
            message(f"update start {row.FullName}")
            print(f"index {index + 1}/{len(df)}")
            fullName = row.FullName
            firstName = row.FirstName
            lastName = row.LastName

            if type(firstName) == float:
                firstName = ""
            if type(lastName) == float:
                lastName = ""

            update(
                fullName,
                firstName,
                lastName,
            )
            message(f"update end {row.FullName}")
    except Exception as e:
        print(e)
        utils.message(e)
