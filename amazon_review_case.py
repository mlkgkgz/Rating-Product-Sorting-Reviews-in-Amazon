
###################################################
# PROJE: Rating Product & Sorting Reviews in Amazon
###################################################

###################################################
# İş Problemi
###################################################

# E-ticaretteki en önemli problemlerden bir tanesi ürünlere satış sonrası verilen puanların doğru şekilde hesaplanmasıdır.
# Bu problemin çözümü e-ticaret sitesi için daha fazla müşteri memnuniyeti sağlamak, satıcılar için ürünün öne çıkması ve satın
# alanlar için sorunsuz bir alışveriş deneyimi demektir. Bir diğer problem ise ürünlere verilen yorumların doğru bir şekilde sıralanması
# olarak karşımıza çıkmaktadır. Yanıltıcı yorumların öne çıkması ürünün satışını doğrudan etkileyeceğinden dolayı hem maddi kayıp
# hem de müşteri kaybına neden olacaktır. Bu 2 temel problemin çözümünde e-ticaret sitesi ve satıcılar satışlarını arttırırken müşteriler
# ise satın alma yolculuğunu sorunsuz olarak tamamlayacaktır.

###################################################
# Veri Seti Hikayesi
###################################################

# Amazon ürün verilerini içeren bu veri seti ürün kategorileri ile çeşitli metadataları içermektedir.
# Elektronik kategorisindeki en fazla yorum alan ürünün kullanıcı puanları ve yorumları vardır.

# Değişkenler:
# reviewerID: Kullanıcı ID’si
# asin: Ürün ID’si
# reviewerName: Kullanıcı Adı
# helpful: Faydalı değerlendirme derecesi
# reviewText: Değerlendirme
# overall: Ürün rating’i
# summary: Değerlendirme özeti
# unixReviewTime: Değerlendirme zamanı
# reviewTime: Değerlendirme zamanı Raw
# day_diff: Değerlendirmeden itibaren geçen gün sayısı
# helpful_yes: Değerlendirmenin faydalı bulunma sayısı
# total_vote: Değerlendirmeye verilen oy sayısı



###################################################
# GÖREV 1: Average Rating'i Güncel Yorumlara Göre Hesaplayınız ve Var Olan Average Rating ile Kıyaslayınız.
###################################################

# Paylaşılan veri setinde kullanıcılar bir ürüne puanlar vermiş ve yorumlar yapmıştır.
# Bu görevde amacımız verilen puanları tarihe göre ağırlıklandırarak değerlendirmek.
# İlk ortalama puan ile elde edilecek tarihe göre ağırlıklı puanın karşılaştırılması gerekmektedir.


###################################################
# Adım 1: Veri Setini Okutunuz ve Ürünün Ortalama Puanını Hesaplayınız.
###################################################

import pandas as pd
import math
import scipy.stats as st
from sklearn.preprocessing import MinMaxScaler

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df = pd.read_csv("C:/Users/.../amazon_review.csv")
df.head()



# Ürünün Ortalama Puanı

#kaç benzersiz ürün var?
df["asin"].value_counts() 



# Ürünün Ortalama Puanı nedir?
df.groupby("asin").agg({"overall": "mean"})




###################################################
# Adım 2: Tarihe Göre Ağırlıklı Puan Ortalamasını Hesaplayınız.
###################################################
df.info()
df.head()
df["reviewTime"]

df["reviewTime"] = pd.to_datetime(df["reviewTime"])


df.groupby("day_diff").agg({"overall": "mean"}) #ürün ratinglerinin günlere göre ortalaması


# son 20 günde yapıln yorumlara nasıl erişirim?
df[df["day_diff"] <= 20].count() #toplam 66 adt var son 20 günde
df.loc[df["day_diff"]<=20, "overall"].mean() # son 20 gündeki yapılan yorumların ortalaması 4.74



df["day_diff"].quantile([0.25, 0.5, 0.75])

#25-50-75lik tarih dilimlerinde ürün ratinglerinin ortalaması
#0.25000   281.00000 
#0.50000   431.00000
#0.75000   601.00000




# son çeyrekte yapılan yorumlar daha çok ağırlıklandırılsın:

df.loc[df["day_diff"] <= 281, "overall"].mean() * 22/100 + \
df.loc[(df["day_diff"] > 281) & (df["day_diff"] <= 431), "overall"].mean() * 24/100 + \
df.loc[(df["day_diff"] > 431) & (df["day_diff"] <= 601), "overall"].mean() * 26/100 + \
df.loc[(df["day_diff"] > 601), "overall"].mean() * 28/100

# Out[161]: 4.57933124861244


###################################################
# Görev 2: Ürün için Ürün Detay Sayfasında Görüntülenecek 20 Review'i Belirleyiniz.
###################################################


###################################################
# Adım 1. helpful_no Değişkenini Üretiniz
###################################################

# Not:
# total_vote bir yoruma verilen toplam up-down sayısıdır.
# up, helpful demektir.
# veri setinde helpful_no değişkeni yoktur, var olan değişkenler üzerinden üretilmesi gerekmektedir.



#df["total_vote"] - df["helpful_yes"] Toplam oy sayısından (total_vote) yararlı oy sayısı (helpful_yes) çıkarılarak yararlı bulunmayan oy sayılarını (helpful_no) bulunuz.

df["helpful_no"] = df["total_vote"] - df["helpful_yes"]
df.head()



df[df['helpful_yes'] != 0].count() #413 tane yorumu faydalı (up) bulan olmuş



###################################################
# Adım 2. score_pos_neg_diff, score_average_rating ve wilson_lower_bound Skorlarını Hesaplayıp Veriye Ekleyiniz
###################################################


def score_pos_neg_diff(up, down):
    return up - down


score_pos_neg_diff(413, 4502)
#Out[158]: -4089



def score_average_rating(up, down):
    if up + down == 0:
        return 0
    return up / (up + down)

score_average_rating(413, 4502)

#Out[157]: 0.08402848423194303

def wilson_lower_bound(up, down, confidence=0.95):
    """
    Wilson Lower Bound Score hesapla

    - Bernoulli parametresi p için hesaplanacak güven aralığının alt sınırı WLB skoru olarak kabul edilir.
    - Hesaplanacak skor ürün sıralaması için kullanılır.
    - Not:
    Eğer skorlar 1-5 arasıdaysa 1-3 negatif, 4-5 pozitif olarak işaretlenir ve bernoulli'ye uygun hale getirilebilir.
    Bu beraberinde bazı problemleri de getirir. Bu sebeple bayesian average rating yapmak gerekir.

    Parameters
    ----------
    up: int
        up count
    down: int
        down count
    confidence: float
        confidence

    Returns
    -------
    wilson score: float

    """
    n = up + down
    if n == 0:
        return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * up / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)


wilson_lower_bound(413, 4502)
#Out[156]: 0.07659352131582126

df.head()


#sıralamaların herhangş bir mantık barındırıp barındırmadıgını anlamaya calısıyoruz.
# score_pos_neg_diff (ilk yöntem)
df["score_pos_neg_diff"] = df.apply(lambda x: score_pos_neg_diff(x["helpful_yes"], x["helpful_no"]), axis=1)

# score_average_rating (ikinci yöntem)
df["score_average_rating"] = df.apply(lambda x: score_average_rating(x["helpful_yes"], x["helpful_no"]), axis=1)

# wilson_lower_bound (üçüncü yöntem)
df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"], x["helpful_no"]), axis=1)

df.head()




##################################################
# Adım 3. 20 Yorumu Belirleyiniz ve Sonuçları Yorumlayınız.
###################################################
df.sort_values("wilson_lower_bound", ascending=False).head(20)
# wilson_lower_bound yöntemine göre puan durumlarını sıraladıgımızda: score_pos_neg_diff e göre 'up' ve 'down' oy sayısı arasındaki farka göre hesaplanIYORdu
# bize herhangi bir oran vermediği için bir miktar yanlılık bulunuyor. oran olmadıgı ıcın dogru bir bilgiye erişemiyorduk.

# Score = Average rating = (up ratings) / (all ratings) ile like atan oranı / bütün oranlar: likeların oranını bulur bunun zuerınden bır skor olusturuluyordu
# burada da #sayı/frekans yüksekliiğini göz önünde bulundurulamıyor. up / (up + down) ile puanlar karsılastırıdıgında bakıldıgında mantıklı bi yoruma erişemiyoduk

# WLB ile #hem oran hemde frekans bilgisi eş zamanlı olarak hesaplanabiliyordu.
# ilk index için diyebiliriz ki 1.yorumun faydalı bulunma skoru daha iyidir. 0.95




#         reviewerID        asin                          reviewerName       helpful                                         reviewText  overall                                            summary  unixReviewTime reviewTime  day_diff  helpful_yes  total_vote  helpful_no  score_pos_neg_diff  score_average_rating  wilson_lower_bound
#2031  A12B7ZMXFI6IXY  B007WTAJTO                  Hyoun Kim "Faluzure"  [1952, 2020]  [[ UPDATE - 6/19/2014 ]]So my lovely wife boug...  5.00000  UPDATED - Great w/ Galaxy S4 & Galaxy Tab 4 10...      1367366400 2013-01-05       702         1952        2020          68                1884               0.96634             0.95754
#3449   AOEAD7DPLZE53  B007WTAJTO                     NLee the Engineer  [1428, 1505]  I have tested dozens of SDHC and micro-SDHC ca...  5.00000  Top of the class among all (budget-priced) mic...      1348617600 2012-09-26       803         1428        1505          77                1351               0.94884             0.93652
#4212   AVBMZZAFEKO58  B007WTAJTO                           SkincareCEO  [1568, 1694]  NOTE:  please read the last update (scroll to ...  1.00000  1 Star reviews - Micro SDXC card unmounts itse...      1375660800 2013-05-08       579         1568        1694         126                1442               0.92562             0.91214
#317   A1ZQAQFYSXL5MQ  B007WTAJTO               Amazon Customer "Kelly"    [422, 495]  If your card gets hot enough to be painful, it...  1.00000                                Warning, read this!      1346544000 2012-02-09      1033          422         495          73                 349               0.85253             0.81858
#4672  A2DKQQIZ793AV5  B007WTAJTO                               Twister      [45, 49]  Sandisk announcement of the first 128GB micro ...  5.00000  Super high capacity!!!  Excellent price (on Am...      1394150400 2014-07-03       158           45          49           4                  41               0.91837             0.80811
#1835  A1J6VSUM80UAF8  B007WTAJTO                           goconfigure      [60, 68]  Bought from BestBuy online the day it was anno...  5.00000                                           I own it      1393545600 2014-02-28       283           60          68           8                  52               0.88235             0.78465
#3981  A1K91XXQ6ZEBQR  B007WTAJTO            R. Sutton, Jr. "RWSynergy"    [112, 139]  The last few days I have been diligently shopp...  5.00000  Resolving confusion between "Mobile Ultra" and...      1350864000 2012-10-22       777          112         139          27                  85               0.80576             0.73214
#3807   AFGRMORWY2QNX  B007WTAJTO                            R. Heisler      [22, 25]  I bought this card to replace a lost 16 gig in...  3.00000   Good buy for the money but wait, I had an issue!      1361923200 2013-02-27       649           22          25           3                  19               0.88000             0.70044
#4306   AOHXKM5URSKAB  B007WTAJTO                         Stellar Eller      [51, 65]  While I got this card as a "deal of the day" o...  5.00000                                      Awesome Card!      1339200000 2012-09-06       823           51          65          14                  37               0.78462             0.67033
#4596  A1WTQUOQ4WG9AI  B007WTAJTO           Tom Henriksen "Doggy Diner"     [82, 109]  Hi:I ordered two card and they arrived the nex...  1.00000     Designed incompatibility/Don't support SanDisk      1348272000 2012-09-22       807           82         109          27                  55               0.75229             0.66359
#315   A2J26NNQX6WKAU  B007WTAJTO            Amazon Customer "johncrea"      [38, 48]  Bought this card to use with my Samsung Galaxy...  5.00000  Samsung Galaxy Tab2 works with this card if re...      1344816000 2012-08-13       847           38          48          10                  28               0.79167             0.65741
#1465   A6I8KXYK24RTB  B007WTAJTO                              D. Stein        [7, 7]  I for one have not bought into Google's, or an...  4.00000                                           Finally.      1397433600 2014-04-14       238            7           7           0                   7               1.00000             0.64567
#1609  A2TPXOZSU1DACQ  B007WTAJTO                                Eskimo        [7, 7]  I have always been a sandisk guy.  This cards ...  5.00000                  Bet you wish you had one of these      1395792000 2014-03-26       257            7           7           0                   7               1.00000             0.64567
#4302  A2EL2GWJ9T0DWY  B007WTAJTO                             Stayeraug      [14, 16]  So I got this SD specifically for my GoPro Bla...  5.00000                        Perfect with GoPro Black 3+      1395360000 2014-03-21       262           14          16           2                  12               0.87500             0.63977
#4072  A22GOZTFA02O2F  B007WTAJTO                           sb21 "sb21"        [6, 6]  I used this for my Samsung Galaxy Tab 2 7.0 . ...  5.00000               Used for my Samsung Galaxy Tab 2 7.0      1347321600 2012-11-09       759            6           6           0                   6               1.00000             0.60967
#1072  A2O96COBMVY9C4  B007WTAJTO                        Crysis Complex        [5, 5]  What more can I say? The 64GB micro SD works f...  5.00000               Works wonders for the Galaxy Note 2!      1349395200 2012-05-10       942            5           5           0                   5               1.00000             0.56552
#2583  A3MEPYZVTAV90W  B007WTAJTO                               J. Wong        [5, 5]  I bought this Class 10 SD card for my GoPro 3 ...  5.00000                  Works Great with a GoPro 3 Black!      1370649600 2013-08-06       489            5           5           0                   5               1.00000             0.56552
#121   A2Z4VVF1NTJWPB  B007WTAJTO                                A. Lee        [5, 5]  Update: providing an update with regard to San...  5.00000                     ready for use on the Galaxy S3      1346803200 2012-05-09       943            5           5           0                   5               1.00000             0.56552
#1142  A1PLHPPAJ5MUXG  B007WTAJTO  Daniel Pham(Danpham_X @ yahoo.  com)        [5, 5]  As soon as I saw that this card was announced ...  5.00000                          Great large capacity card      1396396800 2014-02-04       307            5           5           0                   5               1.00000             0.56552
#1753   ALPLKR59QMBUX  B007WTAJTO                             G. Becker        [5, 5]  Puchased this card right after I received my S...  5.00000                    Use Nothing Other Than the Best      1350864000 2012-10-22       777            5           5           0                   5               1.00000             0.56552







