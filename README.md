azure-functions-table-storage-practice

## 概要
Azure Functions にて、Azure Table Storage へ POST、GET する API のサンプル。
別途、以下の設定が必要。
- Azure API Management にて、各関数の API エンドポイントの設定
- 環境変数の設定 (Azure Storage にて確認)
  - STORAGE_NAME
  - STORAGE_KEY

## 技術要素
- Python
- Azure
  - Azure Functions
  - Azure Table Storage
  - Cosmos DB Table API

## サンプルの内容
質問に対するフィードバックを格納するテーブルにPOSTする。
また、テーブルに蓄積されたフィードバックをGETする。

- table
  - QuestionFeedbacks

- API
  - POST
  - GET
    - Query Parameter
      - feedback_date_from : string
        - ex) 2021-07-01
      - feedback_date_to : string
        - ex) 2021-07-30
      - question_type : string
        - ex) 説明会

