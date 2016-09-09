# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Personel, User
from zengine.lib.test_utils import BaseTestCase
from ulakbus.lib.ogrenci import aktif_sinav_listesi
from ulakbus.lib.date_time_helper import map_etkinlik_hafta_gunleri
import time


class TestCase(BaseTestCase):
    def test_okutman_sinav_programi_goruntule(self):

        user = User.objects.get(username='ogretim_elemani_2')
        # Giriş yapılan user'ın personeli bulunur.
        personel = Personel.objects.get(user=user)
        # Personelden ilgili öğretim görevlisi bulunur.
        okutman = personel.okutman
        okutman_adi = okutman.__unicode__()

        # Öğretim görevlisinin güncel dönemde yayınlanmış ve
        # aktif sınav etkinlikleri bulunur.
        sinav_etkinlikleri = aktif_sinav_listesi(okutman)

        for i in range(2):

            # Testi çalıştırılacak iş akışı seçilir.
            self.prepare_client('/okutman_sinav_programi_goruntule', user=user)

            # İlk test yayınlanmış sınav etkinliğinin olmaması durumudur.
            # Bu yüzden Sınav Etkinliği modelinin published fieldı False yapılır.

            # İkinci test yayınlanmış sınav etkinliğinin olması durumudur.
            # Bu yüzden Sınav Etkinliği modelinin published fieldı True yapılır.

            cond = False if i == 0 else True

            for etkinlik in sinav_etkinlikleri:
                etkinlik.published = cond
                etkinlik.save()

            time.sleep(1)

            resp = self.client.post()

            # Yayınlanmış sınav etkinliği bulunmaması durumunda Uyarı vermesi beklenir.
            if i == 0:
                assert resp.json['msgbox']['title'] == "Uyarı!"

            else:

                # Öğretim görevlisinin güncel dönemde aktif şube
                # sayısının 4 olması beklenir.
                assert len(okutman.donem_subeleri()) == 4

                # Sınav etkinlikleri sayısının 4 olması beklenir.
                assert len(sinav_etkinlikleri) == 4

                # Sınav etkinliklerinin tarihe göre küçükten büyüğe sıralandığı
                # kontrol edilir.
                assert sinav_etkinlikleri[0].tarih <= sinav_etkinlikleri[-1].tarih

                etkinlikler = map_etkinlik_hafta_gunleri(sinav_etkinlikleri)

                # Sınav etkinliklerinin etkinlikler sözlüğü içerisinde istenildiği
                # gibi yerleştirildiği kontrol edilir.
                for etkinlik in sinav_etkinlikleri:
                    assert etkinlik.tarih.isoweekday() in etkinlikler
                    assert etkinlik.__unicode__() in etkinlikler[etkinlik.tarih.isoweekday()]

                # Yayınlanmış sınav etkinliği olması durumunda öğretim görevlisinin adının
                # bulunduğu bir sınav takvimi gösterilmesi beklenir.
                assert okutman_adi in resp.json['forms']['schema']["title"]

                etkinlik_sayisi = 0

                for i in range(1, len(resp.json['objects'])):
                    for k, day in enumerate(resp.json['objects'][i]['fields']):
                        if resp.json['objects'][i]['fields'][day]:
                            # Ekranda gösterilen sınav etkinliklerinin istenildiği gibi
                            # gösterildiği kontrol edilir.
                            assert resp.json['objects'][i]['fields'][day] == etkinlikler[k + 1][i - 1]
                            etkinlik_sayisi += 1

                # Ekranda gösterilen sınav etkinliklerinin sayısının veri tabanından
                # dönen etkinlik sayısıyla eşit olduğu kontrol edilir.
                assert etkinlik_sayisi == len(sinav_etkinlikleri)
