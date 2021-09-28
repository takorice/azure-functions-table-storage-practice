"""This is an Azure function to post question feedback."""
import logging
import os

import json
from datetime import datetime, timedelta, timezone
import azure.functions as func
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('post_question_feedbacks function start.')

    table_service = TableService(
        account_name=os.environ.get('STORAGE_NAME'), account_key=os.environ.get('STORAGE_KEY')
    )

    try:
        # リクエストのbodyデータを取得
        data = req.get_json().get('data')
        question_feedback = {
            'PartitionKey' : str(data["staffId"]),
            'Type' : data["type"],
            'Question' : data["question"],
            'Feedback' : data["feedback"],
            'User' : json.dumps(data["user"], ensure_ascii=False) # 日本語をエスケープしない
        }
    except (ValueError, AttributeError, KeyError) as err:
        print('Error occurred. error = {}'.format(err))
        question_feedback = None

    if question_feedback:
        for _ in range(3):
            try:
                # RowKey をセット (現在時刻のミリ秒までの値)
                question_feedback["RowKey"] = datetime.now(timezone(timedelta(hours=+9), 'JST')).strftime('%Y_%m_%d_%H_%M_%S_%f')

                # フィードバックを Storage Table へ登録
                table_service.insert_entity(
                    'QuestionFeedbacks', question_feedback
                )
            except Exception as err:
                logging.debug('Error occurred. error = {}'.format(err))
                # 最大3回までリトライを実施
                pass
            else:
                return func.HttpResponse(
                    json.dumps({
                        "message": "Registered"
                    }),
                    status_code=200
                )
    # リクエストのbodyデータの取得で問題があった場合
    return func.HttpResponse(
        json.dumps({
            "message": "Request body data is invalid."
        }),
        mimetype="application/json",
        status_code=422
    )
