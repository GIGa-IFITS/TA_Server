import os
import connection
import base64
import json

from flask import request, jsonify, send_file, redirect
from sqlalchemy.orm import Session, sessionmaker, mapper
from model import ResponseData, Serialisasi


# app configuration
app = connection.config.app #config app
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['TESTING'] = True
app.config['DEBUG'] = True
imagedir = './dir/www/'

cursor = connection.config.conn.cursor()

@app.before_request
def before_request():
    if not request.is_secure and app.env != "development":
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)

def Base64Encoder(string):
    with open(string, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string

# ketika di main menu
@app.route("/",methods=['GET','POST'])
def index():
    try : 
        # mengambil jumlah jurnal, conference, books, thesis, paten dan research yang ada
        temp_row = None
        arrayHasilPublikasiITS = []
        # jurnal, konferensi, buku, tesis, patent, penelitian = 0, 0, 0, 0, 0, 0
        cursor.execute('SELECT SUM(journals) AS journals FROM ta.visualisasi_data.mapping_temp_dosen;')
        for row in cursor :
            x = Serialisasi(journals = row.journals)
            temp_row = x.__dict__
            arrayHasilPublikasiITS.append(temp_row)
        
        cursor.execute('SELECT SUM(conferences) AS conferences FROM ta.visualisasi_data.mapping_temp_dosen;')
        for row in cursor :
            x = Serialisasi(conferences = row.conferences)
            temp_row = x.__dict__
            arrayHasilPublikasiITS.append(temp_row)
        
        cursor.execute('SELECT SUM(books) AS books FROM ta.visualisasi_data.mapping_temp_dosen;')
        for row in cursor :
            x = Serialisasi(books = row.books)
            temp_row = x.__dict__
            arrayHasilPublikasiITS.append(temp_row)
        
        cursor.execute('SELECT SUM(thesis) AS thesis FROM ta.visualisasi_data.mapping_temp_dosen;')
        for row in cursor :
            x = Serialisasi(thesis = row.thesis)
            temp_row = x.__dict__
            arrayHasilPublikasiITS.append(temp_row)

        cursor.execute('SELECT SUM(paten) AS paten FROM ta.visualisasi_data.mapping_temp_dosen;')
        for row in cursor :
            x = Serialisasi(paten = row.paten)
            temp_row = x.__dict__
            arrayHasilPublikasiITS.append(temp_row)

        cursor.execute('SELECT SUM(research) AS research FROM ta.visualisasi_data.mapping_temp_dosen;')
        for row in cursor :
            x = Serialisasi(research = row.research)
            temp_row = x.__dict__
            arrayHasilPublikasiITS.append(temp_row)

        result = {}
        result['hasil_publikasi'] = arrayHasilPublikasiITS

        resultDashboard = {}
        resultDashboard['dashboard_data'] = [result]
        result_len = len(arrayHasilPublikasiITS)
        all_data = [resultDashboard]
        response = ResponseData("200","Data Berhasil Ditemukan", all_data, result_len)
        response = json.dumps(response.__dict__)
        return str(response)

    except Exception as e:
        if hasattr(e, 'message'):
            data = [e]
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 001",data, result_len)
            response = json.dumps(response.__dict__)
            return str(response)
        else:
            data = []
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 002",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)

@app.route('/peneliti', methods=['GET'])
def Peneliti():
    try:
        if request.method == 'GET':
            
            abjadDict = {}
            abjadSort = request.args.get('abjad')
            # topSort = request.args.get('top')
            facultySort = request.args.get('fakultas')
            deptSort = request.args.get('departemen')

            # print(abjadSort, topSort, facultySort, deptSort)
            ## APABILA TIDAK ADA ARGUMEN ABJAD YANG INGIN DIKELOMPOKKAN, MAKA HASILNYA
            ## ADALAH TOTAL MASING-MASING INISIAL AWAL
            if abjadSort != None :
                if abjadSort == 'none' :
                    temp_row = None
                    arrayPeneliti = []
                    
                    cursor.execute('SELECT peg.nama FROM ta.visualisasi_data.tmst_pegawai as peg;')
     
                    for row in cursor :
                        
                        if row.nama is None : continue
                        firstLetter = nameInitial(row.nama.upper())
                        isAdded = False
                        if len(abjadDict) == 0 :
                            abjadDict[firstLetter] = 1

                        else :
                            for abjad in abjadDict.keys() :
                                if abjad == firstLetter :
                                    abjadDict[abjad] = abjadDict[abjad] + 1
                                    isAdded = True
                                    break

                            if isAdded == False :
                                abjadDict[firstLetter] = 1

                    for abjad in abjadDict.keys() :
                        x = Serialisasi(inisial = abjad,
                                        total = abjadDict[abjad])
                        temp_row = x.__dict__
                        arrayPeneliti.append(temp_row)
                    
                    ## DEBUG
                    ## BAGIAN INI UNTUK MELIHAT ABJAD YANG TELAH TERSIMPAN DAN
                    ## JUMLAHNYA 
                    # print(abjadDict.keys())
                    # print(abjadDict.values())
                    # total = 0
                    # for jumlahAbjad in abjadDict.values():
                    #     total += jumlahAbjad
                    # print(total)

                    listPeneliti = {}
                    listPeneliti['inisial_peneliti'] = arrayPeneliti

                else :
                    temp_row = None
                    arrayPeneliti = []
                    
                    cursor.execute("SELECT peg.nama, peg.kode as kode, COUNT(pub.id) as jumlah FROM ta.visualisasi_data.tmst_publikasi as pub INNER JOIN ta.visualisasi_data.tmst_pegawai as peg ON peg.kode = pub.kode_dosen WHERE peg.nama LIKE '"+str(abjadSort.upper())+"%' GROUP BY peg.kode, peg.nama ORDER BY peg.kode;")

                    for row in cursor :
                        if row.nama is None : continue
                        x = Serialisasi(kode_dosen = row.kode,
                                        nama = row.nama,
                                        jumlah = row.jumlah)
                        temp_row = x.__dict__
                        arrayPeneliti.append(temp_row)

                    listPeneliti = {}
                    listPeneliti['nama_peneliti'] = arrayPeneliti
            
            if facultySort != None :
                if facultySort == 'none' :
                    temp_row = None
                    arrayPeneliti = []
                    cursor.execute("SELECT peg.kode_fakultas, fak.nama_inggris, COUNT(peg.kode) as jumlah FROM ta.visualisasi_data.tmst_pegawai as peg, ta.visualisasi_data.tmst_fakultas_baru as fak WHERE fak.kode = peg.kode_fakultas GROUP BY peg.kode_fakultas, fak.nama_inggris")
                    print("Fakultas=None")
                    
                    for row in cursor :
                        x = Serialisasi(kode_fakultas = row.kode_fakultas,
                                        nama_fakultas = row.nama_inggris,
                                        jumlah = row.jumlah)
                        temp_row = x.__dict__
                        arrayPeneliti.append(temp_row)
                    
                    listPeneliti = {}
                    listPeneliti['fakultas_peneliti'] = arrayPeneliti

                else :
                
                    temp_row = None
                    arrayPeneliti = []
                    cursor.execute("SELECT peg.kode_fakultas, fak.nama_inggris as nama_fakultas, peg.kode_jurusan, jur.nama_inggris as nama_departemen, count(peg.kode_jurusan) as fakultas_publikasi  FROM ta.visualisasi_data.tmst_pegawai as peg INNER JOIN ta.visualisasi_data.tmst_fakultas_baru as fak ON peg.kode_fakultas = fak.kode INNER JOIN ta.visualisasi_data.tmst_jurusan_baru as jur ON peg.kode_jurusan = jur.kode WHERE peg.kode_fakultas = "+str(facultySort)+" GROUP BY peg.kode_fakultas, peg.kode_jurusan, jur.nama_inggris, fak.nama_inggris")
                    print("Fakultas=Available, Departement=None")

                    for row in cursor :
                        x = Serialisasi(kode_fakultas = row.kode_fakultas,
                                        nama_fakultas = row.nama_fakultas,
                                        kode_departemen = row.kode_jurusan,
                                        nama_departemen = row.nama_departemen,
                                        jumlah = row.fakultas_publikasi
                                        )
                        temp_row = x.__dict__
                        arrayPeneliti.append(temp_row)
                    
                    listPeneliti = {}
                    listPeneliti['departemen_peneliti'] = arrayPeneliti

            if deptSort != None :
                    
                temp_row = None
                arrayPeneliti = []
                cursor.execute("SELECT peg.nama, peg.kode as kode, jur.nama_inggris as nama_departemen, peg.kode_jurusan as kode_jurusan, COUNT(pub.id) as jumlah  FROM ta.visualisasi_data.tmst_publikasi as pub INNER JOIN ta.visualisasi_data.tmst_pegawai as peg ON peg.kode = pub.kode_dosen INNER JOIN ta.visualisasi_data.tmst_jurusan_baru as jur ON jur.kode = peg.kode_jurusan WHERE peg.kode_jurusan = "+str(deptSort)+" GROUP BY peg.kode, peg.nama, peg.kode_jurusan, jur.nama_inggris ORDER BY peg.kode_jurusan;")
                print("Fakultas=Available, Departement=Available")

                for row in cursor :
                    x = Serialisasi(kode_dosen = row.kode,
                                    nama_departemen = row.nama_departemen,
                                    nama = row.nama,
                                    jumlah = row.jumlah
                                    )
                    temp_row = x.__dict__
                    arrayPeneliti.append(temp_row)
                
                listPeneliti = {}
                listPeneliti['nama_peneliti'] = arrayPeneliti

        data_len = len(arrayPeneliti)
        all_data = [listPeneliti]

        response = ResponseData("200","Data Berhasil Ditemukan", all_data, data_len)
        response = json.dumps(response.__dict__)

        return str(response)

    except Exception as e:
        if hasattr(e, 'message'):
            data = [e]
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 005",e, data_len)
            response = json.dumps(response.__dict__)
            return str(response)
        else:
            data = []
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 006",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)

def nameInitial(name):
    for letter in name :
        if letter == ' ' : continue
        else : return letter

# @app.route('/fakultas')

@app.route('/gelar', methods=['GET'])
def gelarPeneliti():
    try:
        if request.method == 'GET':

            gelarDict = {}

            temp_row = None
            id_target = request.args.get('kode')
            if id_target == "none" :

                arrayGelar = []
                cursor.execute("SELECT kode_jenjang_pendidikan as jenjang_pendidikan, COUNT(kode_jenjang_pendidikan) as jumlah FROM ta.visualisasi_data.tmst_pegawai GROUP BY kode_jenjang_pendidikan") 
                
                for row in cursor :
                    
                    jenis_gelar = row.jenjang_pendidikan
                    jumlah_gelar = row.jumlah

                    x = Serialisasi(gelar = jenis_gelar,
                                    jumlah = jumlah_gelar)
                    temp_row = x.__dict__
                    arrayGelar.append(temp_row)
                    
                listGelar = {}
                listGelar['gelar_peneliti'] = arrayGelar

            else :
                
                arrayGelar = []
                cursor.execute("SELECT peg.nama, peg.kode as kode,peg.kode_jenjang_pendidikan as pendidikan, COUNT(pub.id) as jumlah FROM ta.visualisasi_data.tmst_publikasi as pub INNER JOIN ta.visualisasi_data.tmst_pegawai as peg ON peg.kode = pub.kode_dosen WHERE peg.kode_jenjang_pendidikan = '"+str(id_target)+"' GROUP BY peg.kode, peg.nama, peg.kode_jenjang_pendidikan ORDER BY peg.kode_jenjang_pendidikan;")
                
                for row in cursor :
                    
                    nama = row.nama
                    kode = row.kode
                    pendidikan = row.pendidikan
                    jumlah = row.jumlah

                    x = Serialisasi(nama = nama,
                                    kode_dosen = kode,
                                    pendidikan_dosen = pendidikan,
                                    jumlah = jumlah
                                    )

                    temp_row = x.__dict__
                    arrayGelar.append(temp_row)

                listGelar = {}
                listGelar['nama_peneliti'] = arrayGelar

            data_len = len(arrayGelar)
            all_data = [listGelar]

        response = ResponseData("200","Data Berhasil Ditemukan", all_data, data_len)
        response = json.dumps(response.__dict__)
            
        return str(response)
    
    except Exception as e:
        if hasattr(e, 'message'):
            data = [e]
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 001",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)
        else:
            data = []
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 002",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)

@app.route('/publikasi', methods=['GET'])
def publikasi():
    try:
        if request.method == 'GET':

            temp_row = None
            kode_fakultas = request.args.get('fakultas')
            kata_kunci = request.args.get('katakunci')
            kode_publikasi = request.args.get('publikasi')
            if kode_fakultas == "none" :

                arrayLaboratorium = []
                cursor.execute("SELECT peg.kode_fakultas, fak.nama_inggris, COUNT(peg.kode_fakultas) as jumlah_publikasi from ta.visualisasi_data.tmst_publikasi as pub INNER JOIN ta.visualisasi_data.tmst_pegawai as peg ON peg.kode = pub.kode_dosen INNER JOIN ta.visualisasi_data.tmst_fakultas_baru as fak ON fak.kode = peg.kode_fakultas GROUP BY peg.kode_fakultas, fak.nama_inggris ORDER BY peg.kode_fakultas;")
                # print(departemen_kode)
                
                for row in cursor :
                    
                    fakultas_lab = row.kode_fakultas
                    nama_fakultas = row.nama_inggris
                    jumlah_publikasi = row.jumlah_publikasi

                    x = Serialisasi(kode_fakultas = fakultas_lab,
                                    nama_fakultas = nama_fakultas,
                                    jumlah = jumlah_publikasi
                                    )

                    temp_row = x.__dict__
                    arrayLaboratorium.append(temp_row)
                    
                listLaboratorium = {}
                listLaboratorium['fakultas_peneliti'] = arrayLaboratorium

                # print(listGelar)

            else :
                
                if kata_kunci == None :

                    arrayLaboratorium = []
                    # cursor.execute("SELECT lab.kode_jurusan as fakultas, lab.kode_fakultas as kode_jurusan, jurbar.nama_inggris, COUNT(anglab.kode_pegawai) as jumlah  FROM ta.visualisasi_data.tmst_laboratorium_baru as lab  INNER JOIN ta.visualisasi_data.anggota_labs as anglab ON anglab.kode_labs = lab.kode INNER JOIN ta.visualisasi_data.tmst_jurusan_baru as jurbar ON lab.kode_fakultas = jurbar.kode WHERE lab.kode_jurusan = "+str(id_target)+" GROUP BY lab.kode_fakultas, lab.kode_jurusan, jurbar.nama_inggris ORDER BY lab.kode_jurusan;")
                    cursor.execute("SELECT katkun.kode_fakultas, fak.nama_inggris as nama_fakultas, katkun.kata, katkun.idf, katkun.df from ta.visualisasi_data.tmst_bobot_kata_kunci as katkun INNER JOIN ta.visualisasi_data.tmst_fakultas_baru as fak ON katkun.kode_fakultas = fak.kode WHERE katkun.kode_fakultas = "+str(kode_fakultas)+";")

                    
                    for row in cursor :
                        
                        kode_fakultas = row.kode_fakultas
                        nama_fakultas = row.nama_fakultas
                        kata = row.kata
                        idf = row.idf
                        df = row.df

                        x = Serialisasi(kode_fakultas = kode_fakultas,
                                        nama_fakultas = nama_fakultas,
                                        kata_kunci = kata,
                                        idf = idf,
                                        df = df
                                        )

                        temp_row = x.__dict__
                        arrayLaboratorium.append(temp_row)

                    listLaboratorium = {}
                    listLaboratorium['fakultas_publikasi'] = arrayLaboratorium

                else :
                    
                    if kode_publikasi == None :

                        arrayLaboratorium = []
                        # cursor.execute("SELECT lab.kode_fakultas as jurusan, lab.kode_jurusan as fakultas, COUNT(anglab.kode_pegawai) as jumlah, lab.nama_inggris FROM ta.visualisasi_data.tmst_laboratorium_baru as lab INNER JOIN ta.visualisasi_data.anggota_labs as anglab ON anglab.kode_labs = lab.kode WHERE lab.kode_fakultas = "+str(departemen_kode)+" GROUP BY lab.kode_fakultas, lab.kode_jurusan, lab.nama_inggris ORDER BY lab.kode_jurusan")
                        cursor.execute("SELECT pub.kode_dosen, peg.nama, COUNT(pub.judul) as jumlah_publikasi FROM ta.visualisasi_data.tmst_publikasi as pub INNER JOIN ta.visualisasi_data.tmst_pegawai as peg ON peg.kode = pub.kode_dosen WHERE pub.judul LIKE '%"+str(kata_kunci)+"%' AND peg.kode_fakultas = "+str(kode_fakultas)+"GROUP BY peg.nama, kode_dosen ")

                        for row in cursor :
                            
                            kode_dosen = row.kode_dosen
                            nama_dosen = row.nama
                            jumlah_publikasi = row.jumlah_publikasi

                            x = Serialisasi(kode_dosen = kode_dosen,
                                            nama = nama_dosen,
                                            jumlah = jumlah_publikasi
                                            )

                            temp_row = x.__dict__
                            arrayLaboratorium.append(temp_row)

                        listLaboratorium = {}
                        listLaboratorium['nama_peneliti'] = arrayLaboratorium

                    else :

                        arrayLaboratorium = []

            data_len = len(arrayLaboratorium)
            all_data = [listLaboratorium]

        response = ResponseData("200","Data Berhasil Ditemukan", all_data, data_len)
        response = json.dumps(response.__dict__)
            
        return str(response)
    
    except Exception as e:
        if hasattr(e, 'message'):
            data = [e]
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 001",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)
        else:
            data = []
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 002",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)

@app.route('/detailpeneliti', methods=['GET'])
def detailPeneliti():
    try:
        if request.method == 'GET':
            temp_row = None
            id_target = request.args.get('id_peneliti')
            arrayDetailPeneliti = []
            cursor.execute('SELECT peg.nama AS nama_dosen, peg.tanggal_lahir as tanggal_lahir, fak.nama_inggris AS nama_fakultas, jur.nama_inggris AS nama_jurusan, maptemp.journals, maptemp.conferences, maptemp.books, maptemp.thesis, maptemp.paten, maptemp.research FROM ta.visualisasi_data.tmst_pegawai AS peg  INNER JOIN ta.visualisasi_data.tmst_fakultas_baru AS fak ON (peg.kode_fakultas = fak.kode)  INNER JOIN ta.visualisasi_data.tmst_jurusan_baru AS jur ON (peg.kode_jurusan = jur.kode) INNER JOIN ta.visualisasi_data.mapping_temp_dosen AS maptemp ON (peg.kode = maptemp.kode_pegawai) WHERE peg.kode = '+str(id_target)+';') 
            for row in cursor :
                total_publikasi = int(row.journals) + int(row.conferences) + int(row.books) + int(row.thesis) + int(row.paten) + int(row.research)
                x = Serialisasi(nama = row.nama_dosen,
                                tanggal_lahir = row.tanggal_lahir,
                                fakultas = row.nama_fakultas,
                                departemen = row.nama_jurusan,
                                jurnal = row.journals,
                                konferensi = row.conferences,
                                buku = row.books,
                                tesis = row.thesis,
                                paten = row.paten,
                                penelitian = row.research,
                                totalpublikasi = total_publikasi)
                # x = Serialisasi(nama = row.nama_dosen,
                #                 fakultas = row.nama_fakultas)
                temp_row = x.__dict__
                arrayDetailPeneliti.append(temp_row)

            detailPeneliti = {}
            detailPeneliti['detail_peneliti'] = arrayDetailPeneliti
            data_len = len(arrayDetailPeneliti)
            all_data =[detailPeneliti]

            response = ResponseData("200","Data Berhasil Ditemukan", all_data, data_len)
            response = json.dumps(response.__dict__)
            
        return str(response)
    
    except Exception as e:
        if hasattr(e, 'message'):
            data = [e]
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 001",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)
        else:
            data = []
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 002",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)

@app.route('/publikasipeneliti', methods=['GET'])
def publikasiPeneliti():
    try:
        if request.method == 'GET':
            temp_row = None

            # print("a")

            id_target = request.args.get('id_publikasi')
            arrayPublikasiPeneliti = []
            cursor.execute("SELECT peg.nama, peg.kode as kode, pub.kode_publikasi, pub.judul, pub.tahun, pub.abstraksi FROM ta.visualisasi_data.tran_publikasi_dosen_tetap as pub INNER JOIN ta.visualisasi_data.tmst_pegawai as peg ON peg.kode = pub.kode_pegawai WHERE peg.kode = '"+str(id_target)+"';")
           
            for row in cursor :
                kode_publikasi = row.kode_publikasi
                nama_publikasi = row.judul
                tahun = row.tahun
                abstraksi = row.abstraksi

                x = Serialisasi(kode_publikasi = kode_publikasi,
                                nama_publikasi = nama_publikasi,
                                tahun = tahun,
                                abstraksi = abstraksi
                                )

                temp_row = x.__dict__
                arrayPublikasiPeneliti.append(temp_row)
            
            listPublikasi = {}
            listPublikasi['nama_publikasi'] = arrayPublikasiPeneliti

        data_len = len(arrayPublikasiPeneliti)
        all_data = [listPublikasi]

        response = ResponseData("200","Data Berhasil Ditemukan", all_data, data_len)
        response = json.dumps(response.__dict__)
                
        return str(response)

    except Exception as e:
        if hasattr(e, 'message'):
            data = [e]
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 001",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)
        else:
            data = []
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 002",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)

# cek testing
@app.route("/version",methods=['GET','POST'])
def testing():
    try :

        cursor.execute('SELECT @@VERSION;')
        row = cursor.fetchone()
        return str(row)

    except Exception as e:
        if hasattr(e, 'message'):
            data = [e]
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 001",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)
        else:
            data = []
            data_len = ""
            response = ResponseData("500","Terjadi Kesalahan Pada Server, 002",data, data_len)
            response = json.dumps(response.__dict__)
            return str(response)