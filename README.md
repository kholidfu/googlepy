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

Fitur
-----
- Multithreading-based apps, cepat dan efisien, sekali eksekusi bisa mendapatkan sampai 10000 hasil (result).
- Tiap hasil, sudah dilengkapi dengan google suggest dan bing suggest.

Contoh Data (JSON)
-------------------
```
{u'_id': ObjectId('52cbb9ffdde3685e2057738b'),
  u'bing_suggests': [u'grammar for ielts download',
                     u'grammar for ielts',
                     u'grammar for ielts pdf',
                     u'grammar for ielts free download',
                     u'grammar for ielts with answers download',
                     u'grammar for ielts book',
                     u'grammar for ielts.pdf',
                     u'grammar for ielts cambridge',
                     u'grammar for ielts.pdf all pages'],
  u'google_suggests': [u'grammar for ielts',
                       u'grammar for ielts pdf',
                       u'grammar for ielts free download',
                       u'grammar for ielts cambridge',
                       u'grammar for ielts with answers',
                       u'grammar for ielts download',
                       u'grammar for ielts cd',
                       u'grammar for ielts ebook',
                       u'grammar for ielts audio',
                       u'grammar for ielts book'],
  u'keyword': u'grammar for ielts',
  u'snippet': u'F2-IELTS Refund of Deposit Results Form 2012-13 (120817).doc. Hong Kong \nBaptist University ... Activate Your Spoken Grammar for IELTS. P.T.O &. Form 2\xa0...',
  u'title': u'Hong Kong Baptist University Language Centre IELTS Results Form',
  u'url': u'http://lc.hkbu.edu.hk/english/ielts/download/ielts_results_form.pdf'}
```

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
