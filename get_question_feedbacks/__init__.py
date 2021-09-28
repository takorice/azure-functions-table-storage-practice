"""This is an Azure function to get question feedbacks."""
import logging
import os

import json
from datetime import date, datetime
from dateutil.parser import parse
import azure.functions as func
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('get_question_feedbacks function start.')

    table_service = TableService(
        account_name=os.environ.get('STORAGE_NAME'), account_key=os.environ.get('STORAGE_KEY')
    )

    # フィルタ用クエリの作成
    filter_query = ''
    # (フィルタ) レポートの開始日
    if feedback_date_from := req.params.get('feedback_date_from'):
        filter_query += "RowKey ge '{}'".format(parse(feedback_date_from).strftime('%Y_%m_%d_%H_%M_%S_%f'))
    # (フィルタ) レポートの終了日
    if feedback_date_to := req.params.get('feedback_date_to'):
        if filter_query:
            filter_query += ' and '
        filter_query += "RowKey lt '{}'".format(parse(feedback_date_to).strftime('%Y_%m_%d_23_59_59_%f'))
    # (フィルタ) 質問のType
    if question_type := req.params.get('question_type'):
        if filter_query:
            filter_query += ' and '
        filter_query += "Type eq '{}'".format(question_type)

    # Table Storage からエンティティを取得
    feedbacks = table_service.query_entities(
            'QuestionFeedbacks', filter=filter_query, num_results=1000
        )

    # レスポンスのペイロード内容
    payloads = []
    for feedback in list(feedbacks):
        payload = {}
        payload['partitionKey'] = feedback.PartitionKey
        payload['rowKey'] = feedback.RowKey
        payload['type'] = feedback.Type
        payload['question'] = feedback.Question
        payload['feedback'] = feedback.Feedback
        payload['user'] = json.loads(feedback.User) # User を JSON 形式に変換できるよう、事前にdict型へ変換する
        payloads.append(payload)

    return func.HttpResponse(
            json.dumps(list(payloads), default=json_serial),
            mimetype="application/json", status_code=200
        )

def json_serial(obj):
    """
    JSON の変換時エラーを回避する。

    Parameters
    ----------
    obj : object
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError (f'Type {obj} not serializable')
