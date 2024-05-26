# 非同步課程內容摘要

今天的非同步課程主要涵蓋了UDP和TCP的socket programming。以下是詳細內容摘要：

## UDP的實作
- 客戶端先透過socket傳送訊息給server端，server端處理後回傳給客戶端。
- 客戶端使用`recvfrom`等待接收server端傳來的資料。
- Server端使用`bind`方法綁定特定的port，並等待客戶端連線。
- 客戶端接收到資料後，將文字轉成大寫並顯示，然後關閉socket。

## TCP的實作
- TCP需要先建立連線，客戶端與server端通過建立連線進行訊息傳送。
- 客戶端先傳送訊息給server端，server端處理後回傳給客戶端。
- 客戶端使用`send`方法傳送資料，不需要再指定對象。
- Server端等待客戶端連線，建立新的socket來處理資料的傳送和接收。

以上是今天非同步課程的內容摘要，涵蓋了UDP和TCP的socket programming實作過程。希望對您有所幫助。若有任何問題，歡迎提出。祝您學習愉快！
