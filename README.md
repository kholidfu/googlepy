googlepy
========
Skrip python untuk mengambil google search result, 100 hasil untuk setiap
keyword.

Penggunaan
-----------
$ python app.py

Requirements
-------
- beautifulsoup4
- gevent
- greenlet
- pymongo

Ujicoba
-------
- Sekali request 20 keywords (2000 results) berhasil di localhost
- Sekali request 100 keywords (10000 results) gagal dikarenakan modem gak kuat

Alur
-----
- Mengumpulkan database keywords
- Menggunakan database keywords di atas, kita lakukan query ke Google, 100 keywords tiap query, kemudian jeda 10 menit


Todo
-------
- Mengingat nantinya jumlah data akan sangat besar, sebaiknya ketika proses insert tidak perlu mengecek apakah data sebelumnya sudah ada atau belum, tetapi langsung insert saja, nantinya akan dibuat skrip tersendiri untuk menghilangkan data yang ganda dan dijalankan ketika server sedang tidak sibuk.
- Atau bahkan data ini tidak kita jadikan satu dengan web server, melainkan ditaruh dalam sebuah server tersendiri yang terpisah, sehingga proses query cukup menggunakan API call saja.
- Efficient mongodb update with unique id
http://stackoverflow.com/questions/3815633/pymongo-a-more-efficient-update